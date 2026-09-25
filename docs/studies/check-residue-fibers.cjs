// Cross-lesson transfer: derive a total, use it for repetition and cyclic motion.
// All authoring uses controls; API reads below only check resulting captures.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {spawn}=require('node:child_process');
const {chromium}=require(process.env.KALEION_PLAYWRIGHT_MODULE||'playwright');
const output=path.resolve(process.argv[3]||'build/residue-check');fs.mkdirSync(output,{recursive:true});
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
  const apply=async()=>{await page.locator('#preview').click();await idle();assert.equal(await page.locator('#draft-status').getAttribute('data-phase'),'ready',await page.locator('#draft-status').innerText());await page.locator('#apply').click();await idle()};
  const group=label=>page.getByRole('group',{name:label,exact:true});
  async function formula(label,text){const box=group(label);await box.getByRole('button',{name:'Write a formula',exact:true}).click();await box.getByRole('textbox',{name:'Arithmetic formula',exact:true}).fill(text)}
  async function create(name,size,text){await close();await page.locator('#add').click();await page.locator('[data-action="vector"]').click();await page.locator('#result-name').fill(name);await page.getByLabel('Size i',{exact:true}).fill(size);await page.locator('#shape-contents').selectOption('formula');await page.locator('#shape-formula').fill(text);await page.locator('#apply').click();await idle()}
  async function field(source,name,key,text){await tool(source,'field');await page.locator('#result-name').fill(name);await page.locator('#field-name').fill(key);await formula('Field definition',text);await apply()}
  async function keyed(label,source,target){
    const box=group(label);await box.locator('[data-edit-root]').click();await box.getByLabel('Expression type',{exact:true}).selectOption('Keyed read');await box.getByLabel('Read from',{exact:true}).selectOption(source);await box.locator('[data-expression-done]').click();
    await box.locator('[data-path="read/on"]').click();
    if(target==='0'){await box.getByLabel('Expression type',{exact:true}).selectOption('Number');await box.getByLabel('Exact integer',{exact:true}).fill('0')}
    else{await box.getByLabel('Field',{exact:true}).selectOption(target)}
    await box.locator('[data-expression-done]').click();
  }
  async function keys(label){const box=group(label);while(await box.getByRole('button').count())await box.getByRole('button').first().click();for(const k of ['r','s'])await box.getByLabel(`Add ${label.toLowerCase()}`,{exact:true}).selectOption(k)}
  async function compare(right){await tool('Fiber sizes','compare');await keys('Left key fields');await page.locator('#comparison-right').selectOption(right);await keys('Right key fields');await page.locator('#comparison-expected').selectOption('Pair domain');await keys('Expected key fields');await page.locator('#check-comparison').click();await idle()}
  await page.goto(origin);await page.waitForFunction(()=>!document.getElementById('add').disabled);
  for(const [name,value] of [['a','6'],['b','4']]){await page.locator('#cases').click();await page.locator('#declare-parameter').click();await page.getByLabel('Parameter name',{exact:true}).last().fill(name);await page.getByLabel('Parameter value',{exact:true}).fill(value);await apply()}
  await create('Integers','a*b','i');
  await details('Integers');await page.locator('#quick-lens').click();await page.locator('#result-name').fill('Kernel');await page.getByText('Customize the formula',{exact:true}).click();await page.locator('[data-rule-write]').click();await page.getByRole('textbox',{name:'Relation rule',exact:true}).fill('(value % a = 0) and (value % b = 0)');await apply();
  await tool('Kernel','measure');await page.locator('#result-name').fill('Kernel size');await apply();assert.deepEqual((await object('Kernel size')).rows.map(r=>r.fields.value),['2']);
  await tool('Kernel size','values');await page.locator('#result-name').fill('Period');await page.locator('#values-formula').fill('a*b // value');await apply();assert.deepEqual((await object('Period')).rows.map(r=>r.fields.value),['12']);
  await field('Integers','With r','r','value % a');await field('With r','Points','s','value % b');
  await tool('Points','measure');await page.locator('#result-name').fill('Ranks');await page.locator('#reducer').selectOption('rank');for(const f of ['r','s'])await page.getByLabel('Add group keys',{exact:true}).selectOption(f);await page.locator('#rank-key').selectOption('i');await apply();
  await details('Points');await page.locator('#arrange').click();await page.getByLabel('Number of coordinates',{exact:true}).selectOption('3');for(const [c,f] of [['x','r'],['y','s'],['z','0']])await formula(`${c} coordinate`,f);await apply();const folded=await object('Points');
  await details('Points');await page.locator('#arrange').click();await keyed('z coordinate','Ranks','i');await apply();const stacked=await object('Points');assert.deepEqual(stacked.rows.map(r=>r.position[2]),Array(12).fill(0).concat(Array(12).fill(1)));assert.deepEqual(stacked.rows.map(r=>r.ref[1]),folded.rows.map(r=>r.ref[1]));
  await close();await page.locator('.camera-menu > summary').click();await page.getByRole('button',{name:'3D workspace view',exact:true}).click();await page.locator('.camera-menu > summary').click();
  await details('Points');await page.locator('#arrange').click();await page.locator('#transform-kind').selectOption('roll');await keyed('Shift · positive moves toward larger indices','Period','0');await apply();const cycled=await object('Points');assert.deepEqual(cycled.rows.map(r=>r.fields.value),Array.from({length:24},(_,i)=>String((i+12)%24)));await page.screenshot({path:path.join(output,'measured-fiber-action.png')});
  const frozen=await saved();await page.locator('#replay-progress').fill('12');assert.equal(await saved(),frozen);await page.locator('[data-replay-result]').click();await close();await page.locator('#undo').click();await idle();assert.deepEqual((await object('Points')).rows.map(r=>r.ref[1]),stacked.rows.map(r=>r.ref[1]));await page.locator('#redo').click();await idle();assert.equal(await saved(),frozen);
  // A measured singleton supplies a constructor; a pointwise read is not guessed.
  await create('Motif','3','9');await tool('Motif','reindex');await page.locator('#result-name').fill('Copies');await page.locator('#reindex-repeat-mode').selectOption('object');await page.locator('#reindex-repeat-source').selectOption('Kernel size');await apply();assert.equal((await object('Copies')).rows.length,6);
  await tool('Motif','reindex');await page.locator('#result-name').fill('Invalid copies');await page.locator('#reindex-repeat-mode').selectOption('object');await page.locator('#reindex-repeat-source').selectOption('Ranks');const before=await saved();await page.locator('#preview').click();await idle();assert.equal(await page.locator('#draft-status').getAttribute('data-phase'),'failed');assert.equal(await saved(),before);await page.locator('#cancel').click();await idle();
  await page.locator('#cases').click();await page.getByLabel('Value of a',{exact:true}).fill('7');await page.getByLabel('Value of b',{exact:true}).fill('5');await apply();assert.equal((await object('Copies')).rows.length,3);assert.deepEqual((await object('Period')).rows.map(r=>r.fields.value),['35']);assert.equal((await object('Points')).status,'ready');
  // The larger saved investigation retains zero pairs and the predicted formula.
  await close();await page.locator('#open').click();await page.locator('[data-example="12_residue_fibers"]').click();await page.locator('[data-example-load]').click();await page.waitForFunction(()=>!document.getElementById('open-menu').open);await idle();
  await compare('Pair domain');assert.match(await page.locator('#comparison-status').innerText(),/0 equal, 24 different/);
  await compare('Predicted sizes');assert.match(await page.locator('#comparison-status').innerText(),/24 equal/);
  await details('Moving residues');const capture=await saved();for(let i=0;i<3;i++){await page.locator('#undo').click();await idle()}for(let i=0;i<3;i++){await page.locator('#redo').click();await idle()}assert.equal(await saved(),capture);
  await tool('One period','reindex');await page.setViewportSize({width:360,height:900});await page.locator('#reindex-repeat-mode').selectOption('object');await page.locator('#reindex-repeat-source').selectOption('Kernel size');await page.locator('#reindex-repeat-source').scrollIntoViewIfNeeded();assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.screenshot({path:path.join(output,'phone-measured-repeat.png')});
  assert.deepEqual(errors,[]);fs.writeFileSync(path.join(output,'report.json'),JSON.stringify({browser:browser.version(),tasks:['counted period from blank','grouped rank-driven separation','measured kernel action and undo','live measured repetition','invalid multiple-value rejection','coprime parameter transfer','zero fibers and exact comparisons','saved three-stage replay','360px controls'],errors},null,2));console.log('Residue-fiber checks passed.');
 }finally{await browser.close();server?.kill()}
})().catch(error=>{console.error(error);server?.kill();process.exitCode=1});
