const fs = require('fs');
const path = require('path');
const zlib = require('zlib');
const { Buffer } = require('buffer');

// Synchronous inflate via zlib
function inflateSync(buf) {
  const z = new zlib.Deflate(); // placeholder
}

// Use zlib.createInflateSync
function inflateSync2(buf) {
  let result = null;
  try {
    result = zlib.createInflateSync().end(buf);
  } catch(e) {
    try { result = zlib.inflateSync(buf); } catch(e2) { throw e2; }
  }
  return result;
}

// Simple zip reader using built-in zlib.inflateSync (no deps beyond zlib/buffer)

function parseZipCentralDirectory(data) {
  // Returns { entries: [{name, compMethod, compressedSize, uncompressedSize, localHeaderOffset}] }
  const entries = [];
  let pos = 0;
  // find end of central directory
  const eocdSig = 0x06054b50;
  let eocdOff = -1;
  for (let i = data.length - 22; i >= 0; i--) {
    const sig = data.readUInt32LE(i);
    if (sig === eocdSig) { eocdOff = i; break; }
  }
  if (eocdOff < 0) throw new Error('No EOCD');
  const diskNum = data.readUInt16LE(eocdOff + 4);
  const cdDisk = data.readUInt16LE(eocdOff + 6);
  const numEntries = data.readUInt16LE(eocdOff + 8);
  const cdSize = data.readUInt32LE(eocdOff + 12);
  const cdOffset = data.readUInt32LE(eocdOff + 16);
  let off = cdOffset;
  for (let i = 0; i < numEntries; i++) {
    const sig = data.readUInt32LE(off);
    if (sig !== 0x02014b50) throw new Error('Bad central dir entry at '+off);
    const verMade = data.readUInt16LE(off+4);
    const verNeeded = data.readUInt16LE(off+6);
    const flags = data.readUInt16LE(off+8);
    const compMethod = data.readUInt16LE(off+10);
    const lastMod = data.readUInt32LE(off+12);
    const crc = data.readUInt32LE(off+16);
    const compSize = data.readUInt32LE(off+20);
    const uncompSize = data.readUInt32LE(off+24);
    const nameLen = data.readUInt16LE(off+28);
    const extraLen = data.readUInt16LE(off+30);
    const commentLen = data.readUInt16LE(off+32);
    const diskStart = data.readUInt16LE(off+34);
    const intAttr = data.readUInt16LE(off+36);
    const extAttr = data.readUInt32LE(off+38);
    const localHeaderOffset = data.readUInt32LE(off+42);
    const nameBuf = data.slice(off+46, off+46+nameLen);
    const name = Buffer.from(nameBuf).toString('utf8');
    entries.push({ name, compMethod, compSize, uncompSize, localHeaderOffset, crc, flags });
    off += 46 + nameLen + extraLen + commentLen;
  }
  return entries;
}

function inflatorSync(buf) {
  try {
    return zlib.inflateSync(buf);
  } catch(e) {
    throw new Error('inflate failed: '+e.message);
  }
}

function readEntry(buf, entry) {
  const off = entry.localHeaderOffset;
  const sig = buf.readUInt32LE(off);
  if (sig !== 0x04034b50) throw new Error('Bad local header at '+off);
  const compMethod = buf.readUInt16LE(off+8);
  const compSize = buf.readUInt32LE(off+18);
  const nameLen = buf.readUInt16LE(off+26);
  const extraLen = buf.readUInt16LE(off+28);
  const compData = buf.slice(off+30+nameLen+extraLen, off+30+nameLen+extraLen+compSize);
  if (compMethod === 8) {
    return inflatorSync(compData);
  } else if (compMethod === 0) {
    return compData;
  } else {
    throw new Error('Unsupported compression '+compMethod);
  }
}

async function listZip(zipPath) {
  const buf = fs.readFileSync(zipPath);
  const entries = parseZipCentralDirectory(buf);
  for (const e of entries) {
    console.log(e.name);
  }
}

async function extractXlsxSheetNames(zipPath) {
  const buf = fs.readFileSync(zipPath);
  const entries = parseZipCentralDirectory(buf);
  const names = entries.map(e=>e.name).filter(n=>n.startsWith('xl/workbook.xml')||n.startsWith('xl/worksheets/') || n.startsWith('xl/sharedStrings') || n.startsWith('xl/_rels/workbook.xml.rels'));
  for (const n of names) console.log(n);
}

async function extractXlsxAll(zipPath, outDir) {
  const buf = fs.readFileSync(zipPath);
  const entries = parseZipCentralDirectory(buf);
  for (const e of entries) {
    const raw = readEntry(buf, e);
    const outPath = path.join(outDir, e.name);
    fs.mkdirSync(path.dirname(outPath), { recursive: true });
    fs.writeFileSync(outPath, raw);
  }
  console.log('extracted to', outDir);
}

if (require.main === module) {
  const cmd = process.argv[2];
  const arg = process.argv[3];
  const arg2 = process.argv[4];
  if (cmd === 'list') listZip(arg);
  else if (cmd === 'sheets') extractXlsxSheetNames(arg);
  else if (cmd === 'extract') extractXlsxAll(arg, arg2);
}

module.exports = { parseZipCentralDirectory, readEntry };
