// presskit labels the company page's contact email "Press / Business contact:". This relabels it
// "Press contact:". Run after `presskit build`.

const fs = require('fs');
const path = require('path');

const buildFolder = path.join(__dirname, '..', 'build');

for (const folder of ['', 'penal-penguins']) {
  const page = path.join(buildFolder, folder, 'index.html');
  const html = fs.readFileSync(page, 'utf8');
  fs.writeFileSync(page, html.replaceAll('Press / Business contact:', 'Press contact:'));
  console.log(`- "${folder || 'company'}" labels its contact "Press contact:"`);
}
