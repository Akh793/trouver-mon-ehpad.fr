import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch();
const p = await b.newPage({ viewport:{width:390,height:844}, isMobile:true, hasTouch:true });
await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
await p.fill('#cp','69100'); await p.fill('#revenus','1600'); await p.waitForTimeout(3500);
console.log(JSON.stringify(await p.evaluate(()=>{
  const de=document.documentElement;
  return [...document.querySelectorAll('svg')].filter(e=>e.getBoundingClientRect().width>de.clientWidth+2)
   .map(e=>({cls:String(e.getAttribute('class')), w:Math.round(e.getBoundingClientRect().width),
             parent:e.parentElement.tagName+'.'+String(e.parentElement.getAttribute('class')),
             gp:e.parentElement.parentElement?.tagName+'.'+String(e.parentElement.parentElement?.getAttribute('class'))}));
}),null,1));
await b.close();
