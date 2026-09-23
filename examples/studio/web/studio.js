import {creationActions,advancedActions,labels} from './context.js';
import {canvasShell} from './shell.js';
import {shapeControls,shapes} from './creation.js';
import {expressionEditor} from './expressions.js';
import {fieldKeys} from './groups.js';
import {draftSession} from './drafts.js';
import {coverageInspector} from './coverage.js';
import {linkedViews} from './evidence.js';
import {receiptInspector} from './receipts.js';
import {caseFields,caseLabel,caseReport} from './cases.js';
import {replayControls} from './replay.js';
import {comparisonInspector} from './comparison.js';
import {spatialWorkspace} from './workspace.js';
import {constructionInspector} from './construction.js';
import {canvasDocument,readDocument} from './document.js';
import {lensControls,totalControls,reuseControls} from './patterns.js';

const $ = id => document.getElementById(id);
const el = (tag, text, attrs={}) => {
  const node=document.createElement(tag); if(text!==undefined)node.textContent=text;
  for(const [key,value] of Object.entries(attrs))node.setAttribute(key,value);
  return node;
};
const field = name => ({field:name}), number = n => ({integer:String(n)});
const operation = (op,a,b) => ({op,args:[a,b]});
let state={revision:0,objects:[],undo:false,redo:false}, active=null, mode='objects';
let selectedPoint=null, preview=null, busy=false;
let groupReport=null, groupChoice=-1;
let comparisonChoices=null;
let sceneBeforePreview=null;
let objectTabsKey='';
const draft=draftSession();
const shell=canvasShell(document.querySelector('main'),{onClose:()=>{parkDraft();linked.close();render()}});
const linked=linkedViews($('linked-views'),{
  load:capture=>request('capture',{capture}),
  onVisibility:shown=>{if(shown){shell.open('evidence','Captured evidence');status('Reading a saved result. The canvas and camera stay in place.')}}
});
const receipts=receiptInspector({panel:$('activity'),run,query:request,linked,beforeShow:()=>{parkDraft();shell.open('evidence','Why this value?');construction.collapse()}});
const replay=replayControls($('replay'),{draw:frame=>board.frame(frame),restore:()=>board.frame(null),onPresentation:shown=>{
  $('scope').textContent=shown?'Playing a saved movement':resultScope();
}});
const board=spatialWorkspace($('workspace-view'),{
  select:selectObject,details:inspectObject,settings:$('object-view'),
  options:name=>name?inspectObject(name):openMenu(),
  combine:combinePanel,locked:()=>busy||!!preview,status,
  create:()=>openMenu(),
  inspect:(name,ref)=>{active=name;selectedPoint=ref;run(async()=>showReceipt(await request('inspect',{name,ref})))},
});
const construction=constructionInspector($('construction'),{
  state:()=>state,query:target=>request('construction',{name:target.root,path:target.path}),beforeNavigate:parkDraft,locked:()=>busy,
  remember:()=>({active,mode,selectedPoint,groupReport,groupChoice,board:board.remember(),linked:linked.remember(),activity:[...$('activity').childNodes]}),
  restore:async (saved,current)=>{
    linked.close();active=saved.active;mode=saved.mode;selectedPoint=saved.selectedPoint;
    groupReport=saved.groupReport;groupChoice=saved.groupChoice;
    shell.open('details',active);render();board.restore(saved.board);
    $('activity').replaceChildren(...saved.activity);
    if(saved.linked)await linked.open(saved.linked.spec,saved.linked);
    if(current())status('Returned to the same selection and camera. The construction is unchanged.');
  },
  navigate:async data=>{
    linked.close();replay.reset();
    if(data.names.length){
      active=data.names.includes(active)?active:data.names[0];selectedPoint=null;clearGroups();
      $('activity').replaceChildren();render();
    }else if(data.capture)await viewConstruction(data);
    else status(`Reading ${data.label}. No result was captured here; the canvas still shows ${active}.`);
  },
  view:data=>run(()=>viewConstruction(data))
});
async function viewConstruction(data){
  parkDraft();replay.reset();
  $('activity').replaceChildren(el('h3','Why this value?'),el('p','Choose an item in the saved result below to follow its value.'));
  await linked.open({title:`Captured result · ${data.label}`,
    detail:`${data.context}. This picture is the saved result of the inspected definition. No construction is evaluated.`,
    left:{capture:data.capture,label:data.label,contextLabel:`${data.context} · captured result`},
    inspect:ref=>run(async()=>showReceipt(await request('inspect-driver',{ref})))
  });
  shell.open('construction',data.label);
}
function inspectObject(name=active){
  if(busy||!name)return;
  selectObject(name);shell.open('details',name);
}
function selectObject(name){
  if(busy)return;linked.close();replay.reset();parkDraft();active=name;selectedPoint=null;preview=null;clearGroups();mode='objects';
  $('advanced-tools').open=false;
  construction.select(name);
  $('activity').replaceChildren();
  if(shell.visible)shell.open('details',name);
  render();
}
const object = () => state.objects.find(o=>o.name===active);
const displayed = () => preview?.objects.find(o=>o.name===preview.name) || object();
const selectedGroup=()=>groupReport?.revision===state.revision&&groupReport.name===active?groupReport.groups[groupChoice]:null;
const groupLabel=(report,group)=>report.by.map((field,i)=>`${field} = ${group.key_types[i]==='text'?JSON.stringify(group.key[i]):group.key[i]}`).join(', ')||'Whole domain';
function clearGroups(){groupReport=null;groupChoice=-1}
function resultScope(){return preview?'Preview · not saved':object()?.status==='ready'?`${object().rows.length} items${object().fields.includes('value')?'':' · tuples only'}`:object()?.error||''}
function status(text, error=false){$('status').textContent=text;$('status').classList.toggle('error',error)}
const busyControls=new Map();
let busyFocus=null;
function workspaceControls(){
  const drafting=!!draft.current;
  $('undo').disabled=busy||drafting||!state.undo;$('redo').disabled=busy||drafting||!state.redo;
  $('add').disabled=$('open').disabled=$('file').disabled=$('cases').disabled=busy||drafting;
  const selected=object(),ready=selected?.status==='ready';
  $('quick-lens').hidden=selected?.kind==='incidence';
  $('reuse-lens').hidden=selected?.kind!=='incidence';
  for(const id of ['quick-lens','axis-total','reuse-lens','combine'])$(id).disabled=busy||drafting||!ready;
  $('object-tools').querySelectorAll('[data-action]').forEach(b=>b.disabled=busy||drafting);
  document.querySelectorAll('[data-create]').forEach(b=>b.disabled=busy||drafting);
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
  if(!value){const a=$('apply');if(a)a.disabled=!preview&&a.textContent!=='Create';if(busyFocus?.isConnected&&!busyFocus.disabled&&document.activeElement===document.body)busyFocus.focus({preventScroll:true});busyFocus=null}
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
  construction.select(active);
  render();
}
function render(){
  replay.select(active);
  const tabsKey=JSON.stringify([active,state.objects.map(o=>[o.name,o.kind,o.status,o.error])]);
  if(tabsKey!==objectTabsKey){
    objectTabsKey=tabsKey;
    $('objects').replaceChildren(el('option','Select an object',{value:''}),...state.objects.map(o=>el('option',o.name,{value:o.name})));
    $('objects').value=active||'';
    $('advanced-actions').replaceChildren(...advancedActions(object()).map(action=>{
      const b=el('button',labels[action],{'data-action':action,type:'button'});b.onclick=()=>dispatch(action);return b;
    }));
  }
  $('welcome').hidden=!!state.objects.length||!!draft.current;
  $('surface-tools').hidden=!displayed();
  workspaceControls();
  $('title').textContent=displayed()?.name || 'Your blank canvas';
  $('scope').textContent=resultScope();
  draw();
  if(preview){
    if(!sceneBeforePreview)sceneBeforePreview=board.save();
    board.update({...state,objects:preview.objects.map(o=>o.name===preview.name?{...o,preview:true}:o)},preview.name);
  }else{
    board.update(state,active);
    if(sceneBeforePreview){const saved=sceneBeforePreview;sceneBeforePreview=null;board.load(saved)}
  }
}
$('quick-lens').onclick=()=>editor('lens',{workspace:true,scene:true,quick:true});
$('axis-total').onclick=()=>editor('total',{workspace:true,scene:true});
$('reuse-lens').onclick=()=>editor('reuse_lens',{workspace:true,scene:true});
$('objects').onchange=()=>{if($('objects').value)selectObject($('objects').value)};
$('combine').onclick=()=>combinePanel(active,null);
$('options').onclick=()=>inspectObject();
$('view-options').onclick=()=>{parkDraft();linked.close();shell.open('view',active);board.refresh()};
function draw(){board.highlight(mode==='groups'&&!preview?selectedGroup():null)}
function dispatch(action){
  if(action==='group_options'){mode='groups';groupPanel()}
  else if(action==='coverage')coveragePanel();
  else if(action==='compare')comparisonPanel();
  else editor(action,{quick:action==='lens'});
}
function openMenu(){
  if(busy||draft.current)return;
  $('menu-title').textContent='Create a shape';
  $('menu-actions').replaceChildren(...creationActions.map(kind=>{
    const b=el('button',shapes[kind].title,{'data-action':kind});
    b.onclick=()=>{$('menu').close();editor('shape',{shape:kind})};return b;
  }));
  if(!$('menu').open)$('menu').showModal();
}
$('add').onclick=openMenu;$('close-menu').onclick=()=>$('menu').close();
document.querySelectorAll('[data-create]').forEach(b=>b.onclick=()=>editor('shape',{shape:b.dataset.create}));

