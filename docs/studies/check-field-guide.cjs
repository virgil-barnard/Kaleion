// Public construction tasks plus isolated fixtures for asynchronous inspection
// and nested read contexts. No browser calculation supplies a mathematical result.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {spawn}=require('node:child_process');
const {chromium}=require(process.env.KALEION_PLAYWRIGHT_MODULE||'playwright');
const output=path.resolve(process.argv[3]||'build/field-guide-check');fs.mkdirSync(output,{recursive:true});
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
  const camera=()=>page.locator('#workspace-canvas').getAttribute('viewBox');
  const close=async()=>{if(await page.locator('#panel').isVisible())await page.locator('#close-panel').click()};
  const details=async name=>{await page.locator('#objects').selectOption(name);await idle();await page.locator('#options').click();await idle()};
  const preview=async()=>{await page.locator('#preview').click();await idle();assert.equal(await page.locator('#draft-status').getAttribute('data-phase'),'ready',await page.locator('#draft-status').innerText())};
  const apply=async()=>{await preview();await page.locator('#apply').click();await idle()};
  const cancel=async()=>{await page.locator('#cancel').click();await idle();assert.equal(await page.locator('.field-member').count(),0)};
  const summary=()=>page.locator('[data-field-result]');
  const waitSummary=text=>page.waitForFunction(text=>document.querySelector('[data-field-result]')?.textContent.includes(text),text);
  const marks=(name,extra='')=>page.locator(`[data-scene-owner=${JSON.stringify(name)}]${extra}`);
  async function create(kind,name,configure){await close();await page.locator('#add').click();await page.locator(`[data-action="${kind}"]`).click();await page.locator('#result-name').fill(name);await configure();await page.locator('#apply').click();await idle();assert.ok(await object(name))}
  async function rule(source,name,formula){await details(source);await page.locator('#quick-lens').click();await page.locator('#result-name').fill(name);await page.getByText('Customize the formula',{exact:true}).click();await page.locator('[data-rule-write]').click();await page.getByRole('textbox',{name:'Relation rule',exact:true}).fill(formula)}
  await page.goto(origin);await page.waitForFunction(()=>document.getElementById('welcome')&&!document.getElementById('welcome').hidden);
  await create('grid','Residues',async()=>{for(const axis of ['i','j'])await page.getByLabel(`Size ${axis}`,{exact:true}).fill('6')});
  await rule('Residues','Modular incidence','(j - 2*i - 1) % 6 = 0');await apply();
  // The relation has two matches in every odd column and none in any even
  // column, although every column has six candidate items.
  await page.locator('#axis-total').click();await page.locator('#result-name').fill('Column counts');
  await page.getByLabel('Total along j',{exact:true}).uncheck();await page.getByLabel('Total along i',{exact:true}).check();await preview();
  const before=await exported(),requests=mutations.length,view=await camera();
  await page.getByText('See a field on the canvas',{exact:true}).click();
  await page.getByLabel('Field to explore',{exact:true}).selectOption('j');await waitSummary('j = 0: 0 matches among 6 items');
  assert.equal(await marks('Modular incidence','.field-member').count(),6);assert.equal(await marks('Modular incidence','.field-nonmatch').count(),6);
  assert.equal(await marks('Residues','.field-member').count(),0);assert.match(await summary().innerText(),/items exist; none match/);
  await page.getByRole('button',{name:'Next value',exact:true}).focus();await page.keyboard.press('Enter');await waitSummary('j = 1: 2 matches among 6 items');
  assert.equal(await marks('Modular incidence','.field-member').count(),6);assert.equal(await marks('Modular incidence','.field-nonmatch').count(),4);
  assert.equal(await page.locator('#draft-status').getAttribute('data-phase'),'ready');assert.equal(await exported(),before);assert.equal(mutations.length,requests);assert.equal(await camera(),view);
  await page.locator('[data-field-guide]').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(output,'modular-fiber.png')});
  await close();assert.equal(await page.locator('.field-member').count(),0);await page.locator('#resume-draft').click();await waitSummary('j = 1:');assert.equal(await marks('Modular incidence','.field-member').count(),6);
  await apply();assert.equal(await page.locator('.field-member').count(),0);assert.deepEqual((await object('Column counts')).rows.map(r=>r.fields.value),['0','2','0','2','0','2']);
  // A count is a reusable object. Its value fibers contain three distinct
  // measurements; the zero-valued items remain real inspectable occurrences.
  await rule('Column counts','Zero measurements','value = 0');await preview();const measured=await exported(),countRequests=mutations.length;
  await page.getByRole('button',{name:'Explore field value',exact:true}).tap();await waitSummary('value = 0: 3 items');
  assert.equal(await marks('Column counts','.field-member').count(),3);assert.equal(await page.locator('#draft-status').getAttribute('data-phase'),'ready');assert.equal(await exported(),measured);assert.equal(mutations.length,countRequests);await cancel();
  // An identical field name belongs to different objects inside a keyed read.
  await details('Column counts');await page.locator('#combine').click();await page.locator('#combine-target').selectOption('Residues');await page.locator('#combine-place').click();
  const height=page.getByRole('group',{name:'y coordinate',exact:true});
  await height.locator('[data-path="read/value"]').click();await waitSummary('value = 0: 3 items');assert.match(await page.locator('[data-field-scope]').innerText(),/on Column counts/);assert.equal(await marks('Residues','.field-member').count(),0);
  await height.locator('[data-path="read/on"]').click();await waitSummary('key =');assert.match(await page.locator('[data-field-scope]').innerText(),/on Residues/);assert.equal(await marks('Column counts','.field-member').count(),0);
  await height.getByLabel('Field',{exact:true}).selectOption('j');await waitSummary('j = 0: 6 items');await preview();await waitSummary('saved source is hidden by a different preview capture');assert.equal(await marks('Residues','.field-member').count(),0);await cancel();
  // A structured field token and its replacement address the same guide.
  await details('Residues');await page.locator('#quick-lens').click();await page.getByText('Customize the formula',{exact:true}).click();
  await page.getByRole('button',{name:'Edit field i',exact:true}).click();await waitSummary('i = 0: 6 items');
  await page.getByLabel('Field',{exact:true}).selectOption('j');await waitSummary('j = 0: 6 items');await cancel();
  await details('Modular incidence');await page.locator('#advanced-tools summary').click();await page.locator('[data-action="measure"]').click();await page.getByLabel('Add group keys',{exact:true}).selectOption('j');await waitSummary('j = 0: 0 matches among 6 items');await cancel();
  // The same single-field guide serves 3D logical slices without assuming rows.
  await create('cube','Box',async()=>{for(const [axis,n] of [['i',2],['j',3],['k',4]])await page.getByLabel(`Size ${axis}`,{exact:true}).fill(String(n))});
  await page.locator('#axis-total').click();await page.getByText('See a field on the canvas',{exact:true}).click();await page.getByLabel('Field to explore',{exact:true}).selectOption('k');await waitSummary('k = 0: 6 items');
  assert.equal(await marks('Box','.field-member').count(),6);assert.equal(await page.getByLabel('Field to explore',{exact:true}).locator('option[value="value"]').count(),0);await cancel();
  // Contents never pass through JavaScript Number, including adjacent integers
  // beyond its precision. There are two occurrences of the first value.
  await create('vector','Exact contents',async()=>{await page.locator('#shape-contents').selectOption('list');await page.locator('#shape-list').fill('1237940039285380274899124225, 1237940039285380274899124226, 1237940039285380274899124225')});
  await rule('Exact contents','Large labels','value > 0');await preview();await page.getByRole('button',{name:'Explore field value',exact:true}).click();await waitSummary('value = 1237940039285380274899124225: 2 items');
  await page.getByRole('button',{name:'Next value',exact:true}).click();await waitSummary('value = 1237940039285380274899124226: 1 item');
  await page.setViewportSize({width:360,height:900});await page.locator('[data-field-guide]').scrollIntoViewIfNeeded();assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  for(const button of ['Previous value','Next value'])assert.ok((await page.getByRole('button',{name:button,exact:true}).boundingBox()).height>=44);
  await page.screenshot({path:path.join(output,'phone-field.png')});await cancel();
  // Controlled response order reproduces stale completion without a timing sleep.
  await page.setViewportSize({width:1440,height:1000});await rule('Residues','Pending rule','i < j');
  let release,entered;const waiting=new Promise(resolve=>{entered=resolve});
  await page.route('**/api/groups',async route=>{if(route.request().postDataJSON().by[0]!=='i')return route.continue();const response=await route.fetch();entered();await new Promise(resolve=>{release=resolve});await route.fulfill({response})});
  await page.getByRole('button',{name:'Explore field i',exact:true}).click();await waiting;
  await page.getByRole('button',{name:'Explore field j',exact:true}).click();await waitSummary('j = 0: 6 items');
  const delivered=page.waitForResponse(r=>r.url().endsWith('/api/groups')&&r.request().postDataJSON().by[0]==='i');release();await delivered;
  assert.match(await summary().innerText(),/j = 0: 6 items/);assert.ok((await marks('Residues','.field-member').allTextContents()).every(t=>t.includes('j=0')));await page.unroute('**/api/groups');
  // Inspection failure does not become an empty fiber or invalidate a preview.
  await preview();await page.route('**/api/groups',route=>route.fulfill({status:422,contentType:'application/json',body:JSON.stringify({error:'Captured field unavailable'})}));
  await page.getByLabel('Field to explore',{exact:true}).selectOption('i');await waitSummary('Cannot inspect');assert.equal(await page.locator('.field-member').count(),0);assert.equal(await page.locator('#draft-status').getAttribute('data-phase'),'ready');await page.unroute('**/api/groups');await cancel();
  // Isolated expression fixtures test driver ownership, including a nested
  // read's target expression, without adding fabricated roots to the workspace.
  const contexts=await page.evaluate(async()=>{
    const {expressionEditor}=await import('/expressions.js');const f=field=>({field});
    const editor=expressionEditor({read:{object:'Outer',on:f('i'),key:f('key'),value:{read:{object:'Inner',on:f('key'),key:f('key'),value:f('value')}}}},['i'],[{name:'Outer',fields:['key']},{name:'Inner',fields:['key','value']}]);
    const events=[];editor.box.addEventListener('inspect-field',e=>events.push(e.detail));document.body.append(editor.box);
    for(const p of ['read/on','read/key','read/value/read/on','read/value/read/key','read/value/read/value'])editor.box.querySelector(`[data-path="${p}"]`).click();editor.box.remove();return events;
  });assert.deepEqual(contexts,[{field:'i',object:null},{field:'key',object:'Outer'},{field:'key',object:'Outer'},{field:'key',object:'Inner'},{field:'value',object:'Inner'}]);
  assert.deepEqual(errors,[]);fs.writeFileSync(path.join(output,'report.json'),JSON.stringify({browser:browser.version(),tasks:['zero and nonzero incidence fibers','ready preview isolation','park and resume','measurement value reuse','structured field replacement','3D slices','exact contents','keyboard and emulated touch','phone layout','late response','failed inspection','nested read context'],errors},null,2));console.log('Field guide checks passed.');
 }finally{await browser.close();server?.kill()}
})().catch(error=>{console.error(error);server?.kill();process.exitCode=1});
