// HISTORICAL: targets the UI at commit 19928e6. For the current canvas run
// node docs/studies/check-continuous-canvas.cjs. See studies/README.md.
// Real-control acceptance gate for the common scene; core tests remain offline.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {spawn,execFileSync}=require('node:child_process');
const {chromium}=require(process.env.KALEION_PLAYWRIGHT_MODULE||'playwright');
const python=process.env.KALEION_PYTHON||'.venv/bin/python3';
let origin=process.argv[2],server;
const output=path.resolve(process.argv[3]||'build/shared-scene-check');fs.mkdirSync(output,{recursive:true});
(async()=>{
 if(!origin){server=spawn(python,['-m','examples.studio','--port','0'],{stdio:['ignore','pipe','inherit']});origin=await new Promise((resolve,reject)=>{let text='';server.stdout.on('data',chunk=>{text+=chunk;const match=text.match(/http:\/\/127\.0\.0\.1:\d+/);if(match)resolve(match[0])});server.once('error',reject);server.once('exit',code=>reject(Error(`Host stopped: ${code}`)))});}
 const browser=await chromium.launch(JSON.parse(process.env.KALEION_BROWSER_OPTIONS||'{}'));
 try{
  const page=await browser.newPage({viewport:{width:1400,height:1100},hasTouch:true,reducedMotion:'reduce'}),errors=[],mutations=[];
  page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>{if(/\/api\/(preview|preview-case|commit|undo|redo)$/.test(r.url()))mutations.push(r.url())});
  await page.goto(origin);await page.waitForFunction(()=>!document.getElementById('add').disabled);
  const idle=()=>page.waitForFunction(()=>!document.getElementById('options').disabled),state=async()=>await(await page.request.get(origin+'/api/state')).json();
  const exported=async()=>await(await page.request.get(origin+'/api/export')).text();
  const select=async name=>{await page.locator(`[data-object=${JSON.stringify(name)}]`).click();await idle()};
  const marks=name=>page.locator(`[data-scene-owner=${JSON.stringify(name)}]`);
  const load=async file=>{await page.locator('#file').setInputFiles(file);await idle()};
  const loadText=async text=>load({name:'canvas.json',mimeType:'application/json',buffer:Buffer.from(text)});
  const workspace=()=>page.locator('[data-surface="workspace"]').click();
  const fit=()=>page.getByRole('button',{name:'Fit workspace view',exact:true}).click();
  const viewbox=()=>page.locator('#workspace-canvas').getAttribute('viewBox');
  async function saveCanvas(){const promise=page.waitForEvent('download');await page.locator('#save').click();await page.locator('#save-canvas').click();const download=await promise;const file=path.join(output,'saved-canvas.json');await download.saveAs(file);await idle();return fs.readFileSync(file,'utf8')}
  // Direct source creation lowers to the ordinary finite sequence builder.
  await page.locator('[data-scene-source]').click();await page.locator('#result-name').fill('Number line');await page.locator('#preview').click();await idle();await page.locator('#apply').click();await idle();await workspace();
  assert.deepEqual((await state()).objects[0].rows.map(r=>r.fields.value),['0','1','2','3','4','5']);assert.equal(await marks('Number line').count(),6);
  await marks('Number line').nth(2).click();await idle();assert.match(await page.locator('#scene-selection-note').textContent(),/occurrence 2 · value 2/);assert.equal(await page.locator('.scene-mark.chosen').count(),1);
  await load(path.resolve('examples/canvases/07_equal_sums.json'));await workspace();await select('Moving pairs');await fit();
  const before=await exported(),rows=(await state()).objects.find(o=>o.name==='Moving pairs').rows,ref=JSON.stringify(rows[6].ref),refs=await marks('Moving pairs').evaluateAll(ns=>ns.map(n=>n.dataset.sceneMark).sort());
  await page.locator('#scene-chooser > summary').click();await page.locator('#scene-occurrence').selectOption(ref);await idle();
  assert.equal(await page.locator('.scene-mark.chosen').getAttribute('data-scene-mark'),ref);
  assert.match(await page.locator('#activity').innerText(),/Value/);
  const camera=await viewbox();await page.getByRole('button',{name:'Show points',exact:true}).click();
  assert.equal(await viewbox(),camera);assert.deepEqual(await marks('Moving pairs').evaluateAll(ns=>ns.map(n=>n.dataset.sceneMark).sort()),refs);assert.equal(await marks('Moving pairs').locator('circle').count(),16);
  await page.locator('#scene-chart').selectOption('logical');assert.equal(await page.locator('.scene-mark.chosen').getAttribute('data-scene-mark'),ref);
  await page.getByRole('button',{name:'Show cells',exact:true}).click();assert.equal(await viewbox(),camera);
  await page.getByRole('button',{name:'3D workspace view',exact:true}).click();
  await page.locator('[data-scene-selection] > details').first().locator('summary').click();
  await page.locator('#scene-slice-axis').selectOption('left');await page.locator('#scene-slice-value').selectOption('1');
  assert.equal(await marks('Moving pairs').count(),4);assert.equal(await page.locator('#scene-occurrence').inputValue(),ref);
  const selected=await page.locator('.scene-mark.chosen').getAttribute('data-scene-mark');assert.equal(selected,ref);
  await page.locator('[data-workspace-object="Moving pairs"]').focus();await page.keyboard.press('ArrowRight');
  const pose=await page.locator('[data-workspace-object="Moving pairs"]').getAttribute('transform'),savedCamera=await viewbox(),orientation=await page.locator('#workspace-canvas').getAttribute('data-orientation');
  const saved=await saveCanvas();assert.equal(JSON.parse(saved).workspace,before);
  await page.getByRole('button',{name:'XY workspace view',exact:true}).click();await page.locator('#scene-slice-axis').selectOption('');await select('Left');
  await loadText(saved);
  assert.equal(await page.locator('#construction-title').innerText(),'Moving pairs');assert.equal(await viewbox(),savedCamera);assert.equal(await page.locator('#workspace-canvas').getAttribute('data-orientation'),orientation);
  assert.equal(await page.locator('[data-workspace-object="Moving pairs"]').getAttribute('transform'),pose);assert.equal(await page.locator('#scene-chart').inputValue(),'logical');assert.equal(await page.locator('#scene-slice-axis').inputValue(),'left');assert.equal(await page.locator('#scene-slice-value').inputValue(),'1');assert.equal(await page.locator('#scene-occurrence').inputValue(),ref);
  assert.equal(await exported(),before);
  const invalid=JSON.parse(saved);invalid.version=99;const revision=(await state()).revision;await loadText(JSON.stringify(invalid));assert.match(await page.locator('#status').innerText(),/Unsupported canvas document/);assert.equal((await state()).revision,revision);assert.equal(await exported(),before);
  await load(path.resolve('examples/canvases/07_equal_sums.json'));await select('Moving pairs');await page.locator('[data-workspace-tool="connect"]').click();await fit();
  await page.locator('.workbench').screenshot({path:path.join(output,'cells-and-construction.png')});
  // Genuine 3D capture: all 240 occurrences remain addressable; a slice is view-only.
  await load(path.resolve('examples/canvases/03_incidence_box.json'));await select('X region');
  const boxBefore=await exported();assert.equal(await marks('X region').count(),240);assert.equal(await marks('X region').filter({has:page.locator('.scene-face')}).count(),240);
  assert.equal(await marks('X region').evaluateAll(ns=>ns.filter(n=>!n.classList.contains('outside')).length),86);
  const initialOrientation=await page.locator('#workspace-canvas').getAttribute('data-orientation');await page.locator('[data-workspace-tool="orbit"]').click();await page.locator('#workspace-canvas').scrollIntoViewIfNeeded();
  const box=await page.locator('#workspace-canvas').boundingBox(),p={x:box.x+box.width*.1,y:box.y+box.height*.5};
  await page.mouse.move(p.x,p.y);await page.mouse.down();await page.mouse.move(p.x+45,p.y+25,{steps:5});assert.notEqual(await page.locator('#workspace-canvas').getAttribute('data-orientation'),initialOrientation);await page.keyboard.press('Escape');await page.mouse.up();assert.equal(await page.locator('#workspace-canvas').getAttribute('data-orientation'),initialOrientation);
  await page.getByRole('button',{name:'XZ workspace view',exact:true}).click();const fullFit=await viewbox();
  const details=page.locator('[data-scene-selection] > details').first();if(!await details.evaluate(n=>n.open))await details.locator('summary').click();
  await page.locator('#scene-slice-axis').selectOption('z');await page.locator('#scene-slice-value').selectOption('2');assert.equal(await marks('X region').count(),60);
  await fit();assert.equal(await viewbox(),fullFit,'A slice must not change the fitted domain');
  const oracle=Array.from({length:10},(_,i)=>i+1).flatMap(u=>Array.from({length:6},(_,j)=>j+1).map(v=>11*v<=7*u&&11*2<=5*u)).filter(Boolean).length;
  assert.equal(await marks('X region').evaluateAll(ns=>ns.filter(n=>!n.classList.contains('outside')).length),oracle);
  await page.getByRole('button',{name:'3D workspace view',exact:true}).click();await page.getByRole('button',{name:'Center selected object',exact:true}).click();
  if(await page.locator('#scene-chooser').evaluate(n=>n.open))await page.locator('#scene-chooser > summary').click();
  await page.locator('#scene').screenshot({path:path.join(output,'box-slice.png')});assert.equal(await exported(),boxBefore);
  await page.emulateMedia({colorScheme:'dark'});await page.locator('#scene').screenshot({path:path.join(output,'box-slice-dark.png')});await page.emulateMedia({colorScheme:'light'});
  await page.locator('#scene-slice-axis').selectOption('');await page.getByRole('button',{name:'Show points',exact:true}).click();assert.equal(await marks('X region').count(),240);
  // Exact integers survive the document envelope; empty/failed roots stay selectable.
  const fixture=execFileSync(python,['-c',`from kaleion import Collection, Workspace, param
w=Workspace({'Huge':Collection.literal([2**100+1]),'Empty':Collection.grid(0,3,4),'Failed':Collection.sequence(param('n'))},{'n':-1},max_items=2000,max_history=40)
print(w.to_json())`],{encoding:'utf8'});
  await loadText(fixture);await select('Empty');assert.equal(await marks('Empty').count(),0);assert.match(await page.locator('[data-workspace-object="Empty"]').textContent(),/Empty domain/);await select('Failed');assert.match(await page.locator('#construction').innerText(),/Evaluation failed/);
  await select('Huge');const hugeSaved=await saveCanvas();assert.ok(JSON.parse(hugeSaved).workspace.includes('1267650600228229401496703205377'));await loadText(hugeSaved);assert.equal((await state()).objects.find(o=>o.name==='Huge').rows[0].fields.value,'1267650600228229401496703205377');
  await page.setViewportSize({width:360,height:1050});await load(path.resolve('examples/canvases/07_equal_sums.json'));await select('Moving pairs');await page.getByRole('button',{name:'Center selected object',exact:true}).tap();
  await page.getByRole('button',{name:'Show points',exact:true}).tap();await page.getByRole('button',{name:'Show cells',exact:true}).tap();assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.locator('#scene').screenshot({path:path.join(output,'phone-scene.png')});await page.setViewportSize({width:320,height:1000});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  assert.equal(mutations.length,2,'Only the deliberate sequence Preview and Apply evaluate or edit history');assert.deepEqual(errors,[]);
  fs.writeFileSync(path.join(output,'report.json'),JSON.stringify({browser:browser.version(),commonScale:true,identityAcrossCharts:true,sourceCreation:true,viewOnly3dSlices:true,losslessDocument:true,invalidVersionRejected:true,emptyAndFailed:true,phoneEmulation:true,errors},null,2));
  console.log('Shared scene browser checks passed.');
 }finally{await browser.close();server?.kill()}
})().catch(error=>{console.error(error);server?.kill();process.exitCode=1});
