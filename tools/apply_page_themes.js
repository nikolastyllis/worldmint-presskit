// presskit builds every page with the same theme. This gives each product page with a matching
// theme/<product folder>.css its own theme instead, run after `presskit build`.

const fs = require('fs');
const path = require('path');

const themeFolder = path.join(__dirname, '..', 'theme');
const buildFolder = path.join(__dirname, '..', 'build');

for (const file of fs.readdirSync(themeFolder)) {
  const product = path.basename(file, '.css');
  const page = path.join(buildFolder, product, 'index.html');
  if (!fs.existsSync(page)) continue;

  fs.copyFileSync(path.join(themeFolder, file), path.join(buildFolder, 'css', file));
  const html = fs.readFileSync(page, 'utf8');
  fs.writeFileSync(page, html.replace('href="../css/theme.css"', `href="../css/${file}"`));
  console.log(`- "${product}" uses theme/${file}`);
}
