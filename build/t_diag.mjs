import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch(); const p = await b.newPage({viewport:{width:1280,height:900}});
await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
await p.fill('#cp','69003'); await p.fill('#revenus','1600'); await p.waitForTimeout(3000);
console.log(JSON.stringify(await p.evaluate(()=>{
  const o=document.querySelector('.share-opt');
  const cs=getComputedStyle(o), r=o.getBoundingClientRect();
  const sp=o.querySelector('span'), inp=o.querySelector('input');
  return {
    parent: o.parentElement.className || o.parentElement.id,
    parentDisplay: getComputedStyle(o.parentElement).display,
    rect: {h:Math.round(r.height), w:Math.round(r.width)},
    display: cs.display, alignSelf: cs.alignSelf, height: cs.height, padding: cs.padding, margin: cs.margin,
    span: sp ? {h:Math.round(sp.getBoundingClientRect().height), w:Math.round(sp.getBoundingClientRect().width)} : null,
    input: inp ? {h:Math.round(inp.getBoundingClientRect().height), w:Math.round(inp.getBoundingClientRect().width), display:getComputedStyle(inp).display} : null,
  };
}),null,1));
await b.close();
