import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const runs = [];
for (let i=0;i<3;i++){
  const b = await chromium.launch();
  const ctx = await b.newContext({viewport:{width:412,height:915},isMobile:true,hasTouch:true,deviceScaleFactor:2});
  const p = await ctx.newPage();
  const cdp = await ctx.newCDPSession(p);
  await cdp.send('Network.enable');
  await cdp.send('Network.emulateNetworkConditions',{offline:false,latency:150,downloadThroughput:1638400/8,uploadThroughput:750*1024/8});
  await cdp.send('Emulation.setCPUThrottlingRate',{rate:4});
  await p.goto('http://127.0.0.1:8899/index.html',{waitUntil:'load'});
  await p.waitForTimeout(3000);
  const m = await p.evaluate(()=>{
    const fcp=(performance.getEntriesByName('first-contentful-paint')[0]||{}).startTime;
    const lcp=performance.getEntriesByType('largest-contentful-paint').slice(-1)[0];
    const nav=performance.getEntriesByType('navigation')[0];
    let tbt=0; performance.getEntriesByType('longtask').forEach(t=>{tbt+=Math.max(0,t.duration-50)});
    const bytes=performance.getEntriesByType('resource').reduce((a,r)=>a+(r.transferSize||0),0)+(nav.transferSize||0);
    return {fcp:Math.round(fcp), lcp:lcp?Math.round(lcp.startTime):null, dcl:Math.round(nav.domContentLoadedEventEnd), tbt:Math.round(tbt), req:performance.getEntriesByType('resource').length, ko:Math.round(bytes/1024)};
  });
  runs.push(m); await b.close();
}
const med = k => runs.map(r=>r[k]).sort((a,b)=>a-b)[1];
console.log('runs', JSON.stringify(runs));
console.log('médianes — FCP', med('fcp'),'ms | LCP', med('lcp'),'ms | DCL', med('dcl'),'ms | TBT', med('tbt'),'ms | requêtes', med('req'),'| transféré', med('ko'),'Ko');
