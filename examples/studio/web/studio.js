import {actions, labels} from './context.js';
import {expressionEditor} from './expressions.js';
import {fieldKeys} from './groups.js';
import {draftSession} from './drafts.js';
import {coverageInspector} from './coverage.js';
import {viewPositions} from './views.js';
import {linkedViews} from './evidence.js';
import {receiptInspector} from './receipts.js';
import {caseFields,caseLabel,caseReport} from './cases.js';
import {replayControls} from './replay.js';

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
let groupReport=null, groupChoice=-1;
let camera={x:0,y:0,zoom:1}, dots=[], labelField='value', objectTabsKey='', labelOptionsKey='';
const draft=draftSession();
const linked=linkedViews($('linked-views'),{
  load:capture=>request('capture',{capture}),
  onVisibility:shown=>{$('single-view').hidden=shown;$('canvas-tools').hidden=shown;$('scope').textContent=shown?'Read-only captured evidence · close to construct':'Hold for construction tools';if(shown)status('Browsing captured evidence. Selection and view changes do not alter your construction.')}
});
const receipts=receiptInspector({panel:$('panel'),run,query:request,linked,beforeShow:parkDraft});
const replay=replayControls($('replay'),{draw,restore:()=>draw(),onPresentation:shown=>{
  if(shown)$('scope').textContent='Replay · presentation only · applied case unchanged';
  else $('scope').textContent=resultScope();
}});
const object = () => state.objects.find(o=>o.name===active);
const displayed = () => preview?.objects.find(o=>o.name===preview.name) || object();
const selectedGroup=()=>groupReport?.revision===state.revision&&groupReport.name===active?groupReport.groups[groupChoice]:null;
const groupLabel=(report,group)=>report.by.map((field,i)=>`${field} = ${group.key_types[i]==='text'?JSON.stringify(group.key[i]):group.key[i]}`).join(', ')||'Whole domain';
function clearGroups(){groupReport=null;groupChoice=-1}
function resultScope(){return preview?(preview.kind==='case'?`Preview case · ${caseLabel(preview.parameters)} · not applied`:'Preview · not yet applied'):mode==='points'?'Choose an occurrence to explain':mode==='groups'?'Select by declared group keys':mode==='view'?'Drag to pan · pinch or wheel to zoom':'Hold for construction tools'}
function status(text, error=false){$('status').textContent=text;$('status').classList.toggle('error',error)}
const busyControls=new Map();
let busyFocus=null;
function workspaceControls(){
  const drafting=!!draft.current;
  $('undo').disabled=busy||drafting||!state.undo;$('redo').disabled=busy||drafting||!state.redo;
  $('add').disabled=$('open').disabled=$('file').disabled=$('cases').disabled=busy||drafting;
  $('draft-tray').hidden=!drafting;
  if(drafting){
    const context=draft.current.context;
    $('draft-title').textContent=`${context.title} · ${context.subject}${draft.current.parked?' · parked':' · editing'}`;
    $('resume-draft').textContent=draft.current.parked?'Resume draft':'Go to draft';
  }
}
function setBusy(value){
  busy=value;
  if(value){busyFocus=document.activeElement;document.querySelectorAll('button,input,select,fieldset').forEach(n=>{busyControls.set(n,n.disabled);n.disabled=true})}
  else{for(const [n,disabled] of busyControls)n.disabled=disabled;busyControls.clear()}
  workspaceControls();
  if(!value){const a=$('apply');if(a)a.disabled=!preview;if(busyFocus?.isConnected&&!busyFocus.disabled&&document.activeElement===document.body)busyFocus.focus({preventScroll:true});busyFocus=null}
}
async function request(path,body={}){
  const response=await fetch('/api/'+path,{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({revision:state.revision,...body})});
  const data=await response.json();if(!response.ok)throw Error(data.error);return data;
}
async function run(fn){if(busy)return;setBusy(true);try{await fn()}catch(e){status(e.message,true)}finally{setBusy(false)}}
function adopt(next){
  linked.close();replay.clear();state=next;preview=null;selectedPoint=null;clearGroups();
  if(next.active)active=next.active;
  if(!state.objects.some(o=>o.name===active))active=state.objects.at(-1)?.name || null;
  camera={x:0,y:0,zoom:1};render();
}
function render(){
  replay.select(active);
  $('case-summary').textContent=caseLabel(state.parameters);
  // Do not replace an unchanged control on input blur: it can swallow the next click.
  const tabsKey=JSON.stringify([active,state.objects.map(o=>[o.name,o.kind,o.status,o.error])]);
  if(tabsKey!==objectTabsKey){
    const focused=document.activeElement?.dataset.object;objectTabsKey=tabsKey;
    $('objects').replaceChildren(...state.objects.map(o=>{
      const button=el('button',o.name,{'aria-pressed':String(o.name===active),'data-object':o.name});
      button.append(el('small',o.status==='ready'?o.kind:o.error));
      button.onclick=()=>{if(busy)return;linked.close();parkDraft();active=o.name;selectedPoint=null;preview=null;clearGroups();$('panel').replaceChildren(el('h2',o.name),el('p','Hold the canvas or choose Options to continue from this object.'));render();if(mode==='groups')groupPanel()};
      return button;
    }));
    if(focused)[...$('objects').children].find(b=>b.dataset.object===focused)?.focus({preventScroll:true});
  }
  workspaceControls();
  $('title').textContent=displayed()?.name || 'Your blank canvas';
  $('scope').textContent=resultScope();
  const fields=displayed()?.fields||[];if(!fields.includes(labelField))labelField='value';
  const fieldKey=JSON.stringify(fields);if(fieldKey!==labelOptionsKey){labelOptionsKey=fieldKey;$('labels').replaceChildren(...fields.map(f=>el('option',f,{value:f})))}$('labels').value=labelField;
  draw();occurrences();
}
$('labels').onchange=()=>{labelField=$('labels').value;draw()};
function draw(frame=null,bounds=null){
  if(!frame)replay.reset(false);
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
    label.textContent=obj?.status==='failed'?'Evaluation failed':obj?'Empty domain · no occurrences':$('canvas').clientWidth<400?'Start with Add.':'Add something. Give it a rule. See what emerges.';marks.append(label);
  }
  const labelsShown=positions.length<=($('canvas').clientWidth<400?24:90);
  const group=mode==='groups'&&!preview?selectedGroup():null;
  const members=new Set(group?.members.map(r=>r[1])||[]),matches=new Set(group?.matches.map(r=>r[1])||[]);
  positions.forEach((p,i)=>{
    const [x,y]=project(p);const row=frame?rows.find(r=>r.ref[1]===(frame.after[i]||frame.before[i])):rows[i];
    const circle=document.createElementNS('http://www.w3.org/2000/svg','circle');
    const chosen=row&&(mode==='groups'?members.has(row.ref[1]):selectedPoint?.[1]===row.ref[1]);
    const opacity=frame?frame.opacity[i]:group?(matches.has(row?.ref[1])?1:(chosen ? .45 : .12)):(row?.match===false ? .25 : 1);
    for(const [k,v] of Object.entries({cx:x,cy:y,r:(chosen?8:5)*unit,fill:row?.match===false?'#a9b6ad':'#b96429',opacity,stroke:chosen?'#235d48':'none','stroke-width':3,'data-occurrence':row?.ref[1]||'','data-group-member':String(!!group&&chosen)}))circle.setAttribute(k,v);
    marks.append(circle);if(row&&!frame)dots.push({x,y,row});
    if(labelsShown&&row){const t=document.createElementNS(circle.namespaceURI,'text');t.setAttribute('x',x+8*unit);t.setAttribute('y',y-7*unit);t.style.fontSize=`${12*unit}px`;const text=String(row.fields[labelField]);t.textContent=text.length>16?text.slice(0,13)+'…':text;marks.append(t)}
  });
  $('projection').textContent=obj?.placed?`Declared ${obj.dimension}D placement${obj.dimension===3?' · XY projection':''}`:'Approximate table projection · exact labels. Arrange declares positions.';
}
function occurrences(){
  $('occurrence-label').hidden=mode!=='points'||!!preview;
  const select=$('occurrence');select.replaceChildren(el('option','Choose an occurrence',{value:''}));
  for(const r of object()?.rows || [])select.append(el('option',`${r.fields.index} · value ${r.fields.value}${r.match?'':' · outside relation'}`,{value:r.ref[1]}));
  select.value=selectedPoint?.[1]||'';
}
$('occurrence').onchange=()=>{selectedPoint=object()?.rows.find(r=>r.ref[1]===$('occurrence').value)?.ref || null;draw();if(selectedPoint)explain()};
function openMenu(addOnly=false){
  if(busy||preview)return;
  replay.reset();
  const options=actions(addOnly?{mode:'objects'}:{mode,object:object(),point:selectedPoint,group:selectedGroup()});
  $('menu-title').textContent=addOnly?'Add to the canvas':mode==='points'?'Occurrence options':mode==='groups'?'Group options':mode==='view'?'View options':active||'Canvas options';
  $('menu-actions').replaceChildren(...(options.length?options.map(action=>{
    const button=el('button',action==='measure'&&mode==='groups'?'Measure all groups':labels[action],{'data-action':action});
    if(draft.current&&!['explain','fit','group_options','coverage'].includes(action)){button.disabled=true;button.title='Resume or discard your draft before starting another construction.'}
    button.onclick=()=>{$('menu').close();if(action==='explain')explain();else if(action==='fit')fit();else if(action==='group_options')groupPanel();else if(action==='coverage')coveragePanel();else editor(action)};return button;
  }):[el('p','Select an occurrence first. The list also reaches coincident points.')]));
  $('menu').showModal();
}
$('add').onclick=()=>openMenu(true);$('options').onclick=()=>openMenu();$('close-menu').onclick=()=>$('menu').close();
document.querySelectorAll('[data-mode]').forEach(button=>button.onclick=()=>{
  if(busy)return;linked.close();parkDraft();mode=button.dataset.mode;cancelHold();
  document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));render();if(mode==='groups')groupPanel();
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
  if(nearest.length){
    if(mode==='groups'){
      if(!groupReport)return;
      groupChoice=groupReport.groups.findIndex(g=>g.members.some(r=>r[0]===nearest[0].row.ref[0]&&r[1]===nearest[0].row.ref[1]));
      groupPanel();
    }else{selectedPoint=nearest[0].row.ref;occurrences()}
    draw();if(nearest.length>1)status(`${nearest.length} nearby occurrences. Use the ${mode==='groups'?'group':'occurrence'} list to choose exactly.`);
  }
}
$('hit').onpointerdown=e=>{
  if(busy||preview||e.button>0)return;e.preventDefault();held=false;
  const p=point(e);pointers.set(e.pointerId,p);$('hit').setPointerCapture(e.pointerId);
  if(pointers.size>1){cancelHold();return}
  if(mode==='points'||mode==='groups')chooseAt(p);
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
$('canvas').onkeydown=e=>{if((e.shiftKey&&e.key==='F10')||e.key==='ContextMenu'){e.preventDefault();openMenu()}if(e.key==='Escape')cancelHold()};

function parkDraft(){
  if(!draft.current||draft.current.parked)return;
  draft.park();preview=null;
  $('panel').replaceChildren(el('h2','Your draft is parked'),el('p','Inspect another object, then choose Resume draft to continue.'));
  workspaceControls();status('Draft retained. Browsing does not apply it.');
}
$('resume-draft').onclick=()=>{
  if(busy||!draft.current)return;
  try{
    linked.close();const context=draft.resume(state.revision);active=context.target;mode=context.mode;
    groupReport=context.groupReport;groupChoice=context.groupChoice;selectedPoint=null;
    document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.mode===mode)));
    render();$('panel').scrollIntoView({block:'nearest'});($('result-name')||$('panel').querySelector('input,button'))?.focus({preventScroll:true});
    status(preview?'Exact preview ready to apply.':'Draft restored on its original target. Preview to check it.');
  }catch(error){status(error.message,true)}
};
$('discard-draft').onclick=()=>cancelPreview();

