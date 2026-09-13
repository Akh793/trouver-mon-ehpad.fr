import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch(); const p = await b.newPage({ viewport:{width:1280,height:900} });
await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
await p.waitForTimeout(1000);
await (await p.$('.grid4')).scrollIntoViewIfNeeded(); await p.waitForTimeout(400);
await p.type('#cp','01500'); await p.waitForTimeout(1500);
// on survole la cellule voisine pour la transformer, puis on regarde qui est devant
await p.hover('.grid4 .fld:nth-child(2)'); await p.waitForTimeout(400);
console.log(JSON.stringify(await p.evaluate(()=>{
  const dd=document.getElementById('cp-dd'); const r=dd.getBoundingClientRect();
  const pts=[[r.left+30,r.top+15],[r.left+30,(r.top+r.bottom)/2],[r.left+30,r.bottom-10]];
  return { hauteur:Math.round(r.height), dansLaVue: r.bottom < innerHeight,
    points: pts.map(([x,y])=>{const e=document.elementFromPoint(x,y);
      return e ? (e.closest('#cp-dd') ? 'liste' : 'MASQUE:'+(e.className||e.tagName)) : 'hors vue';}) };
})), null, 1);
await p.screenshot({path:'grille-dd.png'});
await b.close();
