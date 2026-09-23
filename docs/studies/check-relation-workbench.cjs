// HISTORICAL: targets the UI at commit 19928e6. For the current canvas run
// node docs/studies/check-continuous-canvas.cjs. See studies/README.md.
// Real-control gate: quick patterns, copied lenses, repeated axis totals and draft isolation.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {spawn,execFileSync}=require('node:child_process');
const {chromium}=require(process.env.KALEION_PLAYWRIGHT_MODULE||'playwright');
const python=process.env.KALEION_PYTHON||'.venv/bin/python3';
let origin=process.argv[2],server;
const output=path.resolve(process.argv[3]||'build/relation-workbench-check');fs.mkdirSync(output,{recursive:true});
(async()=>{
 if(!origin){server=spawn(python,['-m','examples.studio','--port','0'],{stdio:['ignore','pipe','inherit']});origin=await new Promise((resolve,reject)=>{let text='';server.stdout.on('data',chunk=>{text+=chunk;const match=text.match(/http:\/\/127\.0\.0\.1:\d+/);if(match)resolve(match[0])});server.once('error',reject);server.once('exit',code=>reject(Error(`Host stopped: ${code}`)))});}
 const browser=await chromium.launch(JSON.parse(process.env.KALEION_BROWSER_OPTIONS||'{}'));
 try{
  const page=await browser.newPage({viewport:{width:1400,height:1050},hasTouch:true,reducedMotion:'reduce'}),errors=[],evaluations=[];
  page.on('pageerror',e=>errors.push(String(e)));
  page.on('request',r=>{if(/\/api\/(preview|commit|preview-case|undo|redo)$/.test(r.url()))evaluations.push(r.url())});
  await page.goto(origin);await page.waitForFunction(()=>!document.getElementById('add').disabled);
  const idle=()=>page.waitForFunction(()=>!document.getElementById('options').disabled);
  const state=async()=>await(await page.request.get(origin+'/api/state')).json(),exported=async()=>await(await page.request.get(origin+'/api/export')).text();
  const select=async name=>{await page.locator(`[data-object=${JSON.stringify(name)}]`).click();await idle()};
  const object=async name=>(await state()).objects.find(o=>o.name===name);
  const marks=name=>page.locator(`[data-scene-owner=${JSON.stringify(name)}]`);
  const preview=async()=>{await page.locator('#preview').click();await idle();assert.equal(await page.locator('#apply').isEnabled(),true,await page.locator('#draft-status').textContent())};
  const apply=async()=>{await preview();await page.locator('#apply').click();await idle();assert.equal(await page.locator('#workspace-view').isVisible(),true)};
  const lens=async (name,result)=>{await select(name);await page.locator('#quick-lens').click();await page.locator('#result-name').fill(result)};
  const total=async (name,result)=>{await select(name);await page.locator('#axis-total').click();await page.locator('#result-name').fill(result)};
  async function save(){const promise=page.waitForEvent('download');await page.locator('#save').click();await page.locator('#save-canvas').click();const download=await promise,file=path.join(output,'canvas.json');await download.saveAs(file);await idle();return fs.readFileSync(file,'utf8')}
  const fixture=execFileSync(python,['-c',`from kaleion import Collection, Workspace, F
roots={'Numbers':Collection.sequence(6,start=0),'Rectangle':Collection.grid(4,5,values=F.i+F.j),'Renamed':Collection.grid(3,4,axes=('u','v')),'Cube':Collection.grid(3,4,5),'Empty':Collection.grid(2,0,3)}
print(Workspace(roots,max_items=2000,max_history=40).to_json())`],{encoding:'utf8'});
  await page.locator('#file').setInputFiles({name:'patterns.json',mimeType:'application/json',buffer:Buffer.from(fixture)});await idle();await select('Numbers');
  const before=await exported(),camera=await page.locator('#workspace-canvas').getAttribute('viewBox');
  await lens('Numbers','Evens');await preview();assert.equal(await marks('Evens').count(),6);assert.equal(await marks('Evens').evaluateAll(ns=>ns.filter(n=>!n.classList.contains('outside')).length),3);assert.match(await page.locator('#draft-status').innerText(),/3 of 6 match/);assert.equal(await exported(),before);
  const draftSave=JSON.parse(await save());assert.equal(draftSave.workspace,before);assert.equal(draftSave.scene.objects.some(o=>o.name==='Evens'),false);
  await page.locator('#cancel').click();await idle();assert.equal(await marks('Evens').count(),0);assert.equal(await page.locator('#workspace-canvas').getAttribute('viewBox'),camera);
  await lens('Numbers','Evens');await apply();assert.deepEqual((await object('Evens')).rows.filter(r=>r.match).map(r=>r.fields.value),['0','2','4']);
  await lens('Rectangle','Diagonal');assert.equal(await page.getByLabel('Number of lens inputs').inputValue(),'2');await apply();assert.equal((await object('Diagonal')).rows.filter(r=>r.match).length,4);
  await lens('Cube','Add together');assert.equal(await page.getByLabel('Number of lens inputs').inputValue(),'3');
  await preview();assert.match(await page.locator('#draft-status').innerText(),/11 of 60 match/);
  await page.locator('.workbench').screenshot({path:path.join(output,'ternary-preview.png')});
  // Parking a scene draft restores the applied scene and resumes on the same surface.
  await page.getByRole('button',{name:'On Cube · inspect source',exact:true}).click();assert.equal(await marks('Add together').count(),0);assert.match(await page.locator('#draft-title').innerText(),/parked/);assert.equal(await page.locator('#construction').isVisible(),true);
  await page.locator('#resume-draft').click();assert.equal(await page.locator('#workspace-view').isVisible(),true);assert.equal(await page.locator('#result-name').inputValue(),'Add together');await apply();
  // A view slice is not an input filter for the mathematical reduction.
  await page.locator('[data-scene-selection] > details').first().locator('summary').click();await page.locator('#scene-slice-axis').selectOption('k');await page.locator('#scene-slice-value').selectOption('2');assert.equal(await marks('Add together').count(),12);
  await total('Add together','Plane totals');assert.equal(await page.getByLabel('Total along k',{exact:true}).isChecked(),true);await apply();
  const plane=await object('Plane totals'),expected=[];for(let i=0;i<3;i++)for(let j=0;j<4;j++)expected.push(String(i+j<5?1:0));assert.deepEqual(plane.rows.map(r=>r.fields.value),expected);assert.deepEqual(plane.total_fields,['i','j']);assert.equal(plane.dimension,2);
  await page.getByRole('button',{name:'XY workspace view',exact:true}).click();await page.getByRole('button',{name:'Center selected object',exact:true}).click();await page.locator('.workbench').screenshot({path:path.join(output,'plane-totals.png')});
  await total('Plane totals','Line totals');assert.equal(await page.getByLabel('Total operation').inputValue(),'sum');await apply();assert.deepEqual((await object('Line totals')).rows.map(r=>r.fields.value),['4','4','3']);
  await total('Line totals','Grand total');await apply();assert.deepEqual((await object('Grand total')).rows.map(r=>r.fields.value),['11']);
  // A connection proposal never evaluates; applying a rule requires named field bindings.
  await select('Diagonal');const unchanged=await exported(),requestsBeforeDrop=evaluations.length;
  await page.locator('[data-workspace-tool="connect"]').click();await page.getByRole('button',{name:'Fit workspace view',exact:true}).click();await page.locator('#workspace-canvas').scrollIntoViewIfNeeded();
  const center=async name=>{const b=await page.locator(`[data-workspace-object=${JSON.stringify(name)}]`).boundingBox();return{x:b.x+b.width/2,y:b.y+b.height/2}};
  const a=await center('Diagonal'),b=await center('Renamed');await page.mouse.move(a.x,a.y);await page.mouse.down();await page.mouse.move(b.x,b.y,{steps:10});await page.mouse.up();
  assert.equal(await page.locator('#combine-source').inputValue(),'Diagonal');assert.equal(await page.locator('#combine-target').inputValue(),'Renamed');assert.equal(evaluations.length,requestsBeforeDrop);
  await page.locator('#combine-lens').click();assert.equal(await exported(),unchanged);await page.locator('#result-name').fill('New diagonal');
  await page.getByLabel('Map rule input i',{exact:true}).selectOption('u');await page.getByLabel('Map rule input j',{exact:true}).selectOption('v');await apply();assert.deepEqual((await object('New diagonal')).rows.filter(r=>r.match).map(r=>[r.fields.u,r.fields.v]),[['0','0'],['1','1'],['2','2']]);assert.equal((await object('Diagonal')).rows.length,20);
  await total('Empty','Empty fibers');await page.getByLabel('Total along k',{exact:true}).uncheck();await page.getByLabel('Total along j',{exact:true}).check();await apply();assert.deepEqual((await object('Empty fibers')).rows.map(r=>r.fields.value),Array(6).fill('0'));
  // Captured restore never reevaluates. Saved examples retain ordinary core export compatibility.
  const saved=await save(),exact=await exported();await page.locator('#file').setInputFiles({name:'saved.json',mimeType:'application/json',buffer:Buffer.from(saved)});await idle();assert.equal(await exported(),exact);
  await page.locator('#undo').click();await idle();assert.equal((await state()).objects.some(o=>o.name==='Empty fibers'),false);await page.locator('#redo').click();await idle();assert.equal((await object('Empty fibers')).rows.length,6);
  await page.locator('[data-surface="workspace"]').click();await select('Cube');await page.setViewportSize({width:360,height:1050});await page.locator('#quick-lens').tap();await page.locator('#result-name').fill('Phone pattern');await page.getByLabel('Pattern',{exact:true}).selectOption('ordered');await preview();
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.locator('#panel').screenshot({path:path.join(output,'phone-lens.png')});await page.setViewportSize({width:320,height:1000});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  // The full formula editor remains available; a starter is no longer presented as the current rule.
  await page.locator('.pattern-controls details > summary').click();await page.getByRole('button',{name:'Edit field i',exact:true}).click();await page.getByLabel('Field',{exact:true}).selectOption('value');await page.locator('[data-expression-done]').click();
  // Cube values are 20*i + 5*j + k + 1, always greater than j on this domain.
  assert.equal(await page.locator('.pattern-controls details > summary').innerText(),'Custom formula');await preview();assert.match(await page.locator('#draft-status').innerText(),/0 of 60 match/);
  assert.deepEqual(errors,[]);fs.writeFileSync(path.join(output,'report.json'),JSON.stringify({browser:browser.version(),patterns:'one/two/three inputs',reuse:'explicit field mapping',totals:'cube/plane/line/scalar; retained zeros',draftPreview:'not exported; park/resume/cancel',phoneEmulation:true,errors},null,2));
  console.log('Relation workbench browser checks passed.');
 }finally{await browser.close();server?.kill()}
})().catch(error=>{console.error(error);server?.kill();process.exitCode=1});
