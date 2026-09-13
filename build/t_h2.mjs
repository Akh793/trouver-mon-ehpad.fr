import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch(); const p = await b.newPage({ viewport:{width:1280,height:1000} });
await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
await p.fill('#cp','69003'); await p.fill('#revenus','1600'); await p.waitForTimeout(3000);
const r = await p.evaluate(()=>[...document.querySelectorAll('h1,h2,h3,h4')].map(h=>h.innerText.replace(/\s+/g,' ').trim())
  .filter(Boolean));
// un mot colle = une minuscule suivie d'une majuscule, ou deux mots sans espace autour d'une casse
const suspects = r.filter(t=>/[a-zà-ÿ][A-ZÀ-Ý]/.test(t) || /\S{22,}/.test(t));
console.log('titres :', r.length, '| suspects :', suspects.length);
suspects.forEach(t=>console.log('   ⚠', t));
r.slice(0,12).forEach(t=>console.log('   ·', t));
await b.close();
