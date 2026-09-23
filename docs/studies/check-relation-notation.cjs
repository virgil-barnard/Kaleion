// Construct different mathematics through the same public rule controls.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {spawn}=require('node:child_process');
const {chromium}=require(process.env.KALEION_PLAYWRIGHT_MODULE||'playwright');
const output=path.resolve(process.argv[3]||'build/relation-notation-check');fs.mkdirSync(output,{recursive:true});
let origin=process.argv[2],server;
(async()=>{
 if(!origin){server=spawn(process.env.KALEION_PYTHON||'.venv/bin/python3',['-m','examples.studio','--port','0'],{stdio:['ignore','pipe','inherit']});origin=await new Promise((resolve,reject)=>{server.stdout.on('data',d=>{const m=String(d).match(/http:\/\/127\.0\.0\.1:\d+/);if(m)resolve(m[0])});server.once('error',reject)});}
 const browser=await chromium.launch(JSON.parse(process.env.KALEION_BROWSER_OPTIONS||'{}'));
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000},hasTouch:true,reducedMotion:'reduce'}),errors=[],mutations=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/\/api\/(preview|preview-case|commit|undo|redo)$/.test(r.url()))mutations.push(r.url())});
  const idle=()=>page.waitForFunction(()=>!document.getElementById('options').disabled);
  const state=async()=>await(await page.request.get(origin+'/api/state')).json();
  const exported=async()=>await(await page.request.get(origin+'/api/export')).text();
  const object=async name=>(await state()).objects.find(o=>o.name===name);
  const close=async()=>{if(await page.locator('#panel').isVisible())await page.locator('#close-panel').click()};
  const details=async name=>{await page.locator('#objects').selectOption(name);await idle();await page.locator('#options').click();await idle()};
  const preview=async()=>{await page.locator('#preview').click();await idle();assert.equal(await page.locator('#draft-status').getAttribute('data-phase'),'ready',await page.locator('#draft-status').innerText())};
  const apply=async()=>{await preview();await page.locator('#apply').click();await idle()};
  const text=()=>page.getByRole('textbox',{name:'Relation rule',exact:true});
  async function grid(name,n){await close();await page.locator('#add').click();await page.locator('[data-action="grid"]').click();await page.locator('#result-name').fill(name);for(const axis of ['i','j'])await page.getByLabel(`Size ${axis}`,{exact:true}).fill(String(n));await page.locator('#apply').click();await idle();assert.equal((await object(name)).rows.length,n*n)}
  async function rule(source,name,formula){await details(source);await page.locator('#quick-lens').click();await page.locator('#result-name').fill(name);await page.getByText('Customize the formula',{exact:true}).click();await page.locator('[data-rule-write]').click();await text().fill(formula)}
  const matches=async name=>(await object(name)).rows.filter(r=>r.match).map(r=>[Number(r.fields.i),Number(r.fields.j)]);
  await page.goto(origin);await page.waitForFunction(()=>document.getElementById('welcome')&&!document.getElementById('welcome').hidden);
  await grid('Residues',5);
  await rule('Residues','Modular line','(j - 2*i - 1) % 5 = 0');
  const source=await exported(),requestCount=mutations.length;
  await page.locator('[data-rule-controls]').click();await page.waitForFunction(()=>document.querySelector('[data-rule-controls]').getAttribute('aria-pressed')==='true');
  assert.equal(await exported(),source);assert.equal(mutations.length,requestCount);
  // Changing a term in controls then writing again retains the change.
  await page.getByRole('button',{name:'Edit integer 2',exact:true}).click();await page.getByLabel('Exact integer',{exact:true}).fill('3');await page.locator('[data-expression-done]').click();await page.locator('[data-rule-write]').click();assert.match(await text().inputValue(),/3 \* i/);
  await preview();await page.screenshot({path:path.join(output,'modular-rule.png')});await page.locator('#apply').click();await idle();assert.deepEqual(await matches('Modular line'),Array.from({length:5},(_,i)=>[i,(3*i+1)%5]));
  await page.locator('#axis-total').click();await page.locator('#result-name').fill('One per row');await apply();assert.deepEqual((await object('One per row')).rows.map(r=>r.fields.value),Array(5).fill('1'));
  await rule('Residues','Lattice window','0 <= i < 4 and j != i or i+j = 8');
  await close();await page.locator('#resume-draft').click();assert.equal(await text().inputValue(),'0 <= i < 4 and j != i or i+j = 8');await apply();
  const lattice=[];for(let i=0;i<5;i++)for(let j=0;j<5;j++)if((i<4&&i!==j)||i+j===8)lattice.push([i,j]);assert.deepEqual(await matches('Lattice window'),lattice);
  await grid('Binary vectors',7);
  const fano='((i+1)%2*((j+1)%2) + ((i+1)//2)%2*(((j+1)//2)%2) + (i+1)//4*((j+1)//4)) % 2 = 0';
  await rule('Binary vectors','Fano incidence',fano);await page.locator('[data-rule-controls]').click();await page.waitForFunction(()=>document.querySelector('[data-rule-controls]').getAttribute('aria-pressed')==='true');await page.locator('[data-rule-write]').click();await apply();const incidence=await matches('Fano incidence');assert.equal(incidence.length,21);
  const supports=Array.from({length:7},(_,j)=>incidence.filter(pair=>pair[1]===j).map(pair=>pair[0]));assert.ok(supports.every(s=>s.length===3));for(let j=0;j<7;j++)for(let k=j+1;k<7;k++)assert.equal(supports[j].filter(i=>supports[k].includes(i)).length,1);
  // Invalid notation and invalid arithmetic never change applied mathematics.
  await rule('Residues','Unfinished','i < j');await preview();const beforeInvalid=await exported();
  await text().fill('i <');await page.locator('[data-rule-controls]').click();await page.waitForFunction(()=>!document.querySelector('[data-rule-controls]').disabled);assert.match(await page.locator('[data-rule-status]').innerText(),/kept/);assert.equal(await text().inputValue(),'i <');
  await page.locator('#preview').click();await idle();assert.equal(await page.locator('#draft-status').getAttribute('data-phase'),'failed');assert.equal(await exported(),beforeInvalid);
  await text().fill('i >= 0 or 1//0 = 0');await page.locator('#preview').click();await idle();assert.equal(await page.locator('#draft-status').getAttribute('data-phase'),'failed');assert.equal(await exported(),beforeInvalid);
  // A late syntax response cannot overwrite a newer draft. No timing sleep.
  await text().fill('i = j');let release,entered;const waiting=new Promise(resolve=>{entered=resolve});
  await page.route('**/api/parse-relation',async route=>{const response=await route.fetch();entered();await new Promise(resolve=>{release=resolve});await route.fulfill({response})});
  await page.locator('[data-rule-controls]').click();await waiting;await text().fill('i < j');release();await page.waitForFunction(()=>!document.querySelector('[data-rule-controls]').disabled);assert.equal(await text().inputValue(),'i < j');assert.match(await page.locator('[data-rule-status]').innerText(),/text changed/);await page.unroute('**/api/parse-relation');
  // Keyboard-only view switching, and a readable bottom sheet on a small screen.
  await page.locator('[data-rule-controls]').focus();await page.keyboard.press('Enter');await page.waitForFunction(()=>document.querySelector('[data-rule-controls]').getAttribute('aria-pressed')==='true');
  await page.locator('[data-rule-write]').focus();await page.keyboard.press('Enter');assert.equal(await text().evaluate(e=>e===document.activeElement),true);
  await page.setViewportSize({width:360,height:900});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await text().fill('0 <= i < 3 and j < 2');await preview();await text().scrollIntoViewIfNeeded();await page.screenshot({path:path.join(output,'phone-rule.png')});
  await page.locator('#cancel').click();await idle();assert.equal(await exported(),beforeInvalid);
  // Captured save/reopen/undo preserves the rule; it is not stored as executable text.
  const saved=await exported();await page.locator('#file').setInputFiles({name:'rules.json',mimeType:'application/json',buffer:Buffer.from(saved)});await idle();await close();await page.locator('#undo').click();await idle();assert.equal(await object('Fano incidence'),undefined);await page.locator('#redo').click();await idle();assert.equal((await matches('Fano incidence')).length,21);
  // Formatter refusals keep unsupported structured definitions intact. These
  // intentionally isolated syntax fixtures do not seed the task constructions.
  const refusals=await page.evaluate(async()=>{
    const {formulaText}=await import('/notation.js');const f=name=>({field:name}),n=integer=>({integer}),eq=(a,b)=>({op:'=',args:[a,b]});
    return [eq(f('i'),n('2')),eq(f('i'),{read:{object:'driver'}}),eq(f('class'),n('0')),f('flag'),eq(f('i'),n('9'.repeat(260))),eq(f('i'),n('1+2')),eq({parameter:'i'},n('0')),eq(f('p'),n('0'))].map((spec,index)=>{try{return formulaText(spec,['i','class','flag'],index===0?['i']:['p'])}catch(error){return error.message}});
  });assert.match(refusals[0],/explicit/);assert.match(refusals[1],/keyed read/);assert.match(refusals[2],/explicit/);assert.match(refusals[3],/comparisons/);assert.match(refusals[4],/longer/);assert.match(refusals[5],/exact integer/);assert.match(refusals[6],/explicit/);assert.match(refusals[7],/explicit/);
  assert.deepEqual(errors,[]);fs.writeFileSync(path.join(output,'report.json'),JSON.stringify({browser:browser.version(),tasks:['modular line','lattice window','binary projective incidence','text/control transfer','failed drafts','delayed parse','keyboard','phone layout','captured restore'],errors},null,2));console.log('Relation notation checks passed.');
 }finally{await browser.close();server?.kill()}
})().catch(error=>{console.error(error);server?.kill();process.exitCode=1});
