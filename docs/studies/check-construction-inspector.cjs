// Read-only definition navigation through real controls; run separately from core tests.
// node docs/studies/check-construction-inspector.cjs [origin] [output directory]
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {spawn,execFileSync}=require('node:child_process');
const {chromium}=require(process.env.KALEION_PLAYWRIGHT_MODULE||'playwright');
const python=process.env.KALEION_PYTHON||'.venv/bin/python3';
let origin=process.argv[2],server;
const output=path.resolve(process.argv[3]||'build/construction-inspector-check');fs.mkdirSync(output,{recursive:true});
(async()=>{
 if(!origin){
   server=spawn(python,['-m','examples.studio','--port','0'],{stdio:['ignore','pipe','inherit']});
   origin=await new Promise((resolve,reject)=>{let text='';server.stdout.on('data',chunk=>{text+=chunk;const match=text.match(/http:\/\/127\.0\.0\.1:\d+/);if(match)resolve(match[0])});server.once('error',reject);server.once('exit',code=>reject(Error(`Host stopped: ${code}`)))});
 }
 const browser=await chromium.launch(JSON.parse(process.env.KALEION_BROWSER_OPTIONS||'{}'));
 try{
   const page=await browser.newPage({viewport:{width:1400,height:1050},reducedMotion:'reduce',hasTouch:true}),errors=[],mutations=[];
   page.on('pageerror',e=>errors.push(String(e)));
   page.on('request',r=>{if(/\/api\/(preview|preview-case|commit|undo|redo)$/.test(r.url()))mutations.push(r.url())});
   await page.goto(origin);await page.waitForFunction(()=>!document.getElementById('add').disabled);
   const idle=()=>page.waitForFunction(()=>!document.getElementById('options').disabled);
   const ready=()=>page.waitForFunction(()=>!document.getElementById('construction').hasAttribute('aria-busy'));
   const exported=async()=>await(await page.request.get(origin+'/api/export')).text();
   const select=async name=>{await page.locator(`[data-object=${JSON.stringify(name)}]`).click();await ready()};
   const follow=async name=>{await page.getByRole('button',{name,exact:true}).click();await ready()};
   const back=async()=>{await page.locator('#construction-back').click();await ready()};
   const load=async capture=>{await page.locator('#file').setInputFiles({name:'inspection.json',mimeType:'application/json',buffer:Buffer.from(capture)});await idle()};
   const report={};
   for(const [file,name] of [['02_floor_sums','Pieces'],['05_radon_reconstruction','Image heights'],['06_young_layers','Cells'],['07_equal_sums','Moving pairs']]){
     await page.locator('#file').setInputFiles(path.resolve(`examples/canvases/${file}.json`));await idle();await select(name);
     assert.equal(await page.locator('#construction-title').innerText(),name);
     assert.equal(await page.locator('#construction-details').evaluate(n=>n.open),true);
     assert.ok(await page.locator('.construction-arguments dd').count());
     assert.ok(await page.locator('[data-construction-input]').count());
     report[file]=await page.locator('.construction-arguments').innerText();
   }
   const original=await exported();
   assert.match(await page.locator('.construction-arguments').innerText(),/x coordinate\s+total/);
   assert.match(await page.locator('.construction-read').innerText(),/Target key\s+pair_key\s+Driver key\s+key\s+Field read\s+value/);
   await page.getByRole('button',{name:'Zoom in workspace view',exact:true}).click();
   const boardCamera=await page.locator('#workspace-canvas').getAttribute('viewBox');
   await follow('Inspect Ranks · Read for y coordinate');
   assert.equal(await page.locator('#construction-title').innerText(),'Ranks');
   assert.equal(await page.locator('[data-object="Ranks"]').getAttribute('aria-pressed'),'true');
   assert.match(await page.locator('#construction-details').innerText(),/Strict member order/);
   await page.getByRole('button',{name:'Zoom in workspace view',exact:true}).click();await back();
   assert.equal(await page.locator('#construction-title').innerText(),'Moving pairs');
   assert.equal(await page.locator('#workspace-canvas').getAttribute('viewBox'),boardCamera);
   assert.match(await page.evaluate(()=>document.activeElement.getAttribute('aria-label')),/Inspect Ranks/);
   await page.getByRole('button',{name:'Fit workspace view',exact:true}).click();
   await page.getByRole('button',{name:'Connections',exact:true}).click();
   await page.locator('#scene').screenshot({path:path.join(output,'workspace.png')});
   await page.locator('#panel').screenshot({path:path.join(output,'construction-sheet.png')});
   await page.locator('.workbench').screenshot({path:path.join(output,'workbench.png')});
   await page.locator('[data-surface="focus"]').click();await page.locator('[data-mode="points"]').click();
   const ref=await page.locator('#occurrence option').nth(6).getAttribute('value');await page.locator('#occurrence').selectOption(ref);await idle();
   await page.getByRole('button',{name:'Zoom in main view',exact:true}).click();
   const marks=await page.locator('#marks').innerHTML();
   await page.locator('#construction-details > summary').click();
   await follow('Inspect Ranks · Read for y coordinate');await back();
   assert.equal(await page.locator('#occurrence').inputValue(),ref);
   assert.equal(await page.locator('#marks').innerHTML(),marks);
   assert.ok(await page.locator('#activity .receipt-read').count());
   await page.locator('#construction-view').click();await idle();
   assert.equal(await page.locator('.linked-card').count(),1);
   await page.locator('[data-linked-inspect="left"]').click();await idle();
   assert.equal(await page.locator('#construction-title').innerText(),'Moving pairs');
   assert.match(await page.locator('#activity').innerText(),/Value/);
   assert.equal(await exported(),original,'Reading definitions and values leaves exported history unchanged');
   // Following an input parks the existing form; resuming restores its target and exact draft.
   await page.locator('#close-linked').click();await page.locator('[data-mode="objects"]').click();
   await page.locator('#options').click();await page.locator('[data-action="field"]').click();
   await page.locator('#result-name').fill('Keep this idea');
   const draft=await page.locator('#declaration').textContent();
   await page.locator('#construction-details > summary').click();await follow('Inspect Ranks · Read for y coordinate');
   assert.match(await page.locator('#draft-title').innerText(),/parked/);
   await page.locator('#resume-draft').click();
   assert.equal(await page.locator('#declaration').textContent(),draft);
   assert.equal(await page.locator('#construction-title').innerText(),'Moving pairs');
   await page.locator('#cancel').click();await idle();assert.equal(await exported(),original);

   const fixture=execFileSync(python,['-c',`
from kaleion import Collection, F, Workspace, param
from kaleion.api import wrap
from kaleion.ir import Node
d=Collection.literal([9,4],keys=[1,0],name='Heights')
b=Collection.sequence(param('n')-3)
p=Collection.literal([0,1]).arrange(F.value,d.bind(on=F.value))
w=Workspace({'Heights':d,'Points':p,'Global':b,'Local':b.with_params(n=4),'Same':b.with_params(n=5),'Failed':b.with_params(n=2),'Empty':Collection.sequence(0),'Unfamiliar':wrap(Node('future_recipe','collection',(d.node,),{'huge':2**100+1}))},{'n':5},max_items=2000,max_history=40)
w.set('Heights',d.arrange(F.key,99))
print(w.to_json())
   `],{encoding:'utf8'});
   await load(fixture);const before=await exported();
   await select('Points');await follow('Inspect Integers · Heights · Read for y coordinate');
   assert.match(await page.locator('.construction-status').innerText(),/Earlier or unnamed/);
   assert.equal(await page.locator('.linked-card').count(),1);
   assert.match(await page.locator('[data-capture-label]').innerText(),/Earlier or unnamed input/);
   assert.deepEqual(await page.locator('[data-linked-occurrence="left"] option').allTextContents(),['0 · value 9','1 · value 4']);await back();
   await select('Local');await follow('Inspect Sequence · Definition in local case');
   assert.match(await page.locator('[data-construction-case]').innerText(),/n = 4/);
   assert.match(await page.locator('.construction-status').innerText(),/Local case input/);
   assert.equal(await page.locator('[data-linked-occurrence="left"] option').count(),1);await back();
   await select('Same');await follow('Inspect Sequence · Definition in local case');
   assert.match(await page.locator('[data-capture-label]').innerText(),/Local case input/);await back();
   await select('Failed');assert.match(await page.locator('.construction-status').innerText(),/Evaluation failed/);
   await follow('Inspect Sequence · Definition in local case');
   assert.match(await page.locator('.construction-status').innerText(),/Not captured/);
   assert.equal(await page.locator('#construction-view').isEnabled(),false);
   assert.match(await page.locator('.construction-arguments').innerText(),/\$n − 3/);await back();
   await select('Unfamiliar');assert.match(await page.locator('#construction').innerText(),/1267650600228229401496703205377/);
   await select('Empty');await page.locator('#construction-view').click();await idle();
   assert.equal(await page.locator('[data-linked-occurrence="left"]').isEnabled(),false);
   assert.equal(await page.locator('[data-linked-inspect="left"]').isEnabled(),false);
   assert.equal(await exported(),before);
   // A delayed input description must not replace a more recent object selection.
   await load(fixture);await select('Points');let release,received;
   const wait=new Promise(resolve=>received=resolve),gate=new Promise(resolve=>release=resolve);
   await page.route('**/api/construction',async route=>{received();await gate;await route.continue()});
   await page.getByRole('button',{name:'Inspect Integers · Heights · Read for y coordinate',exact:true}).click();
   await wait;await select('Global');release();await page.waitForResponse(r=>r.url().endsWith('/api/construction'));
   await ready();assert.equal(await page.locator('#construction-title').innerText(),'Global');
   await page.unroute('**/api/construction');
   await page.setViewportSize({width:360,height:980});await select('Points');
   await follow('Inspect Integers · Heights · Read for y coordinate');await back();
   assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   assert.ok((await page.locator('[data-construction-input]').first().boundingBox()).height>=44);
   await page.locator('#panel').screenshot({path:path.join(output,'phone-construction.png')});
   await page.setViewportSize({width:320,height:950});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   await page.setViewportSize({width:1400,height:1050});await page.emulateMedia({colorScheme:'dark'});
   await page.locator('#panel').screenshot({path:path.join(output,'dark-construction.png')});
   assert.deepEqual(mutations,[]);assert.deepEqual(errors,[]);
   fs.writeFileSync(path.join(output,'report.json'),JSON.stringify({canvases:report,definitionAndEvidence:true,earlierDriver:true,localCase:true,failedAndEmpty:true,exactInteger:true,cameraAndSelectionReturn:true,draftContinuity:true,staleReplyGuard:true,phoneEmulation:true,mutations,errors},null,2));
   process.stdout.write('Construction inspector browser checks passed.\n');
 }finally{await browser.close();server?.kill()}
})().catch(error=>{console.error(error);server?.kill();process.exitCode=1});
