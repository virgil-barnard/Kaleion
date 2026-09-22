const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
// Optional browser check; not part of the offline Python unit suite.
// node docs/studies/check-touch-study.cjs [build/touch-study.html] [build/touch-check]
const {chromium} = require(process.env.KALEION_PLAYWRIGHT_MODULE || 'playwright');
const input=path.resolve(process.argv[2] || 'build/touch-study.html');
const output=path.resolve(process.argv[3] || 'build/touch-check');
fs.mkdirSync(output,{recursive:true});
(async()=>{
 const options=JSON.parse(process.env.KALEION_BROWSER_OPTIONS || '{}');
 const browser=await chromium.launch(options);
 try {
 const context=await browser.newContext({viewport:{width:1100,height:900},hasTouch:true});
 await context.route(/^https?:/, route=>route.abort());
 const page=await context.newPage(), errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(require('node:url').pathToFileURL(input).href);
 const tool=name=>page.locator(`[data-tool=${name}]`).click();
 const layout=name=>page.locator(`[data-layout=${name}]`).click();
 const idle=()=>page.waitForFunction(()=>!document.getElementById('ks-source').disabled);
 const positions=()=>page.locator('circle.dot').evaluateAll(a=>a.map(e=>[e.getAttribute('cx'),e.getAttribute('cy')]));
 const setSum=async(value,commit)=>page.locator('#ks-sum').evaluate((e, {value,commit})=>{e.value=value;e.dispatchEvent(new Event('input',{bubbles:true}));if(commit)e.dispatchEvent(new Event('change',{bubbles:true}))},{value,commit});
 const matches=()=>page.locator('circle.match').count();
 const initial=await positions();assert.equal(await matches(),4);
 await setSum(8,false);assert.equal(await matches(),0);assert.equal(await page.locator('#ks-undo').isDisabled(),true);
 await page.locator('#ks-sum').press('Escape');assert.equal(await matches(),4);
 await setSum(8,false);await page.locator('#ks-sum').dispatchEvent('pointercancel');assert.equal(await matches(),4);
 await setSum(8,true);assert.equal(await matches(),0);await page.locator('#ks-undo').click();assert.equal(await matches(),4);
 await page.locator('#ks-redo').click();assert.equal(await matches(),0);await page.locator('#ks-undo').click();
 await tool('measure');await page.locator('#ks-derive').click();assert.equal(await page.locator('.bin').count(),9);
 assert.equal(await page.locator('#ks-counts').isVisible(),true);
 await page.locator('.bin').nth(8).click();assert.equal(await page.evaluate(()=>document.activeElement.dataset.bin),'8');assert.match(await page.locator('#ks-count-receipt').textContent(),/0 contributors/);
 await tool('arrange');await layout('gather');assert.equal(await page.locator('#ks-source').isDisabled(),true);await idle();
 assert.equal(new Set((await positions()).map(p=>p.join(','))).size,7);assert.equal(await page.locator('circle.dot').count(),16);
 await tool('inspect');await page.locator('#ks-point').selectOption('12');assert.match(await page.locator('#ks-point-receipt').textContent(),/stack height is 3/);
 await tool('arrange');await layout('stack');await idle();assert.equal(new Set((await positions()).map(p=>p.join(','))).size,16);
 const stacked=await positions();await page.locator('#ks-undo').click();await idle();assert.equal(new Set((await positions()).map(p=>p.join(','))).size,7);
 await page.locator('#ks-redo').click();await idle();assert.deepEqual(await positions(),stacked);
 await page.screenshot({path:path.join(output,'stack.png'),fullPage:true});
 await page.locator('#ks-undo').click();await idle();await page.locator('#ks-undo').click();await idle();assert.deepEqual(await positions(),initial);
 await tool('relate');const dot=await page.locator('circle.dot').nth(0).boundingBox();const end=await page.locator('circle.dot').nth(15).boundingBox();
 await page.mouse.move(dot.x+dot.width/2,dot.y+dot.height/2);await page.mouse.down();await page.mouse.move(end.x+end.width/2,end.y+end.height/2,{steps:4});
 assert.equal(await page.locator('#ks-sum').inputValue(),'6');await page.mouse.up();await page.locator('#ks-undo').click();assert.equal(await page.locator('#ks-sum').inputValue(),'8');
 await tool('source');await page.locator('#ks-source').selectOption('1');assert.equal(await page.locator('#ks-counts').isVisible(),false);
 assert.equal(await page.locator('#ks-redo').isDisabled(),true);
 await tool('relate');const expected=[1,2,1,2,2,0,1,2,2,0,2,0,0,0,1,0,0];
 for(let i=0;i<expected.length;i++){await setSum(i,true);assert.equal(await matches(),expected[i],`sum ${i}`)}
 await tool('measure');await page.locator('#ks-derive').click();assert.equal(await page.locator('.bin').count(),17);
 // Make symbolic declarations separately executable by Python; check both captured choices.
 const snippets=[];
 for(const preset of ['0','1']){await tool('source');await page.locator('#ks-source').selectOption(preset);snippets.push(await page.locator('#ks-code').textContent())}
 fs.writeFileSync(path.join(output,'visible-python.json'),JSON.stringify(snippets));
 const layouts=[];
 for(const width of [1024,736,360,320]){
  await page.setViewportSize({width,height:900});await page.emulateMedia({colorScheme:width===320?'dark':'light'});
  await tool('measure');if(await page.locator('#ks-derive').isEnabled())await page.locator('#ks-derive').click();
  await tool('arrange');await layout('stack');await idle();
  const geometry=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,buttons:[...document.querySelectorAll('button')].filter(e=>e.offsetHeight).map(e=>({text:e.textContent,w:e.getBoundingClientRect().width,h:e.getBoundingClientRect().height}))}));
  assert.ok(geometry.scroll<=geometry.width,JSON.stringify(geometry));assert.ok(geometry.buttons.every(b=>b.h>=44));
  layouts.push({width,scroll:geometry.scroll});await page.screenshot({path:path.join(output,`width-${width}.png`),fullPage:true});
 }
 await page.emulateMedia({reducedMotion:'reduce'});await layout('grid');assert.equal(await page.locator('#ks-source').isDisabled(),false);await page.locator('#ks-undo').click();assert.equal(await page.locator('[data-layout=stack]').getAttribute('aria-pressed'),'true');
 // Native keyboard route remains usable; no pointer is necessary for construction.
 await tool('relate');await page.locator('#ks-sum').focus();await page.locator('#ks-sum').press('ArrowRight');assert.equal(await page.locator('#ks-sum').inputValue(),'4');

 // A fresh page tests actual emulated touch events, including a fast gesture.
 const touch=await context.newPage();touch.on('pageerror',e=>errors.push(String(e)));
 await touch.goto(require('node:url').pathToFileURL(input).href);
 const client=await context.newCDPSession(touch);
 const tap=async selector=>{
   const box=await touch.locator(selector).boundingBox();
   await client.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:box.x+box.width/2,y:box.y+box.height/2,id:1}]});
   await touch.evaluate(()=>new Promise(requestAnimationFrame));
   await client.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
 };
 const point=async i=>{const b=await touch.locator('circle.dot').nth(i).boundingBox();return {x:b.x+b.width/2,y:b.y+b.height/2,id:1}};
 const first=await point(0),last=await point(15);
 for(const type of ['touchStart','touchMove','touchEnd']){
   await client.send('Input.dispatchTouchEvent',{type,touchPoints:type==='touchEnd'?[]:[type==='touchStart'?first:last]});
 }
 await touch.waitForFunction(()=>!document.getElementById('ks-undo').disabled);
 assert.equal(await touch.locator('#ks-sum').inputValue(),'6');
 await tap('#ks-undo');
 await touch.waitForFunction(()=>document.getElementById('ks-sum').value==='3');
 assert.equal(await touch.locator('#ks-undo').isDisabled(),true);
 await client.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[first]});
 await client.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[last]});
 assert.equal(await touch.locator('#ks-sum').inputValue(),'6');
 await client.send('Input.dispatchTouchEvent',{type:'touchCancel',touchPoints:[]});
 await touch.waitForFunction(()=>document.getElementById('ks-sum').value==='3');
 assert.equal(await touch.locator('#ks-undo').isDisabled(),true);
 await tap('[data-tool=measure]');await tap('#ks-derive');
 await touch.waitForFunction(()=>!document.getElementById('ks-counts').hidden);
 await tap('[data-bin="8"]');await touch.waitForFunction(()=>document.getElementById('ks-sum').value==='8');
 assert.match(await touch.locator('#ks-count-receipt').textContent(),/Pairs: none/);
 assert.deepEqual(errors,[]);
 const report={browser:await browser.version(),errors,layouts,verified:[
   'preview/cancel','single gesture undo','redo/branch','zero bins','coincident chooser',
   'rank contributors','captured placement endpoints','both source masks','keyboard',
   'reduced motion','focus retained on bin selection','touch drag then immediate undo',
   'touch cancellation and menu taps']};
 fs.writeFileSync(path.join(output,'report.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report));
 } finally {await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
