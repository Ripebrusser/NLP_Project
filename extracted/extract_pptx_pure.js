const fs = require('fs');
const path = require('path');

// Minimal regex-based XML text extractor for PPTX slide XML.
// Strips tags, keeps text in <a:t> and similar, preserving order.
function extractText(xml) {
  // Remove XML comments
  let s = xml.replace(/<!--[\s\S]*?-->/g, '');
  // Replace self-closing breaks and placeholders with newline placeholders
  s = s.replace(/<a:br\s*\/?>/gi, '\n');
  // Match text inside any <...>text</...> but mostly <a:t>
  // Approach: remove all tags but capture text within them in order by replacing tags with space, then normalize whitespace.
  // Better: extract all <a:t>...</a:t> and <a:ph> etc text, plus any other inner text
  const texts = [];
  // find all occurrences of <a:t ...>...</a:t>
  const reT = /<a:t[^>]*>([\s\S]*?)<\/a:t>/gi;
  let m;
  while ((m = reT.exec(s)) !== null) {
    const t = m[1].replace(/<[^>]+>/g, '').trim();
    if (t) texts.push(t);
  }
  // In case some text is in other elements (e.g. a:set, drawings), fallback: remove tags and grab remaining text
  if (texts.length === 0) {
    const noTags = s.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
    if (noTags) texts.push(noTags);
  }
  return texts;
}

function readSlides(dir) {
  const files = fs.readdirSync(dir).filter(f=>/^slide\d+\.xml$/.test(f));
  files.sort((a,b)=>{
    const na = parseInt(a.replace(/\D/g,''),10), nb=parseInt(b.replace(/\D/g,''),10);
    return na-nb;
  });
  const results = {};
  for (const f of files) {
    const xml = fs.readFileSync(path.join(dir,f),'utf8');
    results[f] = extractText(xml);
  }
  return results;
}

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
