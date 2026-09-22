import {actions, labels} from './context.js';

const $ = id => document.getElementById(id);
const el = (tag, text, attrs={}) => {
  const node=document.createElement(tag); if(text!==undefined)node.textContent=text;
  for(const [key,value] of Object.entries(attrs))node.setAttribute(key,value);
  return node;
};
const field = name => ({field:name}), number = n => ({integer:String(n)});
const operation = (op,a,b) => ({op,args:[a,b]});
let state={revision:0,objects:[],undo:false,redo:false}, active=null, mode='objects';
let selectedPoint=null, preview=null, busy=false, gesture=null, held=false;
let camera={x:0,y:0,zoom:1}, dots=[], getCommand=null, editorRevision=0, labelField='value';
const object = () => state.objects.find(o=>o.name===active);
const displayed = () => preview?.objects.find(o=>o.name===preview.name) || object();
function status(text, error=false){$('status').textContent=text;$('status').classList.toggle('error',error)}
function setBusy(value){
  busy=value;
  document.querySelectorAll('button,input,select,fieldset').forEach(n=>n.disabled=value);
  if(!value){$('undo').disabled=!state.undo;$('redo').disabled=!state.redo;const a=$('apply');if(a)a.disabled=!preview}
}
async function request(path,body={}){
  const response=await fetch('/api/'+path,{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({revision:state.revision,...body})});
  const data=await response.json();if(!response.ok)throw Error(data.error);return data;
}
async function run(fn){if(busy)return;setBusy(true);try{await fn()}catch(e){status(e.message,true)}finally{setBusy(false)}}
function adopt(next){
  state=next;preview=null;selectedPoint=null;
  if(next.active)active=next.active;
  if(!state.objects.some(o=>o.name===active))active=state.objects.at(-1)?.name || null;
  camera={x:0,y:0,zoom:1};render();
}
function render(){
  $('objects').replaceChildren(...state.objects.map(o=>{
    const button=el('button',o.name,{'aria-pressed':String(o.name===active),'data-object':o.name});
    button.append(el('small',o.status==='ready'?o.kind:o.error));
    button.onclick=()=>{if(busy)return;active=o.name;selectedPoint=null;preview=null;getCommand=null;$('panel').replaceChildren(el('h2',o.name),el('p','Hold the canvas or choose Options to continue from this object.'));render()};
    return button;
  }));
  $('undo').disabled=busy||!state.undo;$('redo').disabled=busy||!state.redo;
  $('title').textContent=displayed()?.name || 'Your blank canvas';
  $('scope').textContent=preview?'Preview · not yet applied':mode==='points'?'Choose an occurrence to explain':mode==='view'?'Drag to pan · pinch or wheel to zoom':'Hold for construction tools';
  const fields=displayed()?.fields||[];if(!fields.includes(labelField))labelField='value';
  $('labels').replaceChildren(...fields.map(f=>el('option',f,{value:f})));$('labels').value=labelField;
  draw();occurrences();
}
$('labels').onchange=()=>{labelField=$('labels').value;draw()};
function viewPositions(obj){
  if(!obj?.rows)return [];
  if(obj.placed)return obj.rows.map(r=>[r.position[0],r.position[1]||0]);
  const [a,b]=obj.axes.length?obj.axes:['index','value'];
  return obj.rows.map(r=>[Number(r.fields[a]),Number(r.fields[b] || 0)]);
}
function draw(frame=null,bounds=null){
  const obj=displayed(), rows=obj?.rows || [], positions=frame?.positions || viewPositions(obj);
  if(positions.some(p=>p.some(v=>!Number.isFinite(v)))){
    $('marks').replaceChildren();dots=[];status('Exact values are available, but this table projection exceeds floating coordinate range. Declare a bounded placement.',true);return;
  }
  const samples=bounds || positions;
  let xs=samples.map(p=>p[0]),ys=samples.map(p=>p[1]||0);
  const xmin=Math.min(0,...xs),xmax=Math.max(1,...xs),ymin=Math.min(0,...ys),ymax=Math.max(1,...ys);
  const scale=Math.min(590/(xmax-xmin),340/(ymax-ymin))*camera.zoom;
  const project=p=>[350+(p[0]-(xmin+xmax)/2)*scale+camera.x,225-((p[1]||0)-(ymin+ymax)/2)*scale+camera.y];
  const marks=$('marks');marks.replaceChildren();dots=[];
  const unit=700/Math.max(260,$('canvas').getBoundingClientRect().width);
  if(!positions.length){
    const label=document.createElementNS('http://www.w3.org/2000/svg','text');
    label.setAttribute('x','350');label.setAttribute('y','220');label.setAttribute('text-anchor','middle');
    label.style.fontSize=`${12*unit}px`;
    label.textContent=obj?'Empty domain · no occurrences':$('canvas').clientWidth<400?'Start with Add.':'Add something. Give it a rule. See what emerges.';marks.append(label);
  }
  const labelsShown=positions.length<=($('canvas').clientWidth<400?24:90);
  positions.forEach((p,i)=>{
    const [x,y]=project(p);const row=frame?rows.find(r=>r.ref[1]===(frame.after[i]||frame.before[i])):rows[i];
    const circle=document.createElementNS('http://www.w3.org/2000/svg','circle');
    const chosen=row&&selectedPoint?.[1]===row.ref[1];
    for(const [k,v] of Object.entries({cx:x,cy:y,r:(chosen?8:5)*unit,fill:row?.match===false?'#a9b6ad':'#b96429',opacity:frame?frame.opacity[i]:(row?.match===false ? .25 : 1),stroke:chosen?'#235d48':'none','stroke-width':3}))circle.setAttribute(k,v);
    marks.append(circle);if(row)dots.push({x,y,row});
    if(labelsShown&&row){const t=document.createElementNS(circle.namespaceURI,'text');t.setAttribute('x',x+8*unit);t.setAttribute('y',y-7*unit);t.style.fontSize=`${12*unit}px`;const text=String(row.fields[labelField]);t.textContent=text.length>16?text.slice(0,13)+'…':text;marks.append(t)}
  });
  $('projection').textContent=obj?.placed?`Declared ${obj.dimension}D placement${obj.dimension===3?' · XY projection':''}`:'Approximate table projection · exact labels. Arrange declares positions.';
}
function occurrences(){
  $('occurrence-label').hidden=mode!=='points';
  const select=$('occurrence');select.replaceChildren(el('option','Choose an occurrence',{value:''}));
  for(const r of object()?.rows || [])select.append(el('option',`${r.fields.index} · value ${r.fields.value}${r.match?'':' · outside relation'}`,{value:r.ref[1]}));
  select.value=selectedPoint?.[1]||'';
}
$('occurrence').onchange=()=>{selectedPoint=object()?.rows.find(r=>r.ref[1]===$('occurrence').value)?.ref || null;draw();if(selectedPoint)explain()};
function openMenu(addOnly=false){
  if(busy||preview)return;
  const options=actions(addOnly?{mode:'objects'}:{mode,object:object(),point:selectedPoint});
  $('menu-title').textContent=addOnly?'Add to the canvas':mode==='points'?'Occurrence options':mode==='view'?'View options':active||'Canvas options';
  $('menu-actions').replaceChildren(...(options.length?options.map(action=>{
    const button=el('button',labels[action],{'data-action':action});button.onclick=()=>{$('menu').close();if(action==='explain')explain();else if(action==='fit')fit();else editor(action)};return button;
  }):[el('p','Select an occurrence first. The list also reaches coincident points.')]));
  $('menu').showModal();
}
$('add').onclick=()=>openMenu(true);$('options').onclick=()=>openMenu();$('close-menu').onclick=()=>$('menu').close();
document.querySelectorAll('[data-mode]').forEach(button=>button.onclick=()=>{
  if(busy||preview)return;mode=button.dataset.mode;cancelHold();
  document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));render();
});
function fit(){camera={x:0,y:0,zoom:1};draw()}
$('fit').onclick=fit;

