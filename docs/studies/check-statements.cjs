// Optional real-browser gate for finite evidence -> conditional statement.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {spawn}=require('node:child_process');
const {chromium}=require(process.env.KALEION_PLAYWRIGHT_MODULE||'playwright');
const output=path.resolve(process.argv[3]||'build/statements-check');fs.mkdirSync(output,{recursive:true});
let origin=process.argv[2],server;
(async()=>{
 if(!origin){server=spawn(process.env.KALEION_PYTHON||'.venv/bin/python3',['-m','examples.studio','--port','0'],{stdio:['ignore','pipe','inherit']});origin=await new Promise((resolve,reject)=>{server.stdout.on('data',d=>{const m=String(d).match(/http:\/\/127\.0\.0\.1:\d+/);if(m)resolve(m[0])});server.once('error',reject)});}
 const browser=await chromium.launch(JSON.parse(process.env.KALEION_BROWSER_OPTIONS||'{}'));
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1050},hasTouch:true,reducedMotion:'reduce'}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  const idle=()=>page.waitForFunction(()=>!document.getElementById('options').disabled);
  const math=async()=>await(await page.request.get(origin+'/api/export')).text();
  const close=async()=>{if(await page.locator('#panel').isVisible())await page.locator('#close-panel').click()};
  async function keys(label,fields){const box=page.getByRole('group',{name:label,exact:true});while(await box.getByRole('button').count())await box.getByRole('button').first().click();for(const k of fields)await box.getByLabel(`Add ${label.toLowerCase()}`,{exact:true}).selectOption(k)}
  async function compare(left='Moving cover',right='Independent ones',fields=['i','j']){
    await close();await page.locator('#objects').selectOption(left);await idle();await page.locator('#options').click();await page.locator('#advanced-tools summary').click();await page.locator('[data-action="compare"]').click();
    await keys('Left key fields',fields);await page.locator('#comparison-right').selectOption(right);await keys('Right key fields',fields);await page.locator('#comparison-expected').selectOption(right);await keys('Expected key fields',fields);await page.locator('#check-comparison').click();await idle();
  }
  async function expand(){await page.locator('#expand-statement').focus();await page.keyboard.press('Enter');await idle()}
  async function choose(){
    if(await page.locator('#construction-statement').getAttribute('open')===null)await page.getByText('Expand construction',{exact:true}).click();
    await page.locator('#construction-statement input[value="a"]').check();await page.locator('#construction-statement input[value="b"]').check();
    await page.locator('#statement-assumptions').fill('a > 1 and b > 1');await page.getByRole('button',{name:'Assume two parameters are coprime',exact:true}).click();
  }
  async function save(name){const pending=page.waitForEvent('download');await page.locator('#save-comparison').click();const d=await pending,file=path.join(output,name);await d.saveAs(file);await idle();return file}
  await page.goto(origin);await page.waitForFunction(()=>!document.getElementById('add').disabled);
  await page.locator('#file').setInputFiles('examples/canvases/13_quotient_equality.json');await idle();
  const original=await math();await compare();await choose();await expand();
  assert.match(await page.locator('#statement-status').innerText(),/No proof attempted/);
  assert.match(await page.locator('#statement-result').innerText(),/gcd\(a, b\)/);
  assert.match(await page.locator('#statement-result pre').first().innerText(),/\[.*≤.*\].*\+.*\[/);
  assert.match(await page.locator('#statement-result').innerText(),/k\[0\].*b − 1/);
  assert.equal(await math(),original);
  const saved=await save('quotient-statement.json'),record=JSON.parse(fs.readFileSync(saved,'utf8'));
  assert.equal(record.comparison.version,2);assert.deepEqual(record.comparison.expansion,{vary:['a','b'],assumptions:'a > 1 and b > 1',coprime:[['a','b']]});assert.equal(record.comparison.proof,undefined);assert.equal(record.workspace,original);
  await page.locator('#statement-result > pre').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(output,'expanded-quotient.png')});
  // Invalid formula cannot silently replace the accepted statement.
  await page.locator('#statement-assumptions').fill('abs(a) > 1');await expand();assert.match(await page.locator('#statement-status').innerText(),/Could not expand/);assert.equal(await page.locator('#statement-result pre').count(),0);assert.equal(await math(),original);
  await page.getByRole('button',{name:'Keep only the finite question',exact:true}).click();
  const finite=await save('finite-only.json');assert.equal(JSON.parse(fs.readFileSync(finite,'utf8')).comparison.version,1);
  await page.locator('#file').setInputFiles(saved);await idle();assert.equal(await page.locator('#comparison-status').getAttribute('data-phase'),'passed');
  assert.equal(await page.locator('#statement-assumptions').inputValue(),'a > 1 and b > 1');assert.equal(await page.locator('#statement-result pre').count(),0);await expand();assert.match(await page.locator('#statement-status').innerText(),/No proof attempted/);assert.equal(await math(),original);
  // A finite failure that violates coprimality is not a counterexample to it.
  await close();await page.locator('#cases').click();await page.getByLabel('Value of a',{exact:true}).fill('6');await page.getByLabel('Value of b',{exact:true}).fill('4');await page.locator('#preview').click();await idle();await page.locator('#apply').click();await idle();await compare();await choose();await expand();
  assert.equal(await page.locator('#comparison-status').getAttribute('data-phase'),'failed');assert.match(await page.locator('#statement-result').innerText(),/gcd\(a, b\).*not satisfied/);assert.match(await page.locator('#statement-result').innerText(),/does not refute/);
  await page.getByRole('button',{name:'Inspect left occurrence',exact:true}).click();await idle();await page.getByRole('button',{name:'Back to comparison',exact:true}).click();await idle();assert.match(await page.locator('#statement-result').innerText(),/does not refute/);
  await page.setViewportSize({width:360,height:900});await page.locator('#statement-result > pre').scrollIntoViewIfNeeded();assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.screenshot({path:path.join(output,'phone-statement.png')});
  await page.setViewportSize({width:1440,height:1050});
  // The same controls handle total sums, then the 3D ownership construction.
  await compare('Counted area','Rectangle area',['key']);await choose();await expand();assert.match(await page.locator('#statement-result pre').first().innerText(),/Σ/);
  await page.locator('#file').setInputFiles('examples/canvases/03_cell_coverage.json');await idle();await compare('Cell owners','One per cell',['i','j','k']);
  await page.getByText('Expand construction',{exact:true}).click();for(const name of ['a','b','c'])await page.locator(`#construction-statement input[value="${name}"]`).check();await page.locator('#statement-assumptions').fill('a > 1 and b > 1 and c > 1');await expand();
  assert.match(await page.locator('#statement-status').innerText(),/No proof attempted/);assert.match(await page.locator('#statement-result pre').first().innerText(),/k\[2\]/);
  assert.deepEqual(errors,[]);fs.writeFileSync(path.join(output,'report.json'),JSON.stringify({browser:browser.version(),tasks:'quotient indicators, parameter scopes, hypotheses, coprimality, total sums, 3D transfer, invalid formula, exact save/reopen, finite evidence return, phone width and keyboard',errors},null,2));
  console.log('Algebraic statement browser checks passed.');
 }finally{await browser.close();server?.kill()}
})().catch(error=>{console.error(error);server?.kill();process.exitCode=1});
