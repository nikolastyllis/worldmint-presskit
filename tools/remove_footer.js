// presskit ends every page with a footer crediting presskit.html and presskit(). This removes it.
// Run after `presskit build`.

const fs = require('fs');
const path = require('path');

const buildFolder = path.join(__dirname, '..', 'build');

for (const folder of ['', 'penal-penguins']) {
  const page = path.join(buildFolder, folder, 'index.html');
  const html = fs.readFileSync(page, 'utf8');
  fs.writeFileSync(page, html.replace(/\s*<footer class="page-footer">[\s\S]*?<\/footer>/, ''));
  console.log(`- "${folder || 'company'}" has no footer`);
}
