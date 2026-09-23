// Task-based acceptance for the continuous canvas. No DOM compatibility shims
// for the retired Focus surface; all actions use the new visible routes.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {spawn}=require('node:child_process');
const {chromium}=require(process.env.KALEION_PLAYWRIGHT_MODULE||'playwright');
const output=path.resolve(process.argv[3]||'build/continuous-canvas-check');fs.mkdirSync(output,{recursive:true});
let origin=process.argv[2],server;
(async()=>{
 if(!origin){server=spawn(process.env.KALEION_PYTHON||'.venv/bin/python3',['-m','examples.studio','--port','0'],{stdio:['ignore','pipe','inherit']});origin=await new Promise((resolve,reject)=>{server.stdout.on('data',d=>{const m=String(d).match(/http:\/\/127\.0\.0\.1:\d+/);if(m)resolve(m[0])});server.once('error',reject)});}
 const browser=await chromium.launch(JSON.parse(process.env.KALEION_BROWSER_OPTIONS||'{}'));
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000},hasTouch:true,reducedMotion:'reduce'}),errors=[],mutations=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/\/api\/(preview|preview-case|commit|undo|redo)$/.test(r.url()))mutations.push(r.url())});
  const idle=()=>page.waitForFunction(()=>!document.getElementById('options').disabled),state=async()=>await(await page.request.get(origin+'/api/state')).json();
  const exported=async()=>await(await page.request.get(origin+'/api/export')).text();
  const object=async name=>(await state()).objects.find(o=>o.name===name);
  const select=async name=>{await page.locator('#objects').selectOption(name);await idle()};
  const details=async name=>{if(name)await select(name);await page.locator('#options').click();await idle()};
  const close=async()=>{if(await page.locator('#panel').isVisible())await page.locator('#close-panel').click()};
  const camera=()=>page.locator('#workspace-canvas').getAttribute('viewBox');
  const marks=name=>page.locator(`[data-scene-owner=${JSON.stringify(name)}]`);
  const preview=async()=>{await page.locator('#preview').click();await idle();assert.equal(await page.locator('#draft-status').getAttribute('data-phase'),'ready',await page.locator('#draft-status').innerText())};
  const apply=async()=>{await preview();await page.locator('#apply').click();await idle()};
  const load=async file=>{await page.locator('#file').setInputFiles(file);await idle()};
  async function save(){const event=page.waitForEvent('download');await page.locator('#save').click();await page.locator('#save-canvas').click();const file=path.join(output,'canvas.json');await(await event).saveAs(file);await idle();return fs.readFileSync(file,'utf8')}
  async function create(kind,name,configure){await close();await page.locator('#add').click();assert.deepEqual(await page.locator('#menu-actions button').allTextContents(),['Vector','Grid','Cube']);await page.locator(`[data-action="${kind}"]`).click();await page.locator('#result-name').fill(name);if(configure)await configure();await page.locator('#apply').click();await idle();assert.ok(await object(name),await page.locator('#status').innerText())}
  await page.goto(origin);await page.waitForFunction(()=>document.getElementById('welcome')&&!document.getElementById('welcome').hidden);
  assert.equal(await page.getByRole('button',{name:'Focus',exact:true}).count(),0);
  await page.screenshot({path:path.join(output,'blank-canvas.png')});
  await create('grid','Tiles');assert.equal((await object('Tiles')).rows.length,25);assert.equal((await object('Tiles')).fields.includes('value'),false);assert.equal(await marks('Tiles').locator('.scene-value').count(),0);
  await close();const beforeMenu=await exported(),beforeCamera=await camera();
  // A real right click on background is creation-only even with Tiles selected.
  const canvas=await page.locator('#workspace-canvas').boundingBox();await page.mouse.click(canvas.x+30,canvas.y+canvas.height*.7,{button:'right'});
  assert.deepEqual(await page.locator('#menu-actions button').allTextContents(),['Vector','Grid','Cube']);await page.locator('#close-menu').click();
  await page.locator('[data-workspace-object="Tiles"]').click({button:'right'});assert.equal(await page.locator('#panel').isVisible(),true);assert.equal(await camera(),beforeCamera);assert.equal(await exported(),beforeMenu);
  await close();assert.equal(await camera(),beforeCamera);
  await create('grid','Numbers',async()=>{await page.getByLabel('Size i',{exact:true}).fill('3');await page.getByLabel('Size j',{exact:true}).fill('4');await page.locator('#shape-contents').selectOption('formula');await page.locator('#shape-formula').fill('10*i + j')});
  assert.deepEqual((await object('Numbers')).rows.map(r=>r.fields.value),['0','1','2','3','10','11','12','13','20','21','22','23']);
  await create('vector','Exact values',async()=>{await page.locator('#shape-contents').selectOption('list');await page.locator('#shape-list').fill('9007199254740993, 0, -2')});assert.equal((await object('Exact values')).rows[0].fields.value,'9007199254740993');
  // Failed formulas retain the draft and never publish a source or a false zero.
  await close();await page.locator('#add').click();await page.locator('[data-action="grid"]').click();await page.locator('#result-name').fill('Invalid');await page.locator('#shape-contents').selectOption('formula');await page.locator('#shape-formula').fill('i / 2');
  const valid=await exported();await page.locator('#apply').click();await idle();assert.equal(await page.locator('#draft-status').getAttribute('data-phase'),'failed');assert.equal(await exported(),valid);await page.locator('#cancel').click();await idle();
  // Exact assignment is a new child of a tuple source; construction navigation
  // and item evidence stay alongside all the other objects at the same camera.
  await details('Tiles');await page.locator('#advanced-tools summary').click();await page.locator('[data-action="values"]').click();await page.locator('#result-name').fill('Tile values');await page.locator('#values-formula').fill('i+j');await apply();
  const pointCamera=await camera(),count=await page.locator('[data-workspace-object]').count();await page.locator('[data-construction-input]').first().click();await idle();assert.equal(await camera(),pointCamera);assert.equal(await page.locator('[data-workspace-object]').count(),count);await page.locator('#construction-back').click();await idle();assert.equal(await page.locator('#objects').inputValue(),'Tile values');assert.equal(await camera(),pointCamera);
  await close();await marks('Tiles').nth(0).click();await idle();assert.match(await page.locator('#activity').innerText(),/Tuple · no value/);assert.equal(await camera(),pointCamera);
  // A relation and an axis total retain the tuple universe and exact contributors.
  await details('Tiles');await page.locator('#quick-lens').click();await page.locator('#result-name').fill('Even columns');await page.getByLabel('Number of lens inputs',{exact:true}).selectOption('1');await apply();assert.equal((await object('Even columns')).rows.filter(r=>r.match).length,15);
  await page.locator('#axis-total').click();await page.locator('#result-name').fill('Column counts');await apply();assert.deepEqual((await object('Column counts')).rows.map(r=>r.fields.value),['5','0','5','0','5']);
  await page.screenshot({path:path.join(output,'relation-and-totals.png')});
  await close();await create('cube','Box',async()=>{await page.getByLabel('Size i',{exact:true}).fill('2');await page.getByLabel('Size j',{exact:true}).fill('3');await page.getByLabel('Size k',{exact:true}).fill('4')});
  assert.equal((await object('Box')).rows.length,24);await page.locator('#quick-lens').click();await page.locator('#result-name').fill('Add indices');await page.getByLabel('Number of lens inputs',{exact:true}).selectOption('3');await page.getByLabel('Pattern',{exact:true}).selectOption('add');await apply();assert.equal((await object('Add indices')).rows.filter(r=>r.match).length,6);
  // All axes can be reduced together into a reusable scalar count.
  await page.locator('#axis-total').click();await page.locator('#result-name').fill('Six matches');for(const axis of ['i','j','k'])await page.getByLabel(`Total along ${axis}`,{exact:true}).check();await apply();assert.deepEqual((await object('Six matches')).rows.map(r=>r.fields.value),['6']);
  // Draft interruption retains its formula and restores the applied view.
  await details('Numbers');await page.locator('#quick-lens').click();await page.locator('#result-name').fill('Parked rule');await preview();await page.locator('#close-panel').click();await page.locator('#resume-draft').click();assert.equal(await page.locator('#result-name').inputValue(),'Parked rule');await page.locator('#cancel').click();await idle();
  const math=await exported(),saved=await save();assert.equal(JSON.parse(saved).workspace,math);assert.equal(JSON.parse(math).schema,2);await load({name:'canvas.json',mimeType:'application/json',buffer:Buffer.from(saved)});assert.equal(await exported(),math);
  await close();await page.locator('#undo').click();await idle();await page.locator('#redo').click();await idle();assert.equal((await object('Six matches')).rows[0].fields.value,'6');
  // Saved lesson replay shares the board. Scrubbing makes no evaluation request.
  await load(path.resolve('examples/canvases/07_equal_sums.json'));await close();await select('Moving pairs');await page.locator('#undo').click();await idle();await page.locator('#redo').click();await idle();
  assert.equal(await page.locator('#replay').isVisible(),true,JSON.stringify({status:await page.locator('#status').innerText(),active:await page.locator('#objects').inputValue(),errors}));const replayCamera=await camera(),replayMath=await exported(),requests=mutations.length,other=await marks('Left').first().getAttribute('data-scene-mark');
  await page.locator('#replay-progress').fill('12');assert.equal(await camera(),replayCamera);assert.equal(await exported(),replayMath);assert.equal(mutations.length,requests);assert.equal(await marks('Left').first().getAttribute('data-scene-mark'),other);assert.equal(await page.locator('#workspace-view').isVisible(),true);
  await page.locator('[data-replay-result]').click();
  // Keyed comparison and coverage remain accessible through one More tools
  // disclosure. A finite equality check and its evidence do not change history.
  await details('Left');await page.locator('#advanced-tools summary').click();await page.locator('[data-action="compare"]').click();
  await page.getByLabel('Add left key fields',{exact:true}).selectOption('key');await page.locator('#comparison-right').selectOption('Left');await page.getByLabel('Add right key fields',{exact:true}).selectOption('key');await page.locator('#comparison-expected').selectOption('Left');await page.getByLabel('Add expected key fields',{exact:true}).selectOption('key');
  const beforeCompare=await exported();await page.locator('#check-comparison').click();await idle();assert.equal(await page.locator('#comparison-status').getAttribute('data-phase'),'passed');await page.locator('#view-comparison').click();await idle();assert.equal(await page.locator('#linked-views').isVisible(),true);assert.equal(await page.locator('#workspace-view').isVisible(),true);assert.equal(await exported(),beforeCompare);
  await details('Sum lens');await page.locator('#advanced-tools summary').click();await page.locator('[data-action="coverage"]').click();
  await page.getByLabel('Add source group keys',{exact:true}).selectOption('key');await page.locator('#coverage-expected').selectOption('Pairs');await page.getByLabel('Add expected key fields',{exact:true}).selectOption('key');await page.locator('#check-coverage').click();await idle();assert.match(await page.locator('#coverage-status').innerText(),/missing/);
  // The ordered measurement editor still exposes strict order and weight.
  await details('Left');await page.locator('#advanced-tools summary').click();await page.locator('[data-action="measure"]').click();await page.locator('#result-name').fill('Running totals');await page.locator('#reducer').selectOption('prefix_sum');await apply();
  const leftValues=(await object('Left')).rows.map(r=>BigInt(r.fields.value)),expectedPrefixes=leftValues.map((_,i)=>leftValues.slice(0,i).reduce((a,b)=>a+b,0n).toString());assert.deepEqual((await object('Running totals')).rows.map(r=>r.fields.value),expectedPrefixes);
  // Five schema-1 lessons open without evaluation, and their construction paths
  // remain present. Read a weighted Radon driver in the drawer.
  for(const file of ['02_floor_sums','03_incidence_box','05_radon_reconstruction','06_young_layers','07_equal_sums']){
    await load(path.resolve(`examples/canvases/${file}.json`));const st=await state();assert.ok(st.objects.every(o=>o.status==='ready'));await details(st.objects.at(-1).name);assert.ok(await page.locator('#construction-details').innerText());assert.equal(await page.locator('[data-workspace-object]').count(),st.objects.length);
  }
  await load(path.resolve('examples/canvases/05_radon_reconstruction.json'));await details('Backprojection');const radonCamera=await camera(),radonCapture=await exported();
  await close();await page.locator('#view-options').click();await page.locator('#scene-chooser summary').click();const height=(await object('Backprojection')).rows[0];await page.locator('#scene-occurrence').selectOption(JSON.stringify(height.ref));await idle();
  await page.locator('#view-contributors').click();await idle();await page.locator('[data-linked-inspect="right"]').click();await idle();
  const follow=page.getByRole('button',{name:/Follow weight read/}).first();assert.equal(await follow.isVisible(),true);await follow.click();await idle();assert.equal(await page.locator('#linked-views').isVisible(),true);assert.equal(await camera(),radonCamera);await page.locator('#receipt-back').click();await idle();assert.equal(await camera(),radonCamera);assert.equal(await exported(),radonCapture);
  await load(path.resolve('examples/canvases/03_incidence_box.json'));await close();await select('X region');await page.locator('[data-workspace-tool="orbit"]').click();const oriented=await page.locator('#workspace-canvas').getAttribute('data-orientation'),bounds=await page.locator('#workspace-canvas').boundingBox();
  await page.mouse.move(bounds.x+40,bounds.y+bounds.height*.6);await page.mouse.down();await page.mouse.move(bounds.x+85,bounds.y+bounds.height*.6+20,{steps:5});await page.mouse.up();assert.notEqual(await page.locator('#workspace-canvas').getAttribute('data-orientation'),oriented);
  const orientCapture=await exported();await page.locator('#view-options').click();await page.getByRole('button',{name:'Show points',exact:true}).click();await page.getByRole('button',{name:'Show cells',exact:true}).click();await page.locator('#scene-chart').selectOption('logical');await page.getByText('Chart and slice',{exact:true}).click();await page.locator('#scene-slice-axis').selectOption('k');await page.locator('#scene-slice-value').selectOption('0');assert.equal(await exported(),orientCapture);await page.screenshot({path:path.join(output,'cube-in-context.png')});
  await page.locator('#scene-slice-axis').selectOption('');await close();await page.locator('[data-workspace-tool="move"]').click();
  // Native emulated touch hold opens the same contextual inspector. A held
  // background opens only the three constructors, with no evaluation request.
  const touch=await page.context().newCDPSession(page),handle=await page.locator('[data-workspace-object="X region"] rect').boundingBox(),touchCamera=await camera(),holdRequests=mutations.length;
  await touch.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:handle.x+handle.width/2,y:handle.y+handle.height/2}]});await page.waitForTimeout(550);await touch.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});assert.equal(await page.locator('#panel').isVisible(),true);assert.equal(await camera(),touchCamera);assert.equal(mutations.length,holdRequests);await close();
  await touch.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:bounds.x+25,y:bounds.y+bounds.height*.8}]});await page.waitForTimeout(550);await touch.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});assert.equal(await page.locator('#menu').isVisible(),true);assert.deepEqual(await page.locator('#menu-actions button').allTextContents(),['Vector','Grid','Cube']);await page.locator('#close-menu').click();await touch.detach();
  await load(path.resolve('examples/canvases/07_equal_sums.json'));
  // Mobile emulation: drawer uses a bottom sheet and the canvas remains visible.
  await page.setViewportSize({width:360,height:900});await details('Pairs');assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));const panel=await page.locator('#panel').boundingBox(),phoneCanvas=await page.locator('#workspace-canvas').boundingBox();assert.ok(panel.y>phoneCanvas.y+phoneCanvas.height*.25);await page.screenshot({path:path.join(output,'phone-inspector.png')});
  await page.setViewportSize({width:320,height:800});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  assert.deepEqual(errors,[]);fs.writeFileSync(path.join(output,'report.json'),JSON.stringify({browser:browser.version(),tasks:'creation, exact formulas, tuples, relations, totals, provenance, history, shared replay, mobile layout',errors},null,2));
  console.log('Continuous canvas checks passed.');
 }finally{await browser.close();server?.kill()}
})().catch(error=>{console.error(error);server?.kill();process.exitCode=1});
