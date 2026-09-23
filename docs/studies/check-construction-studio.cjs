// HISTORICAL: targets the UI at commit 19928e6. For the current canvas run
// node docs/studies/check-continuous-canvas.cjs. See studies/README.md.
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
 async function expression(card,spec,path=[]){
   if(path.length)await card.locator(`[data-path="${path.join('/')}"]`).click();
   else await card.locator('[data-edit-root]').click();
   const sheet=card.locator('.expression-sheet'),type=sheet.getByLabel('Expression type');
   const desired='field'in spec?'Field':'integer'in spec?'Number':'parameter'in spec?'Parameter':spec.op?'Operation':spec.tuple?'Key tuple':'Keyed read';
   if(await type.inputValue()!==desired)await type.selectOption(desired);
   if(desired==='Field'){assert.ok((await sheet.getByLabel('Field',{exact:true}).locator('option').allTextContents()).includes(spec.field),`Unavailable field ${spec.field} at ${path.join('/')}`);await sheet.getByLabel('Field',{exact:true}).selectOption(spec.field);}
   else if(desired==='Number')await sheet.getByLabel('Exact integer',{exact:true}).fill(String(spec.integer));
   else if(desired==='Parameter')await sheet.getByLabel('Parameter',{exact:true}).selectOption(spec.parameter);
   else if(desired==='Operation'){
     await sheet.getByLabel('Operation',{exact:true}).selectOption(spec.op);
     await expression(card,spec.args[0],[...path,'args',0]);
     await expression(card,spec.args[1],[...path,'args',1]);
   }else if(desired==='Key tuple'){
     for(let i=0;i<spec.tuple.length;i++)await expression(card,spec.tuple[i],[...path,'tuple',i]);
   }else{
     await sheet.getByLabel('Read from',{exact:true}).selectOption(spec.read.object);
     await expression(card,spec.read.on,[...path,'read','on']);
     await expression(card,spec.read.key,[...path,'read','key']);
     await expression(card,spec.read.value,[...path,'read','value']);
   }
   if(!path.length)await card.locator('[data-expression-done]').click();
 }
 async function retain(field){await page.locator('#panel fieldset > .field-keys').first().locator('[data-group-add]').selectOption(field)}

 const f=field=>({field}),n=integer=>({integer:String(integer)}),op=(op,a,b)=>({op,args:[a,b]});
 const cards=()=>page.locator('#panel fieldset > .expression');
 async function apply(){await page.locator('#preview').click();await idle();assert.equal(await page.locator('#apply').isEnabled(),true,await page.locator('#status').textContent());await page.locator('#apply').click();await idle()}
 async function integers(name,values){await tool('integers',true);await page.locator('#result-name').fill(name);await page.locator('#integer-values').fill(values);await apply()}
 async function select(name){await page.locator('[data-object]').filter({hasText:name}).first().click()}
 async function values(name){return (await state()).objects.find(o=>o.name===name).rows.map(r=>r.fields.value)}
 async function declare(name,value){
   await page.locator('#cases').click();await page.locator('#declare-parameter').click();
   await page.getByLabel('Parameter name',{exact:true}).last().fill(name);await page.getByLabel('Parameter value',{exact:true}).fill(value);await apply();
 }
 async function compare(left,leftKeys,right,rightKeys,expected,expectedKeys,leftValue='value'){
   await select(left);await tool('compare');
   await page.locator('#comparison-left-value').selectOption(leftValue);
   await page.locator('#comparison-right').selectOption(right);await page.locator('#comparison-expected').selectOption(expected);
   const keySets=page.locator('#comparison-tool .field-keys');
   for(const [i,fields] of [leftKeys,rightKeys,expectedKeys].entries()){
     while(await keySets.nth(i).locator('.key-chips button').count())await keySets.nth(i).locator('.key-chips button').first().click();
     for(const field of fields)await keySets.nth(i).locator('[data-group-add]').selectOption(field);
   }
   await page.locator('#check-comparison').click();await idle();
 }
 await declare('p','3');
 assert.deepEqual((await state()).parameters,{p:'3'});
 assert.equal(await page.locator('#replay').isVisible(),false);
 await integers('A','0, 1, 3');await integers('B','0, 2');await select('A');
 await tool('product');await page.locator('#result-name').fill('Pairs');
 const sources=page.locator('#panel fieldset > label > select');await sources.nth(0).selectOption('A');await sources.nth(1).selectOption('B');await apply();
 await tool('field');await page.locator('#result-name').fill('Sums');await expression(cards().nth(0),op('+',f('left_value'),f('right_value')));await apply();
 assert.deepEqual((await state()).objects.find(o=>o.name==='Sums').rows.map(r=>r.fields.total),['0','2','1','3','3','5']);
 await tool('place');await expression(cards().nth(0),f('total'));await expression(cards().nth(1),n(0));await apply();
 const coincident=(await state()).objects.find(o=>o.name==='Sums').rows;assert.equal(new Set(coincident.map(r=>JSON.stringify(r.position))).size,5);
 await tool('measure');await page.locator('#result-name').fill('Ranks');await page.locator('#reducer').selectOption('rank');await retain('total');await apply();
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
 await page.locator('#close-linked').click();
 await page.locator('#labels').selectOption('total');
 await page.screenshot({path:path.join(output,'sum-stacks.png'),fullPage:true});

 // The same group selector browses sum fibers, keeping selection outside history.
 await page.locator('[data-mode="groups"]').click();await page.locator('#activity > .field-keys [data-group-add]').selectOption('total');
 const groupRevision=(await state()).revision;
 await page.locator('#browse-groups').click();await idle();await page.locator('#group-choice').selectOption('3');
 assert.match(await page.locator('#group-summary').textContent(),/2 incident occurrences · 2 occurrences/);
 assert.equal(await page.locator('[data-group-member="true"]').count(),2);assert.equal((await state()).revision,groupRevision);
 await page.screenshot({path:path.join(output,'sum-group.png'),fullPage:true});
 await tool('measure');assert.deepEqual(await page.locator('#panel fieldset > .field-keys').first().locator('.key-chips button').allTextContents(),['total ×']);
 await page.locator('#result-name').fill('Fiber ranks');await page.locator('#reducer').selectOption('rank');
 await page.locator('#rank-order').getByRole('button',{name:'Remove key index'}).click();await page.locator('#rank-order [data-group-add]').selectOption('value');
 await page.locator('#preview').click();await idle();assert.match(await page.locator('#status').textContent(),/ties/);assert.equal((await state()).revision,groupRevision);
 await page.locator('#rank-order [data-group-add]').selectOption('key');await apply();assert.deepEqual(await values('Fiber ranks'),['0','0','0','0','1','0']);
 await select('Sums');await page.locator('#activity > .field-keys [data-group-add]').selectOption('total');await page.locator('#browse-groups').click();await idle();await page.locator('#group-choice').selectOption('3');
 await tool('group_lens');await page.locator('#result-name').fill('Sum three');await apply();
 const sumLens=(await state()).objects.find(o=>o.name==='Sum three');assert.equal(sumLens.rows.length,6);assert.equal(sumLens.rows.filter(r=>r.match).length,2);

 // Same mode + target, different mathematics. Build a modular diagonal from blank inputs.
 await page.locator('[data-mode="objects"]').click();await tool('grid',true);await page.locator('#result-name').fill('Square');await page.locator('#grid-shape').fill('3, 3');await apply();
 await tool('lens');await page.locator('#result-name').fill('Diagonal');const rule=op('=',op('%',op('-',f('j'),f('i')),n(3)),n(0));await expression(cards().nth(0),rule);
 assert.equal(await cards().nth(0).locator('.formula').getAttribute('aria-label'),'(((j − i) mod 3) = 0)');
 assert.deepEqual(JSON.parse(await page.locator('#declaration').textContent()).args.rule,rule);
 assert.ok((await cards().nth(0).boundingBox()).height<220,'Collapsed compound expression should stay compact');
 await cards().nth(0).locator('[data-path="args/0/args/1"]').click();await cards().nth(0).getByLabel('Exact integer',{exact:true}).fill('5');
 await cards().nth(0).locator('[data-expression-undo]').click();assert.deepEqual(JSON.parse(await page.locator('#declaration').textContent()).args.rule,rule);
 await page.screenshot({path:path.join(output,'compact-expression.png'),fullPage:true});await apply();
 await page.locator('[data-mode="groups"]').click();await page.locator('#activity > .field-keys [data-group-add]').selectOption('i');await page.locator('#browse-groups').click();await idle();
 assert.match(await page.locator('#group-summary').textContent(),/1 incident occurrences · 3 occurrences/);assert.equal(await page.locator('[data-group-member="true"]').count(),3);
 await page.screenshot({path:path.join(output,'modular-group.png'),fullPage:true});
 await page.locator('[data-mode="objects"]').click();
 await tool('measure');await page.locator('#result-name').fill('Row counts');await retain('i');await apply();assert.deepEqual(await values('Row counts'),['1','1','1']);
 await select('Square');await tool('lens');await page.locator('#result-name').fill('Empty relation');await expression(cards().nth(0),op('=',f('value'),n(0)));await apply();
 await tool('measure');await page.locator('#result-name').fill('Zero counts');await retain('i');await apply();assert.deepEqual(await values('Zero counts'),['0','0','0']);
 await page.locator('[data-mode="points"]').click();const zero=(await state()).objects.find(o=>o.name==='Zero counts').rows[0];await page.locator('#occurrence').selectOption(zero.ref[1]);await idle();assert.match(await page.locator('#panel').textContent(),/0 contributors/);

 // Coverage witnesses use the same selector: zero, one, or two incident candidates.
 await page.locator('[data-mode="objects"]').click();await select('Square');await tool('lens');await page.locator('#result-name').fill('Assignment candidates');
 await expression(cards().nth(0),op('and',op('>',f('i'),n(0)),op('<',f('j'),f('i'))));await apply();
 await page.locator('[data-mode="groups"]').click();await page.locator('#activity > .field-keys [data-group-add]').selectOption('i');await page.locator('#browse-groups').click();await idle();
 assert.deepEqual(await page.locator('#group-choice option').allTextContents(),['i = 0 · 0 of 3 incident','i = 1 · 1 of 3 incident','i = 2 · 2 of 3 incident']);
 assert.match(await page.locator('#group-summary').textContent(),/0 incident occurrences · 3 occurrences/);
 assert.equal(await page.locator('[data-group-member="true"]').count(),3);
 await tool('group_lens');await page.locator('#result-name').fill('Uncovered group');await apply();
 const uncovered=(await state()).objects.find(o=>o.name==='Uncovered group');assert.equal(uncovered.rows.length,9);assert.equal(uncovered.rows.filter(r=>r.match).length,0);
 await page.locator('[data-mode="groups"]').click();await page.locator('#activity > .field-keys [data-group-add]').selectOption('i');await page.locator('#browse-groups').click();await idle();assert.equal(await page.locator('#group-choice option').count(),3);

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
 const downloadPromise=page.waitForEvent('download');await page.locator('#save').click();await page.locator('#save-math').click();const download=await downloadPromise;const saved=path.join(output,'workspace.json');await download.saveAs(saved);await idle();
 await page.locator('#undo').click();await idle();assert.equal((await state()).objects.some(o=>o.name==='Exact'),false);
 await page.locator('#file').setInputFiles(saved);await idle();assert.deepEqual(await values('Exact'),['1152921504606846977']);
 assert.equal((await page.request.post(origin+'/api/cancel',{headers:{Origin:'https://example.invalid'},data:{revision:(await state()).revision}})).status(),403);
 // A formula draft survives an unrelated inspection; its target and undo stay local.
 const committedBeforeDraft=await(await page.request.get(origin+'/api/export')).text();
 await select('Square');await tool('lens');await page.locator('#result-name').fill('Recovered diagonal');await expression(cards().nth(0),rule);
 const modulus=cards().nth(0).locator('[data-path="args/0/args/1"]');await modulus.focus();await page.keyboard.press('Enter');
 assert.equal(await page.getByLabel('Exact integer',{exact:true}).evaluate(n=>n===document.activeElement),true,'Opening a formula token must focus its editor');
 await page.getByLabel('Exact integer',{exact:true}).fill('0');await page.keyboard.press('Escape');
 assert.equal(await modulus.evaluate(n=>n===document.activeElement),true,'Closing an inspector returns to its initiating token');
 assert.equal(await page.locator('#panel form').count(),1,'Escape in an expression must not discard the construction');
 await page.locator('#preview').click();await idle();assert.equal(await page.locator('#draft-status').getAttribute('data-phase'),'failed');assert.match(await page.locator('#draft-status').textContent(),/Preview failed/);
 await modulus.click();await page.getByLabel('Exact integer',{exact:true}).fill('5');await page.locator('#preview').click();await idle();assert.equal(await page.locator('#draft-status').getAttribute('data-phase'),'ready');
 await page.getByLabel('Exact integer',{exact:true}).fill('3');assert.equal(await page.locator('#draft-status').getAttribute('data-phase'),'editing');assert.equal(await page.locator('#apply').isEnabled(),false);assert.doesNotMatch(await page.locator('#status').textContent(),/preview ready/i);
 // A single click immediately after input blur must select the requested object.
 await page.locator('[data-object="Sums"]').click();assert.equal(await page.locator('[data-object="Sums"]').getAttribute('aria-pressed'),'true');
 assert.equal(await page.locator('#panel form').count(),0);assert.equal(await page.locator('#resume-draft').isVisible(),true);
 for(const id of ['add','open','undo'])assert.equal(await page.locator('#'+id).isEnabled(),false,'Workspace changes wait for the draft: '+id);
 await page.locator('[data-mode="groups"]').click();await page.locator('#activity > .field-keys [data-group-add]').selectOption('total');await page.locator('#browse-groups').click();await idle();
 await page.locator('#group-choice').selectOption('3');assert.match(await page.locator('#group-summary').textContent(),/2 incident occurrences/);
 await page.locator('#options').click();assert.equal(await page.locator('[data-action="measure"]').isEnabled(),false);await page.locator('#close-menu').click();
 assert.equal(await(await page.request.get(origin+'/api/export')).text(),committedBeforeDraft,'Draft edits and inspection must not change captured workspace data');
 await page.screenshot({path:path.join(output,'parked-draft.png'),fullPage:true});
 await page.locator('#resume-draft').click();assert.equal(await page.locator('#result-name').inputValue(),'Recovered diagonal');assert.equal(JSON.parse(await page.locator('#declaration').textContent()).args.source,'Square');
 assert.equal(await page.locator('#draft-status').getAttribute('data-phase'),'editing');
 await cards().nth(0).locator('[data-expression-undo]').click();assert.equal(JSON.parse(await page.locator('#declaration').textContent()).args.rule.args[0].args[1].integer,'5','Local expression undo survives parking');
 await expression(cards().nth(0),rule);await page.locator('#preview').click();await idle();
 await select('A');await page.locator('#resume-draft').click();assert.equal(await page.locator('#apply').isEnabled(),false,'Parking invalidates even a successful preview');
 await apply();const recovered=(await state()).objects.find(o=>o.name==='Recovered diagonal');assert.equal(recovered.rows.length,9);assert.equal(recovered.rows.filter(r=>r.match).length,3);
 // Transfer the same detour to a grouped measurement and a captured rank receipt.
 await page.setViewportSize({width:320,height:950});await select('Sums');await tool('measure');await page.locator('#result-name').fill('Recovered counts');await retain('total');
 const chip=page.locator('#panel fieldset > .field-keys').first().getByRole('button',{name:'Remove key total'});await chip.focus();await page.keyboard.press('Enter');
 assert.equal(await page.locator('#panel fieldset > .field-keys').first().locator('[data-group-add]').evaluate(n=>n===document.activeElement),true,'Removing the last key preserves a useful focus target');
 await retain('total');const countDraft=JSON.parse(await page.locator('#declaration').textContent());
 await select('Ranks');await page.locator('[data-mode="points"]').tap();const ranked=(await state()).objects.find(o=>o.name==='Ranks').rows;
 await page.locator('#occurrence').selectOption(ranked[4].ref[1]);await idle();assert.match(await page.locator('#panel').textContent(),/1 contributors/);
 await page.locator('#resume-draft').tap();assert.deepEqual(JSON.parse(await page.locator('#declaration').textContent()),countDraft);
 await page.locator('#preview').tap();await idle();assert.equal(await page.locator('#draft-status').getAttribute('role'),'status');
 assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Draft tray and feedback must fit phone width');
 await page.locator('#draft-status').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(output,'phone-draft-feedback.png'),fullPage:true});
 await page.locator('#apply').tap();await idle();assert.deepEqual(await values('Recovered counts'),['1','1','1','2','1']);
 // Escape from the form parks an idea; only explicit Cancel/Discard drops it.
 await select('Square');await tool('lens');await page.locator('#result-name').fill('Keep this idea');await page.locator('#result-name').press('Escape');
 assert.equal(await page.locator('#panel form').count(),0);await page.locator('#resume-draft').tap();assert.equal(await page.locator('#result-name').inputValue(),'Keep this idea');
 await page.locator('#discard-draft').tap();await idle();assert.equal(await page.locator('#draft-tray').isVisible(),false);assert.equal(await page.locator('#add').isEnabled(),true);
 const authoring={retainedFormula:true,retainedGrouping:true,retainedLocalUndo:true,originalTarget:true,inspectionLeavesCaptureUnchanged:true,localStatus:true,focusRecovery:true,firstClickNavigation:true};
 const layouts=[];
 for(const width of [1250,736,360,320]){await page.setViewportSize({width,height:950});await page.emulateMedia({colorScheme:width===320?'dark':'light'});await select('Sums');await page.locator('#labels').selectOption('total');const size=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth}));assert.ok(size.scroll<=size.width,JSON.stringify(size));layouts.push(size);await page.screenshot({path:path.join(output,`width-${width}.png`),fullPage:true})}
 // SVG letterboxing on phones must not change the occurrence selected by a tap.
 await page.locator('[data-mode="points"]').click();const mark=await page.locator('#marks circle').nth(4).boundingBox();await page.touchscreen.tap(mark.x+mark.width/2,mark.y+mark.height/2);await idle();assert.equal(await page.locator('#occurrence').inputValue(),stacked[4].ref[1]);await page.locator('#options').click();assert.deepEqual(await page.locator('#menu-actions button').allTextContents(),['Explain this occurrence']);await page.locator('#close-menu').click();
 // At phone width, author a compound formula and wrap the latest edited value.
 await page.locator('[data-mode="objects"]').tap();await select('Square');await tool('lens');await expression(cards().nth(0),rule);
 await cards().nth(0).locator('[data-path="args/0/args/1"]').tap();await cards().nth(0).getByLabel('Exact integer',{exact:true}).fill('5');
 await cards().nth(0).getByLabel('Expression type',{exact:true}).selectOption('Operation');
 assert.deepEqual(JSON.parse(await page.locator('#declaration').textContent()).args.rule.args[0].args[1],op('+',n(5),n(1)),'Wrapping must retain the latest edit, not the initial subtree');
 await cards().nth(0).locator('[data-expression-undo]').tap();await cards().nth(0).locator('[data-expression-undo]').tap();
 assert.deepEqual(JSON.parse(await page.locator('#declaration').textContent()).args.rule,rule);
 assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Formula controls must fit phone width');
 await page.screenshot({path:path.join(output,'phone-expression.png'),fullPage:true});await page.locator('#cancel').tap();await idle();
 // Group taps use captured membership even when the SVG is letterboxed.
 await select('Diagonal');await page.locator('[data-mode="groups"]').tap();await page.locator('#activity > .field-keys [data-group-add]').selectOption('i');await page.locator('#browse-groups').tap();await idle();
 const phoneRevision=(await state()).revision;
 // Use the phone's Canvas jump so the sticky navigation does not cover the tap.
 await page.locator('[data-workspace-jump="scene"]').tap();
 assert.equal(await page.evaluate(()=>document.activeElement.id),'scene');
 const member=await page.locator('#marks circle').nth(8).boundingBox();
 assert.ok(await page.evaluate(({x,y})=>document.elementFromPoint(x,y)?.closest('#canvas'),{x:member.x+member.width/2,y:member.y+member.height/2}),'Group member must be reachable below the sticky navigation');
 await page.touchscreen.tap(member.x+member.width/2,member.y+member.height/2);
 assert.equal(await page.locator('#group-choice').inputValue(),'2');assert.equal(await page.locator('[data-group-member="true"]').count(),3);
 await page.locator('#options').tap();assert.deepEqual(await page.locator('#menu-actions button').allTextContents(),['Choose group keys','Create a group lens','Measure all groups','Check coverage']);await page.locator('#close-menu').tap();
 assert.equal((await state()).revision,phoneRevision);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 await page.screenshot({path:path.join(output,'phone-group.png'),fullPage:true});
 // The same coverage instrument checks assignments and additive fibers against chosen keys.
 await page.setViewportSize({width:1250,height:950});await page.emulateMedia({colorScheme:'light'});
 await page.locator('[data-mode="objects"]').click();await integers('Expected points','2, 0, 1');
 async function coverage(source,by,expected,expectedBy='value'){
   await select(source);await tool('coverage');
   await page.locator('#coverage-tool > .field-keys [data-group-add]').selectOption(by);
   await page.locator('#coverage-expected').selectOption(expected);
   await page.locator('#coverage-expected-keys [data-group-add]').selectOption(expectedBy);
   await page.locator('#check-coverage').click();await idle();
 }
 const beforeCoverage=await(await page.request.get(origin+'/api/export')).text();
 await coverage('Assignment candidates','i','Expected points');
 assert.match(await page.locator('#coverage-status').textContent(),/1 of 3.*1 missing, 1 multiple, 0 outside/);
 assert.equal(await page.locator('#coverage-adopt').isEnabled(),false);
 await page.locator('#coverage-filter').selectOption('multiple');await page.locator('#coverage-match').selectOption('1');await page.getByRole('button',{name:'Inspect selected match',exact:true}).click();await idle();
 assert.match(await page.locator('#panel').textContent(),/"i": "2"/);await page.getByRole('button',{name:'Back to coverage'}).click();
 assert.equal(await page.getByRole('button',{name:'Inspect selected match',exact:true}).evaluate(n=>n===document.activeElement),true,'Returning to witnesses restores focus to the initiating control');
 assert.equal(await page.locator('#coverage-match').inputValue(),'1');
 assert.equal(await page.locator('#coverage-filter').inputValue(),'multiple');
 await page.locator('#coverage-filter').selectOption('missing');
 await page.locator('#view-coverage').click();await idle();
 const leftCard=()=>page.locator('.linked-card[data-side="left"]'),rightCard=()=>page.locator('.linked-card[data-side="right"]');
 assert.equal(await leftCard().locator('[data-linked-member="true"]').count(),1);
 assert.equal(await rightCard().locator('[data-linked-member="true"]').count(),3);
 assert.match(await rightCard().locator('.linked-detail').textContent(),/outside relation/);
 // Zoom is local to a view and remains after changing the evidence link.
 const leftBefore=await leftCard().locator('circle').first().getAttribute('cx'),rightBefore=await rightCard().locator('circle').first().getAttribute('cx');
 await page.getByRole('button',{name:'Zoom in right view',exact:true}).click();
 const rightZoomed=await rightCard().locator('circle').first().getAttribute('cx');
 assert.notEqual(rightZoomed,rightBefore);assert.equal(await leftCard().locator('circle').first().getAttribute('cx'),leftBefore);
 await page.locator('#linked-choice').selectOption('0');
 assert.equal(await page.locator('#coverage-key').inputValue(),'0');assert.equal(await page.locator('#coverage-filter').inputValue(),'all');
 assert.equal(await rightCard().locator('circle').first().getAttribute('cx'),rightZoomed);
 const rightSvg=rightCard().locator('svg'),box=await rightSvg.boundingBox();
 await page.mouse.move(box.x+80,box.y+80);await page.mouse.down();
 await page.mouse.move(box.x+110,box.y+90);
 assert.notEqual(await rightCard().locator('circle').first().getAttribute('cx'),rightZoomed);
 await rightSvg.dispatchEvent('pointercancel',{pointerId:901,isPrimary:true});
 const cancelledPosition=await rightCard().locator('circle').first().getAttribute('cx');
 await page.mouse.move(box.x+140,box.y+100);await page.mouse.up();
 assert.equal(await rightCard().locator('circle').first().getAttribute('cx'),cancelledPosition);
 assert.equal(await leftCard().locator('circle').first().getAttribute('cx'),leftBefore);
 assert.equal(await rightCard().locator('[data-linked-member="true"]').count(),3);
 // A tap in the independent expected domain selects its declared correspondence.
 const expectedMark=await leftCard().locator('circle').nth(1).boundingBox();
 await page.touchscreen.tap(expectedMark.x+expectedMark.width/2,expectedMark.y+expectedMark.height/2);
 assert.equal(await page.locator('#coverage-key').inputValue(),'1');
 await page.locator('#linked-views').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(output,'linked-coverage.png'),fullPage:true});
 await page.getByRole('button',{name:'Show candidate group'}).click();await idle();
 assert.equal(await page.locator('[data-group-member="true"]').count(),3);
 assert.equal(await(await page.request.get(origin+'/api/export')).text(),beforeCoverage);
 await page.screenshot({path:path.join(output,'coverage-witnesses.png'),fullPage:true});
 // Selecting the surviving occurrences removes a candidate group, not an expected key.
 await page.locator('[data-mode="objects"]').click();await select('Assignment candidates');await tool('select');await page.locator('#result-name').fill('Surviving candidates');await apply();
 await coverage('Surviving candidates','i','Expected points');await page.locator('#coverage-filter').selectOption('missing');
 assert.match(await page.locator('#coverage-witness').textContent(),/No candidate group exists/);
 assert.equal(await page.getByRole('button',{name:'Show candidate group'}).count(),0);
 await page.locator('#view-coverage').click();await idle();
 assert.equal(await leftCard().locator('[data-linked-member="true"]').count(),1);
 assert.equal(await rightCard().locator('[data-linked-member="true"]').count(),0);
 assert.equal(await rightCard().locator('[data-linked-occurrence]').isEnabled(),false);
 assert.equal(await rightCard().locator('[data-linked-inspect]').isEnabled(),false);
 assert.match(await rightCard().locator('.linked-detail').textContent(),/No candidate group/);
 await leftCard().locator('[data-linked-inspect]').click();await idle();assert.match(await page.locator('#panel').textContent(),/"value": "0"/);
 await page.getByRole('button',{name:'Back to coverage'}).click();assert.equal(await page.locator('#coverage-filter').inputValue(),'missing');
 await page.locator('#linked-views').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(output,'linked-missing.png'),fullPage:true});
 await page.locator('#close-linked').click();
 await page.locator('#coverage-filter').selectOption('outside');assert.equal(await page.locator('#view-coverage').isEnabled(),false,'An empty filtered category cannot open a different link silently');await page.locator('#coverage-filter').selectOption('missing');
 await page.getByRole('button',{name:'Inspect expected occurrence'}).click();await idle();assert.match(await page.locator('#panel').textContent(),/"value": "0"/);await page.getByRole('button',{name:'Back to coverage'}).click();
 // A new rule supplies one value per point. Attach it without overwriting point labels.
 await coverage('Diagonal','i','Expected points');assert.equal(await page.locator('#coverage-status').getAttribute('data-phase'),'passed');
 await page.locator('#coverage-expected-keys').getByRole('button',{name:'Remove key value'}).click();assert.equal(await page.locator('#coverage-adopt').count(),0);
 await page.locator('#coverage-expected-keys [data-group-add]').selectOption('value');await page.locator('#check-coverage').click();await idle();
 await page.locator('#coverage-adopt').click();await page.locator('#result-name').fill('Assigned points');await page.locator('#assigned-field').fill('owner');await expression(cards().nth(0),f('j'));
 const assignmentDraft=JSON.parse(await page.locator('#declaration').textContent());await coverage('Diagonal','i','Expected points');
 assert.equal(await page.locator('#coverage-status').getAttribute('data-phase'),'passed');assert.equal(await page.locator('#coverage-adopt').isEnabled(),false,'A read-only coverage check cannot replace the parked draft');
 await page.locator('#resume-draft').click();assert.deepEqual(JSON.parse(await page.locator('#declaration').textContent()),assignmentDraft);await apply();
 const assigned=(await state()).objects.find(o=>o.name==='Assigned points');assert.deepEqual(assigned.rows.map(r=>r.fields.owner),['2','0','1']);assert.deepEqual(await values('Assigned points'),['2','0','1']);
 await page.locator('#undo').click();await idle();assert.equal((await state()).objects.some(o=>o.name==='Assigned points'),false);await page.locator('#redo').click();await idle();
 await select('Assigned points');await page.locator('[data-mode="points"]').click();await page.locator('#occurrence').selectOption(assigned.rows[1].ref[1]);await idle();await page.getByRole('button',{name:'Follow keyed read · 0'}).click();await idle();assert.match(await page.locator('#panel').textContent(),/1 contributors/);assert.match(await page.locator('#panel').textContent(),/weight 0/);await page.locator('#close-linked').click();
 // Reuse that new field as a placement driver; undo restores the captured endpoints.
 await page.locator('[data-mode="objects"]').click();await select('Expected points');await tool('place');await expression(cards().nth(0),f('value'));await expression(cards().nth(1),n(0));await apply();
 const flat=(await state()).objects.find(o=>o.name==='Expected points').rows;
 await tool('place');await expression(cards().nth(0),f('value'));await expression(cards().nth(1),{read:{object:'Assigned points',on:f('value'),key:f('value'),value:f('owner')}});await apply();
 assert.deepEqual((await state()).objects.find(o=>o.name==='Expected points').rows.map(r=>r.position),[[2,2],[0,0],[1,1]]);
 await page.locator('#undo').click();await idle();assert.deepEqual((await state()).objects.find(o=>o.name==='Expected points').rows,flat);await page.locator('#redo').click();await idle();
 // Transfer: additive fibers, including outside matches even when every expected key is unique.
 await integers('Sum targets','5, 0, 2, 1');await coverage('Sums','total','Sum targets');
 assert.match(await page.locator('#coverage-status').textContent(),/4 of 4.*0 missing, 0 multiple, 1 outside/);assert.equal(await page.locator('#coverage-adopt').isEnabled(),false);
 await page.locator('#coverage-filter').selectOption('outside');assert.match(await page.locator('#coverage-key').textContent(),/3 · 2 matches · outside/);
 await select('Sums');await tool('lens');await page.locator('#result-name').fill('Unique sums');await expression(cards().nth(0),op('≠',f('total'),n(3)));await apply();
 await page.setViewportSize({width:320,height:950});await coverage('Unique sums','total','Sum targets');assert.equal(await page.locator('#coverage-status').getAttribute('data-phase'),'passed');
 assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Coverage choices and witnesses fit a phone');await page.locator('#coverage-status').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(output,'coverage-phone.png'),fullPage:true});
 await page.locator('#coverage-adopt').tap();await page.locator('#result-name').fill('Assigned sums');await page.locator('#assigned-field').fill('partner');await expression(cards().nth(0),f('right_value'));await apply();
 assert.deepEqual((await state()).objects.find(o=>o.name==='Assigned sums').rows.map(r=>r.fields.partner),['2','0','2','0']);
 const coverageDownload=page.waitForEvent('download');await page.locator('#save').click();await page.locator('#save-math').click();const capture=await coverageDownload;const coverageSaved=path.join(output,'coverage-workspace.json');await capture.saveAs(coverageSaved);await idle();
 await page.locator('#undo').click();await idle();await page.locator('#file').setInputFiles(coverageSaved);await idle();assert.deepEqual((await state()).objects.find(o=>o.name==='Assigned sums').rows.map(r=>r.fields.partner),['2','0','2','0']);
 const coverageChecks={balancedFailure:true,absentExpectedKey:true,candidateAndMatchInspection:true,unchangedCapture:true,originalKeysRetained:true,zeroValuedOwner:true,drivenPlacementUndo:true,additiveTransfer:true,phoneLayout:true,savedAssignment:true};

 // Transfer the same captured-view instrument to quotient measurements and keyed motion.
 await page.setViewportSize({width:1250,height:950});await page.locator('[data-mode="objects"]').click();
 await tool('grid',true);await page.locator('#result-name').fill('Quotient cells');await page.locator('#grid-shape').fill('7, 11');
 await expression(cards().nth(0),op('+',op('*',n(11),f('i')),op('*',n(7),f('j'))));await apply();
 await tool('lens');await page.locator('#result-name').fill('Quotient hits');await expression(cards().nth(0),op('≥',f('value'),n(77)));await apply();
 await tool('measure');await page.locator('#result-name').fill('Quotient counts');await retain('i');await apply();
 assert.deepEqual(await values('Quotient counts'),['0','1','3','4','6','7','9']);
 const quotientCounts=(await state()).objects.find(o=>o.name==='Quotient counts');
 await page.locator('[data-mode="points"]').click();await page.locator('#occurrence').selectOption(quotientCounts.rows[3].ref[1]);await idle();
 const beforeLinked=await(await page.request.get(origin+'/api/export')).text();
 await page.locator('#view-contributors').click();await idle();
 assert.equal(await leftCard().locator('[data-linked-member="true"]').count(),1);
 assert.equal(await rightCard().locator('[data-linked-member="true"]').count(),4);
 assert.equal(await rightCard().locator('circle').count(),77);
 await rightCard().locator('[data-linked-occurrence]').selectOption({index:3});await rightCard().locator('[data-linked-inspect]').click();await idle();
 assert.match(await page.locator('#panel').textContent(),/"i": "3"/);assert.match(await page.locator('#panel').textContent(),/"j": "10"/);
 assert.equal(await page.locator('#linked-views').isVisible(),true,'Inspecting a contributor keeps both views');
 await page.locator('#close-linked').click();await page.locator('#occurrence').selectOption(quotientCounts.rows[0].ref[1]);await idle();
 await page.locator('#view-contributors').click();await idle();
 assert.equal(await rightCard().locator('circle').count(),77);assert.equal(await rightCard().locator('[data-linked-member="true"]').count(),0);
 assert.match(await rightCard().locator('.linked-detail').textContent(),/Zero contributors/);
 assert.equal(await rightCard().locator('[data-linked-inspect]').isEnabled(),false);
 assert.equal(await(await page.request.get(origin+'/api/export')).text(),beforeLinked);
 await page.locator('#linked-views').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(output,'linked-zero.png'),fullPage:true});
 await page.locator('#close-linked').click();await page.locator('[data-mode="objects"]').click();
 // A driver is addressed by its captured version, even after its named view changes.
 await integers('Quotient probes','6, 0, 3');await tool('place');await expression(cards().nth(0),f('value'));
 await expression(cards().nth(1),{read:{object:'Quotient counts',on:f('value'),key:f('i'),value:f('value')}});await apply();
 const probes=(await state()).objects.find(o=>o.name==='Quotient probes');assert.deepEqual(probes.rows.map(r=>r.position),[[6,9],[0,0],[3,4]]);
 await select('Quotient counts');await tool('place');await expression(cards().nth(0),f('i'));await expression(cards().nth(1),n(99));await apply();
 await select('Quotient probes');await page.locator('[data-mode="points"]').click();await page.locator('#occurrence').selectOption(probes.rows[2].ref[1]);await idle();
 const beforeEarlier=await(await page.request.get(origin+'/api/export')).text();
 await page.getByRole('button',{name:'Follow keyed read · 4'}).click();await idle();
 assert.match(await rightCard().locator('[data-capture-label]').textContent(),/Captured dependency/);
 assert.match(await rightCard().locator('.linked-detail').textContent(),/Read 4/);
 await page.locator('#view-contributors').click();await idle();assert.equal(await rightCard().locator('[data-linked-member="true"]').count(),4);
 // Phone layout and keyboard inspection do not change the evidence.
 await page.setViewportSize({width:320,height:950});
 assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 await rightCard().locator('[data-linked-occurrence]').selectOption({index:1});
 const followContributor=rightCard().locator('[data-linked-inspect]');await followContributor.focus();await page.keyboard.press('Enter');await idle();
 assert.match(await page.locator('#panel').textContent(),/"j": "8"/);
 await page.locator('#linked-views').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(output,'linked-phone.png'),fullPage:true});
 assert.equal(await(await page.request.get(origin+'/api/export')).text(),beforeEarlier);
 await page.locator('#close-linked').click();await page.locator('#undo').click();await idle();assert.equal(await page.locator('#linked-views').isVisible(),false);await page.locator('#redo').click();await idle();
 const linkedChecks={coverageSelection:true,missingExpectedItem:true,independentCameras:true,quotientContributors:true,zeroSourceRetained:true,earlierDriver:true,keyboardInspection:true,phoneLayout:true,unchangedCapture:true};

 // Radon: compose ordered-key reads, then follow a contribution's weight to another sum.
 await page.setViewportSize({width:1250,height:950});await page.locator('[data-mode="objects"]').click();
 const tuple=(...fields)=>({tuple:fields.map(f)}),read=(object,on,key,value=f('value'))=>({read:{object,on,key,value}});
 const p={parameter:'p'};
 await tool('grid',true);await page.locator('#result-name').fill('Radon image');await page.locator('#grid-shape').fill('p, p');await page.locator('#grid-axes').fill('u, v');await page.locator('#grid-axes').press('Tab');
 await expression(cards().nth(0),op('*',f('u'),op('+',f('v'),n(1))));await apply();
 await tool('place');await expression(cards().nth(0),f('u'));await expression(cards().nth(1),f('v'));await apply();
 await tool('grid',true);await page.locator('#result-name').fill('Radon lines');await page.locator('#grid-shape').fill('p, p');await page.locator('#edit-axis-lengths').click();
 await expression(page.getByRole('group',{name:'Axis 1 length',exact:true}),op('+',p,n(1)));
 await page.locator('#grid-axes').fill('m, t');await page.locator('#grid-axes').press('Tab');await expression(cards().nth(0),n(0));await apply();
 await tool('product');await page.locator('#result-name').fill('Radon pairs');
 const roles=page.locator('#panel fieldset > label > input:not(#result-name)'),factors=page.locator('#panel fieldset > label > select'),copies=page.locator('#panel fieldset > div');
 await roles.nth(0).fill('point');await roles.nth(1).fill('line');await factors.nth(0).selectOption('Radon image');await factors.nth(1).selectOption('Radon lines');
 for(const field of ['u','v'])await copies.nth(0).locator(`input[value="${field}"]`).check();
 for(const field of ['m','t'])await copies.nth(1).locator(`input[value="${field}"]`).check();await apply();
 const onLine=op('or',op('and',op('<',f('line_m'),p),op('=',op('%',op('-',op('-',f('point_v'),op('*',f('line_m'),f('point_u'))),f('line_t')),p),n(0))),op('and',op('=',f('line_m'),p),op('=',f('point_u'),f('line_t'))));
 await tool('lens');await page.locator('#result-name').fill('Radon incidence');await expression(cards().nth(0),onLine);await apply();
 await tool('measure');await page.locator('#result-name').fill('Radon counts');await page.locator('#reducer').selectOption('sum');await retain('line_m');await retain('line_t');await expression(cards().nth(0),f('point_value'));await apply();
 assert.deepEqual(await values('Radon counts'),['3','6','9','8','5','5','7','7','4','0','6','12']);
 await tool('place');await expression(cards().nth(0),f('line_m'));await expression(cards().nth(1),f('line_t'));await apply();
 await select('Radon incidence');await tool('measure');await page.locator('#result-name').fill('Radon backprojection');await page.locator('#reducer').selectOption('sum');await retain('point_u');await retain('point_v');
 const compositeRead=read('Radon counts',tuple('line_m','line_t'),tuple('line_m','line_t'));
 await expression(cards().nth(0),compositeRead);
 // Tuple edits preserve context, local undo, and a parked declaration.
 await cards().nth(0).locator('[data-path="read/on"]').click();await cards().nth(0).getByRole('button',{name:'Add component',exact:true}).click();
 assert.equal(JSON.parse(await page.locator('#declaration').textContent()).args.weight.read.on.tuple.length,3);
 await cards().nth(0).getByRole('button',{name:'Remove last component',exact:true}).click();
 await cards().nth(0).locator('[data-expression-done]').click();
 const radonDraft=JSON.parse(await page.locator('#declaration').textContent());await select('Radon image');await page.locator('#resume-draft').click();assert.deepEqual(JSON.parse(await page.locator('#declaration').textContent()),radonDraft);
 // Swapping only the target key fails at the vertical family, rather than guessing.
 await expression(cards().nth(0),tuple('line_t','line_m'),['read','on']);await cards().nth(0).locator('[data-expression-done]').click();
 await page.locator('#preview').click();await idle();assert.equal(await page.locator('#apply').isEnabled(),false);
 await cards().nth(0).locator('[data-expression-undo]').click();await cards().nth(0).locator('[data-expression-undo]').click();
 assert.deepEqual(JSON.parse(await page.locator('#declaration').textContent()).args.weight,compositeRead);await apply();
 assert.deepEqual(await values('Radon backprojection'),['18','18','18','21','24','27','24','30','36']);
 await select('Radon counts');await tool('lens');await page.locator('#result-name').fill('Radon family');await expression(cards().nth(0),op('=',f('line_m'),n(0)));await apply();
 await tool('measure');await page.locator('#result-name').fill('Radon total');await page.locator('#reducer').selectOption('sum');await expression(cards().nth(0),f('value'));await apply();assert.deepEqual(await values('Radon total'),['18']);
 await select('Radon backprojection');await tool('field');await page.locator('#result-name').fill('Radon recovered');await page.locator('#field-name').fill('recovered');
 const numerator=op('-',f('value'),read('Radon total',n(0),f('key')));
 await expression(cards().nth(0),op('//',numerator,p));await apply();
 assert.deepEqual((await state()).objects.find(o=>o.name==='Radon recovered').rows.map(r=>r.fields.recovered),['0','0','0','1','2','3','2','4','6']);
 await tool('place');await expression(cards().nth(0),f('point_u'));await expression(cards().nth(1),f('point_v'));await apply();
 await select('Radon backprojection');await tool('field');await page.locator('#result-name').fill('Radon division check');await page.locator('#field-name').fill('remainder');await expression(cards().nth(0),op('%',numerator,p));await apply();
 assert.deepEqual((await state()).objects.find(o=>o.name==='Radon division check').rows.map(r=>r.fields.remainder),Array(9).fill('0'));
 await select('Radon image');const flatRadon=(await state()).objects.find(o=>o.name==='Radon image').rows;
 await tool('place');await expression(cards().nth(0),f('u'));await expression(cards().nth(1),op('+',f('v'),read('Radon recovered',tuple('u','v'),tuple('point_u','point_v'),f('recovered'))));await apply();
 const raisedRadon=(await state()).objects.find(o=>o.name==='Radon image').rows;assert.deepEqual(raisedRadon.map(r=>r.position),[[0,0],[0,1],[0,2],[1,1],[1,3],[1,5],[2,2],[2,5],[2,8]]);
 await page.emulateMedia({reducedMotion:'reduce'});
 await page.evaluate(()=>{window.replayLabels=[];window.replayObserver=new MutationObserver(records=>{for(const record of records)for(const node of record.addedNodes)window.replayLabels.push(node.textContent)});window.replayObserver.observe(document.querySelector('#replay output'),{childList:true})});
 await page.locator('#undo').click();await idle();assert.deepEqual((await state()).objects.find(o=>o.name==='Radon image').rows,flatRadon);await page.locator('#redo').click();await idle();assert.deepEqual((await state()).objects.find(o=>o.name==='Radon image').rows,raisedRadon);
 assert.equal(await page.evaluate(()=>{window.replayObserver.disconnect();return window.replayLabels.some(text=>text.startsWith('Replay '))}),false);
 // Scrubbing has no evaluation or history request; construction returns to the exact endpoint.
 const beforeReplay=await(await page.request.get(origin+'/api/export')).text();
 let replayRequests=0;const countRequest=request=>{if(request.url().includes('/api/'))replayRequests++};page.on('request',countRequest);
 await page.locator('#replay-progress').fill('12');assert.match(await page.locator('#scope').textContent(),/presentation only/);
 await page.locator('#play-replay').click();await idle();page.off('request',countRequest);assert.equal(replayRequests,0);
 assert.equal(await(await page.request.get(origin+'/api/export')).text(),beforeReplay);
 await page.locator('#replay-progress').fill('6');await page.locator('#options').click();assert.equal(await page.locator('#replay-progress').inputValue(),'24');await page.locator('#close-menu').click();
 await page.emulateMedia({reducedMotion:'no-preference'});
 await compare('Radon recovered',['point_u','point_v'],'Radon image',['u','v'],'Radon image',['u','v'],'recovered');
 assert.match(await page.locator('#comparison-status').textContent(),/Finite equality holds. 9 equal/);
 // Traverse pixel -> line-count weight -> source pixels, preserving return views.
 await select('Radon backprojection');await page.locator('[data-mode="points"]').click();const backPixel=(await state()).objects.find(o=>o.name==='Radon backprojection').rows[0];await page.locator('#occurrence').selectOption(backPixel.ref[1]);await idle();
 const radonBefore=await(await page.request.get(origin+'/api/export')).text();await page.locator('#view-contributors').click();await idle();
 await rightCard().locator('[data-linked-occurrence]').selectOption({index:3});await page.getByRole('button',{name:'Zoom in right view',exact:true}).click();
 const selectedContribution=await rightCard().locator('[data-linked-occurrence]').inputValue(),cameraBefore=await rightCard().locator('circle').first().getAttribute('cx');
 await rightCard().locator('[data-linked-inspect]').click();await idle();
 assert.match(await page.locator('#contribution-evidence').textContent(),/Source value 1 · weight 0/);
 await page.getByRole('button',{name:'Follow weight read · 0',exact:true}).click();await idle();
 assert.match(await page.locator('#linked-views').textContent(),/Key 3, 0/);assert.match(await page.locator('#panel').textContent(),/3 contributors/);
 await page.locator('#view-contributors').click();await idle();assert.equal(await rightCard().locator('[data-linked-member="true"]').count(),3);
 assert.match(await rightCard().locator('.linked-detail').textContent(),/weight 0/);
 await rightCard().locator('[data-linked-inspect]').click();await idle();assert.match(await page.locator('#contribution-evidence').textContent(),/Source value 1 · weight 0/);
 // The sum's field weight came from a copied pixel attribute; follow that distinct read.
 await page.locator('.receipt-read[data-read-site="point_value"]').getByRole('button').click();await idle();
 assert.equal(await rightCard().locator('circle').count(),9);assert.match(await rightCard().locator('[data-capture-label]').textContent(),/Captured dependency/);
 assert.match(await rightCard().locator('.linked-detail').textContent(),/Value 0 · Read 0/);
 await page.getByRole('button',{name:'Back to read origin',exact:true}).click();await idle();
 await page.getByRole('button',{name:'Back to measurement',exact:true}).click();await idle();
 await page.getByRole('button',{name:'Back to contribution',exact:true}).click();await idle();
 assert.equal(await rightCard().locator('[data-linked-occurrence]').inputValue(),selectedContribution);
 assert.equal(await rightCard().locator('circle').first().getAttribute('cx'),cameraBefore);
 assert.match(await page.locator('#contribution-evidence').textContent(),/weight 0/);
 await page.locator('#linked-views').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(output,'radon-weight-evidence.png'),fullPage:true});
 await page.setViewportSize({width:320,height:950});await page.getByRole('button',{name:'Follow weight read · 0',exact:true}).focus();await page.keyboard.press('Enter');await idle();
 assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.locator('#linked-views').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(output,'radon-weight-phone.png'),fullPage:true});
 assert.equal(await(await page.request.get(origin+'/api/export')).text(),radonBefore);
 await page.locator('#close-linked').click();await page.locator('[data-mode="objects"]').click();
 // Change one declaration. Every unbound use reevaluates; the current case stays visible until Apply.
 await page.setViewportSize({width:1250,height:950});await select('Radon recovered');
 const primeRows=(await state()).objects.find(o=>o.name==='Radon recovered').rows;
 await page.locator('[data-mode="points"]').click();
 await page.locator('#cases').click();await page.getByLabel('Value of p',{exact:true}).fill('4');
 await page.locator('#preview').click();await idle();assert.match(await page.locator('#case-report').textContent(),/0 failed/);
 assert.equal(await page.locator('#occurrence-label').isVisible(),false,'Applied occurrence references must not appear on a proposed case');
 assert.deepEqual((await state()).parameters,{p:'3'});assert.match(await page.locator('#scope').textContent(),/Preview case · p = 4/);
 await page.locator('#cancel').click();await idle();assert.deepEqual((await state()).objects.find(o=>o.name==='Radon recovered').rows,primeRows);
 assert.equal(await page.locator('#occurrence-label').isVisible(),true);
 await page.locator('[data-mode="objects"]').click();
 await page.locator('#cases').click();await page.getByLabel('Value of p',{exact:true}).fill('4');
 // Inspect a source while the case is parked; the proposed binding returns unchanged.
 await select('Radon image');await page.locator('#resume-draft').click();assert.equal(await page.getByLabel('Value of p',{exact:true}).inputValue(),'4');
 await apply();assert.deepEqual((await state()).parameters,{p:'4'});assert.equal(await page.locator('#replay').isVisible(),false);
 const composite=(await state()).objects;
 assert.equal(composite.find(o=>o.name==='Radon recovered').rows[0].fields.recovered,'-1');
 assert.equal(composite.find(o=>o.name==='Radon division check').rows[0].fields.remainder,'0');
 assert.equal(composite.find(o=>o.name==='Radon image').rows[0].fields.value,'0');
 await page.locator('#labels').selectOption('recovered');
 await page.screenshot({path:path.join(output,'parameter-case-four.png'),fullPage:true});
 await page.locator('#undo').click();await idle();assert.deepEqual((await state()).objects.find(o=>o.name==='Radon recovered').rows,primeRows);assert.equal(await page.locator('#replay').isVisible(),false);
 await page.locator('#redo').click();await idle();assert.deepEqual((await state()).parameters,{p:'4'});
 // The declaration survives a case change; no old comparison verdict does.
 await select('Radon recovered');await tool('compare');
 assert.equal(await page.locator('#comparison-left-value').inputValue(),'recovered');
 assert.equal(await page.locator('#comparison-right').inputValue(),'Radon image');
 assert.equal(await page.locator('#comparison-results').textContent(),'');
 const beforeComparison=await(await page.request.get(origin+'/api/export')).text();
 await page.locator('#check-comparison').click();await idle();
 assert.match(await page.locator('#comparison-status').textContent(),/Finite equality fails/);
 assert.match(await page.locator('#comparison-key option').first().textContent(),/\(0, 0\).*residual -1/);
 assert.match(await page.locator('#comparison-witness').textContent(),/Left recovered: -1 · Right value: 0/);
 await page.locator('#view-comparison').click();await idle();
 assert.match(await leftCard().locator('.linked-detail').textContent(),/recovered -1/);
 await leftCard().locator('summary').click();await page.getByRole('button',{name:'Pan left view right',exact:true}).focus();await page.keyboard.press('Enter');
 const comparisonCamera=await leftCard().locator('circle').first().getAttribute('cx'),comparisonKey=await page.locator('#comparison-key').inputValue();
 await page.getByRole('button',{name:'Inspect left occurrence',exact:true}).click();await idle();
 assert.match(await page.locator('.comparison-context').textContent(),/recovered = -1/);
 assert.match(await page.locator('#panel').textContent(),/"value": "56"/);
 await page.locator('#view-contributors').click();await idle();
 await rightCard().locator('[data-linked-inspect]').click();await idle();
 await page.getByRole('button',{name:/Follow weight read/}).first().click();await idle();
 await page.getByRole('button',{name:'Back to contribution',exact:true}).click();await idle();
 await page.getByRole('button',{name:'Back to measurement',exact:true}).click();await idle();
 await page.getByRole('button',{name:'Back to comparison',exact:true}).click();await idle();
 assert.equal(await page.locator('#comparison-key').inputValue(),comparisonKey);
 assert.equal(await leftCard().locator('circle').first().getAttribute('cx'),comparisonCamera);
 assert.equal(await(await page.request.get(origin+'/api/export')).text(),beforeComparison);
 await page.locator('#linked-views').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(output,'comparison-radon.png'),fullPage:true});
 await page.locator('#close-linked').click();
 await select('Radon backprojection');await page.locator('[data-mode="points"]').click();await page.locator('#occurrence').selectOption((await state()).objects.find(o=>o.name==='Radon backprojection').rows[0].ref[1]);await idle();
 assert.match(await page.locator('#panel').textContent(),/5 contributors/);await page.locator('#view-contributors').click();await idle();assert.equal(await rightCard().locator('[data-linked-member="true"]').count(),5);
 await page.locator('#close-linked').click();await page.locator('[data-mode="objects"]').click();
 // Transfer the same parameter control to lattice growth, with a retained zero row.
 await declare('n','2');const parameterN={parameter:'n'};
 await tool('grid',true);await page.locator('#result-name').fill('Growing square');await page.locator('#grid-shape').fill('n, n');await page.locator('#edit-axis-lengths').click();
 for(const axis of [1,2])await expression(page.getByRole('group',{name:`Axis ${axis} length`,exact:true}),op('+',parameterN,n(1)));await apply();
 await tool('lens');await page.locator('#result-name').fill('Growing triangle');await expression(cards().nth(0),op('<',op('+',f('i'),f('j')),parameterN));await apply();
 await tool('measure');await page.locator('#result-name').fill('Triangle rows');await retain('i');await apply();assert.deepEqual(await values('Triangle rows'),['2','1','0']);
 await page.locator('#cases').click();await page.getByLabel('Value of n',{exact:true}).fill('4');await apply();assert.deepEqual(await values('Triangle rows'),['4','3','2','1','0']);
 await page.setViewportSize({width:320,height:950});await page.locator('#cases').click();await page.getByLabel('Value of n',{exact:true}).fill('0');await page.locator('#preview').focus();await page.keyboard.press('Enter');await idle();
 assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.screenshot({path:path.join(output,'parameter-case-phone.png'),fullPage:true});
 await page.locator('#apply').click();await idle();assert.deepEqual(await values('Triangle rows'),['0']);
 // The same comparison checks a lattice formula, retaining the zero measurement.
 await tool('grid',true);await page.locator('#result-name').fill('Triangle formula');await page.locator('#grid-shape').fill('1');await page.locator('#grid-axes').fill('i');await page.locator('#grid-axes').press('Tab');await page.locator('#edit-axis-lengths').click();
 await expression(page.getByRole('group',{name:'Axis 1 length',exact:true}),op('+',parameterN,n(1)));
 await expression(cards().nth(0),op('-',parameterN,f('i')));await apply();
 await compare('Triangle rows',['i'],'Triangle formula',['i'],'Triangle formula',['i']);
 assert.match(await page.locator('#comparison-status').textContent(),/Finite equality holds. 1 equal/);
 await page.getByRole('button',{name:'Inspect left occurrence',exact:true}).click();await idle();assert.match(await page.locator('#panel').textContent(),/0 contributors/);
 await page.getByRole('button',{name:'Back to comparison',exact:true}).click();await idle();
 await page.locator('#cases').click();await page.getByLabel('Value of n',{exact:true}).fill('4');await apply();
 await select('Triangle rows');await tool('compare');await page.locator('#check-comparison').click();await idle();
 assert.match(await page.locator('#comparison-status').textContent(),/Finite equality holds. 5 equal/);
 const cameraExport=await(await page.request.get(origin+'/api/export')).text();
 await page.locator('#view-controls summary').tap();const canvasBeforePan=await page.locator('#marks circle').first().getAttribute('cx');
 await page.getByRole('button',{name:'Pan main view left',exact:true}).tap();
 assert.notEqual(await page.locator('#marks circle').first().getAttribute('cx'),canvasBeforePan);
 await page.locator('[data-workspace-jump="panel"]').tap();assert.equal(await page.evaluate(()=>document.activeElement.id),'panel');
 await page.locator('[data-workspace-jump="scene"]').tap();assert.equal(await page.evaluate(()=>document.activeElement.id),'scene');
 for(const control of await page.locator('.workspace-jumps a,#view-controls button').all()){
   const size=await control.boundingBox();assert.ok(size.width>=44&&size.height>=44,'Camera and navigation targets reach the 44px project goal');
 }
 assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 assert.equal(await(await page.request.get(origin+'/api/export')).text(),cameraExport);
 await page.locator('[data-workspace-jump="panel"]').tap();await page.screenshot({path:path.join(output,'comparison-phone.png'),fullPage:true});
 await page.locator('#cases').click();await page.getByLabel('Value of n',{exact:true}).fill('0');await apply();
 // Removing a zero-valued expected item from both sides cannot establish equality.
 await tool('grid',true);await page.locator('#result-name').fill('Comparison domain');await page.locator('#grid-shape').fill('3');await page.locator('#grid-axes').fill('i');await page.locator('#grid-axes').press('Tab');await expression(cards().nth(0),n(0));await apply();
 await tool('lens');await page.locator('#result-name').fill('Comparison retained');await expression(cards().nth(0),op('≠',f('i'),n(1)));await apply();
 await tool('select');await page.locator('#result-name').fill('Comparison truncated');await apply();
 await compare('Comparison truncated',['i'],'Comparison truncated',['i'],'Comparison domain',['i']);
 assert.match(await page.locator('#comparison-status').textContent(),/missing left 1, right 1/);
 await page.locator('#comparison-filter').selectOption('missing');assert.match(await page.locator('#comparison-witness').textContent(),/Left value: absent · Right value: absent/);
 await page.locator('#view-comparison').click();await idle();assert.equal(await leftCard().locator('[data-linked-member="true"]').count(),0);assert.equal(await rightCard().locator('[data-linked-member="true"]').count(),0);
 await page.getByRole('button',{name:'Inspect expected key',exact:true}).click();await idle();assert.match(await page.locator('#panel').textContent(),/"i": "1"/);
 await page.getByRole('button',{name:'Back to comparison',exact:true}).click();await idle();await page.locator('#close-linked').click();
 await compare('Comparison domain',['i'],'Comparison domain',['i'],'Comparison truncated',['i']);
 assert.match(await page.locator('#comparison-status').textContent(),/outside left 1, right 1/);
 await compare('Comparison domain',['value'],'Comparison domain',['i'],'Comparison domain',['i']);
 assert.match(await page.locator('#comparison-status').textContent(),/Could not compare: Duplicate key/);
 // Read-only comparison also leaves a parked mathematical draft intact.
 await select('Triangle rows');await tool('field');await page.locator('#result-name').fill('Still drafting');const parkedComparisonDraft=JSON.parse(await page.locator('#declaration').textContent());
 await compare('Triangle rows',['i'],'Triangle formula',['i'],'Triangle formula',['i']);
 await page.locator('#resume-draft').click();assert.deepEqual(JSON.parse(await page.locator('#declaration').textContent()),parkedComparisonDraft);await page.locator('#cancel').click();await idle();
 const comparisonChecks={primeEquality:true,compositeCounterexample:true,selectedFields:true,retainedCaseChoices:true,nestedEvidenceReturn:true,latticeFormulaAndZero:true,missingBoth:true,outsideDomain:true,duplicateRejection:true,parkedDraft:true,cameraButtons:true,phoneJumps:true,unchangedCapture:true};
 // Invalid arithmetic blocks dependents, never erases an independent count or masquerades as zero.
 await select('A');await tool('field');await page.locator('#result-name').fill('Parameter residue');await page.locator('#field-name').fill('residue');await expression(cards().nth(0),op('%',f('value'),p));await apply();
 await page.locator('#cases').click();await page.getByLabel('Value of p',{exact:true}).fill('0');await page.locator('#preview').click();await idle();assert.match(await page.locator('#case-report').textContent(),/Parameter residue:.*Division or remainder by zero/i);
 await page.locator('#apply').click();await idle();assert.equal((await state()).objects.find(o=>o.name==='Parameter residue').status,'failed');assert.deepEqual(await values('Triangle rows'),['0']);
 await page.locator('#undo').click();await idle();assert.equal((await state()).objects.find(o=>o.name==='Parameter residue').status,'ready');
 const caseChecks={declaredOnce:true,parameterExpressions:true,formulaExtents:true,primeComposite:true,exactButWrong:true,casePreviewCancel:true,parkedCase:true,capturedCaseUndo:true,caseEvidence:true,replayWithoutRequests:true,latticeTransfer:true,failedCaseIsolation:true,keyboardAndPhone:true};
 // A weight expression may transform its read: 2*read - 4 gives [-4,0,6].
 await integers('Weight driver','0, 2, 5');await integers('Weighted items','99, 99, 99');await tool('measure');await page.locator('#result-name').fill('Signed total');await page.locator('#reducer').selectOption('sum');
 await expression(cards().nth(0),op('-',op('*',n(2),read('Weight driver',f('index'),f('index'))),n(4)));await apply();assert.deepEqual(await values('Signed total'),['2']);
 await page.locator('[data-mode="points"]').click();await page.locator('#occurrence').selectOption((await state()).objects.find(o=>o.name==='Signed total').rows[0].ref[1]);await idle();await page.locator('#view-contributors').click();await idle();
 await rightCard().locator('[data-linked-occurrence]').selectOption({index:1});await rightCard().locator('[data-linked-inspect]').click();await idle();
 assert.match(await page.locator('#contribution-evidence').textContent(),/Source value 99 · weight 0/);await page.getByRole('button',{name:'Follow weight read · 2',exact:true}).click();await idle();
 assert.match(await leftCard().locator('.linked-detail').textContent(),/Weight 0/);assert.match(await rightCard().locator('.linked-detail').textContent(),/Read 2/);
 const weightedChecks={compositeKeyEditing:true,tupleDraftAndUndo:true,orderedKeyFailure:true,radonReconstruction:true,exactDivision:true,measurementDrivenUndo:true,weightReadNavigation:true,zeroWeightSource:true,returnSelectionAndCamera:true,keyboardAndPhone:true,unchangedCapture:true,transformedReadWeight:true};
 // Ordered accumulation: measured layer sizes become offsets without a pair domain.
 await page.setViewportSize({width:1250,height:950});await page.locator('#close-linked').click();await page.locator('[data-mode="objects"]').click();
 async function memberOrder(fields){
   while(await page.locator('#rank-order .key-chips button').count())await page.locator('#rank-order .key-chips button').first().click();
   for(const field of fields)await page.locator('#rank-order [data-group-add]').selectOption(field);
 }
 async function prefix(name,source,order,key,weight=f('value')){
   await select(source);await tool('measure');await page.locator('#result-name').fill(name);await page.locator('#reducer').selectOption('prefix_sum');
   await memberOrder(order);await page.locator('#rank-key').selectOption(key);await expression(cards().nth(0),weight);await apply();
 }
 await integers('Young heights','5, 3, 2, 0');
 await tool('grid',true);await page.locator('#result-name').fill('Young domain');await page.locator('#grid-shape').fill('4, 5');await expression(cards().nth(0),n(1));await apply();
 await tool('lens');await page.locator('#result-name').fill('Young diagram');await expression(cards().nth(0),op('<',f('j'),read('Young heights',f('i'),f('key'))));await apply();
 await tool('measure');await page.locator('#result-name').fill('Young layers');await retain('j');await apply();assert.deepEqual(await values('Young layers'),['3','3','2','1','1']);
 await tool('measure');await page.locator('#result-name').fill('Layer offsets');await page.locator('#reducer').selectOption('prefix_sum');
 assert.match(await page.locator('#measurement-meaning').textContent(),/current item is excluded/);
 await memberOrder(['value']);await page.locator('#rank-key').selectOption('j');
 const prefixRevision=(await state()).revision;
 await page.locator('#preview').click();await idle();assert.equal(await page.locator('#apply').isEnabled(),false);assert.match(await page.locator('#draft-status').textContent(),/ties within a group/);assert.equal((await state()).revision,prefixRevision);
 const prefixDraft=JSON.parse(await page.locator('#declaration').textContent());await select('Young heights');await page.locator('#resume-draft').click();assert.deepEqual(JSON.parse(await page.locator('#declaration').textContent()),prefixDraft);
 await memberOrder(['j']);await apply();assert.deepEqual(await values('Layer offsets'),['0','3','6','8','9']);
 const offsetRows=(await state()).objects.find(o=>o.name==='Layer offsets').rows;
 await page.locator('[data-mode="points"]').click();await page.locator('#occurrence').selectOption(offsetRows[0].ref[1]);await idle();
 assert.match(await page.locator('#panel').textContent(),/prefix sum · 0 contributors/);await page.locator('#view-contributors').click();await idle();
 assert.equal(await rightCard().locator('circle').count(),5);assert.equal(await rightCard().locator('[data-linked-member="true"]').count(),0);await page.locator('#close-linked').click();
 await page.locator('#occurrence').selectOption(offsetRows[3].ref[1]);await idle();await page.locator('#view-contributors').click();await idle();
 assert.equal(await rightCard().locator('[data-linked-member="true"]').count(),3);
 await rightCard().locator('[data-linked-occurrence]').selectOption({index:2});await page.getByRole('button',{name:'Zoom in right view',exact:true}).click();
 const offsetSelection=await rightCard().locator('[data-linked-occurrence]').inputValue(),offsetCamera=await rightCard().locator('circle').first().getAttribute('cx'),offsetExport=await(await page.request.get(origin+'/api/export')).text();
 await rightCard().locator('[data-linked-inspect]').click();await idle();assert.match(await page.locator('#contribution-evidence').textContent(),/Source value 2 · weight 2/);
 await page.locator('#view-contributors').click();await idle();assert.equal(await rightCard().locator('[data-linked-member="true"]').count(),2);
 await rightCard().locator('[data-linked-inspect]').click();await idle();await page.getByRole('button',{name:'Back to measurement',exact:true}).click();await idle();await page.getByRole('button',{name:'Back to measurement',exact:true}).click();await idle();
 assert.equal(await rightCard().locator('[data-linked-occurrence]').inputValue(),offsetSelection);assert.equal(await rightCard().locator('circle').first().getAttribute('cx'),offsetCamera);
 assert.equal(await(await page.request.get(origin+'/api/export')).text(),offsetExport);
 await page.locator('#linked-views').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(output,'prefix-layer-evidence.png'),fullPage:true});
 await page.setViewportSize({width:320,height:950});await rightCard().locator('[data-linked-inspect]').focus();await page.keyboard.press('Enter');await idle();
 assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.screenshot({path:path.join(output,'prefix-layer-phone.png'),fullPage:true});
 await page.locator('#close-linked').click();await page.locator('[data-mode="objects"]').click();await page.setViewportSize({width:1250,height:950});
 await select('Young diagram');await tool('select');await page.locator('#result-name').fill('Young cells');await apply();
 await tool('place');await expression(cards().nth(0),f('i'));await expression(cards().nth(1),f('j'));await apply();
 const beforePacking=(await state()).objects.find(o=>o.name==='Young cells').rows;
 await tool('place');await expression(cards().nth(0),op('+',f('i'),read('Layer offsets',f('j'),f('j'))));await expression(cards().nth(1),n(0));await apply();
 const packedLayers=(await state()).objects.find(o=>o.name==='Young cells').rows;
 assert.deepEqual(packedLayers.map(r=>r.position[0]).sort((a,b)=>a-b),Array.from({length:10},(_,i)=>i));assert.deepEqual(packedLayers.map(r=>r.ref[1]),beforePacking.map(r=>r.ref[1]));
 await page.locator('#undo').click();await idle();assert.deepEqual((await state()).objects.find(o=>o.name==='Young cells').rows,beforePacking);await page.locator('#redo').click();await idle();assert.deepEqual((await state()).objects.find(o=>o.name==='Young cells').rows,packedLayers);
 await page.locator('#labels').selectOption('j');await page.screenshot({path:path.join(output,'prefix-packed-layers.png'),fullPage:true});
 await integers('Expected layer offsets','0, 3, 6, 8, 9');await compare('Layer offsets',['j'],'Expected layer offsets',['key'],'Expected layer offsets',['key']);assert.match(await page.locator('#comparison-status').textContent(),/Finite equality holds. 5 equal/);
 // Transfer to quotient columns: the zero-length column is a real contributor.
 await prefix('Quotient offsets','Quotient counts',['i'],'i');assert.deepEqual(await values('Quotient offsets'),['0','0','1','4','8','14','21']);
 await page.locator('[data-mode="points"]').click();await page.locator('#occurrence').selectOption((await state()).objects.find(o=>o.name==='Quotient offsets').rows[1].ref[1]);await idle();
 assert.match(await page.locator('#panel').textContent(),/prefix sum · 1 contributors/);await page.locator('#view-contributors').click();await idle();await rightCard().locator('[data-linked-inspect]').click();await idle();assert.match(await page.locator('#contribution-evidence').textContent(),/Source value 0 · weight 0/);assert.match(await page.locator('#panel').textContent(),/count · 0 contributors/);
 await page.locator('#close-linked').click();await page.locator('[data-mode="objects"]').click();await select('Quotient hits');await tool('measure');await page.locator('#result-name').fill('Quotient row ranks');await page.locator('#reducer').selectOption('rank');await retain('i');await memberOrder(['j']);await apply();
 await select('Quotient hits');await tool('select');await page.locator('#result-name').fill('Quotient packed cells');await apply();await tool('place');
 await expression(cards().nth(0),op('+',read('Quotient offsets',f('i'),f('i')),read('Quotient row ranks',f('key'),f('key'))));await expression(cards().nth(1),n(0));await apply();
 assert.deepEqual((await state()).objects.find(o=>o.name==='Quotient packed cells').rows.map(r=>r.position[0]).sort((a,b)=>a-b),Array.from({length:30},(_,i)=>i));
 // A general accumulation can contain negative and zero weights; it need not pack lengths.
 await prefix('Signed prefixes','Weighted items',['key'],'key',op('-',op('*',n(2),read('Weight driver',f('key'),f('key'))),n(4)));assert.deepEqual(await values('Signed prefixes'),['0','-4','-4']);
 await page.locator('[data-mode="points"]').click();await page.locator('#occurrence').selectOption((await state()).objects.find(o=>o.name==='Signed prefixes').rows[2].ref[1]);await idle();await page.locator('#view-contributors').click();await idle();
 await rightCard().locator('[data-linked-occurrence]').selectOption({index:1});await rightCard().locator('[data-linked-inspect]').click();await idle();assert.match(await page.locator('#contribution-evidence').textContent(),/Source value 99 · weight 0/);
 await page.getByRole('button',{name:'Follow weight read · 2',exact:true}).click();await idle();assert.match(await rightCard().locator('.linked-detail').textContent(),/Read 2/);
 const prefixChecks={youngLayers:true,exclusiveZero:true,strictOrderFailure:true,parkedDraft:true,measuredContributors:true,nestedReturn:true,unchangedCapture:true,phoneAndKeyboard:true,drivenPackingUndo:true,keyedComparison:true,quotientTransfer:true,zeroWeightContributor:true,signedWeightReads:true};
 assert.deepEqual(errors,[]);fs.writeFileSync(path.join(output,'report.json'),JSON.stringify({browser:browser.version(),errors,layouts,authoring,coverage:coverageChecks,linked:linkedChecks,weighted:weightedChecks,cases:caseChecks,comparison:comparisonChecks,prefix:prefixChecks,objects:(await state()).objects.length,checks:['two constructions through controls','sum/modular/coverage group selection','zero-group lens retains universe','tied order and explicit tie breaker','compact formula/subtree edit/local undo','phone formula edits and captured group taps','recoverable drafts across relation/measurement inspections','current local preview status and keyboard focus','independent coverage keys and guarded field assignment','coverage witnesses and absent groups','assigned fields drive reversible placement','preview/cancel/failure','keyed rank placement and inspection','zero contributors','captured undo/redo/save/open','exact integer transport','hold/drag/cancel/multi-touch','mode/context and keyboard menus','same-origin mutation guard']},null,2));
 console.log('Construction studio browser checks passed.');
 }finally{await browser.close();server?.kill()}
})().catch(e=>{server?.kill();console.error(e);process.exitCode=1});
