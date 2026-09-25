// Construct from blank through public controls. Requests below only read oracles.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {spawn}=require('node:child_process');
const {chromium}=require(process.env.KALEION_PLAYWRIGHT_MODULE||'playwright');
const output=path.resolve(process.argv[3]||'build/division-check');fs.mkdirSync(output,{recursive:true});
let origin=process.argv[2],server;
(async()=>{
 if(!origin){server=spawn(process.env.KALEION_PYTHON||'.venv/bin/python3',['-m','examples.studio','--port','0'],{stdio:['ignore','pipe','inherit']});origin=await new Promise((resolve,reject)=>{server.stdout.on('data',d=>{const m=String(d).match(/http:\/\/127\.0\.0\.1:\d+/);if(m)resolve(m[0])});server.once('error',reject)});}
 const browser=await chromium.launch(JSON.parse(process.env.KALEION_BROWSER_OPTIONS||'{}'));
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1050},hasTouch:true,reducedMotion:'reduce'}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  const idle=()=>page.waitForFunction(()=>!document.getElementById('options').disabled);
  const state=async()=>await(await page.request.get(origin+'/api/state')).json();
  const exported=async()=>await(await page.request.get(origin+'/api/export')).text();
  const object=async name=>(await state()).objects.find(o=>o.name===name);
  const close=async()=>{if(await page.locator('#panel').isVisible())await page.locator('#close-panel').click()};
  const details=async name=>{await page.locator('#objects').selectOption(name);await idle();await page.locator('#options').click();await idle()};
  const preview=async()=>{await page.locator('#preview').click();await idle();assert.equal(await page.locator('#draft-status').getAttribute('data-phase'),'ready',await page.locator('#draft-status').innerText())};
  const apply=async()=>{await preview();await page.locator('#apply').click();await idle()};
  const group=label=>page.getByRole('group',{name:label,exact:true});
  async function formula(label,text){const box=group(label);await box.getByRole('button',{name:'Write a formula',exact:true}).click();await box.getByRole('textbox',{name:'Arithmetic formula',exact:true}).fill(text)}
  async function keyed(label,source){
    const box=group(label);
    if(source){await box.locator('[data-edit-root]').click();await box.getByLabel('Expression type',{exact:true}).selectOption('Keyed read');
      await box.getByLabel('Read from',{exact:true}).selectOption(source);await box.locator('[data-expression-done]').click();}
    for(const part of ['on','key']){await box.locator(`[data-path="read/${part}"]`).click();await box.getByLabel('Field',{exact:true}).selectOption('i');await box.locator('[data-expression-done]').click()}
  }
  async function transform(name,kind){await details(name);await page.locator('#arrange').click();await page.locator('#transform-kind').selectOption(kind)}
  async function driven(name,kind){await details('Quotients');await page.locator('#combine').click();await page.locator('#combine-target').selectOption(name);await page.getByRole('button',{name:'Drive a transformation',exact:true}).click();await page.locator('#transform-kind').selectOption(kind)}
  async function create(name,sizes,rule){await close();await page.locator('#add').click();await page.locator('[data-action="grid"]').click();await page.locator('#result-name').fill(name);await page.getByLabel('Size i',{exact:true}).fill(sizes[0]);await page.getByLabel('Size j',{exact:true}).fill(sizes[1]);await page.locator('#shape-contents').selectOption('formula');await page.locator('#shape-formula').fill(rule);await page.locator('#apply').click();await idle()}
  async function load(id){await close();await page.locator('#open').click();await page.locator(`[data-example="${id}"]`).click();await page.locator('[data-example-load]').click();await page.waitForFunction(()=>!document.getElementById('open-menu').open);await idle()}
  async function relation(source,name,text){await details(source);await page.locator('#quick-lens').click();await page.locator('#result-name').fill(name);await page.getByText('Customize the formula',{exact:true}).click();await page.locator('[data-rule-write]').click();await page.getByRole('textbox',{name:'Relation rule',exact:true}).fill(text);await apply()}
  async function field(source,name,key,text){await details(source);await page.locator('#advanced-tools summary').click();await page.locator('[data-action="field"]').click();await page.locator('#result-name').fill(name);await page.locator('#field-name').fill(key);await formula('Field definition',text);await apply()}
  async function compare(left,leftKeys,right,rightKeys,expected,expectedKeys){await details(left);await page.locator('#advanced-tools summary').click();await page.locator('[data-action="compare"]').click();for(const k of leftKeys)await page.getByLabel('Add left key fields',{exact:true}).selectOption(k);await page.locator('#comparison-right').selectOption(right);for(const k of rightKeys)await page.getByLabel('Add right key fields',{exact:true}).selectOption(k);await page.locator('#comparison-expected').selectOption(expected);for(const k of expectedKeys)await page.getByLabel('Add expected key fields',{exact:true}).selectOption(k);await page.locator('#check-comparison').click();await idle()}
  await page.goto(origin);await page.waitForFunction(()=>!document.getElementById('add').disabled);
  await create('Raw',['7','11'],'11*i + 7*j');
  await relation('Raw','Carries','value >= 77');
  await page.locator('#axis-total').click();await page.locator('#result-name').fill('Quotients');await apply();assert.deepEqual((await object('Quotients')).rows.map(r=>r.fields.value),['0','1','3','4','6','7','9']);
  await create('Residues',['7','11'],'(11*i + 7*j) % 77');
  await transform('Residues','place');await formula('x coordinate','j');await formula('y coordinate','i');await apply();
  const original=await object('Residues');
  await transform('Residues','move');await keyed('x displacement','Quotients');await preview();const beforeCancel=await exported();await page.locator('#cancel').click();await idle();assert.equal(await exported(),beforeCancel);
  await driven('Residues','move');await keyed('x displacement');await apply();
  const displaced=await object('Residues');assert.deepEqual(displaced.rows.map(r=>r.ref[1]),original.rows.map(r=>r.ref[1]));assert.equal(displaced.rows[66].position[0],9);
  await page.screenshot({path:path.join(output,'measured-shear.png')});
  await close();await page.locator('#undo').click();await idle();assert.deepEqual((await object('Residues')).rows.map(r=>r.position),original.rows.map(r=>r.position));
  await driven('Residues','roll');await keyed('Shift · positive moves toward larger indices');await apply();
  const rolled=await object('Residues');assert.deepEqual(rolled.rows.map(r=>r.position),original.rows.map(r=>r.position));assert.deepEqual(rolled.rows.filter((_,i)=>i%11===0).map(r=>r.fields.value),['0','4','1','5','2','6','3']);
  const saved=await exported();await page.locator('#replay-progress').fill('12');assert.equal(await exported(),saved);await page.screenshot({path:path.join(output,'cyclic-motion.png')});await page.locator('[data-replay-result]').click();
  // A shift cannot silently vary along the axis it cycles.
  await transform('Residues','roll');await formula('Shift · positive moves toward larger indices','j');await page.locator('#preview').click();await idle();assert.equal(await page.locator('#draft-status').getAttribute('data-phase'),'failed');assert.match(await page.locator('#draft-status').innerText(),/constant along/);assert.equal(await exported(),saved);await page.locator('#cancel').click();await idle();
  // The same displacement and formula controls construct the Euclidean shear.
  await create('Extension',['4','7'],'(3*i + 4*j) % 28');
  await field('Extension','With destination','destination','(j - i) % 7');
  await transform('With destination','place');await formula('x coordinate','j');await formula('y coordinate','i');await apply();
  await transform('With destination','move');await formula('x displacement','0 - i');
  // Switching syntax views is read-only; the arithmetic form has the same tree.
  const unedited=await exported();await group('x displacement').getByRole('button',{name:'Use controls',exact:true}).click();await page.waitForFunction(()=>document.querySelector('[aria-label="x displacement"] [data-rule-controls]').getAttribute('aria-pressed')==='true');assert.equal(await exported(),unedited);
  await apply();assert.equal((await object('With destination')).rows[21].position[0],-3);
  await transform('With destination','place');await formula('x coordinate','destination');await formula('y coordinate','i');await apply();
  await create('Larger',['4','7'],'(7*i + 4*j) % 28');
  await compare('With destination',['i','destination'],'Larger',['i','j'],'Larger',['i','j']);assert.match(await page.locator('#comparison-status').innerText(),/28 equal/);
  // The Q/R composition and failed assumption are inspectable loaded constructions.
  await load('12_relation_matrices');await compare('Composed Q',['n','q'],'Direct Q',['n','q'],'Comparison domain',['n','q']);assert.match(await page.locator('#comparison-status').innerText(),/77 equal/);
  await page.locator('#cases').click();await page.getByLabel('Value of a',{exact:true}).fill('12');await page.getByLabel('Value of b',{exact:true}).fill('8');await apply();
  await details('Composed Q');await page.locator('#advanced-tools summary').click();await page.locator('[data-action="compare"]').click();await page.locator('#check-comparison').click();await idle();assert.match(await page.locator('#comparison-status').innerText(),/60 equal, 36 different/);await page.screenshot({path:path.join(output,'composition-counterexample.png')});
  for(const [id,name,steps] of [['12_division_motion','Moving table',3],['12_euclidean_step','Moving extension',2],['12_euclidean_next','Moving extension',2]]){
    await load(id);const capture=await exported();for(let i=0;i<steps;i++){await page.locator('#undo').click();await idle()}for(let i=0;i<steps;i++){await page.locator('#redo').click();await idle()}assert.equal(await exported(),capture);assert.equal(await page.locator('#objects').inputValue(),name);
  }
  await details('Moving extension');await page.locator('#arrange').click();await page.setViewportSize({width:360,height:900});await page.locator('#transform-kind').selectOption('move');await group('x displacement').getByRole('button',{name:'Write a formula',exact:true}).tap();assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.screenshot({path:path.join(output,'phone-displacement.png')});
  assert.deepEqual(errors,[]);fs.writeFileSync(path.join(output,'report.json'),JSON.stringify({browser:browser.version(),tasks:['counted keyed displacement from blank','cyclic contents from blank','cancel and invalid fiber isolation','arithmetic syntax round trip','Euclidean extension and shear from blank','exact comparison on declared integer keys','modular factorization and nonunit counterexample','all four saved investigations','captured reverse paths','360px and emulated touch'],errors},null,2));console.log('Division motion checks passed.');
 }finally{await browser.close();server?.kill()}
})().catch(error=>{console.error(error);server?.kill();process.exitCode=1});
