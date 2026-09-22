// Optional browser gate. Starts a fresh Python host unless a URL is supplied.
// Uses real controls and the Python adapter; no prerecorded lesson results.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {chromium}=require(process.env.KALEION_PLAYWRIGHT_MODULE||'playwright');
let origin=process.argv[2],server;
const output=path.resolve(process.argv[3]||'build/studio-check');fs.mkdirSync(output,{recursive:true});
(async()=>{
 if(!origin){
   server=require('node:child_process').spawn(process.env.KALEION_PYTHON||'.venv/bin/python3',['-m','examples.studio','--port','0'],{stdio:['ignore','pipe','inherit']});
   origin=await new Promise((resolve,reject)=>{let text='';server.stdout.on('data',chunk=>{text+=chunk;const match=text.match(/http:\/\/127\.0\.0\.1:\d+/);if(match)resolve(match[0])});server.once('error',reject);server.once('exit',code=>reject(Error(`Studio host stopped: ${code}`)))});
 }
 const browser=await chromium.launch(JSON.parse(process.env.KALEION_BROWSER_OPTIONS||'{}'));
 try{
 const context=await browser.newContext({viewport:{width:1250,height:950},hasTouch:true,acceptDownloads:true});
 const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(origin);await page.waitForFunction(()=>document.getElementById('add').disabled===false);
 const state=async()=>await(await page.request.get(origin+'/api/state')).json();
 assert.equal((await state()).objects.length,0,'Start a fresh studio server for this check');
 const idle=()=>page.waitForFunction(()=>!document.getElementById('options').disabled);
 async function tool(action,add=false){await page.locator(add?'#add':'#options').click();await page.locator(`[data-action="${action}"]`).click()}
 async function expression(card,spec){
   const select=card.locator(':scope > select');
   if('field'in spec){await select.selectOption('Field');await card.locator(':scope > .children > select').selectOption(spec.field)}
   else if('integer'in spec){await select.selectOption('Number');await card.locator(':scope > .children > input').fill(String(spec.integer))}
   else if(spec.op){await select.selectOption('Operation');await card.locator(':scope > .children > select').selectOption(spec.op);const children=card.locator(':scope > .children > .expression');await expression(children.nth(0),spec.args[0]);await expression(children.nth(1),spec.args[1])}
   else{await select.selectOption('Keyed read');const labels=card.locator(':scope > .children > label > select');await labels.nth(0).selectOption(spec.read.object);await expression(card.locator(':scope > .children > .expression'),spec.read.on);await labels.nth(1).selectOption(spec.read.key.field);await labels.nth(2).selectOption(spec.read.value.field)}
 }
 const f=field=>({field}),n=integer=>({integer:String(integer)}),op=(op,a,b)=>({op,args:[a,b]});
 const cards=()=>page.locator('#panel fieldset > .expression');
 async function apply(){await page.locator('#preview').click();await idle();assert.equal(await page.locator('#apply').isEnabled(),true,await page.locator('#status').textContent());await page.locator('#apply').click();await idle()}
 async function integers(name,values){await tool('integers',true);await page.locator('#result-name').fill(name);await page.locator('#integer-values').fill(values);await apply()}
 async function select(name){await page.locator('[data-object]').filter({hasText:name}).first().click()}
 async function values(name){return (await state()).objects.find(o=>o.name===name).rows.map(r=>r.fields.value)}
 await integers('A','0, 1, 3');await integers('B','0, 2');await select('A');
 await tool('product');await page.locator('#result-name').fill('Pairs');
 const sources=page.locator('#panel fieldset > label > select');await sources.nth(0).selectOption('A');await sources.nth(1).selectOption('B');await apply();
 await tool('field');await page.locator('#result-name').fill('Sums');await expression(cards().nth(0),op('+',f('left_value'),f('right_value')));await apply();
 assert.deepEqual((await state()).objects.find(o=>o.name==='Sums').rows.map(r=>r.fields.total),['0','2','1','3','3','5']);
 await tool('place');await expression(cards().nth(0),f('total'));await expression(cards().nth(1),n(0));await apply();
 const coincident=(await state()).objects.find(o=>o.name==='Sums').rows;assert.equal(new Set(coincident.map(r=>JSON.stringify(r.position))).size,5);
 await tool('measure');await page.locator('#result-name').fill('Ranks');await page.locator('#reducer').selectOption('rank');await page.locator('[data-group="total"]').check();await apply();
 assert.deepEqual(await values('Ranks'),['0','0','0','0','1','0']);
 await select('Sums');await tool('place');await expression(cards().nth(0),f('total'));await expression(cards().nth(1),{read:{object:'Ranks',on:f('key'),key:f('key'),value:f('value')}});
 const before=(await state()).revision;await page.locator('#preview').click();await idle();assert.equal((await state()).revision,before);
 await page.locator('#cancel').click();await idle();assert.equal((await state()).revision,before);
 await tool('place');await expression(cards().nth(0),f('total'));await expression(cards().nth(1),{read:{object:'Ranks',on:f('key'),key:f('key'),value:f('value')}});await apply();
 const stacked=(await state()).objects.find(o=>o.name==='Sums').rows;assert.equal(new Set(stacked.map(r=>JSON.stringify(r.position))).size,6);
 await page.locator('#undo').click();await idle();assert.deepEqual((await state()).objects.find(o=>o.name==='Sums').rows,coincident);
 await page.locator('#redo').click();await idle();assert.deepEqual((await state()).objects.find(o=>o.name==='Sums').rows,stacked);
 await page.locator('[data-mode="points"]').click();await page.locator('#occurrence').selectOption(stacked[4].ref[1]);await idle();
 await page.getByRole('button',{name:'Follow keyed read · 1'}).click();await idle();assert.match(await page.locator('#panel').textContent(),/"contributor_count": "1"/);
 await page.locator('#labels').selectOption('total');
 await page.screenshot({path:path.join(output,'sum-stacks.png'),fullPage:true});

 // Same mode + target, different mathematics. Build a modular diagonal from blank inputs.
 await page.locator('[data-mode="objects"]').click();await tool('grid',true);await page.locator('#result-name').fill('Square');await page.locator('#grid-shape').fill('3, 3');await apply();
 await tool('lens');await page.locator('#result-name').fill('Diagonal');await expression(cards().nth(0),op('=',op('%',op('-',f('j'),f('i')),n(3)),n(0)));await apply();
 await tool('measure');await page.locator('#result-name').fill('Row counts');await page.locator('[data-group="i"]').check();await apply();assert.deepEqual(await values('Row counts'),['1','1','1']);
 await select('Square');await tool('lens');await page.locator('#result-name').fill('Empty relation');await expression(cards().nth(0),op('=',f('value'),n(0)));await apply();
 await tool('measure');await page.locator('#result-name').fill('Zero counts');await page.locator('[data-group="i"]').check();await apply();assert.deepEqual(await values('Zero counts'),['0','0','0']);
 await page.locator('[data-mode="points"]').click();const zero=(await state()).objects.find(o=>o.name==='Zero counts').rows[0];await page.locator('#occurrence').selectOption(zero.ref[1]);await idle();assert.match(await page.locator('#panel').textContent(),/0 contributors/);

 // Failure is a failed draft; it must not relabel the previous picture as a success.
 await page.locator('[data-mode="objects"]').click();await select('Square');await tool('lens');await page.locator('#result-name').fill('Bad');await expression(cards().nth(0),op('=',op('%',f('i'),n(0)),n(0)));const revision=(await state()).revision;await page.locator('#preview').click();await idle();assert.equal(await page.locator('#apply').isEnabled(),false);assert.equal((await state()).revision,revision);assert.equal(await page.locator('#status').getAttribute('class'),'error');await page.locator('#cancel').click();await idle();

 // Long hold, drag cancellation, pointer cancel, mode-sensitive menus, keyboard alternative.
 const canvas=await page.locator('#hit').boundingBox(),x=canvas.x+canvas.width*.45,y=canvas.y+canvas.height*.45;
 await page.mouse.move(x,y);await page.mouse.down();await page.waitForTimeout(550);assert.equal(await page.locator('#menu').evaluate(d=>d.open),true);assert.equal(await page.locator('[data-action="lens"]').count(),1);await page.mouse.up();await page.locator('#close-menu').click();
 await page.mouse.move(x,y);await page.mouse.down();await page.mouse.move(x+70,y);await page.waitForTimeout(550);await page.mouse.up();assert.equal(await page.locator('#menu').evaluate(d=>d.open),false);
 await page.locator('[data-mode="view"]').click();await page.locator('#options').click();assert.equal(await page.locator('#menu-actions button').count(),1);assert.equal(await page.locator('[data-action="fit"]').count(),1);await page.locator('#close-menu').click();
 await page.locator('[data-mode="objects"]').click();await page.locator('#canvas').press('Shift+F10');assert.equal(await page.locator('#menu').evaluate(d=>d.open),true);await page.locator('#menu').press('Escape');
 const client=await context.newCDPSession(page);
 await client.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x,y,id:1}]});await page.waitForTimeout(550);assert.equal(await page.locator('#menu').evaluate(d=>d.open),true);await client.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await page.locator('#close-menu').tap();
 await client.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x,y,id:1}]});await client.send('Input.dispatchTouchEvent',{type:'touchCancel',touchPoints:[]});await page.waitForTimeout(550);assert.equal(await page.locator('#menu').evaluate(d=>d.open),false);
 await client.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x,y,id:1}]});await client.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x,y,id:1},{x:x+50,y,id:2}]});await page.waitForTimeout(550);await client.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});assert.equal(await page.locator('#menu').evaluate(d=>d.open),false);

 // Browser transport preserves integers that cannot be represented by Number.
 await integers('Exact','1152921504606846977');assert.deepEqual(await values('Exact'),['1152921504606846977']);
 const downloadPromise=page.waitForEvent('download');await page.locator('#save').click();const download=await downloadPromise;const saved=path.join(output,'workspace.json');await download.saveAs(saved);await idle();
 await page.locator('#undo').click();await idle();assert.equal((await state()).objects.some(o=>o.name==='Exact'),false);
 await page.locator('#file').setInputFiles(saved);await idle();assert.deepEqual(await values('Exact'),['1152921504606846977']);
 assert.equal((await page.request.post(origin+'/api/cancel',{headers:{Origin:'https://example.invalid'},data:{revision:(await state()).revision}})).status(),403);
 const layouts=[];
 for(const width of [1250,736,360,320]){await page.setViewportSize({width,height:950});await page.emulateMedia({colorScheme:width===320?'dark':'light'});await select('Sums');await page.locator('#labels').selectOption('total');const size=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth}));assert.ok(size.scroll<=size.width,JSON.stringify(size));layouts.push(size);await page.screenshot({path:path.join(output,`width-${width}.png`),fullPage:true})}
 // SVG letterboxing on phones must not change the occurrence selected by a tap.
 await page.locator('[data-mode="points"]').click();const mark=await page.locator('#marks circle').nth(4).boundingBox();await page.touchscreen.tap(mark.x+mark.width/2,mark.y+mark.height/2);await idle();assert.equal(await page.locator('#occurrence').inputValue(),stacked[4].ref[1]);await page.locator('#options').click();assert.deepEqual(await page.locator('#menu-actions button').allTextContents(),['Explain this occurrence']);await page.locator('#close-menu').click();
 assert.deepEqual(errors,[]);fs.writeFileSync(path.join(output,'report.json'),JSON.stringify({browser:browser.version(),errors,layouts,objects:(await state()).objects.length,checks:['two constructions through controls','preview/cancel/failure','keyed rank placement and inspection','zero contributors','captured undo/redo/save/open','exact integer transport','hold/drag/cancel/multi-touch','mode/context and keyboard menus','same-origin mutation guard']},null,2));
 console.log('Construction studio browser checks passed.');
 }finally{await browser.close();server?.kill()}
})().catch(e=>{server?.kill();console.error(e);process.exitCode=1});
