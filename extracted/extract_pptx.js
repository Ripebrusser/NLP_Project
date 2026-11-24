const fs = require('fs');
const path = require('path');
const xml2js = require('fast-xml-parser');

function extractTextFromSlide(xml) {
  // Parse and find all text nodes inside pptx slide xml
  // namespace-aware: a:t, a:r, etc.
  let texts = [];
  function walk(node) {
    if (!node || typeof node !== 'object') return;
    if (Array.isArray(node)) {
      node.forEach(walk);
      return;
    }
    // If it's a leaf with #text
    if (node['#text'] !== undefined) {
      const t = (node['#text']||'').trim();
      if (t) texts.push(t);
    }
    for (const k of Object.keys(node)) {
      if (k === '$') continue;
      walk(node[k]);
    }
  }
  // The xml parser returns {root:{...}} 
  walk(xml);
  return texts;
}

function readSlides(dir) {
  const files = fs.readdirSync(dir).filter(f=>f.startsWith('slide') && f.endsWith('.xml') && !f.includes('_rels'));
  files.sort((a,b)=>{
    const na = parseInt(a.match(/\d+/)[0]), nb=parseInt(b.match(/\d+/)[0]);
    return na-nb;
  });
  const parser = new xml2js.XMLParser({ignoreAttributes:false, attributeNamePrefix:'@_', isArray:(name, jpath, isAttribute)=>{
    // make common repeatable elements arrays
    if (['a:sp','a:r','a:p','a:t','a:br','a:pic','a:bodyPr','a:ln','a:solidFill','a:srgbClr','a:choice','a:schemeClr','a:prstGeom','a:off','a:ext','a:xfrm','a:blip','a:stretch','a:fill','a:lnRef','a:fillRef','a:effectLst','a:effectDag','a:headEnd','a:tailEnd','a:lat','a:lnLgToCtr','a:lnCtToBx','a:lnCtrToBg'].includes(name)) return true;
    return false;
  }});
  const results = {};
  for (const f of files) {
    const xml = fs.readFileSync(path.join(dir,f),'utf8');
    const parsed = parser.parse(xml);
    results[f] = extractTextFromSlide(parsed);
  }
  return results;
}

if (require.main === module) {
  const dir = process.argv[2];
  const out = process.argv[3];
  const res = readSlides(dir);
  let outText = '';
  for (const [f, texts] of Object.entries(res)) {
    outText += `\n=== ${f} ===\n`;
    outText += texts.join('\n');
  }
  if (out) fs.writeFileSync(out, outText, 'utf8');
  else console.log(outText);
} else {
  module.exports = { readSlides, extractTextFromSlide };
}
