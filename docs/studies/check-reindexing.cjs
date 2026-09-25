// Author copies, padding and guarded addresses through public controls from blank.
// API requests are read-only oracles, never shortcuts for authoring.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {spawn}=require('node:child_process');
const {chromium}=require(process.env.KALEION_PLAYWRIGHT_MODULE||'playwright');
const output=path.resolve(process.argv[3]||'build/reindex-check');fs.mkdirSync(output,{recursive:true});
let origin=process.argv[2],server;
(async()=>{
 if(!origin){server=spawn(process.env.KALEION_PYTHON||'.venv/bin/python3',['-m','examples.studio','--port','0'],{stdio:['ignore','pipe','inherit']});origin=await new Promise((resolve,reject)=>{server.stdout.on('data',d=>{const m=String(d).match(/http:\/\/127\.0\.0\.1:\d+/);if(m)resolve(m[0])});server.once('error',reject)});}
 const browser=await chromium.launch(JSON.parse(process.env.KALEION_BROWSER_OPTIONS||'{}'));
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1050},hasTouch:true,reducedMotion:'reduce'}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  const idle=()=>page.waitForFunction(()=>!document.getElementById('options').disabled);
  const state=async()=>await(await page.request.get(origin+'/api/state')).json();
  const saved=async()=>await(await page.request.get(origin+'/api/export')).text();
  const object=async name=>(await state()).objects.find(o=>o.name===name);
  const close=async()=>{if(await page.locator('#panel').isVisible())await page.locator('#close-panel').click()};
  const details=async name=>{await page.locator('#objects').selectOption(name);await idle();await page.locator('#options').click();await idle()};
  const tool=async(name,action)=>{await details(name);await page.locator('#advanced-tools summary').click();await page.locator(`[data-action="${action}"]`).click()};
  const preview=async()=>{await page.locator('#preview').click();await idle();assert.equal(await page.locator('#draft-status').getAttribute('data-phase'),'ready',await page.locator('#draft-status').innerText())};
  const apply=async()=>{await preview();await page.locator('#apply').click();await idle()};
  const group=label=>page.getByRole('group',{name:label,exact:true});
  async function formula(label,text){const box=group(label);await box.getByRole('button',{name:'Write a formula',exact:true}).click();await box.getByRole('textbox',{name:'Arithmetic formula',exact:true}).fill(text)}
  async function create(name,sizes,formulaText){await close();await page.locator('#add').click();await page.locator(`[data-action="${sizes.length===1?'vector':'grid'}"]`).click();await page.locator('#result-name').fill(name);for(let i=0;i<sizes.length;i++)await page.getByLabel(`Size ${['i','j'][i]}`,{exact:true}).fill(sizes[i]);await page.locator('#shape-contents').selectOption('formula');await page.locator('#shape-formula').fill(formulaText);await page.locator('#apply').click();await idle()}
  async function rule(source,name,text){await details(source);await page.locator('#quick-lens').click();await page.locator('#result-name').fill(name);await page.getByText('Customize the formula',{exact:true}).click();await page.locator('[data-rule-write]').click();await page.getByRole('textbox',{name:'Relation rule',exact:true}).fill(text);await apply()}
  async function copy(source,name,kind,axis){await tool(source,'reindex');await page.locator('#result-name').fill(name);await page.locator('#reindex-kind').selectOption(kind);await page.locator('#reindex-axis').selectOption(axis)}
  async function load(id){await close();await page.locator('#open').click();await page.locator(`[data-example="${id}"]`).click();await page.locator('[data-example-load]').click();await page.waitForFunction(()=>!document.getElementById('open-menu').open);await idle()}
  async function inspect(name,index){await details(name);await page.locator('#view-options').click();if(await page.locator('#scene-chooser').getAttribute('open')===null)await page.locator('#scene-chooser summary').click();const ref=(await object(name)).rows[index].ref;await page.locator('#scene-occurrence').selectOption(JSON.stringify(ref));await idle()}
  async function keyedTuple(label,source){
    const box=group(label);await box.getByRole('button',{name:'Use controls',exact:true}).click();await page.waitForFunction(label=>document.querySelector(`[aria-label="${label}"] [data-rule-controls]`).getAttribute('aria-pressed')==='true',label);
    await box.locator('[data-edit-root]').click();await box.getByLabel('Expression type',{exact:true}).selectOption('Keyed read');await box.getByLabel('Read from',{exact:true}).selectOption(source);await box.locator('[data-expression-done]').click();
    for(const part of ['on','key']){
      await box.locator(`[data-path="read/${part}"]`).click();await box.getByLabel('Expression type',{exact:true}).selectOption('Key tuple');await box.locator('[data-expression-done]').click();
      for(const [i,field] of ['i','j'].entries()){await box.locator(`[data-path="read/${part}/tuple/${i}"]`).click();await box.getByLabel('Field',{exact:true}).selectOption(field);await box.locator('[data-expression-done]').click()}
    }
  }
  await page.goto(origin);await page.waitForFunction(()=>!document.getElementById('add').disabled);
  await page.locator('#cases').click();await page.locator('#declare-parameter').click();await page.getByLabel('Parameter name',{exact:true}).fill('a');await page.getByLabel('Parameter value',{exact:true}).fill('5');await apply();
  await create('Period domain',['3','3'],'0');await rule('Period domain','Period relation','(a*j + i) % 3 = 0');
  await tool('Period relation','measure');await page.locator('#result-name').fill('Measured cells');for(const k of ['i','j'])await page.getByLabel('Add group keys',{exact:true}).selectOption(k);await apply();
  await tool('Period domain','values');await page.locator('#result-name').fill('Period');await keyedTuple('Value at each location','Measured cells');await apply();
  assert.deepEqual((await object('Period')).rows.map(r=>r.fields.value),['1','0','0','0','1','0','0','0','1']);
  // First attach the explicit chart, so extension can split recorded source tracks.
  await details('Period');await page.locator('#arrange').click();await formula('x coordinate','j');await formula('y coordinate','i');await apply();
  const original=await object('Period');await copy('Period','Period','tile','i');await page.locator('#reindex-times').fill('2');await preview();const unedited=await saved();await page.locator('#cancel').click();await idle();assert.equal(await saved(),unedited);
  await copy('Period','Period','tile','i');await page.locator('#reindex-times').fill('2');await apply();assert.equal((await object('Period')).rows.length,18);
  const repeated=await saved();await page.locator('#replay-progress').fill('12');assert.equal(await saved(),repeated);await page.screenshot({path:path.join(output,'repeated-period.png')});await page.locator('[data-replay-result]').click();
  // Copy evidence follows recorded parents, not an equal-valued cell.
  await inspect('Period',9);const captured=await saved();await page.locator('#follow-source-occurrence').click();await idle();await page.locator('#follow-source-occurrence').click();await idle();assert.equal(await saved(),captured);assert.ok(await page.locator('#receipt-back').isVisible());await page.screenshot({path:path.join(output,'copy-source.png')});
  await close();await page.locator('#undo').click();await idle();assert.deepEqual((await object('Period')).rows.map(r=>r.ref),original.rows.map(r=>r.ref));await page.locator('#redo').click();await idle();assert.equal(await saved(),repeated);
  await create('Rows',['5'],'i');await copy('Period','Prefix','gather','i');await page.locator('#reindex-addresses').selectOption('Rows');await apply();assert.equal((await object('Prefix')).rows.length,15);
  await copy('Prefix','Rejected','gather','i');await page.locator('#reindex-addresses').selectOption('Measured cells');await page.locator('#reindex-order').selectOption('value');await page.locator('#preview').click();await idle();assert.match(await page.locator('#draft-status').innerText(),/order must be unique/);await page.locator('#cancel').click();await idle();
  // Explicit new zero occurrences, with matching fields and nonjoined sizes.
  await create('Zeros',['5','2'],'0');await copy('Prefix','Padded','concat','j');await page.locator('#reindex-other').selectOption('Zeros');await apply();const padded=await object('Padded');assert.deepEqual(padded.shape,['5','5']);assert.ok(padded.rows.filter(r=>Number(r.fields.j)>=3).every(r=>r.fields.value==='0'));
  await inspect('Padded',3);await page.locator('#follow-source-occurrence').click();await idle();await page.locator('#follow-source-occurrence').click();await idle();assert.match(await page.locator('#activity h2').first().innerText(),/0/);
  // Derive addresses through coverage, then use them on unrelated identical labels.
  await create('R domain',['3','3'],'0');await rule('R domain','R relation','j = (a*i) % 3');await create('Slots',['3'],'0');
  await tool('R relation','coverage');await page.getByLabel('Add source group keys',{exact:true}).selectOption('j');await page.locator('#coverage-expected').selectOption('Slots');await page.getByLabel('Add expected key fields',{exact:true}).selectOption('i');await page.locator('#check-coverage').click();await idle();assert.match(await page.locator('#coverage-status').innerText(),/3 of 3/);
  await page.locator('#coverage-adopt').click();await page.locator('#result-name').fill('Addresses');await page.locator('#assigned-field').fill('address');await formula('Value supplied by the unique match','i');await apply();assert.deepEqual((await object('Addresses')).rows.map(r=>r.fields.address),['0','2','1']);
  await create('Scattered',['3'],'9');await details('Scattered');await page.locator('#arrange').click();await page.getByLabel('Number of coordinates',{exact:true}).selectOption('3');for(const [c,f] of [['x','i'],['y','i*i'],['z','i%2']])await formula(`${c} coordinate`,f);await apply();
  const points=await object('Scattered');await copy('Scattered','Scattered','gather','');await page.locator('#reindex-addresses').selectOption('Addresses');await page.locator('#reindex-field').selectOption('address');await page.locator('#reindex-order').selectOption('i');await page.locator('#reindex-claim').selectOption('bijective');await apply();const moved=await object('Scattered');assert.deepEqual(moved.rows.map(r=>r.fields.value),['9','9','9']);assert.deepEqual(moved.rows.map(r=>r.fields.i),['0','2','1']);assert.ok(moved.rows.every(r=>!points.rows.some(p=>p.ref[1]===r.ref[1])));assert.equal(moved.dimension,3);
  await page.locator('#cases').click();await page.getByLabel('Value of a',{exact:true}).fill('6');await apply();assert.equal((await object('R relation')).status,'ready');assert.equal((await object('Addresses')).status,'failed');assert.equal((await object('Scattered')).status,'failed');assert.equal((await object('Padded')).status,'ready');
  for(const [id,name,steps] of [['12_periodic_extension','Moving factor',2],['12_guarded_addresses','Moving copies',1]]){await load(id);const before=await saved();for(let i=0;i<steps;i++){await page.locator('#undo').click();await idle()}for(let i=0;i<steps;i++){await page.locator('#redo').click();await idle()}assert.equal(await saved(),before);assert.equal(await page.locator('#objects').inputValue(),name)}
  await copy('Scattered source','More copies','tile','i');await page.setViewportSize({width:360,height:900});await page.locator('#reindex-times').tap();await page.locator('#reindex-times').fill('2');assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.screenshot({path:path.join(output,'phone-reindex.png')});
  assert.deepEqual(errors,[]);fs.writeFileSync(path.join(output,'report.json'),JSON.stringify({browser:browser.version(),tasks:['incidence measurements become contents through tuple reads','repeat and truncate from blank','copy source navigation','explicit zero join','unique address order','guarded relation addresses on identical labels in 3D','nonunit failure isolation','new captures and reverse motion','360px emulated touch'],errors},null,2));console.log('Reindexing checks passed.');
 }finally{await browser.close();server?.kill()}
})().catch(error=>{console.error(error);server?.kill();process.exitCode=1});
