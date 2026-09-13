import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch();

// tactile : aucun etat colle
const m = await b.newPage({ viewport:{width:390,height:844}, isMobile:true, hasTouch:true });
await m.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
await m.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
await m.fill('#cp','69003'); await m.fill('#revenus','1600'); await m.waitForTimeout(3200);
console.log('tactile — transform applique :', await m.evaluate(()=>{
  const f=document.querySelector('.grid4 .fld'), r=document.querySelector('#liste .res');
  return { fld:getComputedStyle(f).transform, res: r?getComputedStyle(r).transform:'-' };
}) && JSON.stringify(await m.evaluate(()=>({
  fld:getComputedStyle(document.querySelector('.grid4 .fld')).transform,
  res:getComputedStyle(document.querySelector('#liste .res')||document.body).transform}))));
const de = await m.evaluate(()=>({doc:document.documentElement.scrollWidth, vue:document.documentElement.clientWidth}));
console.log('largeur doc/vue :', JSON.stringify(de));
await (await m.$('.grid4')).scrollIntoViewIfNeeded(); await m.waitForTimeout(300);
await m.screenshot({path:'grille-390.png'});
await m.close();

// theme sombre
const d = await b.newPage({ viewport:{width:1280,height:900}, colorScheme:'dark' });
await d.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
await d.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
await d.waitForTimeout(1200);
await (await d.$('.grid4')).scrollIntoViewIfNeeded();
await d.hover('.grid4 .fld:nth-child(3)'); await d.waitForTimeout(400);
await (await d.$('.grid4')).screenshot({path:'grille-sombre.png'});
console.log('sombre — cellule survolee :', JSON.stringify(await d.evaluate(()=>{
  const c=document.querySelectorAll('.grid4 .fld')[2], cs=getComputedStyle(c);
  return { fond:cs.backgroundColor, bordure:cs.borderColor.split(' ')[0], transform:cs.transform };
})));
await d.close();
await b.close();
