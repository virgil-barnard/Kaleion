// Optional browser gate: colors stay presentation; a saved equality stays finite.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {spawn}=require('node:child_process');
const {chromium}=require(process.env.KALEION_PLAYWRIGHT_MODULE||'playwright');
const output=path.resolve(process.argv[3]||'build/colors-equality-check');fs.mkdirSync(output,{recursive:true});
let origin=process.argv[2],server;
(async()=>{
 if(!origin){server=spawn(process.env.KALEION_PYTHON||'.venv/bin/python3',['-m','examples.studio','--port','0'],{stdio:['ignore','pipe','inherit']});origin=await new Promise((resolve,reject)=>{server.stdout.on('data',d=>{const m=String(d).match(/http:\/\/127\.0\.0\.1:\d+/);if(m)resolve(m[0])});server.once('error',reject)});}
 const browser=await chromium.launch(JSON.parse(process.env.KALEION_BROWSER_OPTIONS||'{}'));
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1050},hasTouch:true,reducedMotion:'reduce'}),errors=[],posts=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(r.method()==='POST')posts.push(new URL(r.url()).pathname)});
  const idle=()=>page.waitForFunction(()=>!document.getElementById('options').disabled);
  const state=async()=>await(await page.request.get(origin+'/api/state')).json();
  const math=async()=>await(await page.request.get(origin+'/api/export')).text();
  const close=async()=>{if(await page.locator('#panel').isVisible())await page.locator('#close-panel').click()};
  const select=async name=>{await close();await page.locator('#objects').selectOption(name);await idle()};
  const colors=async name=>{await select(name);await page.locator('#view-options').click();if(await page.locator('.color-controls').getAttribute('open')===null)await page.getByText('Color',{exact:true}).click()};
  const paint=async(mode='field',palette='ocean',range='fixed',min='0',max='2')=>{await page.getByLabel('Color by',{exact:true}).selectOption(mode);if(mode==='field'){await page.getByLabel('Color field',{exact:true}).selectOption('value');await page.getByLabel('Palette',{exact:true}).selectOption(palette);await page.getByLabel('Color range',{exact:true}).selectOption(range);if(range==='fixed'){await page.getByLabel('Color minimum',{exact:true}).fill(min);await page.getByLabel('Color maximum',{exact:true}).fill(max)}}await page.getByRole('button',{name:'Apply colors',exact:true}).click()};
  const marks=name=>page.locator(`[data-scene-owner="${name}"]`);
  const fills=async name=>marks(name).evaluateAll(ns=>ns.map(n=>n.dataset.color));
  const load=async file=>{await page.locator('#file').setInputFiles(file);await idle()};
  const apply=async()=>{await page.locator('#preview').click();await idle();assert.equal(await page.locator('#draft-status').getAttribute('data-phase'),'ready');await page.locator('#apply').click();await idle()};
  const download=async(selector,filename)=>{const promise=page.waitForEvent('download');await page.locator(selector).click();const d=await promise,file=path.join(output,filename);await d.saveAs(file);return file};
  async function keys(label){const box=page.getByRole('group',{name:label,exact:true});while(await box.getByRole('button').count())await box.getByRole('button').first().click();for(const k of ['i','j'])await box.getByLabel(`Add ${label.toLowerCase()}`,{exact:true}).selectOption(k)}
  async function compare(){await select('Moving cover');await page.locator('#options').click();await page.locator('#advanced-tools summary').click();await page.locator('[data-action="compare"]').click();await keys('Left key fields');await page.locator('#comparison-right').selectOption('Independent ones');await keys('Right key fields');await page.locator('#comparison-expected').selectOption('Independent ones');await keys('Expected key fields');await page.locator('#check-comparison').click();await idle()}
  await page.goto(origin);await page.waitForFunction(()=>!document.getElementById('add').disabled);
  await page.locator('#open').click();await page.getByRole('button',{name:'Two quotient fields make one',exact:true}).click();await page.getByRole('button',{name:'Load example',exact:true}).click();await idle();
  const original=await math(),revision=(await state()).revision,beforeColors=posts.length;
  await colors('Moving cover');await paint();const middle=(await fills('Moving cover'))[0];assert.ok((await fills('Moving cover')).every(v=>v===middle));
  // Invalid ranges retain both the old paint and the exact workspace.
  await page.getByLabel('Color minimum',{exact:true}).fill('3');await page.getByRole('button',{name:'Apply colors',exact:true}).click();assert.match(await page.locator('[data-color-status]').innerText(),/minimum/);assert.equal((await fills('Moving cover'))[0],middle);await page.getByLabel('Color minimum',{exact:true}).fill('0');await page.getByRole('button',{name:'Apply colors',exact:true}).click();
  await close();await page.locator('.camera-menu > summary').click();await page.getByLabel('Canvas theme',{exact:true}).selectOption('dark');await page.getByRole('button',{name:'3D workspace view',exact:true}).click();await page.locator('.camera-menu > summary').click();
  assert.equal(await page.locator('html').getAttribute('data-theme'),'dark');assert.equal(await math(),original);assert.equal((await state()).revision,revision);assert.equal(posts.length,beforeColors);
  await page.locator('#save').click();const canvasFile=await download('#save-canvas','colored-canvas.json'),canvas=JSON.parse(fs.readFileSync(canvasFile,'utf8'));
  assert.equal(canvas.version,2);assert.equal(canvas.scene.theme,'dark');assert.equal(canvas.scene.objects.find(o=>o.name==='Moving cover').color.max,'2');assert.equal(canvas.workspace,original);
  await compare();assert.equal(await page.locator('#comparison-status').getAttribute('data-phase'),'passed');assert.match(await page.locator('.finite-statement pre').innerText(),/dom\(L\) = dom\(R\) = D/);
  const recordFile=await download('#save-comparison','coprime-comparison.json'),record=JSON.parse(fs.readFileSync(recordFile,'utf8'));
  assert.equal(record.format,'kaleion-comparison');assert.equal(record.workspace,original);assert.equal(record.comparison.passed,undefined);
  await load(recordFile);assert.equal(await page.locator('#comparison-status').getAttribute('data-phase'),'passed');assert.equal(await math(),original);
  await close();await page.locator('#cases').click();await page.getByLabel('Value of a',{exact:true}).fill('6');await page.getByLabel('Value of b',{exact:true}).fill('4');await apply();await compare();
  assert.equal(await page.locator('#comparison-status').getAttribute('data-phase'),'failed');assert.match(await page.locator('#comparison-status').innerText(),/14 equal, 1 different/);assert.match(await page.locator('#comparison-witness').innerText(),/Left value: 2/);
  const failedFile=await download('#save-comparison','noncoprime-comparison.json');
  // Follow the actual disagreeing occurrence to its measured input.
  await page.getByRole('button',{name:'Inspect left occurrence',exact:true}).click();await idle();assert.match(await page.locator('#activity').innerText(),/2/);await page.getByRole('button',{name:'Back to comparison',exact:true}).click();await idle();
  await close();await page.locator('.camera-menu > summary').click();await page.getByLabel('Canvas theme',{exact:true}).selectOption('light');await page.getByRole('button',{name:'Center selected object',exact:true}).click();await page.locator('.camera-menu > summary').click();
  assert.equal(new Set(await fills('Moving cover')).size,2);assert.ok((await fills('Moving cover')).includes(middle));await page.screenshot({path:path.join(output,'quotient-counterexample.png')});
  // Opening the earlier record recovers its own case, never the later verdict.
  await load(recordFile);assert.equal(await page.locator('#comparison-status').getAttribute('data-phase'),'passed');assert.deepEqual((await state()).parameters,{a:'7',b:'5'});
  await close();await page.locator('#undo').click();await idle();await page.locator('#redo').click();await idle();
  const final=await math();const endpointColors=await fills('Moving cover');
  for(const progress of ['0','12','24']){await page.locator('#replay-progress').fill(progress);await page.locator('#replay-progress').dispatchEvent('input');assert.equal(await math(),final)}
  await page.locator('[data-replay-result]').click();assert.deepEqual(await fills('Moving cover'),endpointColors);
  await load(failedFile);assert.equal(await page.locator('#comparison-status').getAttribute('data-phase'),'failed');
  await colors('Lower incidence');await paint('field','balance','auto');assert.equal(await page.locator('.color-controls .color-gradient').evaluate(n=>n.style.background.includes('gradient')),false);assert.ok(await marks('Lower incidence').filter({has:page.locator('polygon')}).count()>0);assert.ok(await page.locator('[data-scene-owner="Lower incidence"].outside').count()>0);
  const incBefore=await math();await page.getByRole('button',{name:'Show points',exact:true}).click();assert.equal(await marks('Lower incidence').locator('circle').count(),15);assert.equal(await math(),incBefore);
  // Exact neighboring huge integers remain distinguishable without conversion to Number.
  await close();await page.locator('#add').click();await page.locator('[data-action="vector"]').click();await page.locator('#result-name').fill('Huge');await page.getByLabel('Size i',{exact:true}).fill('3');await page.locator('#shape-contents').selectOption('formula');await page.locator('#shape-formula').fill('1'+'0'.repeat(90)+' + i');await page.locator('#apply').click();await idle();
  await colors('Huge');await paint('field','violet','auto');assert.equal(new Set(await fills('Huge')).size,3);assert.match(await page.locator('[data-color-note]').innerText(),new RegExp('1'+'0'.repeat(90)));
  await page.getByRole('button',{name:'Use current limits',exact:true}).click();assert.equal(await page.getByLabel('Color minimum',{exact:true}).inputValue(),'1'+'0'.repeat(90));await page.getByRole('button',{name:'Apply colors',exact:true}).click();
  await page.setViewportSize({width:360,height:900});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.screenshot({path:path.join(output,'phone-colors.png')});
  await page.getByLabel('Reverse palette',{exact:true}).check();await page.getByRole('button',{name:'Apply colors',exact:true}).focus();await page.keyboard.press('Enter');assert.equal(new Set(await fills('Huge')).size,3);
  assert.deepEqual(errors,[]);fs.writeFileSync(path.join(output,'report.json'),JSON.stringify({browser:browser.version(),tasks:'palette, exact ranges, invalid edit, theme, 2D/3D, points, nonmatches, save/reopen, finite equality/counterexample, evidence, reverse replay, huge integers, phone width and keyboard',errors},null,2));
  console.log('Color and finite equality browser checks passed.');
 }finally{await browser.close();server?.kill()}
})().catch(error=>{console.error(error);server?.kill();process.exitCode=1});
