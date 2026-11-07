// Adds a hash of each stylesheet to the links that load it, so browsers fetch the new stylesheet as
// soon as it changes instead of using a cached copy. Run after the other build steps.

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const buildFolder = path.join(__dirname, '..', 'build');
const cssFolder = path.join(buildFolder, 'css');

function pages(folder) {
  return fs.readdirSync(folder, { withFileTypes: true }).flatMap((entry) => {
    const entryPath = path.join(folder, entry.name);
    if (entry.isDirectory()) return pages(entryPath);
    return entry.name.endsWith('.html') ? [entryPath] : [];
  });
}

const hashes = {};
for (const file of fs.readdirSync(cssFolder).filter((name) => name.endsWith('.css'))) {
  const contents = fs.readFileSync(path.join(cssFolder, file));
  hashes[file] = crypto.createHash('sha256').update(contents).digest('hex').slice(0, 10);
}

for (const page of pages(buildFolder)) {
  const html = fs.readFileSync(page, 'utf8');
  const versioned = html.replace(/href="([^"?]*css\/([^"/?]+\.css))"/g, (link, href, file) =>
    hashes[file] ? `href="${href}?v=${hashes[file]}"` : link);
  fs.writeFileSync(page, versioned);
  console.log(`- "${path.relative(buildFolder, page)}" stylesheets versioned`);
}
