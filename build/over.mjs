import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch(); const m = await b.newPage({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
await m.goto('http://127.0.0.1:8899/index.html',{waitUntil:'networkidle'});
await m.fill('#cp','69003'); await m.fill('#revenus','1600'); await m.waitForTimeout(2500);
const r = await m.evaluate(()=>{
  const w=document.documentElement.clientWidth, bad=[];
  document.querySelectorAll('*').forEach(el=>{const b=el.getBoundingClientRect(); if(b.right>w+1||b.left<-1) bad.push((el.id?'#'+el.id:el.className&&typeof el.className==='string'?'.'+el.className.split(' ')[0]:el.tagName)+' '+Math.round(b.left)+'→'+Math.round(b.right));});
  return {w, sw:document.documentElement.scrollWidth, bad:bad.slice(0,8)};
});
console.log(JSON.stringify(r));
await m.screenshot({path:'v-mobile.png'});
await b.close();
