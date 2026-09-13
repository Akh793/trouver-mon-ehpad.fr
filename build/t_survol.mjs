import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch();
const p = await b.newPage({ viewport:{width:1280,height:900} });
const errs=[]; p.on('pageerror', e=>errs.push(e.message));
await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
await p.fill('#cp','69003'); await p.fill('#revenus','1600'); await p.waitForTimeout(3200);
await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); document.activeElement.blur(); });
await p.waitForTimeout(400);

// grille au repos
const g = await p.$('.grid4'); await g.scrollIntoViewIfNeeded(); await p.waitForTimeout(300);
await g.screenshot({path:'grille-repos.png'});

// grille avec la 3e cellule survolee
await p.hover('.grid4 .fld:nth-child(3)'); await p.waitForTimeout(400);
await g.screenshot({path:'grille-survol.png'});
const t = await p.evaluate(()=>{
  const c=document.querySelectorAll('.grid4 .fld')[2];
  return { transform:getComputedStyle(c).transform, ombre:getComputedStyle(c).boxShadow.slice(0,40),
           bordure:getComputedStyle(c).borderColor };
});
console.log('cellule survolee :', JSON.stringify(t));

// focus : le mouvement doit cesser
await p.click('#revenus'); await p.hover('.grid4 .fld:nth-child(4)'); await p.waitForTimeout(400);
console.log('cellule au focus :', JSON.stringify(await p.evaluate(()=>{
  const c=document.querySelectorAll('.grid4 .fld')[3];
  return { transform:getComputedStyle(c).transform, zIndex:getComputedStyle(c).zIndex };
})));

// liste deroulante des communes au-dessus des voisines
await p.fill('#cp',''); await p.type('#cp','6900'); await p.waitForTimeout(600);
await p.type('#cp','3'); await p.waitForTimeout(900);
console.log('liste communes :', JSON.stringify(await p.evaluate(()=>{
  const dd=document.getElementById('cp-dd');
  if (!dd || dd.hidden) return 'fermee';
  const r=dd.getBoundingClientRect();
  const dessus=document.elementFromPoint(r.left+20, r.top+10);
  return { visible:true, h:Math.round(r.height), auDessus: dessus ? (dessus.closest('#cp-dd')?'la liste':'MASQUEE par '+dessus.className) : null };
})));
console.log('ERREURS', errs.length, errs.slice(0,3));
await b.close();
