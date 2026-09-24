// Reproduce the walkthrough through public controls, then open the same saved
// investigations a reader can choose. API calls below are read-only oracles.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {spawn}=require('node:child_process');
const {chromium}=require(process.env.KALEION_PLAYWRIGHT_MODULE||'playwright');
const output=path.resolve(process.argv[3]||'build/tutorial-check');fs.mkdirSync(output,{recursive:true});
let origin=process.argv[2],server;
(async()=>{
 if(!origin){server=spawn(process.env.KALEION_PYTHON||'.venv/bin/python3',['-m','examples.studio','--port','0'],{stdio:['ignore','pipe','inherit']});origin=await new Promise((resolve,reject)=>{server.stdout.on('data',d=>{const m=String(d).match(/http:\/\/127\.0\.0\.1:\d+/);if(m)resolve(m[0])});server.once('error',reject)});}
 const browser=await chromium.launch(JSON.parse(process.env.KALEION_BROWSER_OPTIONS||'{}'));
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1050},hasTouch:true,reducedMotion:'reduce'}),errors=[],mutations=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/\/api\/(preview|preview-case|commit|undo|redo|import)$/.test(r.url()))mutations.push(r.url())});
  const idle=()=>page.waitForFunction(()=>!document.getElementById('options').disabled);
  const state=async()=>await(await page.request.get(origin+'/api/state')).json(),exported=async()=>await(await page.request.get(origin+'/api/export')).text();
  const object=async name=>(await state()).objects.find(o=>o.name===name),camera=()=>page.locator('#workspace-canvas').getAttribute('viewBox');
  const close=async()=>{if(await page.locator('#panel').isVisible())await page.locator('#close-panel').click()};
  const details=async name=>{await page.locator('#objects').selectOption(name);await idle();await page.locator('#options').click();await idle()};
  const preview=async()=>{await page.locator('#preview').click();await idle();assert.equal(await page.locator('#draft-status').getAttribute('data-phase'),'ready',await page.locator('#draft-status').innerText())};
  const apply=async()=>{await preview();await page.locator('#apply').click();await idle()};
  const next=()=>page.locator('[data-tutorial-next]').click();
  async function create(kind,name,formula){await close();await page.locator('#add').click();await page.locator(`[data-action="${kind}"]`).click();await page.locator('#result-name').fill(name);await page.getByLabel('Size i',{exact:true}).fill('n + 1');if(kind==='grid')await page.getByLabel('Size j',{exact:true}).fill('n + 1');await page.locator('#shape-contents').selectOption('formula');await page.locator('#shape-formula').fill(formula);await page.locator('#apply').click();await idle();assert.ok(await object(name))}
  async function load(id){await close();await page.locator('#open').click();await page.locator(`[data-example="${id}"]`).click();await page.locator('[data-example-load]').click();await page.waitForFunction(()=>!document.getElementById('open-menu').open);await idle()}
  async function compare(left,right,expected,keys){await details(left);await page.locator('#advanced-tools summary').click();await page.locator('[data-action="compare"]').click();for(const k of keys)await page.getByLabel('Add left key fields',{exact:true}).selectOption(k);await page.locator('#comparison-right').selectOption(right);for(const k of keys)await page.getByLabel('Add right key fields',{exact:true}).selectOption(k);await page.locator('#comparison-expected').selectOption(expected);for(const k of keys)await page.getByLabel('Add expected key fields',{exact:true}).selectOption(k);await page.locator('#check-comparison').click();await idle()}
  await page.goto(origin);await page.waitForFunction(()=>!document.getElementById('add').disabled);
  const initial=await exported(),requests=mutations.length;
  await page.locator('#open').click();await page.locator('[data-example="00_blank"]').waitFor();assert.equal(await page.locator('[data-example]').count(),11);
  await page.locator('[data-example="04_measured_plane"]').click();assert.equal(await exported(),initial);assert.equal(mutations.length,requests);
  await page.screenshot({path:path.join(output,'example-chooser.png')});
  await page.locator('[data-start-tutorial]').click();await next();await page.locator('[data-tutorial-previous]').click();assert.equal(await exported(),initial);assert.equal(mutations.length,requests);
  // The first step explicitly opens a blank capture; starting a guide alone did not.
  await load('00_blank');assert.equal((await state()).objects.length,0);await next();
  await page.locator('#cases').click();await page.locator('#declare-parameter').click();await page.getByLabel('Parameter name',{exact:true}).fill('n');await page.getByLabel('Parameter value',{exact:true}).fill('4');await apply();await next();
  await create('grid','Numbers','i + j');assert.equal((await object('Numbers')).rows.length,25);await next();
  await details('Numbers');await page.locator('#quick-lens').click();await page.locator('#result-name').fill('Triangle');await page.getByText('Customize the formula',{exact:true}).click();await page.locator('[data-rule-write]').click();await page.getByRole('textbox',{name:'Relation rule',exact:true}).fill('value < n');await apply();assert.equal((await object('Triangle')).rows.filter(r=>r.match).length,10);await next();
  await page.locator('#axis-total').click();await page.locator('#result-name').fill('Counts');await apply();assert.deepEqual((await object('Counts')).rows.map(r=>r.fields.value),['4','3','2','1','0']);await next();
  await create('vector','Markers','0');const beforeIds=(await object('Markers')).rows.map(r=>r.ref[1]);await next();
  await details('Counts');await page.locator('#combine').click();await page.locator('#combine-target').selectOption('Markers');await page.locator('#combine-place').click();await preview();assert.equal(await page.locator('#scene-chart').inputValue(),'placement');await page.locator('#apply').click();await idle();assert.equal(await page.locator('#scene-chart').inputValue(),'placement');
  assert.deepEqual((await object('Markers')).rows.map(r=>r.position),[[0,4],[1,3],[2,2],[3,1],[4,0]]);assert.deepEqual((await object('Markers')).rows.map(r=>r.ref[1]),beforeIds);assert.equal(await page.locator('#replay').isVisible(),true);await next();
  const captured=await exported(),replayRequests=mutations.length;await page.locator('#replay-progress').fill('12');assert.equal(await exported(),captured);assert.equal(mutations.length,replayRequests);await page.locator('[data-replay-result]').click();await close();await page.locator('#undo').click();await idle();assert.equal(await page.locator('#scene-chart').inputValue(),'logical');await page.locator('#redo').click();await idle();assert.equal(await exported(),captured);assert.equal(await page.locator('#scene-chart').inputValue(),'placement');
  await page.screenshot({path:path.join(output,'first-motion.png')});await next();
  await page.locator('#view-options').click();await page.locator('#scene-chooser summary').click();await page.locator('#scene-occurrence').selectOption({label:'2 · value 0'});await idle();await page.getByRole('button',{name:'Follow keyed read · 2',exact:true}).click();await idle();await page.locator('#view-contributors').click();await idle();assert.equal(await page.locator('.linked-card').nth(1).locator('[data-linked-member="true"]').count(),2);await next();
  await create('vector','Formula','n - i');await next();
  const beforeComparison=await exported();await compare('Counts','Formula','Formula',['i']);assert.equal(await page.locator('#comparison-status').getAttribute('data-phase'),'passed');assert.match(await page.locator('#comparison-status').innerText(),/5 equal/);assert.equal(await exported(),beforeComparison);await next();
  await page.locator('#cases').click();await page.getByLabel('Value of n',{exact:true}).fill('6');await apply();assert.deepEqual((await object('Counts')).rows.map(r=>r.fields.value),['6','5','4','3','2','1','0']);
  await details('Counts');await page.locator('#advanced-tools summary').click();await page.locator('[data-action="compare"]').click();await page.locator('#check-comparison').click();await idle();assert.match(await page.locator('#comparison-status').innerText(),/7 equal/);
  const saveEvent=page.waitForEvent('download');await page.locator('#save').click();await page.locator('#save-canvas').click();const saved=path.join(output,'tutorial-canvas.json');await(await saveEvent).saveAs(saved);await idle();
  const math=await exported();await page.locator('#open').click();const chooser=page.waitForEvent('filechooser');await page.locator('[data-open-file]').click();await(await chooser).setFiles(saved);await idle();assert.equal(await exported(),math);
  await page.locator('#cases').click();await page.getByLabel('Value of n',{exact:true}).fill('0');await apply();assert.deepEqual((await object('Counts')).rows.map(r=>r.fields.value),['0']);
  await page.getByRole('button',{name:'End guide',exact:true}).click();
  // The larger comparison asks for one owner at every key, not just a total.
  await load('03_cell_coverage');await compare('Cell owners','One per cell','Box',['i','j','k']);assert.match(await page.locator('#comparison-status').innerText(),/24 equal/);
  await load('03_tied_coverage');await compare('Cell owners','One per cell','Box',['i','j','k']);assert.match(await page.locator('#comparison-status').innerText(),/58 equal, 2 different/);assert.match(await page.locator('#comparison-witness').innerText(),/Residual \(left − right\): 1/);await page.screenshot({path:path.join(output,'shared-cell-witness.png')});
  // Open every other shipped example through the chooser, with reversible motion.
  for(const [id,active,moves] of [['00_first_motion','Markers',1],['01_triangle_packing','Moving cells',1],['04_measured_plane','Lifted plane',3],['02_floor_sums','Pieces',1],['03_incidence_box','X region',0],['05_radon_reconstruction','Image heights',1],['06_young_layers','Cells',2],['07_equal_sums','Moving pairs',2]]){
    await load(id);assert.equal(await page.locator('#objects').inputValue(),active);assert.ok((await state()).objects.every(o=>o.status==='ready'));const before=await exported();
    for(let i=0;i<moves;i++){await page.locator('#undo').click();await idle()}
    for(let i=0;i<moves;i++){await page.locator('#redo').click();await idle()}
    assert.equal(await exported(),before);if(moves)assert.equal(await page.locator('#replay').isVisible(),true);
  }
  // Catalog reads cannot serve a supplied path, nor does a failed load lose work.
  assert.equal((await page.request.get(origin+'/api/examples/%2e%2e%2fserver.py')).status(),404);
  const kept=await exported();await page.locator('#open').click();await page.locator('[data-example="00_first_motion"]').click();await page.route('**/api/examples/00_first_motion',r=>r.fulfill({status:404,contentType:'application/json',body:'{}'}));await page.locator('[data-example-load]').click();await page.waitForFunction(()=>document.querySelector('[data-example-status]').textContent.includes('Could not open'));assert.equal(await exported(),kept);await page.unroute('**/api/examples/00_first_motion');
  await page.locator('[data-close-library]').click();await load('00_first_motion');
  // A deliberate logical chart survives browsing, replay and cancelled edits.
  // A new coordinate command explicitly previews/applies the placement again.
  await page.locator('#view-options').click();await page.locator('#scene-chart').selectOption('logical');await close();await page.locator('#undo').click();await idle();await page.locator('#redo').click();await idle();
  await page.locator('#view-options').click();await page.locator('#scene-chart').selectOption('logical');await close();await page.locator('#replay-progress').fill('12');await page.locator('[data-replay-result]').click();assert.equal(await page.locator('#scene-chart').inputValue(),'logical');
  await details('Counts');await details('Markers');assert.equal(await page.locator('#scene-chart').inputValue(),'logical');
  const unedited=await exported();await page.locator('#advanced-tools summary').click();await page.locator('[data-action="place"]').click();await preview();assert.equal(await page.locator('#scene-chart').inputValue(),'placement');await page.locator('#cancel').click();await idle();assert.equal(await page.locator('#scene-chart').inputValue(),'logical');assert.equal(await exported(),unedited);
  await details('Markers');await page.locator('#advanced-tools summary').click();await page.locator('[data-action="place"]').click();await apply();assert.equal(await page.locator('#scene-chart').inputValue(),'placement');await load('00_first_motion');
  await page.setViewportSize({width:360,height:900});await page.locator('#open').click();await page.locator('[data-example="04_measured_plane"]').tap();assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.screenshot({path:path.join(output,'phone-examples.png')});
  await page.locator('[data-start-tutorial]').click();const beforeGuide=await exported(),beforeCamera=await camera(),guideRequests=mutations.length;await page.locator('[data-tutorial-next]').focus();await page.keyboard.press('Enter');assert.equal(await page.locator('[data-tutorial-next]').evaluate(n=>n===document.activeElement),true);assert.equal(await exported(),beforeGuide);assert.equal(await camera(),beforeCamera);assert.equal(mutations.length,guideRequests);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.screenshot({path:path.join(output,'phone-guide.png')});
  await page.getByRole('button',{name:'End guide',exact:true}).click();assert.equal(await page.locator('#open').evaluate(n=>n===document.activeElement),true);assert.equal(await exported(),beforeGuide);
  assert.deepEqual(errors,[]);fs.writeFileSync(path.join(output,'report.json'),JSON.stringify({browser:browser.version(),tasks:['all eleven catalog entries','walkthrough from blank','measurement-driven motion','placement visibility and cancelled preview','nested contributors','finite comparison','parameter change and zero case','save and reopen','3D equality and counterexample','captured multi-stage reverse','read-only guide navigation','failed load','keyboard and emulated touch'],errors},null,2));console.log('Canvas tutorial checks passed.');
 }finally{await browser.close();server?.kill()}
})().catch(error=>{console.error(error);server?.kill();process.exitCode=1});
