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
   const desired='field'in spec?'Field':'integer'in spec?'Number':spec.op?'Operation':'Keyed read';
   if(await type.inputValue()!==desired)await type.selectOption(desired);
   if(desired==='Field')await sheet.getByLabel('Field',{exact:true}).selectOption(spec.field);
   else if(desired==='Number')await sheet.getByLabel('Exact integer',{exact:true}).fill(String(spec.integer));
   else if(desired==='Operation'){
     await sheet.getByLabel('Operation',{exact:true}).selectOption(spec.op);
     await expression(card,spec.args[0],[...path,'args',0]);
     await expression(card,spec.args[1],[...path,'args',1]);
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
 await page.locator('#labels').selectOption('total');
 await page.screenshot({path:path.join(output,'sum-stacks.png'),fullPage:true});

 // The same group selector browses sum fibers, keeping selection outside history.
 await page.locator('[data-mode="groups"]').click();await page.locator('#panel > .field-keys [data-group-add]').selectOption('total');
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
 await select('Sums');await page.locator('#panel > .field-keys [data-group-add]').selectOption('total');await page.locator('#browse-groups').click();await idle();await page.locator('#group-choice').selectOption('3');
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
 await page.locator('[data-mode="groups"]').click();await page.locator('#panel > .field-keys [data-group-add]').selectOption('i');await page.locator('#browse-groups').click();await idle();
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
 await page.locator('[data-mode="groups"]').click();await page.locator('#panel > .field-keys [data-group-add]').selectOption('i');await page.locator('#browse-groups').click();await idle();
 assert.deepEqual(await page.locator('#group-choice option').allTextContents(),['i = 0 · 0 of 3 incident','i = 1 · 1 of 3 incident','i = 2 · 2 of 3 incident']);
 assert.match(await page.locator('#group-summary').textContent(),/0 incident occurrences · 3 occurrences/);
 assert.equal(await page.locator('[data-group-member="true"]').count(),3);
 await tool('group_lens');await page.locator('#result-name').fill('Uncovered group');await apply();
 const uncovered=(await state()).objects.find(o=>o.name==='Uncovered group');assert.equal(uncovered.rows.length,9);assert.equal(uncovered.rows.filter(r=>r.match).length,0);
 await page.locator('[data-mode="groups"]').click();await page.locator('#panel > .field-keys [data-group-add]').selectOption('i');await page.locator('#browse-groups').click();await idle();assert.equal(await page.locator('#group-choice option').count(),3);

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
 await page.locator('[data-mode="groups"]').click();await page.locator('#panel > .field-keys [data-group-add]').selectOption('total');await page.locator('#browse-groups').click();await idle();
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
 await select('Diagonal');await page.locator('[data-mode="groups"]').tap();await page.locator('#panel > .field-keys [data-group-add]').selectOption('i');await page.locator('#browse-groups').tap();await idle();
 const phoneRevision=(await state()).revision;await page.locator('#canvas').scrollIntoViewIfNeeded();const member=await page.locator('#marks circle').nth(8).boundingBox();
 await page.touchscreen.tap(member.x+member.width/2,member.y+member.height/2);
 assert.equal(await page.locator('#group-choice').inputValue(),'2');assert.equal(await page.locator('[data-group-member="true"]').count(),3);
 await page.locator('#options').tap();assert.deepEqual(await page.locator('#menu-actions button').allTextContents(),['Choose group keys','Create a group lens','Measure all groups']);await page.locator('#close-menu').tap();
 assert.equal((await state()).revision,phoneRevision);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 await page.screenshot({path:path.join(output,'phone-group.png'),fullPage:true});
 assert.deepEqual(errors,[]);fs.writeFileSync(path.join(output,'report.json'),JSON.stringify({browser:browser.version(),errors,layouts,authoring,objects:(await state()).objects.length,checks:['two constructions through controls','sum/modular/coverage group selection','zero-group lens retains universe','tied order and explicit tie breaker','compact formula/subtree edit/local undo','phone formula edits and captured group taps','recoverable drafts across relation/measurement inspections','current local preview status and keyboard focus','preview/cancel/failure','keyed rank placement and inspection','zero contributors','captured undo/redo/save/open','exact integer transport','hold/drag/cancel/multi-touch','mode/context and keyboard menus','same-origin mutation guard']},null,2));
 console.log('Construction studio browser checks passed.');
 }finally{await browser.close();server?.kill()}
})().catch(e=>{server?.kill();console.error(e);process.exitCode=1});
