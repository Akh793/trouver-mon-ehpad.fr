import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch();
const ok = (c,t)=>console.log((c?'✅':'❌')+' '+t);
for (const w of [1440,1280,1100,1024,900,700,390]) {
  const p = await b.newPage({ viewport:{width:w,height:1000} });
  await p.goto('http://127.0.0.1:8899/retours/', { waitUntil:'networkidle' });
  await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(300);
  const d = await p.evaluate(() => {
    const pos = s => { const e=document.querySelector(s); if(!e) return null;
      const r=e.getBoundingClientRect(); return Math.round(r.top+scrollY); };
    const l = document.querySelector('.lead');
    return { lignes: Math.round(l.getBoundingClientRect().height / parseFloat(getComputedStyle(l).lineHeight)),
             lead: pos('.lead'), avert: pos('.avert'), liste: pos('.r-liste'),
             fsrc: document.querySelector('.f-src') ? 'PRESENT' : null,
             garde: !!document.querySelector('#form-retour .fld-h b'),
             deborde: document.documentElement.scrollWidth - document.documentElement.clientWidth > 1 };
  });
  ok(d.lignes <= 2 || w < 900, `${w}px : introduction sur ${d.lignes} ligne(s)`);
  ok(d.avert > d.liste, `${w}px : encadré (${d.avert}) après la liste (${d.liste})`);
  ok(d.fsrc === null, `${w}px : paragraphe en doublon supprimé`);
  ok(d.garde, `${w}px : mise en garde conservée sous le champ de saisie`);
  ok(!d.deborde, `${w}px : pas de débordement horizontal`);
  await p.close();
}
const p = await b.newPage({ viewport:{width:1280,height:1200} });
await p.goto('http://127.0.0.1:8899/retours/', { waitUntil:'networkidle' });
await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(400);
await p.screenshot({ path:'v-ret-haut.png' });
await p.evaluate(()=>window.scrollTo(0, document.body.scrollHeight));
await p.waitForTimeout(300);
await p.screenshot({ path:'v-ret-bas.png' });
await b.close();