// Hold recognition owns time, movement, multi-touch, and cancellation only.
// It sends the same open-options intent as the visible/keyboard command.
const pointers=new Map();
function point(event){const p=$('canvas').createSVGPoint();p.x=event.clientX;p.y=event.clientY;return p.matrixTransform($('canvas').getScreenCTM().inverse())}
function cancelHold(){if(gesture)clearTimeout(gesture.timer);gesture=null}
function chooseAt(p){
  const radius=24/$('canvas').getScreenCTM().a;
  const nearest=dots.map(d=>({...d,d:Math.hypot(d.x-p.x,d.y-p.y)})).filter(d=>d.d<radius).sort((a,b)=>a.d-b.d);
  if(nearest.length){selectedPoint=nearest[0].row.ref;draw();occurrences();if(nearest.length>1)status(`${nearest.length} nearby occurrences. Use the occurrence list to choose exactly.`)}
}
$('hit').onpointerdown=e=>{
  if(busy||preview||e.button>0)return;e.preventDefault();held=false;
  const p=point(e);pointers.set(e.pointerId,p);$('hit').setPointerCapture(e.pointerId);
  if(pointers.size>1){cancelHold();return}
  if(mode==='points')chooseAt(p);
  gesture={start:p,last:p,moved:false,timer:setTimeout(()=>{held=true;openMenu();cancelHold()},480)};
};
$('hit').onpointermove=e=>{
  if(!pointers.has(e.pointerId))return;const p=point(e),old=pointers.get(e.pointerId);
  if(mode==='view'&&pointers.size===2){const other=[...pointers.entries()].find(([id])=>id!==e.pointerId)[1];const a=Math.hypot(old.x-other.x,old.y-other.y),b=Math.hypot(p.x-other.x,p.y-other.y);if(a>1)camera.zoom=Math.min(12,Math.max(.2,camera.zoom*b/a));draw()}
  pointers.set(e.pointerId,p);
  if(!gesture)return;
  if(Math.hypot(p.x-gesture.start.x,p.y-gesture.start.y)*$('canvas').getScreenCTM().a>9){clearTimeout(gesture.timer);gesture.moved=true}
  if(mode==='view'){camera.x+=p.x-gesture.last.x;camera.y+=p.y-gesture.last.y;draw()}
  gesture.last=p;
};
$('hit').onpointerup=e=>{const tap=gesture&&!gesture.moved&&!held;pointers.delete(e.pointerId);cancelHold();if(tap&&mode==='points'&&selectedPoint)explain()};
$('hit').onpointercancel=e=>{pointers.delete(e.pointerId);cancelHold()};
$('canvas').addEventListener('touchstart',e=>e.preventDefault(),{passive:false});
$('canvas').addEventListener('wheel',e=>{if(mode!=='view'||busy)return;e.preventDefault();camera.zoom=Math.min(12,Math.max(.2,camera.zoom*Math.exp(-e.deltaY*.002)));draw()},{passive:false});
$('canvas').oncontextmenu=e=>{e.preventDefault();cancelHold();if(!$('menu').open)openMenu()};
$('canvas').onkeydown=e=>{if((e.shiftKey&&e.key==='F10')||e.key==='ContextMenu'){e.preventDefault();openMenu()}if(e.key==='Escape'){cancelHold();if(preview)cancelPreview()}};

