import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch();
const errs=[];
// --- desktop ---
const p = await b.newPage({ viewport:{width:1280,height:900} });
p.on('pageerror',e=>errs.push('PE '+e.message));
p.on('console',m=>{if(m.type()==='error'&&!/geopf/.test(m.text()))errs.push('C '+m.text().slice(0,120));});
await p.goto('http://127.0.0.1:8899/index.html',{waitUntil:'networkidle'});
console.log('runTests:', await p.evaluate(()=>window.runTests()));
await p.fill('#cp','75011'); await p.fill('#revenus','2200'); await p.evaluate(()=>{const d=document.getElementById('plus-situation'); if(d) d.open=true;});
await p.fill('#epargne','25000');
await p.waitForTimeout(2500);
// filtre habilité + tri distance
await p.click('.filtres summary'); await p.waitForTimeout(300); await p.check('[data-check="ashOnly"]'); await p.selectOption('#tri','dist'); await p.waitForTimeout(1500);
const paris = await p.evaluate(()=>({items:document.querySelectorAll('#liste .res').length, titre:document.getElementById('res-titre').textContent, chiffre:document.getElementById('res-chiffre').textContent, ctx:document.getElementById('contexte').textContent.replace(/\s+/g,' ').slice(0,200)}));
console.log('Paris 11e + habilités:', JSON.stringify(paris));
// comparaison
await p.click('#liste .res [data-cmp]'); await p.waitForTimeout(800);
console.log('comparaison lignes:', await p.evaluate(()=>document.querySelectorAll('#comparaison tr').length));
// mode pro + export
await p.click('.seg-mode button:nth-child(2)'); await p.waitForTimeout(1200);
console.log('bouton export visible:', await p.isVisible('#export-btn'));
const dl = p.waitForEvent('download',{timeout:8000}).catch(()=>null);
await p.click('#export-btn'); const d = await dl;
console.log('CSV téléchargé:', d ? d.suggestedFilename() : 'NON');
// détail d'une fiche
await p.evaluate(()=>document.querySelectorAll('.res')[0].click()); await p.waitForTimeout(400);
const det = await p.evaluate(()=>document.querySelector('#fiche')?.textContent.replace(/\s+/g,' ').slice(0,400));
console.log('détail:', det);
await p.evaluate(()=>window.scrollTo(0,0));
await p.screenshot({path:'v-desktop.png', fullPage:false});
// --- mobile ---
const m = await b.newPage({ viewport:{width:390,height:844}, isMobile:true, hasTouch:true, deviceScaleFactor:2 });
m.on('pageerror',e=>errs.push('MPE '+e.message));
await m.goto('http://127.0.0.1:8899/index.html',{waitUntil:'networkidle'});
await m.fill('#cp','69003'); await m.fill('#revenus','1600'); await m.waitForTimeout(2500);
const over = await m.evaluate(()=>({sw:document.documentElement.scrollWidth, cw:document.documentElement.clientWidth}));
console.log('mobile débordement horizontal:', over.sw>over.cw+1 ? 'OUI ('+over.sw+'>'+over.cw+')' : 'non');
await m.screenshot({path:'v-mobile.png', fullPage:false});
await m.evaluate(()=>document.getElementById('bande-carte').scrollIntoView());
await m.waitForTimeout(1000);
await m.screenshot({path:'v-mobile-carte.png'});
// --- impression ---
await p.emulateMedia({media:'print'});
const printed = await p.evaluate(()=>({situation:getComputedStyle(document.getElementById('bande-situation')).display, faq:getComputedStyle(document.getElementById('bande-faq')).display, carte:getComputedStyle(document.getElementById('bande-carte')).display}));
console.log('impression:', JSON.stringify(printed));
console.log('ERREURS JS:', errs.length, errs.slice(0,6));
await b.close();
