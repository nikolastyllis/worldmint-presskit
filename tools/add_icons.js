// presskit only links each page's favicon.ico. This adds PNG and Apple touch icons for browsers that
// prefer them, and a favicon.ico at the root of the site for browsers that look there first. Run
// after `presskit build`.

const fs = require('fs');
const path = require('path');

const iconFolder = path.join(__dirname, 'assets', 'icons');
const buildFolder = path.join(__dirname, '..', 'build');
// Every page uses the WorldMint icons, so search results show the studio's logo for each of them.
const pages = ['', 'penal-penguins'];

fs.copyFileSync(path.join(buildFolder, 'images', 'favicon.ico'), path.join(buildFolder, 'favicon.ico'));

for (const folder of pages) {
  const images = path.join(buildFolder, folder, 'images');
  fs.copyFileSync(path.join(iconFolder, 'worldmint.png'), path.join(images, 'icon.png'));
  fs.copyFileSync(path.join(iconFolder, 'worldmint-apple-touch.png'), path.join(images, 'apple-touch-icon.png'));

  const page = path.join(buildFolder, folder, 'index.html');
  const links = '<link rel="icon" type="image/png" sizes="192x192" href="images/icon.png">\n'
    + '    <link rel="apple-touch-icon" href="images/apple-touch-icon.png">\n    ';
  const html = fs.readFileSync(page, 'utf8');
  fs.writeFileSync(page, html.replace('<link rel="shortcut icon"', `${links}<link rel="shortcut icon"`));
  console.log(`- "${folder || 'company'}" uses the WorldMint icons`);
}