function options(values,selected){const s=el('select');for(const v of values)s.append(el('option',v,{value:v}));if(selected!==undefined)s.value=selected;return s}
function labeled(parent,text,node){const label=el('label',text);label.append(node);parent.append(label);return node}
function input(value){const n=el('input',undefined,{type:'text'});n.value=value;return n}
function groupPanel(){
  linked.close();parkDraft();const source=object();
  const panel=$('panel');panel.replaceChildren(el('span','SELECT BY A DECLARED KEY',{class:'eyebrow'}),el('h2','Groups'));
  if(!source||source.status!=='ready'){panel.append(el('p','Select a ready object first.'));return}
  const keys=fieldKeys(source.fields,groupReport?.by||[]);panel.append(keys.box);
  const browse=el('button','Browse groups',{type:'button',id:'browse-groups',class:'primary'});panel.append(browse);
  panel.append(el('p','Browsing reads this capture. It does not add a measurement or a history action.',{class:'help'}));
  keys.box.addEventListener('change',()=>{clearGroups();draw();panel.querySelector('.group-results')?.remove()});
  browse.onclick=()=>run(async()=>{groupReport=await request('groups',{name:active,by:keys.read()});groupChoice=groupReport.groups.length?0:-1;show();draw()});
  function show(){
    panel.querySelector('.group-results')?.remove();if(!groupReport)return;
    const results=el('div',undefined,{class:'group-results'});panel.append(results);
    results.append(el('p',`Key domain: ${groupReport.domain}. Group listing order is not member order.`,{class:'help'}));
    const select=labeled(results,'Captured group',el('select',undefined,{id:'group-choice'}));
    for(const [i,g] of groupReport.groups.entries()){
      select.append(el('option',`${groupLabel(groupReport,g)} · ${g.count} of ${g.population} incident`,{value:String(i)}));
    }
    select.value=String(groupChoice);
    const receipt=el('p',undefined,{id:'group-summary'});results.append(receipt);
    function summary(){const g=selectedGroup();receipt.textContent=g?`${g.count} incident occurrences · ${g.population} occurrences in the group. An empty group remains selectable.`:'No observed groups. Choose a declared axis or explicitly construct the expected bins.'}
    select.onchange=()=>{groupChoice=Number(select.value);summary();draw()};summary();
    const menu=el('button','Group options',{type:'button'});menu.onclick=()=>openMenu();results.append(menu);
  }
  show();
}
function coveragePanel(){
  linked.close();parkDraft();const source=object();
  const box=coverageInspector({source,objects:state.objects,initialBy:groupReport?.name===active?groupReport.by:[],run,
    check:spec=>request('coverage',spec),canAdopt:()=>!draft.current,
    inspect:async(ref,trigger)=>{const receipt=await request('inspect-driver',{ref});showReceipt(receipt,'Value',()=>{$('panel').replaceChildren(box);trigger.focus({preventScroll:true})})},
    clearLink:()=>linked.close(),
    chooseLink:index=>linked.choose(index,false),
    link:async(report,rows,index,onChoose)=>{
      const back=()=>{$('panel').replaceChildren(box);$('view-coverage').focus({preventScroll:true})};
      await linked.open({title:'Expected items and their matches',
        inspect:ref=>run(async()=>showReceipt(await request('inspect-driver',{ref}),'Value',back)),
        detail:'Links follow the declared coverage keys. Faint points give context; a missing match does not create a source point.',
        left:{capture:report.expected_capture,label:'Expected items'},
        right:{capture:report.capture,label:'Candidates'},index,onChoose,
        links:rows.map(row=>({label:`${row.key.map((key,i)=>row.key_types[i]==='text'?JSON.stringify(key):String(key)).join(', ')} · ${row.count} matches${row.outside?' · outside':''}`,
          left:row.expected_ref?[{ref:row.expected_ref,note:'Expected occurrence'}]:[],
          right:row.members.map(ref=>{const match=row.matches.some(r=>r[0]===ref[0]&&r[1]===ref[1]);return {ref,emphasis:match,note:match?'Match':'Candidate · outside relation'}}),
          emptyLeft:'No expected item for this outside key.',
          emptyRight:'No candidate group for this expected item. No match is hidden here.'}))});
    },
    showGroup:async(report,group)=>{
      linked.close();groupReport=await request('groups',{name:source.name,by:report.by});groupChoice=group;active=source.name;mode='groups';selectedPoint=null;
      document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.mode===mode)));render();
    },
    adopt:spec=>editor('assignment',spec),
  });
  $('panel').replaceChildren(box);
}
function expr(initial,fields){
  return expressionEditor(initial,fields,state.objects.filter(o=>o.kind!=='incidence'&&o.status==='ready'),Object.keys(state.parameters||{}));
}
function editor(action,seed=null){
  linked.close();
  if(draft.current){status('Resume or discard your draft before starting another construction.',true);return}
  replay.clear();
  preview=null;const editorRevision=state.revision,sourceName=seed?.source||active;render();
  const panel=$('panel');panel.replaceChildren(el('span','DECLARE / PREVIEW / APPLY',{class:'eyebrow'}),el('h2',labels[action]));
  const form=el('form'), controls=el('fieldset');controls.style.cssText='border:0;padding:0;margin:0;min-width:0';form.append(controls);panel.append(form);
  const source=state.objects.find(o=>o.name===sourceName), fields=source?.fields||['i','j','value','index','key'];
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
    controls.append(el('p','Use exact integers or declared parameter names. For a length such as n + 1, edit axis formulas.',{class:'help'}));
    const editLengths=el('button','Edit axis formulas',{type:'button',id:'edit-axis-lengths'}),lengthBox=el('div',undefined,{class:'axis-expressions'});controls.append(editLengths,lengthBox);
    let lengths=null;
    const extent=text=>Object.hasOwn(state.parameters||{},text)?{parameter:text}:number(text);
    editLengths.onclick=()=>{
      if(lengths)return;
      const sizes=shape.value.split(',').map(s=>s.trim());
      if(sizes.length<1||sizes.length>3){status('Use one to three axis lengths.',true);return}
      lengths=sizes.map((size,i)=>{const card=expr(extent(size),[]);card.box.setAttribute('role','group');card.box.setAttribute('aria-label',`Axis ${i+1} length`);lengthBox.append(el('label',`Axis ${i+1} length`),card.box);return card});
      shape.parentElement.hidden=true;editLengths.hidden=true;
      controls.dispatchEvent(new Event('change',{bubbles:true}));
    };
    const axes=labeled(controls,'Axis names · in the same order',input('i, j'));axes.id='grid-axes';
    let value=expressionControl('Value at each occurrence',number(1),['i','j','index']);
    axes.addEventListener('change',()=>{const next=expr(value.read(),[...axes.value.split(',').map(s=>s.trim()),'index']);value.box.replaceWith(next.box);value=next});
    args=()=>({shape:lengths?lengths.map(card=>card.read()):shape.value.split(',').map(s=>Object.hasOwn(state.parameters||{},s.trim())?{parameter:s.trim()}:s.trim()),axes:axes.value.split(',').map(s=>s.trim()),value:value.read()});
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
    args=()=>({source:sourceName,field:f.value,value:value.read()});
  }else if(action==='lens'){
    const rule=expressionControl('Relation · true means incident',operation('=',field('value'),number(0)));
    args=()=>({source:sourceName,rule:rule.read()});
  }else if(action==='measure'){
    const reducer=labeled(controls,'Measurement',options(['count','sum','rank']));reducer.id='reducer';
    const groups=fieldKeys(fields,mode==='groups'?(groupReport?.by||[]):[],'Retained group keys');controls.append(groups.box);
    controls.append(el('p','No retained fields means one total. Count keeps zero groups from the declared domain; it does not invent missing keys.',{class:'help'}));
    const weight=expressionControl('Weight · used by Sum',field('value'));
    const order=fieldKeys(fields,['index'],'Member order','Choose at least one ordering field');order.box.id='rank-order';controls.append(order.box);
    const key=labeled(controls,'Unique item key · used by Rank',options(fields,'key'));key.id='rank-key';
    function measurementFields(){weight.box.hidden=weight.box.previousElementSibling.hidden=reducer.value!=='sum';order.box.hidden=key.parentElement.hidden=reducer.value!=='rank'}
    reducer.onchange=measurementFields;measurementFields();
    args=()=>({source:sourceName,reducer:reducer.value,by:groups.read(),weight:weight.read(),order:order.read(),key:key.value});
  }else if(action==='assignment'){
    controls.append(el('p',`Assign onto ${seed.expected}, matching ${seed.expected_by.join(', ')} to ${seed.by.join(', ')} in ${seed.source}. Its identities, positions, and labels are retained. Coverage is checked again before adoption.`,{class:'help'}));
    const assigned=labeled(controls,'New field name',input('assigned'));assigned.id='assigned-field';
    const value=expressionControl('Value supplied by the unique match',field('value'));
    args=()=>({...seed,value:value.read(),field:assigned.value});
  }else if(action==='place'){
    controls.append(el('p','Change this object’s placement. Use a Keyed read to let a measurement supply a coordinate. Existing derived objects keep their earlier input definitions.',{class:'help'}));
    const x=expressionControl('x coordinate',field(fields.includes('i')?'i':'key'));
    const y=expressionControl('y coordinate',field(fields.includes('j')?'j':'value'));
    args=()=>({source:sourceName,coordinates:[x.read(),y.read()]});
  }else if(action==='select'){
    controls.append(el('p','Keep matching occurrences as a new finite universe. Its later groups may differ from the original relation’s zero groups.',{class:'help'}));args=()=>({source:sourceName});
  }else if(action==='group_lens'){
    const selection={source:sourceName,capture:groupReport.capture,by:groupReport.by,group:groupChoice};
    controls.append(el('p','Create a relation for this exact captured group, intersecting any existing incidence. The original universe and its zero groups stay available.',{class:'help'}));
    controls.append(el('pre',groupLabel(groupReport,selectedGroup())));
    args=()=>selection;
  }
  const feedback=el('p',undefined,{id:'draft-status',role:'status','aria-live':'polite','aria-atomic':'true'});form.append(feedback);
  const effect=action==='place'?`Change placement of ${sourceName}`:action==='assignment'?`Create a new field on a copy of ${seed.expected}`:action==='product'?'Create a new object from the chosen factors':`Create a new object${sourceName&&!['integers','grid'].includes(action)?` from ${sourceName}`:''}`;
  form.append(el('p',effect,{class:'help',id:'draft-effect'}));
  const bar=el('div',undefined,{class:'form-actions'}), test=el('button','Preview',{type:'submit',class:'primary',id:'preview'}), apply=el('button','Apply',{type:'button',id:'apply'}),cancel=el('button','Cancel',{type:'button',id:'cancel'});apply.disabled=true;bar.append(test,apply,cancel);form.append(bar);
  const detail=el('details'), summary=el('summary','Read the declaration'),code=el('pre',undefined,{id:'declaration'});detail.append(summary,code);panel.append(detail);
  const getCommand=()=>({action,name:name.value,args:args()});
  function message(phase,text){feedback.dataset.phase=phase;feedback.textContent=text}
  function invalidate(){preview=null;apply.disabled=true;message('editing','Not previewed. Preview checks your current choices; Apply records them.')}
  function changed(){invalidate();try{code.textContent=JSON.stringify(getCommand(),null,2)}catch(e){code.textContent=e.message}status('Draft changed. Preview again before applying.');render()}
  draft.begin({target:sourceName,subject:['integers','grid'].includes(action)?'new source':action==='product'?'chosen factors':sourceName,title:labels[action],mode,groupReport,groupChoice,revision:editorRevision},panel,invalidate);
  form.addEventListener('change',changed);form.addEventListener('input',changed);changed();
  form.onsubmit=e=>{e.preventDefault();run(async()=>{
    try{
      if(editorRevision!==state.revision)throw Error('The workspace changed. Open this tool again.');
      const command=getCommand();preview=null;message('evaluating','Checking your current choices…');render();
      const result=await request('preview',{command});preview=result;render();apply.disabled=false;
      message('ready','Exact preview ready. Apply records this result; changing a choice requires another preview.');status('Exact preview ready. Apply keeps this capture; Cancel leaves history unchanged.');
    }catch(error){invalidate();message('failed',`Preview failed: ${error.message} Your applied work is unchanged.`);render();throw error}
  })};
  apply.onclick=()=>run(async()=>{if(!preview)return;try{const next=await request('commit',{token:preview.token});draft.clear();adopt(next);panel.replaceChildren(el('h2','Construction applied'),el('p','Choose any object and continue composing. Hold the canvas or use Options.'));await animate(next.motion);status('Applied one construction. Undo restores its captured predecessor.')}catch(error){invalidate();message('failed',`Apply failed: ${error.message} Preview again to check the draft.`);render();throw error}});
  cancel.onclick=cancelPreview;
}
function cancelPreview(){run(async()=>{await request('cancel');draft.clear();preview=null;render();$('panel').replaceChildren(el('h2','Draft discarded'),el('p','Your construction and its history are unchanged.'));status('Cancelled.')})}
function caseEditor(){
  if(busy||draft.current)return;
  linked.close();replay.clear();preview=null;
  const panel=$('panel'),editorRevision=state.revision;
  panel.replaceChildren(el('span','DECLARE / EVALUATE / APPLY',{class:'eyebrow'}),el('h2','Explore parameter cases'));
  const form=el('form'),fields=caseFields(state.parameters),report=el('div');
  const feedback=el('p',undefined,{id:'draft-status',role:'status','aria-live':'polite'});
  const bar=el('div',undefined,{class:'form-actions'}),evaluate=el('button','Evaluate case',{type:'submit',id:'preview',class:'primary'}),apply=el('button','Apply case',{type:'button',id:'apply'}),cancel=el('button','Cancel',{type:'button',id:'cancel'});
  bar.append(evaluate,apply,cancel);form.append(fields.box,feedback,report,bar);panel.append(form);
  panel.append(el('p','Undo and Redo restore captured cases without evaluation. Case changes appear as exact endpoints. Replay controls belong to captured construction edits.',{class:'help'}));
  function invalidate(){preview=null;apply.disabled=true;report.replaceChildren();feedback.dataset.phase='editing';feedback.textContent='Applied case unchanged. Evaluate to inspect the proposed results.'}
  draft.begin({target:active,subject:'parameter case',title:'Cases',mode,groupReport,groupChoice,revision:editorRevision},panel,invalidate);
  form.addEventListener('input',()=>{invalidate();render()});form.addEventListener('change',()=>{invalidate();render()});
  invalidate();render();
  form.onsubmit=e=>{e.preventDefault();run(async()=>{
    try{
      if(editorRevision!==state.revision)throw Error('The workspace changed. Open Cases again.');
      invalidate();feedback.dataset.phase='evaluating';feedback.textContent='Evaluating the proposed case…';
      preview=await request('preview-case',{parameters:fields.read(),active});
      report.replaceChildren(caseReport(preview));feedback.dataset.phase='ready';feedback.textContent='Case evaluated. Apply retains this capture, including reported failures.';
      apply.disabled=false;render();status('Case preview ready. The applied case is unchanged.');
    }catch(error){invalidate();feedback.dataset.phase='failed';feedback.textContent=error.message;render();throw error}
  })};
  apply.onclick=()=>run(async()=>{
    if(!preview)return;
    try{
      const next=await request('commit',{token:preview.token});draft.clear();adopt(next);
      panel.replaceChildren(el('h2',`Case applied · ${caseLabel(next.parameters)}`),caseReport(next,{applied:true}));
      status('New case applied. No replay time was advanced.');
    }catch(error){invalidate();feedback.dataset.phase='failed';feedback.textContent=error.message;render();throw error}
  });
  cancel.onclick=cancelPreview;
}
$('cases').onclick=caseEditor;
async function animate(frames){
  replay.record(frames,active);
  if(!matchMedia('(prefers-reduced-motion: reduce)').matches)await replay.play();
}
$('play-replay').onclick=()=>run(()=>replay.play());
for(const direction of ['undo','redo'])$(direction).onclick=()=>{if(draft.current)return;run(async()=>{const next=await request(direction,{active});adopt(next);$('panel').replaceChildren(el('h2',direction==='undo'?'Earlier capture restored':'Capture restored again'),el('p',next.change==='case'?`Exact case · ${caseLabel(next.parameters)}. No construction was evaluated; no intermediate cases were created.`:'Playback uses recorded endpoints. No construction was evaluated.'));await animate(next.motion);status(direction==='undo'?'Undone.':'Redone.')})};
function explain(){run(async()=>{
  const receipt=await request('inspect',{name:active,ref:selectedPoint});showReceipt(receipt);
})}
function showReceipt(receipt,heading='Value',back=null){receipts.show(receipt,{heading,back:back?{label:'Back to coverage',restore:back}:null})}
$('save').onclick=()=>run(async()=>{
  const response=await fetch('/api/export');const text=await response.text();
  const url=URL.createObjectURL(new Blob([text],{type:'application/json'})),a=el('a',undefined,{href:url,download:'kaleion-studio.json'});a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);status(`Saved captured definitions, evidence, and undo/redo.${draft.current?' The unfinished draft stays in this tab only.':''}`);
});
$('open').onclick=()=>{if(!draft.current)$('file').click()};$('file').onchange=()=>{if(draft.current)return;run(async()=>{const file=$('file').files[0];if(!file)return;const next=await request('import',{capture:await file.text()});adopt(next);$('panel').replaceChildren(el('h2','Saved workspace opened'),el('p','Its captures and history are available without reevaluating definitions.'));status('Reopened captured workspace.');$('file').value=''})};
window.addEventListener('blur',()=>{cancelHold();pointers.clear()});
document.addEventListener('keydown',e=>{if(e.key==='Escape'){cancelHold();if(!e.defaultPrevented&&e.target.tagName!=='SELECT'&&!$('menu').open&&draft.current&&!busy){parkDraft();render()}}});
new ResizeObserver(()=>{if(!busy)draw()}).observe($('canvas'));
adopt(await (await fetch('/api/state')).json());
