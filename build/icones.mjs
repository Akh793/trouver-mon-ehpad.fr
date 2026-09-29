// Rend favicon.svg en PNG : Google Search n'accepte pas le SVG comme favicon (formats listés :
// BMP, GIF, ICO, PNG, JPEG…), l'écran d'accueil iOS attend un apple-touch-icon 180×180,
// et le logo de l'Organization doit être une image matricielle.   node build/icones.mjs
import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
import fs from 'fs';
const svg = fs.readFileSync(new URL('../site/favicon.svg', import.meta.url), 'utf8');
const b = await chromium.launch();
for (const [f, n] of [['favicon-48.png', 48], ['favicon-96.png', 96], ['favicon-192.png', 192], ['apple-touch-icon.png', 180], ['assets/logo-512.png', 512]]) {
  const p = await b.newPage({ viewport: { width: n, height: n }, deviceScaleFactor: 1 });
  await p.setContent(`<html><body style="margin:0;background:transparent">${svg.replace('<svg ', `<svg width="${n}" height="${n}" `)}</body></html>`);
  await p.screenshot({ path: new URL('../site/' + f, import.meta.url).pathname, omitBackground: true, clip: { x: 0, y: 0, width: n, height: n } });
  await p.close(); console.log(f, n);
}
await b.close();