function parkDraft(){
  if(!draft.current||draft.current.parked)return;
  draft.park();preview=null;
  $('activity').replaceChildren(el('h2','Your draft is parked'),el('p','Inspect another object, then choose Resume draft to continue.'));
  workspaceControls();status('Draft retained. Browsing does not apply it.');
}
$('resume-draft').onclick=()=>{
  if(busy||!draft.current)return;
  try{
    shell.open('edit',draft.current.context.title);const context=draft.resume(state.revision);active=context.target;mode=context.mode;
    construction.select(active);construction.collapse();
    groupReport=context.groupReport;groupChoice=context.groupChoice;selectedPoint=null;
    document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.mode===mode)));
    render();$('activity').scrollIntoView({block:'nearest'});($('result-name')||$('activity').querySelector('input,button'))?.focus({preventScroll:true});
    status(preview?'Exact preview ready to apply.':'Draft restored on its original target. Preview to check it.');
  }catch(error){status(error.message,true)}
};
$('discard-draft').onclick=()=>cancelPreview();

function options(values,selected){const s=el('select');for(const v of values)s.append(el('option',v,{value:v}));if(selected!==undefined)s.value=selected;return s}
function labeled(parent,text,node){const label=el('label',text);label.append(node);parent.append(label);return node}
function input(value){const n=el('input',undefined,{type:'text'});n.value=value;return n}
function combinePanel(from,to){
  if(busy)return;
  if(draft.current){status('Resume or discard your draft before proposing another construction.',true);return}
  linked.close();replay.reset();preview=null;
  shell.open('edit','Combine');construction.collapse();
  const panel=$('activity');panel.replaceChildren(el('span','CONNECT / REVIEW / PREVIEW',{class:'eyebrow'}),el('h2','Combine objects'));
  const source=labeled(panel,'Source object',options(state.objects.map(o=>o.name),from));source.id='combine-source';
  const target=labeled(panel,'Destination object',options(state.objects.map(o=>o.name),to||state.objects.find(o=>o.name!==from)?.name||from));target.id='combine-target';
  const product=el('button','Make every pair',{id:'combine-product',type:'button'}),place=el('button','Use source values as destination height',{id:'combine-place',type:'button'});
  const reuse=el('button','Use lens on destination',{id:'combine-lens',type:'button'});
  const choices=el('div',undefined,{class:'combine-choices'}),reason=el('p',undefined,{class:'help',id:'combine-reason'});choices.append(product,place,reuse);panel.append(choices,reason);
  panel.append(el('p','Choose an operation, review its roles or matching keys, then Preview and Apply. Connecting never applies a change by itself.',{class:'help'}));
  function eligibility(){
    const a=state.objects.find(o=>o.name===source.value),b=state.objects.find(o=>o.name===target.value);
    const ready=a?.status==='ready'&&b?.status==='ready',collections=a?.kind!=='incidence'&&b?.kind!=='incidence';
    product.disabled=!ready||!collections;place.disabled=product.disabled||!a?.fields.includes('value');
    reuse.hidden=a?.kind!=='incidence';reuse.disabled=!ready||b?.kind==='incidence'||!a?.reusable_rule?.available;
    reason.textContent=!ready?'Both objects need a successful captured result.':a?.kind==='incidence'?(a.reusable_rule?.available?'Map this lens’s inputs to destination fields. Preview shows its incidence; the original stays in place.':a.reusable_rule?.reason):!collections?'Choose a lens as source and a collection or arrangement as destination to reuse its rule.':`Every pair creates ${a.rows.length} × ${b.rows.length} item tuples. Height reads need a unique source key for each destination key; the next editor shows both. The scene uses one scale; object offsets only organize the view.`;
  }
  source.onchange=target.onchange=eligibility;eligibility();
  product.onclick=()=>editor('product',{scene:true,factors:{left:source.value,right:target.value}});
  reuse.onclick=()=>editor('reuse_lens',{workspace:true,scene:true,source:source.value,target:target.value});
  place.onclick=()=>{
    const destination=state.objects.find(o=>o.name===target.value);active=target.value;
    editor('place',{source:target.value,coordinates:[field(destination.fields.includes('i')?'i':'key'),{read:{object:source.value,on:field('key'),key:field('key'),value:field('value')}}]});
  };
  status(`Proposing a connection from ${from}${to?` to ${to}`:''}. Applied work is unchanged.`);
  panel.focus({preventScroll:true});panel.scrollIntoView({block:'nearest'});
}
function groupPanel(){
  shell.open('edit','Groups');construction.collapse();
  linked.close();parkDraft();const source=object();
  const panel=$('activity');panel.replaceChildren(el('span','SELECT BY A DECLARED KEY',{class:'eyebrow'}),el('h2','Groups'));
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
    function summary(){const g=selectedGroup();receipt.textContent=g?`${g.count} incident items · ${g.population} items in the group. An empty group remains selectable.`:'No observed groups. Choose a declared axis or explicitly construct the expected bins.'}
    select.onchange=()=>{groupChoice=Number(select.value);summary();draw()};summary();
    for(const action of ['group_lens','measure','coverage']){const b=el('button',labels[action],{type:'button'});b.onclick=()=>dispatch(action);results.append(b)}
  }
  show();
}
function coveragePanel(){
  shell.open('edit','Coverage');construction.collapse();
  linked.close();parkDraft();const source=object();
  const box=coverageInspector({source,objects:state.objects,initialBy:groupReport?.name===active?groupReport.by:[],run,
    check:spec=>request('coverage',spec),canAdopt:()=>!draft.current,
    inspect:async(ref,trigger)=>{const receipt=await request('inspect-driver',{ref});showReceipt(receipt,'Value',()=>{$('activity').replaceChildren(box);trigger.focus({preventScroll:true})})},
    clearLink:()=>linked.close(),
    chooseLink:index=>linked.choose(index,false),
    link:async(report,rows,index,onChoose)=>{
      const back=()=>{$('activity').replaceChildren(box);$('view-coverage').focus({preventScroll:true})};
      await linked.open({title:'Expected items and their matches',
        inspect:ref=>run(async()=>showReceipt(await request('inspect-driver',{ref}),'Value',back)),
        detail:'Links follow the declared coverage keys. Faint points give context; a missing match does not create a source point.',
        left:{capture:report.expected_capture,label:'Expected items'},
        right:{capture:report.capture,label:'Candidates'},index,onChoose,
        links:rows.map(row=>({label:`${row.key.map((key,i)=>row.key_types[i]==='text'?JSON.stringify(key):String(key)).join(', ')} · ${row.count} matches${row.outside?' · outside':''}`,
          left:row.expected_ref?[{ref:row.expected_ref,note:'Expected item'}]:[],
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
  $('activity').replaceChildren(box);
}
function expr(initial,fields){
  return expressionEditor(initial,fields,state.objects.filter(o=>o.kind!=='incidence'&&o.status==='ready'),Object.keys(state.parameters||{}));
}
function comparisonPanel(){
  shell.open('edit','Compare');construction.collapse();
  linked.close();replay.clear();parkDraft();const source=object();
  async function inspect(ref,trigger,note){
    const saved=linked.remember(),receipt=await request('inspect-driver',{ref});
    receipts.show(receipt,{heading:'Source value',back:{label:'Back to comparison',restore:async()=>{
      if(saved)await linked.open(saved.spec,saved);else linked.close();
      $('activity').replaceChildren(box);(trigger.isConnected?trigger:$('view-comparison')).focus({preventScroll:true});
    }}});
    if(note)$('activity').insertBefore(el('p',note,{class:'comparison-context'}),$('activity').querySelector('pre'));
  }
  const box=comparisonInspector({source,objects:state.objects,initial:comparisonChoices,
    remember:spec=>{comparisonChoices=spec},run,check:spec=>request('compare',spec),inspect,
    clearLink:()=>linked.close(),chooseLink:index=>linked.choose(index,false),
    link:async(report,rows,index,onChoose)=>{
      const note=(row,side)=>`Compared ${side} field ${report[`${side}_value`]} = ${row[side]}. Residual ${row.residual??'unavailable'}.`;
      await linked.open({title:'Compared fields under declared keys',
        detail:`Residual = left − right. Expected domain: ${report.expected} by (${report.expected_by.join(', ')}). Faint points give context; missing values stay absent.`,
        left:{capture:report.left_capture,label:`Left · ${report.name}.${report.left_value}`,valueField:report.left_value},
        right:{capture:report.right_capture,label:`Right · ${report.right}.${report.right_value}`,valueField:report.right_value},index,onChoose,
        links:rows.map(row=>({label:`(${row.key.join(', ')}) · ${row.status}${row.residual!==null?` · residual ${row.residual}`:''}`,
          left:row.left_ref?[{ref:row.left_ref,note:note(row,'left'),comparisonNote:note(row,'left')}]:[],
          right:row.right_ref?[{ref:row.right_ref,note:note(row,'right'),comparisonNote:note(row,'right')}]:[],
          emptyLeft:'No left item for this key. Absence is not a zero value.',
          emptyRight:'No right item for this key. Absence is not a zero value.'})),
        inspect:(ref,trigger,item)=>run(()=>inspect(ref,trigger,item?.comparisonNote)),
      });
    },
  });
  $('activity').replaceChildren(box);
}
function editor(action,seed=null){
  seed=seed||{};
  linked.close();
  if(draft.current){status('Resume or discard your draft before starting another construction.',true);return}
  shell.open('edit',action==='shape'?`Create a ${shapes[seed.shape].title.toLowerCase()}`:labels[action]);
  construction.select(active);construction.collapse();
  replay.clear();
  preview=null;const editorRevision=state.revision,sourceName=seed?.source||active;render();
  const panel=$('activity');panel.replaceChildren(el('span','DECLARE / PREVIEW / APPLY',{class:'eyebrow'}),el('h2',labels[action]));
  const form=el('form'), controls=el('fieldset');controls.style.cssText='border:0;padding:0;margin:0;min-width:0';form.append(controls);panel.append(form);
  const source=state.objects.find(o=>o.name===sourceName), fields=source?.fields||['i','j','value','index','key'];
  if(source&&!['shape','integers','sequence','grid'].includes(action)){const inspectSource=el('button',`On ${sourceName} · inspect source`,{type:'button',class:'draft-source'});inspectSource.onclick=()=>selectObject(sourceName);form.before(inspectSource)}
  const name=labeled(controls,'Result name',input(action==='place'?sourceName:`${action==='shape'?shapes[seed.shape].title:labels[action]} ${state.objects.length+1}`));
  name.id='result-name';if(action==='place')name.readOnly=true;
  let args,shape;
  function expressionControl(label,spec,fs=fields){const card=expr(spec,fs);card.box.setAttribute('role','group');card.box.setAttribute('aria-label',label);controls.append(el('label',label),card.box);return card}
  if(action==='shape'){
    shape=shapeControls(seed.shape,state.parameters);controls.append(shape.box);
  }else if(action==='values'){
    const value=labeled(controls,'Value at each location',input(source?.axes?.join(' + ')||'index'));value.id='values-formula';
    controls.append(el('p','Use index fields, integer constants, + − * // %, and parentheses. The source stays available.',{class:'help'}));
    args=()=>({source:sourceName,value:{formula:value.value}});
  }else if(action==='product'){
    const sources=state.objects.filter(o=>o.kind!=='incidence'&&o.status==='ready'), choices=[];
    for(const role of ['left','right']){
      const r=labeled(controls,'Role name',input(role)),s=labeled(controls,'Source for this role',options(sources.map(o=>o.name),seed?.factors?.[role]||active));
      const copies=el('div');controls.append(copies);let checks=[];
      const rebuild=()=>{copies.replaceChildren(el('label','Fields to copy into this role'));checks=sources.find(o=>o.name===s.value).fields.map(f=>{const l=el('label',f),c=el('input',undefined,{type:'checkbox',value:f});c.checked=f==='value';c.style.cssText='width:auto;display:inline;margin-right:8px;vertical-align:middle';l.prepend(c);copies.append(l);return c})};s.onchange=rebuild;rebuild();choices.push(()=>[r.value,{source:s.value,fields:checks.filter(c=>c.checked).map(c=>c.value)}]);
    }
    controls.append(el('p','Every pair of current source slots. Copied fields are named role_field; labels do not identify tuples.',{class:'help'}));
    args=()=>{const entries=choices.map(f=>f());if(entries[0][0]===entries[1][0])throw Error('Choose distinct role names');return {factors:Object.fromEntries(entries)}};
  }else if(action==='field'){
    const f=labeled(controls,'New field name',input('total'));f.id='field-name';const value=expressionControl('Field definition',operation('+',field(fields[0]),number(1)));
    args=()=>({source:sourceName,field:f.value,value:value.read()});
  }else if(action==='lens'&&seed?.quick){
    const rule=lensControls(source,expr);controls.append(rule.box);
    args=()=>({source:sourceName,rule:rule.read()});
  }else if(action==='reuse_lens'){
    const reuse=reuseControls(source,state.objects,seed?.target);controls.append(reuse.box);
    args=()=>({source:sourceName,...reuse.read()});
  }else if(action==='total'){
    const total=totalControls(source,expr);controls.append(total.box);
    args=()=>({source:sourceName,...total.read()});
  }else if(action==='lens'){
    const rule=expressionControl('Relation · true means incident',operation('=',field('value'),number(0)));
    args=()=>({source:sourceName,rule:rule.read()});
  }else if(action==='measure'){
    const reducer=labeled(controls,'Measurement',options(['count','sum','rank','prefix_sum']));reducer.id='reducer';
    reducer.lastElementChild.textContent='Prefix sum · before each item';
    const groups=fieldKeys(fields,mode==='groups'?(groupReport?.by||[]):[],'Group keys');controls.append(groups.box);
    const meaning=el('p',undefined,{class:'help',id:'measurement-meaning'});controls.append(meaning);
    const weight=expressionControl('Weight',field(fields.includes('value')?'value':source.axes[0]||'index'));
    const order=fieldKeys(fields,['index'],'Member order','Choose at least one ordering field');order.box.id='rank-order';controls.append(order.box);
    const key=labeled(controls,'Unique item key',options(fields,'key'));key.id='rank-key';
    function measurementFields(){
      const prefix=reducer.value==='prefix_sum',ordered=prefix||reducer.value==='rank';
      weight.box.hidden=weight.box.previousElementSibling.hidden=!prefix&&reducer.value!=='sum';order.box.hidden=key.parentElement.hidden=!ordered;
      meaning.textContent=ordered
        ?`Return one measurement per selected item. ${prefix?'Sum the weights of earlier items':'Count earlier items'} within each group. No group fields means one group. The first result is zero; the current item is excluded. Order ties and duplicate item keys must be resolved explicitly.${prefix?' Zero and negative weights still contribute.':''}`
        :'No group fields means one total. Count and Sum retain zero groups from the declared domain; they do not invent missing keys.';
    }
    reducer.onchange=measurementFields;measurementFields();
    args=()=>({source:sourceName,reducer:reducer.value,by:groups.read(),weight:weight.read(),order:order.read(),key:key.value});
  }else if(action==='assignment'){
    controls.append(el('p',`Assign onto ${seed.expected}, matching ${seed.expected_by.join(', ')} to ${seed.by.join(', ')} in ${seed.source}. Its identities, positions, and labels are retained. Coverage is checked again before adoption.`,{class:'help'}));
    const assigned=labeled(controls,'New field name',input('assigned'));assigned.id='assigned-field';
    const value=expressionControl('Value supplied by the unique match',field('value'));
    args=()=>({...seed,value:value.read(),field:assigned.value});
  }else if(action==='place'){
    controls.append(el('p','Change this object’s placement. Use a Keyed read to let a measurement supply a coordinate. Existing derived objects keep their earlier input definitions.',{class:'help'}));
    const dimensions=labeled(controls,'Number of coordinates',options(['1','2','3'],String(Math.max(2,source.dimension||source.axes.length))));
    const coordinates=['x','y','z'].map((axis,i)=>expressionControl(`${axis} coordinate`,seed?.coordinates?.[i]||((source.axes[i]||i===0)?field(source.axes[i]||'key'):i===1&&fields.includes('value')?field('value'):number(0))));
    function showCoordinates(){coordinates.forEach((card,i)=>{card.box.hidden=card.box.previousElementSibling.hidden=i>=Number(dimensions.value)})}
    dimensions.onchange=showCoordinates;showCoordinates();
    args=()=>({source:sourceName,coordinates:coordinates.slice(0,Number(dimensions.value)).map(card=>card.read())});
  }else if(action==='select'){
    controls.append(el('p','Keep matching items as a new finite universe. Its later groups may differ from the original relation’s zero groups.',{class:'help'}));args=()=>({source:sourceName});
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
  const getCommand=()=>shape?{...shape.read(),name:name.value}:{action,name:name.value,args:args()};
  function message(phase,text){feedback.dataset.phase=phase;feedback.textContent=text}
  function invalidate(){preview=null;apply.disabled=!shape;message('editing','Not previewed. Preview checks your current choices; Apply records them.')}
  function changed(){invalidate();try{code.textContent=JSON.stringify(getCommand(),null,2)}catch(e){code.textContent=e.message}status('Draft changed. Preview again before applying.');render()}
  draft.begin({target:sourceName,subject:['shape','integers','grid','sequence'].includes(action)?'new source':action==='product'?'chosen factors':sourceName,title:labels[action],mode,groupReport,groupChoice,revision:editorRevision},panel,invalidate);
  form.addEventListener('change',changed);form.addEventListener('input',changed);changed();
  form.onsubmit=e=>{e.preventDefault();run(async()=>{
    try{
      if(editorRevision!==state.revision)throw Error('The workspace changed. Open this tool again.');
      const command=getCommand();preview=null;message('evaluating','Checking your current choices…');render();
      const result=await request('preview',{command});preview=result;render();apply.disabled=false;
      board.fit();
      const object=result.objects.find(o=>o.name===result.name),count=object?.rows?.filter(r=>r.match).length;
      message('ready',`${object?.kind==='incidence'?`${count} of ${object.rows.length} match. `:''}Exact preview ready. Apply keeps it; changing a choice requires another preview.`);status('Exact preview ready. Apply keeps this capture; Cancel leaves history unchanged.');
    }catch(error){invalidate();message('failed',`Preview failed: ${error.message} Your applied work is unchanged.`);render();throw error}
  })};
  if(shape){apply.textContent='Create';apply.disabled=false}
  apply.onclick=()=>run(async()=>{
    try{
      if(!preview&&shape){preview=await request('preview',{command:getCommand()});render()}
      if(!preview)return;
      const next=await request('commit',{token:preview.token});draft.clear();adopt(next);
      shell.open('details',active);$('activity').replaceChildren();
      board.fit();
      await animate(next.motion);status('Saved on the canvas. Undo returns to the previous result.');
    }catch(error){invalidate();message('failed',error.message);render();throw error}
  });
  cancel.onclick=cancelPreview;
  name.focus({preventScroll:true});
}
function cancelPreview(){run(async()=>{await request('cancel');draft.clear();preview=null;render();$('activity').replaceChildren(el('h2','Draft discarded'),el('p','Your construction and its history are unchanged.'));status('Cancelled.')})}
function caseEditor(){
  if(busy||draft.current)return;
  shell.open('edit','Parameters');
  construction.collapse();
  linked.close();replay.clear();preview=null;
  const panel=$('activity'),editorRevision=state.revision;
  panel.replaceChildren(el('span','DECLARE / EVALUATE / APPLY',{class:'eyebrow'}),el('h2','Change parameters'));
  const form=el('form'),fields=caseFields(state.parameters),report=el('div');
  const feedback=el('p',undefined,{id:'draft-status',role:'status','aria-live':'polite'});
  const bar=el('div',undefined,{class:'form-actions'}),evaluate=el('button','Preview results',{type:'submit',id:'preview',class:'primary'}),apply=el('button','Keep results',{type:'button',id:'apply'}),cancel=el('button','Cancel',{type:'button',id:'cancel'});
  bar.append(evaluate,apply,cancel);form.append(fields.box,feedback,report,bar);panel.append(form);
  panel.append(el('p','Undo and Redo restore captured cases without evaluation. Case changes appear as exact endpoints. Replay controls belong to captured construction edits.',{class:'help'}));
  function invalidate(){preview=null;apply.disabled=true;report.replaceChildren();feedback.dataset.phase='editing';feedback.textContent='Current results unchanged. Evaluate to inspect the proposed results.'}
  draft.begin({target:active,subject:'parameter values',title:'Parameters',mode,groupReport,groupChoice,revision:editorRevision},panel,invalidate);
  form.addEventListener('input',()=>{invalidate();render()});form.addEventListener('change',()=>{invalidate();render()});
  invalidate();render();
  form.onsubmit=e=>{e.preventDefault();run(async()=>{
    try{
      if(editorRevision!==state.revision)throw Error('The workspace changed. Open Parameters again.');
      invalidate();feedback.dataset.phase='evaluating';feedback.textContent='Evaluating the new parameter values…';
      preview=await request('preview-case',{parameters:fields.read(),active});
      report.replaceChildren(caseReport(preview));feedback.dataset.phase='ready';feedback.textContent='Results evaluated. Apply retains this capture, including reported failures.';
      apply.disabled=false;render();status('Preview ready. Your current results are unchanged.');
    }catch(error){invalidate();feedback.dataset.phase='failed';feedback.textContent=error.message;render();throw error}
  })};
  apply.onclick=()=>run(async()=>{
    if(!preview)return;
    try{
      const next=await request('commit',{token:preview.token});draft.clear();adopt(next);
      panel.replaceChildren(el('h2',`Parameters saved · ${caseLabel(next.parameters)}`),caseReport(next,{applied:true}));
      status('New parameter values saved. Playback is separate.');
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
for(const direction of ['undo','redo'])$(direction).onclick=()=>{if(draft.current)return;run(async()=>{const next=await request(direction,{active});adopt(next);$('activity').replaceChildren(el('h2',direction==='undo'?'Earlier capture restored':'Capture restored again'),el('p',next.change==='case'?`Exact case · ${caseLabel(next.parameters)}. No construction was evaluated; no intermediate cases were created.`:'Playback uses recorded endpoints. No construction was evaluated.'));await animate(next.motion);status(direction==='undo'?'Undone.':'Redone.')})};
function showReceipt(receipt,heading='Value',back=null){receipts.show(receipt,{heading,back:back?{label:'Back to coverage',restore:back}:null})}
$('save').onclick=()=>$('save-menu').showModal();$('close-save').onclick=()=>$('save-menu').close();
for(const choice of ['canvas','math'])$('save-'+choice).onclick=()=>{$('save-menu').close();run(async()=>{
  const response=await fetch('/api/export');const text=await response.text();
  const content=choice==='canvas'?canvasDocument(text,sceneBeforePreview||board.save()):text;
  const url=URL.createObjectURL(new Blob([content],{type:'application/json'})),a=el('a',undefined,{href:url,download:choice==='canvas'?'kaleion-canvas.json':'kaleion-workspace.json'});a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);status(`Saved ${choice==='canvas'?'canvas and view':'mathematics'}, captured evidence, and undo/redo.${draft.current?' The unfinished draft stays in this tab only.':''}`);
})};
$('open').onclick=()=>{if(!draft.current)$('file').click()};$('file').onchange=()=>{if(draft.current)return;run(async()=>{const file=$('file').files[0];if(!file)return;const document=readDocument(await file.text());const next=await request('import',{capture:document.workspace});comparisonChoices=null;board.reset();adopt(next);if(document.scene){if(next.objects.some(o=>o.name===document.scene.selected?.name)){active=document.scene.selected.name;construction.select(active);render()}board.load(document.scene);selectedPoint=board.save().selected?.ref||null} $('activity').replaceChildren(el('h2','Saved workspace opened'),el('p','Captured definitions and history are restored. A canvas document also restores its scene view.'));status('Reopened captured workspace.');$('file').value=''})};
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!e.defaultPrevented&&e.target.tagName!=='SELECT'&&!$('menu').open&&draft.current&&!busy){parkDraft();render()}});
new ResizeObserver(()=>document.querySelector('.workbench').style.setProperty('--transport-clearance',`${$('replay').getBoundingClientRect().height+44}px`)).observe($('replay'));
adopt(await (await fetch('/api/state')).json());
