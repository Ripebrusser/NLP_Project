const fs = require('fs');
const path = require('path');

// Minimal XLSX reader: read sharedStrings.xml and a sheetN.xml, output rows as TSV lines.
// Handles <si><t>text</t></si> (possibly with rich runs) and <c r="A1" t="s"><v>idx</v></c>

function stripNs(tag) {
  return tag.replace(/^<\w+:/,'<').replace(/\/>$/,'/>').replace(/^<\/?/,'<?').replace(/([\s>])/,'$1');
}

function parseSharedStrings(xml) {
  const map = [];
  // Match <x:si> ... </x:si> allowing any prefix or no prefix
  const reSi = /<[\w:]*si[^>]*>([\s\S]*?)<\/[\w:]*si>/gi;
  let m;
  while ((m = reSi.exec(xml)) !== null) {
    const inner = m[1];
    // join all <t>...</t> within this si (rich text runs), allow xml:space
    const reT = /<[\w:]*t([\s\S]*?)>([\s\S]*?)<\/[\w:]*t>/gi;
    let parts = [];
    let tm;
    while ((tm = reT.exec(inner)) !== null) {
      parts.push(tm[2]);
    }
    if (parts.length === 0) {
      // maybe whitespace-only or empty si
      const ws = inner.replace(/<[\w:]*[^>]*>/g,'').trim();
      if (ws) parts.push(ws);
    }
    map.push(parts.join(''));
  }
  return map;
}

function parseSheet(xml, shared) {
  // rows: <x:row r="1" ...>...<x:c ...>...</x:c>...</x:row>
  const rows = [];
  const reRow = /<[\w:]*row[^>]*>([\s\S]*?)<\/[\w:]*row>/gi;
  let m;
  while ((m = reRow.exec(xml)) !== null) {
    const inner = m[1];
    const cells = {};
    const reCell = /<[\w:]*c\b([^>]*)>([\s\S]*?)<\/[\w:]*c>/gi;
    let cm;
    while ((cm = reCell.exec(inner)) !== null) {
      const attrs = cm[1];
      const innerC = cm[2];
      const rMatch = attrs.match(/r="([A-Z]+\d+)"/);
      const tMatch = attrs.match(/t="([^"]+)"/);
      const ref = rMatch ? rMatch[1] : null;
      const t = tMatch ? tMatch[1] : 'n';
      let val = '';
      if (t === 's') {
        // shared string index
        const vM = innerC.match(/<[\w:]*v>([\s\S]*?)<\/[\w:]*v>/i);
        if (vM) {
          const idx = parseInt(vM[1],10);
          if (!isNaN(idx) && shared[idx] !== undefined) val = shared[idx];
        }
      } else if (t === 'str') {
        const vM = innerC.match(/<[\w:]*v>([\s\S]*?)<\/[\w:]*v>/i);
        if (vM) val = vM[1];
      } else if (t === 'inlineStr') {
        const isM = innerC.match(/<[\w:]*is>[\s\S]*?<[\w:]*t[^>]*>([\s\S]*?)<\/[\w:]*t>/i);
        if (isM) val = isM[1];
      } else {
        const vM = innerC.match(/<[\w:]*v>([\s\S]*?)<\/[\w:]*v>/i);
        if (vM) val = vM[1];
      }
      if (ref) cells[ref] = val;
    }
    rows.push(cells);
  }
  return rows;
}

function colToIdx(col) {
  let n = 0;
  for (let i=0;i<col.length;i++){
    n = n*26 + (col.charCodeAt(i)-'A'.charCodeAt(0)+1);
  }
  return n-1;
}

function rowsToTsv(rows) {
  if (!rows.length) return '';
  // find max col
  let maxCol = 0;
  for (const r of rows) {
    for (const ref of Object.keys(r)) {
      const m = ref.match(/^([A-Z]+)(\d+)$/);
      if (m) maxCol = Math.max(maxCol, colToIdx(m[1]));
    }
  }
  const lines = [];
  for (const r of rows) {
    const arr = new Array(maxCol+1).fill('');
    for (const ref of Object.keys(r)) {
      const m = ref.match(/^([A-Z]+)(\d+)$/);
      if (m) {
        const idx = colToIdx(m[1]);
        arr[idx] = r[ref];
      }
    }
    lines.push(arr.join('\t'));
  }
  return lines.join('\n');
}

function sheetFileNameToNum(name) {
  const m = name.match(/sheet(\d+)\.xml$/);
  return m ? parseInt(m[1],10) : null;
}

if (require.main === module) {
  const xlsxDir = process.argv[2];
  const outBase = process.argv[3] || 'xlsx_out';
  fs.mkdirSync(outBase, { recursive: true });
  // shared strings
  let shared = [];
  try {
    const ss = fs.readFileSync(path.join(xlsxDir,'xl','sharedStrings.xml'),'utf8');
    shared = parseSharedStrings(ss);
    console.log('shared strings count:', shared.length);
  } catch(e) {
    console.log('no sharedStrings.xml');
  }
  // workbook.xml for sheet names
  let sheetNames = {};
  try {
    const wb = fs.readFileSync(path.join(xlsxDir,'xl','workbook.xml'),'utf8');
    const reName = /<sheet\b[^>]*name="([^"]*)"[^>]*sheetId="(\d+)"[^>]*r:id="(rId\d+)"/gi;
    let m;
    while ((m = reName.exec(wb)) !== null) {
      sheetNames[m[3]] = m[1];
    }
    // fallback: find all sheet name attributes
    if (Object.keys(sheetNames).length === 0) {
      const re2 = /<sheet\b[^>]*name="([^"]*)"[^>]*\/?>/gi;
      while ((m = re2.exec(wb)) !== null) sheetNames['?'+m[0]] = m[1];
    }
  } catch(e) {}
  // rels to map rId to target
  let rels = {};
  try {
    const relsXml = fs.readFileSync(path.join(xlsxDir,'xl','_rels','workbook.xml.rels'),'utf8');
    const reR = /Id="(rId\d+)"[^>]*Target="([^"]*)"/g;
    let rm;
    while ((rm = reR.exec(relsXml)) !== null) {
      rels[rm[1]] = rm[2];
    }
  } catch(e) {}
  // worksheets
  const wsDir = path.join(xlsxDir,'xl','worksheets');
  if (!fs.existsSync(wsDir)) { console.log('no worksheets dir'); return; }
  const files = fs.readdirSync(wsDir).filter(f=>/^sheet\d+\.xml$/.test(f));
  files.sort((a,b)=>{
    const na=parseInt(a.match(/\d+/)[0],10), nb=parseInt(b.match(/\d+/)[0],10);
    return na-nb;
  });
  for (const f of files) {
    const num = sheetFileNameToNum(f);
    const xml = fs.readFileSync(path.join(wsDir,f),'utf8');
    const rows = parseSheet(xml, shared);
    const label = sheetNames['rId'+(num===1?'1':'?')] || ('sheet'+num);
    // try map from rels
    let nameMapped = 'Sheet'+num;
    const target = rels['rId'+num];
    if (target) {
      const base = path.basename(target, '.xml');
      nameMapped = base || ('Sheet'+num);
    }
    const outPath = path.join(outBase, nameMapped+'.tsv');
    fs.writeFileSync(outPath, rowsToTsv(rows), 'utf8');
    console.log('wrote', outPath, 'rows:', rows.length);
  }
}
