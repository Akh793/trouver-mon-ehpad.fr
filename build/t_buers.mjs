import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch(); const p = await b.newPage();
p.on('pageerror', e => console.log('ERR', e.message));
await p.goto('http://127.0.0.1:8899/index.html', { waitUntil: 'domcontentloaded' });
await p.fill('#cp', '69100'); await p.fill('#revenus', '1600');
await p.waitForTimeout(3000);
const out = await p.evaluate(() => {
  const F = '690025192';
  // accès au moteur via une recherche dans les données chargées
  const rows = window.ME_DEBUG ? null : null;
  return new Promise(r => {
    const card = document.querySelector('[data-fin="'+F+'"]');
    r({ trouve: !!card, texte: card ? card.innerText.replace(/\s+/g,' ').slice(0,300) : null });
  });
});
console.log(JSON.stringify(out,null,1));
await b.close();
