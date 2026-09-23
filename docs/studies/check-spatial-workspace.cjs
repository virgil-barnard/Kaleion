// Optional real-browser gate; core tests remain offline and browser independent.
// node docs/studies/check-spatial-workspace.cjs [origin] [output directory]
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {chromium}=require(process.env.KALEION_PLAYWRIGHT_MODULE||'playwright');
let origin=process.argv[2],server;
const output=path.resolve(process.argv[3]||'build/spatial-check');fs.mkdirSync(output,{recursive:true});
(async()=>{
 if(!origin){
   server=require('node:child_process').spawn(process.env.KALEION_PYTHON||'.venv/bin/python3',['-m','examples.studio','--port','0'],{stdio:['ignore','pipe','inherit']});
   origin=await new Promise((resolve,reject)=>{let text='';server.stdout.on('data',chunk=>{text+=chunk;const match=text.match(/http:\/\/127\.0\.0\.1:\d+/);if(match)resolve(match[0])});server.once('error',reject);server.once('exit',code=>reject(Error(`Host stopped: ${code}`)))});
 }
 const browser=await chromium.launch(JSON.parse(process.env.KALEION_BROWSER_OPTIONS||'{}'));
 try{
   const page=await browser.newPage({viewport:{width:1400,height:1050},hasTouch:true,reducedMotion:'reduce'}),errors=[];
   page.on('pageerror',e=>errors.push(String(e)));
   await page.goto(origin);await page.waitForFunction(()=>!document.getElementById('add').disabled);
   const idle=()=>page.waitForFunction(()=>!document.getElementById('options').disabled);
   const state=async()=>await(await page.request.get(origin+'/api/state')).json();
   const exported=async()=>await(await page.request.get(origin+'/api/export')).text();
   const card=name=>page.locator(`[data-workspace-object=${JSON.stringify(name)}]`);
   const center=async name=>{await page.locator('#workspace-canvas').scrollIntoViewIfNeeded();const b=await card(name).boundingBox();return{x:b.x+b.width/2,y:b.y+b.height/2}};
   const workspace=async()=>await page.locator('[data-surface="workspace"]').click();
   const open=async name=>{await page.locator('#file').setInputFiles(path.resolve('examples/canvases',name+'.json'));await idle()};
   const apply=async()=>{await page.locator('#preview').click();await idle();assert.equal(await page.locator('#apply').isEnabled(),true,await page.locator('#draft-status').textContent());await page.locator('#apply').click();await idle()};
   const report={browser:browser.version(),canvases:[]};
   assert.equal(await page.locator('#workspace-view').isVisible(),true);
   for(const name of ['07_equal_sums','06_young_layers','02_floor_sums','05_radon_reconstruction']){
     await open(name);await workspace();await page.getByRole('button',{name:'Fit workspace view',exact:true}).click();
     const current=await state();assert.equal(await page.locator('[data-workspace-object]').count(),current.objects.length);
     for(const o of current.objects)assert.equal(await card(o.name).locator('circle').count(),Math.min(180,o.rows.length));
     await page.locator('[data-workspace-tool="connect"]').click();
     assert.equal(await page.locator('[data-connection-source]').count(),current.connections.edges.length);
     await page.locator('#scene').screenshot({path:path.join(output,name+'.png')});
     report.canvases.push({name,objects:current.objects.length,connections:current.connections.edges.length});
   }
   await open('07_equal_sums');await workspace();await page.locator('[data-workspace-tool="move"]').click();
   const original=await exported();let requests=0;const count=r=>{if(r.url().includes('/api/'))requests++};page.on('request',count);
   const before=await card('Left').getAttribute('transform');let p=await center('Left');
   await page.mouse.move(p.x,p.y);await page.mouse.down();await page.mouse.move(p.x+55,p.y+28,{steps:8});await page.mouse.up();
   assert.notEqual(await card('Left').getAttribute('transform'),before);
   const moved=await card('Left').getAttribute('transform');p=await center('Left');
   await page.mouse.move(p.x,p.y);await page.mouse.down();await page.mouse.move(p.x+45,p.y+35,{steps:5});await page.keyboard.press('Escape');await page.mouse.up();
   assert.equal(await card('Left').getAttribute('transform'),moved,'Escape restores starting layout');
   await card('Left').focus();await page.keyboard.press('ArrowRight');assert.notEqual(await card('Left').getAttribute('transform'),moved);
   await page.keyboard.press('Shift+F10');assert.equal(await page.locator('#menu-title').textContent(),'Left');
   await page.locator('#close-menu').click();assert.equal(await card('Left').evaluate(n=>n===document.activeElement),true);
   await card('Right').focus();await page.keyboard.press('Space');assert.equal(await card('Right').getAttribute('aria-pressed'),'true');
   // An empty-space camera move changes neither object offsets nor captured work.
   await page.getByRole('button',{name:'Zoom in workspace view',exact:true}).click();await page.getByRole('button',{name:'Fit workspace view',exact:true}).click();
   assert.equal(await exported(),original);assert.equal(requests,0);page.off('request',count);
   await page.locator('[data-workspace-tool="connect"]').click();p=await center('Left');const q=await center('Right');
   await page.mouse.move(p.x,p.y);await page.mouse.down();await page.mouse.move(q.x,q.y,{steps:12});
   assert.equal(await card('Right').evaluate(n=>n.classList.contains('drop-target')),true);
   await page.mouse.up();assert.equal(await page.locator('#combine-source').inputValue(),'Left');assert.equal(await page.locator('#combine-target').inputValue(),'Right');
   assert.equal(await exported(),original,'Dropping proposes only');
   await page.locator('#combine-product').click();await page.locator('#result-name').fill('Connected pairs');
   let declaration=JSON.parse(await page.locator('#declaration').textContent());
   assert.equal(declaration.args.factors.left.source,'Left');assert.equal(declaration.args.factors.right.source,'Right');
   await apply();let current=await state(),pairs=current.objects.find(o=>o.name==='Connected pairs');
   assert.equal(pairs.rows.length,16);assert.deepEqual(pairs.rows.map(r=>[r.fields.left_value,r.fields.right_value]),Array.from({length:16},(_,i)=>[String(Math.floor(i/4)),String(i%4)]));
   await workspace();assert.equal(await card('Connected pairs').count(),1);
   // A tap/keyboard proposal is the same command path; bad keys fail before Apply.
   await card('Counts').click();await page.locator('[data-combine]').click();await page.locator('#combine-target').selectOption('Moving pairs');
   await page.locator('#combine-place').click();const preFailure=await exported();await page.locator('#preview').click();await idle();
   assert.equal(await page.locator('#apply').isEnabled(),false);assert.equal(await page.locator('#draft-status').getAttribute('data-phase'),'failed');assert.equal(await exported(),preFailure);
   await page.locator('#cancel').click();await idle();await workspace();await card('Counts').click();await page.locator('[data-combine]').click();await page.locator('#combine-target').selectOption('Left');
   await page.locator('#combine-place').click();declaration=JSON.parse(await page.locator('#declaration').textContent());
   assert.deepEqual(declaration.args.coordinates[1],{read:{object:'Counts',on:{field:'key'},key:{field:'key'},value:{field:'value'}}});
   await apply();current=await state();assert.deepEqual(current.objects.find(o=>o.name==='Left').rows.map(r=>r.position[1]),[1,2,3,4]);
   assert.ok(current.connections.edges.some(e=>e.source==='Counts'&&e.target==='Left'&&e.kind==='read'));
   assert.ok(!current.connections.edges.some(e=>e.source==='Left'&&e.target==='Connected pairs'),'The pairs still use the earlier Left definition');
   // Parking the connected draft keeps its explicit operands and blocks replacement.
   await workspace();await card('Right').click();await page.locator('[data-combine]').click();await page.locator('#combine-target').selectOption('Left');await page.locator('#combine-product').click();await page.locator('#result-name').fill('Keep my operands');
   const parked=await page.locator('#declaration').textContent();await workspace();await card('Counts').click();assert.equal(await page.locator('[data-combine]').isEnabled(),false);
   await page.locator('#options').click();assert.equal(await page.locator('[data-action="combine"]').isEnabled(),false);await page.locator('#close-menu').click();await page.locator('#resume-draft').click();
   assert.equal(await page.locator('#declaration').textContent(),parked);assert.equal(await page.locator('#single-view').isVisible(),true);await page.locator('#cancel').click();await idle();
   // Narrow-screen alternatives and genuine browser pointer cancellation.
   await page.setViewportSize({width:360,height:1000});await workspace();await open('07_equal_sums');
   await page.locator('[data-workspace-tool="move"]').tap();await page.locator('[data-object="Moving pairs"]').tap();await page.getByRole('button',{name:'Center selected object',exact:true}).tap();
   p=await center('Moving pairs');const phoneBefore=await exported(),layoutBefore=await card('Moving pairs').getAttribute('transform');
   const client=await page.context().newCDPSession(page);
   await client.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{...p,id:1}]});
   await client.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:p.x+28,y:p.y+20,id:1}]});
   await client.send('Input.dispatchTouchEvent',{type:'touchCancel',touchPoints:[]});
   assert.equal(await card('Moving pairs').getAttribute('transform'),layoutBefore);
   await client.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{...p,id:1}]});
   await client.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{...p,id:1},{x:p.x+45,y:p.y,id:2}]});
   await page.waitForTimeout(550);await client.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});assert.equal(await page.locator('#menu').evaluate(n=>n.open),false);
   await client.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{...p,id:1}]});await page.waitForTimeout(550);await client.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
   assert.equal(await page.locator('#menu-title').textContent(),'Moving pairs');assert.equal(await page.locator('#menu').evaluate(n=>n.open),true);await page.locator('#close-menu').tap();
   assert.equal(await exported(),phoneBefore);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   await page.locator('#scene').screenshot({path:path.join(output,'phone-workspace.png')});
   await page.locator('[data-combine]').tap();await page.locator('#combine-target').selectOption('Ranks');assert.equal(await page.locator('#combine-product').isEnabled(),true);
   await page.setViewportSize({width:320,height:950});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   assert.deepEqual(errors,[]);
   fs.writeFileSync(path.join(output,'report.json'),JSON.stringify({...report,viewOnlyGestures:true,cancelledDrag:true,reviewedProduct:true,explicitKeyedPlacement:true,earlierDriver:true,draftContinuity:true,phoneEmulation:true,errors},null,2));
   process.stdout.write('Spatial workspace browser checks passed.\n');
 }finally{await browser.close();server?.kill()}
})().catch(error=>{console.error(error);server?.kill();process.exitCode=1});
