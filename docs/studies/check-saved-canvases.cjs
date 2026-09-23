// HISTORICAL: targets the UI at commit 19928e6. For the current canvas run
// node docs/studies/check-continuous-canvas.cjs. See studies/README.md.
// Optional browser check for the committed canvases in the unmodified studio.
// node docs/studies/check-saved-canvases.cjs [origin] [output directory]
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {chromium}=require(process.env.KALEION_PLAYWRIGHT_MODULE||'playwright');
let origin=process.argv[2],server;
const output=path.resolve(process.argv[3]||'build/canvas-check');fs.mkdirSync(output,{recursive:true});
(async()=>{
 if(!origin){
   server=require('node:child_process').spawn(process.env.KALEION_PYTHON||'.venv/bin/python3',['-m','examples.studio','--port','0'],{stdio:['ignore','pipe','inherit']});
   origin=await new Promise((resolve,reject)=>{let text='';server.stdout.on('data',chunk=>{text+=chunk;const match=text.match(/http:\/\/127\.0\.0\.1:\d+/);if(match)resolve(match[0])});server.once('error',reject);server.once('exit',code=>reject(Error(`Host stopped: ${code}`)))});
 }
 const browser=await chromium.launch(JSON.parse(process.env.KALEION_BROWSER_OPTIONS||'{}'));
 try{
 const page=await browser.newPage({viewport:{width:1250,height:950},hasTouch:true}),errors=[];
 page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(origin);await page.waitForFunction(()=>!document.getElementById('add').disabled);
 const idle=()=>page.waitForFunction(()=>!document.getElementById('options').disabled);
 const state=async()=>await(await page.request.get(origin+'/api/state')).json();
 const exported=async()=>await(await page.request.get(origin+'/api/export')).text();
 const select=async name=>{await page.locator('[data-object]').filter({hasText:name}).first().click()};
 const report={browser:browser.version(),canvases:[]};
 for(const [name,active] of [['07_equal_sums','Moving pairs'],['06_young_layers','Cells'],['02_floor_sums','Pieces'],['05_radon_reconstruction','Image heights']]){
   const chooser=page.waitForEvent('filechooser');await page.locator('#open').click();
   await(await chooser).setFiles(path.resolve('examples/canvases',name+'.json'));await idle();
   assert.equal(await page.locator('#title').textContent(),active);
   assert.ok((await state()).objects.every(o=>o.status==='ready'));
   const before=await exported(),applied=(await state()).objects.find(o=>o.name===active).rows;
   assert.equal(await page.locator('#replay').isVisible(),false,'Current UI does not restore replay on Open');
   await page.locator('#undo').click();await idle();await page.locator('#redo').click();await idle();
   assert.deepEqual((await state()).objects.find(o=>o.name===active).rows,applied);
   assert.equal(await page.locator('#replay').isVisible(),true);
   let requests=0;const count=r=>{if(r.url().includes('/api/'))requests++};page.on('request',count);
   await page.locator('#replay-progress').fill('12');assert.match(await page.locator('#scope').textContent(),/presentation only/);
   await page.locator('#replay-progress').press('Home');assert.equal(await page.locator('#replay-progress').inputValue(),'0');
   await page.locator('#replay-progress').press('End');assert.equal(await page.locator('#replay-progress').inputValue(),'24');
   await page.locator('#replay-progress').fill('12');
   await page.locator('#scene').screenshot({path:path.join(output,name+'-scrub.png')});
   await page.getByRole('button',{name:'Return to result',exact:true}).click();
   page.off('request',count);assert.equal(requests,0);assert.equal(await exported(),before);
   await page.locator('#scene').screenshot({path:path.join(output,name+'.png')});
   report.canvases.push({name,active,objects:(await state()).objects.length,savedUndoRedo:true,scrubWithoutRequests:true});
 }
 // Execute the guide's first-five-minutes route on the committed sum canvas.
 await page.locator('#file').setInputFiles(path.resolve('examples/canvases/07_equal_sums.json'));await idle();
 await page.locator('[data-mode="points"]').click();
 let rows=(await state()).objects.find(o=>o.name==='Moving pairs').rows;
 await page.locator('#occurrence').selectOption(rows[12].ref[1]);await idle();
 await page.getByRole('button',{name:'Follow keyed read · 3',exact:true}).click();await idle();
 await page.locator('#view-contributors').click();await idle();
 const right=()=>page.locator('.linked-card').nth(1);
 assert.equal(await right().locator('[data-linked-member="true"]').count(),3);
 await page.locator('#close-linked').click();await select('Counts');
 rows=(await state()).objects.find(o=>o.name==='Counts').rows;
 await page.locator('#occurrence').selectOption(rows[8].ref[1]);await idle();
 assert.match(await page.locator('#panel').textContent(),/count · 0 contributors/);
 await page.locator('[data-mode="objects"]').click();await select('Moving pairs');
 await page.locator('#options').click();await page.locator('[data-action="lens"]').click();
 await page.locator('#result-name').fill('My sum four');
 const card=page.locator('#panel fieldset > .expression').first();
 await card.locator('[data-path="args/1"]').click();
 await card.getByLabel('Exact integer',{exact:true}).fill('4');await card.locator('[data-expression-done]').click();
 await page.locator('#preview').click();await idle();assert.equal(await page.locator('#apply').isEnabled(),true);
 await page.locator('#apply').click();await idle();
 assert.equal((await state()).objects.find(o=>o.name==='My sum four').rows.filter(r=>r.match).length,3);
 const download=page.waitForEvent('download');await page.locator('#save').click();await page.locator('#save-math').click();const saved=await download;
 await saved.saveAs(path.join(output,'my-canvas.json'));await idle();
 await page.locator('#file').setInputFiles(path.join(output,'my-canvas.json'));await idle();
 assert.equal((await state()).objects.find(o=>o.name==='My sum four').rows.filter(r=>r.match).length,3);
 // Follow a saved prefix to its measured layer, then its original cells.
 await page.locator('#file').setInputFiles(path.resolve('examples/canvases/06_young_layers.json'));await idle();
 await select('Offsets');await page.locator('[data-mode="points"]').click();
 rows=(await state()).objects.find(o=>o.name==='Offsets').rows;
 await page.locator('#occurrence').selectOption(rows[3].ref[1]);await idle();
 await page.locator('#view-contributors').click();await idle();
 await right().locator('[data-linked-occurrence]').selectOption({index:2});
 await right().locator('[data-linked-inspect]').click();await idle();
 assert.match(await page.locator('#panel').textContent(),/count · 2 contributors/);
 await page.locator('#view-contributors').click();await idle();assert.equal(await right().locator('[data-linked-member="true"]').count(),2);
 await page.setViewportSize({width:320,height:950});
 assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 await page.screenshot({path:path.join(output,'young-evidence-phone.png'),fullPage:true});
 assert.deepEqual(errors,[]);
 fs.writeFileSync(path.join(output,'report.json'),JSON.stringify({...report,errors,guideRoute:true,nestedEvidence:true,continuedAuthoring:true,phoneLayout:true},null,2));
 process.stdout.write('Saved canvas browser checks passed.\n');
 }finally{await browser.close();server?.kill()}
})().catch(error=>{console.error(error);server?.kill();process.exitCode=1});