function options(values,selected){const s=el('select');for(const v of values)s.append(el('option',v,{value:v}));if(selected!==undefined)s.value=selected;return s}
function labeled(parent,text,node){const label=el('label',text);label.append(node);parent.append(label);return node}
function input(value){const n=el('input',undefined,{type:'text'});n.value=value;return n}
function expr(initial,fields,depth=0){
  const box=el('div',undefined,{class:'expression'}), type=options(['Field','Number','Operation','Keyed read']), body=el('div',undefined,{class:'children'});
  type.setAttribute('aria-label','Expression type');
  let read;
  box.append(type,body);
  function fill(spec){
    body.replaceChildren();type.value='field'in spec?'Field':'integer'in spec?'Number':'op'in spec?'Operation':'Keyed read';
    if(type.value==='Field'){
      const value=options(fields,spec.field);value.setAttribute('aria-label','Field');body.append(value);read=()=>field(value.value);
    }else if(type.value==='Number'){
      const value=input(spec.integer);value.inputMode='numeric';value.setAttribute('aria-label','Exact integer');body.append(value);read=()=>number(value.value);
    }else if(type.value==='Operation'){
      const op=options(['+','-','*','//','%','=','≠','<','≤','>','≥','and','or'],spec.op);
      op.setAttribute('aria-label','Operation');
      const left=expr(spec.args[0],fields,depth+1),right=expr(spec.args[1],fields,depth+1);
      body.append(left.box,op,right.box);read=()=>operation(op.value,left.read(),right.read());
    }else{
      const sources=state.objects.filter(o=>o.kind!=='incidence'&&o.status==='ready');
      if(!sources.length){body.append(el('p','Create a measurement or source to read first.'));read=()=>{throw Error('No keyed-read source')};return}
      const source=labeled(body,'Read from',options(sources.map(o=>o.name),spec.read?.object || sources[0].name));
      const target=expr(spec.read?.on || field(fields.includes('key')?'key':fields[0]),fields,depth+1);
      body.append(el('span','Target key (this object)',{class:'read-label'}),target.box);
      const key=labeled(body,'Match source key',el('select')),value=labeled(body,'Read source field',el('select'));
      function sourceFields(){const f=sources.find(o=>o.name===source.value).fields;key.replaceChildren(...f.map(v=>el('option',v,{value:v})));value.replaceChildren(...f.map(v=>el('option',v,{value:v})));key.value=spec.read?.key?.field||'key';value.value=spec.read?.value?.field||'value'}
      source.onchange=sourceFields;sourceFields();
      read=()=>({read:{object:source.value,on:target.read(),key:field(key.value),value:field(value.value)}});
    }
  }
  type.onchange=()=>{
    if(depth>=10&&['Operation','Keyed read'].includes(type.value)){status('The study limits editor nesting to ten cards.',true);type.value='Field'}
    fill(type.value==='Field'?field(fields[0]):type.value==='Number'?number(0):type.value==='Operation'?operation('+',field(fields[0]),number(1)):{read:{}});
  };
  fill(initial);return {box,read:()=>read()};
}
function editor(action){
  preview=null;getCommand=null;editorRevision=state.revision;render();
  const panel=$('panel');panel.replaceChildren(el('span','DECLARE / PREVIEW / APPLY',{class:'eyebrow'}),el('h2',labels[action]));
  const form=el('form'), controls=el('fieldset');controls.style.cssText='border:0;padding:0;margin:0;min-width:0';form.append(controls);panel.append(form);
  const source=object(), fields=source?.fields||['i','j','value','index','key'];
  const name=labeled(controls,'Result name',input(action==='place'?active:`${labels[action]} ${state.objects.length+1}`));
  name.id='result-name';if(action==='place')name.readOnly=true;
  let args;
  function expressionControl(label,spec,fs=fields){const card=expr(spec,fs);card.box.setAttribute('role','group');card.box.setAttribute('aria-label',label);controls.append(el('label',label),card.box);return card}
  if(action==='integers'){
    const values=labeled(controls,'Integer values · separated by commas',input('0, 1, 2, 3'));values.id='integer-values';
    controls.append(el('p','Repeated values remain distinct occurrences. An empty list is an empty domain.',{class:'help'}));
    args=()=>({values:values.value.trim()?values.value.split(',').map(s=>s.trim()):[]});
  }else if(action==='grid'){
    const shape=labeled(controls,'Axis lengths · one to three, separated by commas',input('4, 4'));shape.id='grid-shape';
    const axes=labeled(controls,'Axis names · in the same order',input('i, j'));axes.id='grid-axes';
    let value=expressionControl('Value at each occurrence',number(1),['i','j','index']);
    axes.addEventListener('change',()=>{const next=expr(value.read(),[...axes.value.split(',').map(s=>s.trim()),'index']);value.box.replaceWith(next.box);value=next});
    args=()=>({shape:shape.value.split(',').map(s=>s.trim()),axes:axes.value.split(',').map(s=>s.trim()),value:value.read()});
  }else if(action==='product'){
    const sources=state.objects.filter(o=>o.kind!=='incidence'&&o.status==='ready'), choices=[];
    for(const role of ['left','right']){
      const r=labeled(controls,'Role name',input(role)),s=labeled(controls,'Source for this role',options(sources.map(o=>o.name),active));
      const copies=el('div');controls.append(copies);let checks=[];
      const rebuild=()=>{copies.replaceChildren(el('label','Fields to copy into this role'));checks=sources.find(o=>o.name===s.value).fields.map(f=>{const l=el('label',f),c=el('input',undefined,{type:'checkbox',value:f});c.checked=f==='value';c.style.cssText='width:auto;display:inline;margin-right:8px;vertical-align:middle';l.prepend(c);copies.append(l);return c})};s.onchange=rebuild;rebuild();choices.push(()=>[r.value,{source:s.value,fields:checks.filter(c=>c.checked).map(c=>c.value)}]);
    }
    controls.append(el('p','Every pair of current source slots. Copied fields are named role_field; labels do not identify tuples.',{class:'help'}));
    args=()=>{const entries=choices.map(f=>f());if(entries[0][0]===entries[1][0])throw Error('Choose distinct role names');return {factors:Object.fromEntries(entries)}};
  }else if(action==='field'){
    const f=labeled(controls,'New field name',input('total'));f.id='field-name';const value=expressionControl('Field definition',operation('+',field(fields[0]),number(1)));
    args=()=>({source:active,field:f.value,value:value.read()});
  }else if(action==='lens'){
    const rule=expressionControl('Relation · true means incident',operation('=',field('value'),number(0)));
    args=()=>({source:active,rule:rule.read()});
  }else if(action==='measure'){
    const reducer=labeled(controls,'Measurement',options(['count','sum','rank']));reducer.id='reducer';
    controls.append(el('label','Retain these fields as group keys'));
    const groups=fields.map(f=>{const l=el('label',f),c=el('input',undefined,{type:'checkbox',value:f,'data-group':f});c.style.cssText='width:auto;display:inline;margin-right:8px;vertical-align:middle';l.prepend(c);controls.append(l);return c});
    controls.append(el('p','No retained fields means one total. Count keeps zero groups from the declared domain; it does not invent missing keys.',{class:'help'}));
    const weight=expressionControl('Weight · used by Sum',field('value'));
    const order=labeled(controls,'Member order · used by Rank',options(fields,'index'));order.id='rank-order';
    const key=labeled(controls,'Unique item key · used by Rank',options(fields,'key'));key.id='rank-key';
    function measurementFields(){weight.box.hidden=weight.box.previousElementSibling.hidden=reducer.value!=='sum';order.parentElement.hidden=key.parentElement.hidden=reducer.value!=='rank'}
    reducer.onchange=measurementFields;measurementFields();
    args=()=>({source:active,reducer:reducer.value,by:groups.filter(g=>g.checked).map(g=>g.value),weight:weight.read(),order:[order.value],key:key.value});
  }else if(action==='place'){
    controls.append(el('p','Change this object’s placement. Use a Keyed read card to let a measurement supply a coordinate. Existing derived objects keep their earlier input definitions.',{class:'help'}));
    const x=expressionControl('x coordinate',field(fields.includes('i')?'i':'key'));
    const y=expressionControl('y coordinate',field(fields.includes('j')?'j':'value'));
    args=()=>({source:active,coordinates:[x.read(),y.read()]});
  }else if(action==='select'){
    controls.append(el('p','Keep matching occurrences as a new finite universe. Its later groups may differ from the original relation’s zero groups.',{class:'help'}));args=()=>({source:active});
  }
  const bar=el('div',undefined,{class:'form-actions'}), test=el('button','Preview',{type:'submit',class:'primary',id:'preview'}), apply=el('button','Apply',{type:'button',id:'apply'}),cancel=el('button','Cancel',{type:'button',id:'cancel'});apply.disabled=true;bar.append(test,apply,cancel);form.append(bar);
  const detail=el('details'), summary=el('summary','Read the declaration'),code=el('pre',undefined,{id:'declaration'});detail.append(summary,code);panel.append(detail);
  getCommand=()=>({action,name:name.value,args:args()});
  function changed(){preview=null;apply.disabled=true;try{code.textContent=JSON.stringify(getCommand(),null,2)}catch(e){code.textContent=e.message}render()}
  form.addEventListener('change',changed);form.addEventListener('input',changed);changed();
  form.onsubmit=e=>{e.preventDefault();run(async()=>{
    if(editorRevision!==state.revision)throw Error('The workspace changed. Open this tool again.');
    const command=getCommand();preview=null;render();
    const result=await request('preview',{command});preview=result;render();apply.disabled=false;status('Exact preview ready. Apply keeps this capture; Cancel leaves history unchanged.');
  })};
  apply.onclick=()=>run(async()=>{if(!preview)return;const next=await request('commit',{token:preview.token});adopt(next);getCommand=null;panel.replaceChildren(el('h2','Construction applied'),el('p','Choose any object and continue composing. Hold the canvas or use Options.'));await animate(next.motion);status('Applied one construction. Undo restores its captured predecessor.')});
  cancel.onclick=cancelPreview;
}
function cancelPreview(){run(async()=>{await request('cancel');preview=null;getCommand=null;render();$('panel').replaceChildren(el('h2','Draft discarded'),el('p','Your construction and its history are unchanged.'));status('Cancelled.')})}
async function animate(frames){
  if(!frames?.length||matchMedia('(prefers-reduced-motion: reduce)').matches)return;
  const bounds=frames.flatMap(f=>f.positions);let start;
  await new Promise(resolve=>{function tick(t){start??=t;const p=Math.min(1,(t-start)/550),i=Math.round(p*(frames.length-1));draw(frames[i],bounds);if(p<1)requestAnimationFrame(tick);else resolve()}requestAnimationFrame(tick)});draw();
}
for(const direction of ['undo','redo'])$(direction).onclick=()=>run(async()=>{const next=await request(direction,{active});adopt(next);getCommand=null;$('panel').replaceChildren(el('h2',direction==='undo'?'Earlier capture restored':'Capture restored again'),el('p','Playback uses recorded endpoints. No construction was evaluated.'));await animate(next.motion);status(direction==='undo'?'Undone.':'Redone.')});
function explain(){run(async()=>{
  const receipt=await request('inspect',{name:active,ref:selectedPoint});showReceipt(receipt);
})}
function showReceipt(receipt,heading='Value'){
  const panel=$('panel');panel.replaceChildren(el('span','CAPTURED EVIDENCE',{class:'eyebrow'}),el('h2',`${heading} ${receipt.item.value}`));
  panel.append(el('pre',JSON.stringify(receipt.item.fields,null,2)));
  const m=receipt.measurement;
  if(m.unavailable)panel.append(el('p','No active measurement receipt at this occurrence.',{class:'quiet'}));
  else{
    panel.append(el('h2',`${m.reducer} · ${m.contributor_count} contributors`),el('p',m.formula));
    for(const c of m.contributors)panel.append(el('p',`Value ${c.item.value} · weight ${c.weight}`,{class:'receipt-item'}));
    if(m.truncated)panel.append(el('p','Showing the first 32 contributors.'));
  }
  if(Array.isArray(receipt.bindings))for(const b of receipt.bindings){const button=el('button',`Follow keyed read · ${b.value}`);button.onclick=()=>run(async()=>{
    // The driver may be an earlier captured version. Request by scoped reference,
    // never guess it from a current object's equal labels or screen location.
    const driver=await request('inspect-driver',{ref:b.driver});showReceipt(driver,'Driver value');
  });panel.append(button)}
  const details=el('details'),summary=el('summary','Scoped references and receipt'),pre=el('pre',JSON.stringify(receipt,null,2));details.append(summary,pre);panel.append(details);
}
$('save').onclick=()=>run(async()=>{
  const response=await fetch('/api/export');const text=await response.text();
  const url=URL.createObjectURL(new Blob([text],{type:'application/json'})),a=el('a',undefined,{href:url,download:'kaleion-studio.json'});a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);status('Saved captured definitions, evidence, and undo/redo.');
});
$('open').onclick=()=>$('file').click();$('file').onchange=()=>run(async()=>{const file=$('file').files[0];if(!file)return;const next=await request('import',{capture:await file.text()});adopt(next);getCommand=null;$('panel').replaceChildren(el('h2','Saved workspace opened'),el('p','Its captures and history are available without reevaluating definitions.'));status('Reopened captured workspace.');$('file').value=''});
window.addEventListener('blur',()=>{cancelHold();pointers.clear()});
document.addEventListener('keydown',e=>{if(e.key==='Escape'){cancelHold();if(!$('menu').open&&getCommand&&!busy)cancelPreview()}});
new ResizeObserver(()=>{if(!busy)draw()}).observe($('canvas'));
adopt(await (await fetch('/api/state')).json());
