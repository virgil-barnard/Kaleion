// Common scene: captured geometry × object view offset × one camera.
import {UNIT,projection,planes,chartDefaults,geometry,corners,projectedBounds,cellFaces,refKey} from './scene.js';
import {cameraControls} from './camera.js';

const NS='http://www.w3.org/2000/svg',BUDGET=6000;
const svgNode=(tag,attrs={},text)=>{const n=document.createElementNS(NS,tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);if(text!==undefined)n.textContent=text;return n};
const el=(tag,text,attrs={})=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);return n};
const plus=(a,b)=>a.map((v,i)=>v+b[i]);
const initialCamera=()=>({x:-80,y:-500,w:900,h:600,yaw:0,pitch:0});

export function spatialWorkspace(host,{select,focus,options,combine,inspect,create,locked,status}){
  const canvas=host.querySelector('svg'),grid=svgNode('g',{'aria-hidden':'true',class:'scene-grid'}),wires=svgNode('g',{'aria-hidden':'true'}),frames=svgNode('g'),marks=svgNode('g'),labels=svgNode('g');
  canvas.append(grid,wires,frames,marks,labels);
  const layout=new Map(),cards=new Map(),bounds=new Map(),models=new Map(),pointers=new Set();
  let state={objects:[]},active=null,tool='move',drag=null,view=initialCamera(),initialized=false,holdClick=false,chosen=null,drawn=[];
  const help=host.querySelector('[data-spatial-help]'),list=host.querySelector('[data-connection-list]'),caption=host.querySelector('[data-scene-caption]');
  const controls=cameraControls({name:'workspace',fit,zoom:factor=>zoom(factor),pan:(x,y)=>{view.x-=x*view.w/700;view.y-=y*view.h/450;draw()}});
  function button(text,label,fn){const b=el('button',text,{type:'button','aria-label':label});b.onclick=fn;return b}
  controls.prepend(button('Selected','Center selected object',centerSelected));host.querySelector('[data-spatial-camera]').append(controls);
  const orientations=host.querySelector('[data-scene-planes]');
  for(const [name,label] of [['xy','XY'],['xz','XZ'],['yz','YZ'],['space','3D']])orientations.append(button(label,`${label} workspace view`,()=>{cancel();[view.yaw,view.pitch]=planes[name];draw();fit()}));
  const orbit=el('details'),summary=el('summary','Rotate'),row=el('div',undefined,{class:'row'});orbit.append(summary,row);orientations.append(orbit);
  for(const [label,yaw,pitch] of [['left',-.2,0],['right',.2,0],['up',0,-.2],['down',0,.2]])row.append(button(label,`Rotate workspace view ${label}`,()=>{view.yaw+=yaw;view.pitch+=pitch;draw()}));
  host.querySelector('[data-combine]').onclick=()=>{if(active&&!locked())combine(active,null)};
  host.querySelector('[data-scene-source]').onclick=()=>{if(!locked())create()};
  for(const b of host.querySelectorAll('[data-workspace-tool]'))b.onclick=()=>{cancel();tool=b.dataset.workspaceTool;syncTools();draw()};
  function syncTools(){
    host.querySelectorAll('[data-workspace-tool]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.workspaceTool===tool)));
    help.textContent=tool==='move'?'Drag a name to move its view. Tap a cell or point to inspect it. Drag empty space to pan.':tool==='connect'?'Drag a source name onto a destination to propose a combination. Dashed paths are reads; definitions remain fixed.':'Drag the canvas to orbit. XY / XZ / YZ and Rotate offer the same view changes without dragging.';
    list.hidden=tool!=='connect';
  }
  function rebuildModels(){
    models.clear();
    for(const obj of state.objects){const settings=layout.get(obj.name);models.set(obj.name,geometry(obj,settings))}
  }
  function ensureLayout(){
    const present=new Set(state.objects.map(o=>o.name));for(const name of layout.keys())if(!present.has(name))layout.delete(name);
    for(const obj of state.objects){
      if(!layout.has(obj.name)){
        const settings=chartDefaults(obj),model=geometry(obj,settings);
        const existing=[...layout.values()];
        const last=existing.at(-1),right=last?last.pose[0]+(models.get(last.name)?.high[0]||4):0;
        const i=layout.size;
        // Automatic shelf layout uses common units, never independent scaling.
        const pose=[i%3===0?0:right+4-model.low[0],i%3===0&&i?Math.min(...existing.map(o=>o.pose[1]-(models.get(o.name)?.high[1]||1)))-7:existing.at(-1)?.pose[1]||0,0];
        layout.set(obj.name,{name:obj.name,pose,...settings});models.set(obj.name,model);
      }
      const settings=layout.get(obj.name),available=[...new Set([...(obj.axes||[]),'index'])];
      if(settings.axes.some(a=>!available.includes(a)))settings.axes=available.slice(0,3);
      if(!obj.placed&&settings.chart==='placement')settings.chart='logical';
    }
    rebuildModels();
  }
  function camera(){canvas.setAttribute('viewBox',`${view.x} ${view.y} ${view.w} ${view.h}`);canvas.dataset.orientation=JSON.stringify([view.yaw,view.pitch]);}
  function fit(){
    cancel();draw();const all=[...bounds.values()];if(!all.length)return;
    const left=Math.min(...all.map(b=>b.left))-40,right=Math.max(...all.map(b=>b.right))+40,top=Math.min(...all.map(b=>b.top))-50,bottom=Math.max(...all.map(b=>b.bottom))+40;
    const w=Math.max(300,right-left,(bottom-top)*1.5);view={...view,x:(left+right-w)/2,y:(top+bottom-w/1.5)/2,w,h:w/1.5};draw();
  }
  function centerSelected(){
    cancel();const b=bounds.get(active);if(!b)return;
    const w=Math.max(220,(b.right-b.left)+70,(b.bottom-b.top+100)*1.5);view={...view,x:(b.left+b.right-w)/2,y:(b.top+b.bottom-w/1.5)/2,w,h:w/1.5};draw();
  }
  function zoom(factor){cancel();const w=Math.min(1e9,Math.max(80,view.w/factor));view={...view,x:view.x+(view.w-w)/2,y:view.y+(view.h-w/1.5)/2,w,h:w/1.5};draw()}
  function point(event){const p=canvas.createSVGPoint();p.x=event.clientX;p.y=event.clientY;return p.matrixTransform(canvas.getScreenCTM().inverse())}
  function nameAt(event){return event.target.closest('[data-workspace-object]')?.dataset.workspaceObject||event.target.closest('[data-scene-owner]')?.dataset.sceneOwner}
  function targetAt(p,except){return [...state.objects].reverse().find(o=>{const b=bounds.get(o.name);return o.name!==except&&p.x>=b.left&&p.x<=b.right&&p.y>=b.top&&p.y<=b.bottom})?.name}
  function drawGrid(project){
    grid.replaceChildren();if(!state.objects.length)return;
    const settings=[...layout.values()],span=Math.max(12,...settings.map(s=>Math.max(...s.pose.map(Math.abs))));
    const step=10**Math.floor(Math.log10(Math.max(1,span/12))),extent=Math.ceil((span+10)/step)*step;
    for(let t=-extent;t<=extent;t+=step)for(const axis of [0,1]){
      const p=axis?[-extent,t,0]:[t,-extent,0],q=axis?[extent,t,0]:[t,extent,0],a=project.point(p),b=project.point(q);
      grid.append(svgNode('line',{x1:a[0],y1:a[1],x2:b[0],y2:b[1],class:t===0?'scene-grid-axis':''}));
    }
  }
  function draw(){
    const focused=document.activeElement?.dataset.workspaceObject,project=projection(view.yaw,view.pitch);
    camera();frames.replaceChildren();marks.replaceChildren();labels.replaceChildren();cards.clear();bounds.clear();drawn=[];drawGrid(project);
    let budget=BUDGET;const counts=new Map();
    for(const obj of [...state.objects].sort((a,b)=>(b.name===active)-(a.name===active))){
      const settings=layout.get(obj.name),model=models.get(obj.name);let count=0;
      model.positions.forEach((p,i)=>{if(!model.visible(p)||budget<=0)return;budget--;count++;const world=plus(p,settings.pose),screen=project.point(world);drawn.push({name:obj.name,row:obj.rows[i],local:p,world,screen,settings,model})});counts.set(obj.name,count);
    }
    for(const obj of state.objects){
      const s=layout.get(obj.name),m=models.get(obj.name),offset=project.point(s.pose),local=corners(m.low,m.high).map(p=>project.point(p));
      const b=projectedBounds(local);if(!m.positions.length){b.right=Math.max(b.right,b.left+100);b.bottom=Math.max(b.bottom,b.top+70)}
      const total=obj.rows?.length||0,visible=m.positions.filter(m.visible).length;
      const meta=obj.status==='failed'?'Evaluation failed':!m.valid?'Geometry unavailable':`${obj.preview?'Preview · ':''}${total} occurrences${s.slice?` · ${visible} in slice`:''}${counts.get(obj.name)<visible?` · ${counts.get(obj.name)} drawn`:''}`;
      const labelWidth=Math.max(130,Math.min(320,Math.max(obj.name.length*8,meta.length*5.5)+22));
      const bound={left:b.left+offset[0]-14,right:Math.max(b.right+14,b.left-10+labelWidth)+offset[0],top:b.top+offset[1]-53,bottom:b.bottom+offset[1]+14};bounds.set(obj.name,bound);
      const frame=svgNode('g',{'data-scene-frame':obj.name,transform:`translate(${offset[0]},${offset[1]})`});
      frame.append(svgNode('rect',{x:b.left-10,y:b.top-10,width:b.right-b.left+20,height:b.bottom-b.top+20,rx:3,class:`scene-outline ${active===obj.name?'selected':''}`}));
      const origin=project.point([0,0,0]);
      m.axes.forEach((axis,i)=>{const end=[0,0,0];end[i]=1.4;const p=project.point(end);frame.append(svgNode('line',{x1:origin[0],y1:origin[1],x2:p[0],y2:p[1],class:`scene-axis axis-${i}`}),svgNode('text',{x:p[0]+3,y:p[1]-3,class:`scene-axis-label axis-${i}`},axis))});
      frames.append(frame);
      const card=svgNode('g',{'data-workspace-object':obj.name,class:`workspace-object ${obj.name===active?'selected':''}`,transform:`translate(${offset[0]},${offset[1]})`,role:'button',tabindex:'0','aria-label':`${obj.name}. Drag name to move view. Space to select; Enter to focus; Shift F10 for options.`,'aria-pressed':String(obj.name===active)});
      card.append(svgNode('rect',{x:b.left-10,y:b.top-52,width:labelWidth,height:40,rx:7,class:'scene-handle'}),svgNode('text',{x:b.left,y:b.top-34,class:'workspace-name'},obj.name.length>30?obj.name.slice(0,28)+'…':obj.name));
      card.append(svgNode('text',{x:b.left,y:b.top-19,class:'workspace-meta'},meta),svgNode('title',{},`${obj.name}. ${s.chart==='logical'?'Logical chart: '+m.axes.join(', '):'Declared placement'}. View offset ${s.pose.join(', ')}.`));
      if(!total)card.append(svgNode('text',{x:(b.left+b.right)/2,y:(b.top+b.bottom)/2,'text-anchor':'middle',class:'scene-empty'},obj.status==='failed'?'Failed result':'Empty domain'));
      labels.append(card);cards.set(obj.name,card);
    }
    drawn.sort((a,b)=>a.screen[2]-b.screen[2]);
    const readable=UNIT*canvas.getBoundingClientRect().width/view.w>20;
    for(const item of drawn){
      const {name,row,local,world,screen,settings,model}=item,isChosen=chosen?.name===name&&refKey(chosen.ref)===refKey(row.ref);
      const group=svgNode('g',{'data-scene-owner':name,'data-scene-mark':refKey(row.ref),'data-scene-depth':screen[2],class:`scene-mark ${name===active?'active':''} ${row.match?'':'outside'} ${isChosen?'chosen':''}`});
      if(settings.marks==='points')group.append(svgNode('circle',{cx:screen[0],cy:screen[1],r:isChosen?6:4}));
      else cellFaces(world,model.dimension,project).forEach((face,i)=>group.append(svgNode('polygon',{points:face.map(p=>p.slice(0,2).join(',')).join(' '),class:`scene-face face-${i}`})));
      if(settings.marks==='cells'&&readable&&model.dimension<3){const value=String(row.fields.value);group.append(svgNode('text',{x:screen[0],y:screen[1]+4,'text-anchor':'middle',class:'scene-value'},value.length>6?value.slice(0,5)+'…':value))}
      group.append(svgNode('title',{},`${name} · occurrence ${row.fields.index} · value ${row.fields.value} · ${model.axes.map((a,i)=>`${a}=${local[i]}`).join(', ')}${row.match?'':' · outside relation'}`));marks.append(group);
    }
    if(!state.objects.length)labels.append(svgNode('text',{x:350,y:-220,'text-anchor':'middle',class:'workspace-welcome'},'Add a sequence, or open a saved canvas.'));
    connections();syncSelection(project);caption.textContent=`Shared scale · view offsets only · ${drawn.length} marks${budget===0?' · drawing limit reached; select an object to prioritize it':''}`;
    if(focused)cards.get(focused)?.focus({preventScroll:true});
  }
  function connections(){
    wires.replaceChildren();if(tool!=='connect')return;
    for(const edge of state.connections?.edges||[]){
      const a=bounds.get(edge.source),b=bounds.get(edge.target);if(!a||!b)continue;
      const x1=(a.left+a.right)/2,y1=(a.top+a.bottom)/2,x2=(b.left+b.right)/2,y2=(b.top+b.bottom)/2;
      const p=svgNode('path',{d:`M${x1},${y1} C${x1+45},${y1} ${x2-45},${y2} ${x2},${y2}`,class:`workspace-wire ${edge.kind==='read'?'read':''} ${[edge.source,edge.target].includes(active)?'related':''}`,'data-connection-source':edge.source,'data-connection-target':edge.target,'marker-end':'url(#workspace-arrow)'});
      p.append(svgNode('title',{},`${edge.source} → ${edge.target} · ${edge.kind}`));wires.append(p);
    }
    if(drag?.moved&&drag.name){
      const b=bounds.get(drag.name);wires.append(svgNode('path',{d:`M${(b.left+b.right)/2},${b.top} L${drag.last.x},${drag.last.y}`,class:'workspace-proposal'}));
      const target=targetAt(drag.last,drag.name);if(target){cards.get(target)?.classList.add('drop-target');wires.append(svgNode('text',{x:drag.last.x+12,y:drag.last.y-12,class:'scene-drop-label'},`Combine with ${target}`))}
    }
  }
  function connectionText(){
    list.replaceChildren(el('summary',`Inputs of ${active||'selected object'}`));
    const incoming=(state.connections?.edges||[]).filter(e=>e.target===active),boundary=(state.connections?.boundaries||[]).filter(e=>e.target===active);
    for(const edge of incoming)list.append(button(`${edge.source} → ${edge.target} · ${edge.kind==='read'?'read path':'input path'}`,`Select input ${edge.source}`,()=>{if(!locked())select(edge.source)}));
    list.append(el('p',`${incoming.length?'':'No named input in this view. '}${boundary.length?`${boundary.length} earlier/local input boundaries. `:''}Read-only definition paths. The Construction sheet follows actual scoped inputs.`,{class:'help'}));
  }
  // Selected-object representation choices are independent of authoring tools.
  const shelf=host.querySelector('[data-scene-selection]'),markButtons=el('div',undefined,{class:'modes','aria-label':'Selected object marks'});
  for(const value of ['cells','points']){const b=button(value==='cells'?'Cells':'Points',`Show ${value}`,()=>change(s=>{s.marks=value}));b.dataset.sceneMarks=value;markButtons.append(b)}
  const chart=el('select',undefined,{id:'scene-chart','aria-label':'Coordinates to display'});chart.append(el('option','Logical axes',{value:'logical'}),el('option','Placement',{value:'placement'}));
  const detail=el('details'),detailSummary=el('summary','Chart and slice'),axesBox=el('div',undefined,{class:'scene-axes'}),sliceAxis=el('select',undefined,{id:'scene-slice-axis','aria-label':'View slice axis'}),sliceValue=el('select',undefined,{id:'scene-slice-value','aria-label':'View slice value'}),note=el('p',undefined,{class:'help',id:'scene-chart-note'});
  detail.append(detailSummary,axesBox,el('label','Display slice'),sliceAxis,sliceValue,note);
  const selection=el('select',undefined,{id:'scene-occurrence','aria-label':'Scene occurrence, front to back'}),inspectButton=button('Inspect occurrence','Inspect scene occurrence',()=>{if(chosen&&!locked())inspect(chosen.name,chosen.ref)}),selectionNote=el('p',undefined,{class:'help',id:'scene-selection-note'});
  const chartLabel=el('label','Coordinates ');chartLabel.append(chart);
  const chooser=el('details',undefined,{id:'scene-chooser'});chooser.append(el('summary','Choose an occurrence'),el('label','Occurrence · front to back'),selection,inspectButton,selectionNote);
  shelf.append(markButtons,chartLabel,detail,chooser);
  chart.onchange=()=>change(s=>{s.chart=chart.value;s.slice=null});
  sliceAxis.onchange=()=>change(s=>{const m=models.get(active);s.slice=sliceAxis.value?{axis:sliceAxis.value,value:m.positions[0]?.[m.axes.indexOf(sliceAxis.value)]||0}:null});
  sliceValue.onchange=()=>change(s=>{s.slice.value=Number(sliceValue.value)});
  selection.onchange=()=>{const obj=state.objects.find(o=>o.name===active),row=obj?.rows.find(r=>refKey(r.ref)===selection.value);if(row)chooseRow(obj.name,row.ref)};
  function change(fn){if(locked()||!active)return;cancel();fn(layout.get(active));rebuildModels();syncSettings();draw()}
  function syncSettings(){
    const obj=state.objects.find(o=>o.name===active),s=layout.get(active);shelf.hidden=!obj;if(!obj)return;
    host.querySelectorAll('[data-scene-marks]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.sceneMarks===s.marks)));
    chart.value=s.chart;chart.querySelector('[value=placement]').disabled=!obj.placed;axesBox.replaceChildren();
    const available=[...new Set([...(obj.axes||[]),'index'])];
    if(s.chart==='logical')for(let i=0;i<Math.min(3,available.length);i++){
      const choose=el('select',undefined,{'aria-label':`Logical chart axis ${i+1}`});choose.append(el('option','Not shown',{value:''}),...available.map(a=>el('option',a,{value:a})));choose.value=s.axes[i]||'';
      choose.onchange=()=>{const next=[...axesBox.querySelectorAll('select')].map(n=>n.value).filter(Boolean);if(!next.length||new Set(next).size!==next.length){status('Choose at least one distinct logical axis.',true);syncSettings();return}change(s=>{s.axes=next;s.slice=null})};axesBox.append(choose);
    }
    const m=models.get(active);sliceAxis.replaceChildren(el('option','All occurrences',{value:''}),...m.axes.map(a=>el('option',`Slice ${a}`,{value:a})));sliceAxis.value=s.slice?.axis||'';
    sliceValue.hidden=!s.slice;sliceValue.replaceChildren(...m.values.map(v=>el('option',String(v),{value:String(v)})));if(s.slice)sliceValue.value=String(s.slice.value);
    note.textContent=(s.chart==='logical'?`Logical chart: ${m.axes.join(', ')}. `:`Declared ${obj.dimension}D placement. `)+(m.dimension===3?'Cells are cube glyphs. ':'Cells are unit glyphs. ')+(obj.axes?.length>m.axes.length&&s.chart==='logical'?'Other axes are projected out; occurrences may overlap. ':'')+'Slices filter this view only; no new relation is created.';
  }
  function syncSelection(project){
    const obj=state.objects.find(o=>o.name===active),m=models.get(active);selection.replaceChildren(el('option','Choose an occurrence',{value:''}));
    if(!obj){inspectButton.disabled=true;return}
    const items=(obj.rows||[]).map((r,i)=>({r,i,depth:m.positions[i]?project.point(m.positions[i])[2]:0})).sort((a,b)=>b.depth-a.depth||a.i-b.i);
    for(const {r,i,depth} of items)selection.append(el('option',`${r.fields.index} · value ${r.fields.value}${r.match?'':' · outside relation'}${m.positions[i]&&!m.visible(m.positions[i])?' · outside slice':''}`,{value:refKey(r.ref)}));
    selection.value=chosen?.name===active?refKey(chosen.ref):'';inspectButton.disabled=!selection.value;
    const row=items.find(o=>refKey(o.r.ref)===selection.value),p=row&&m.positions[row.i];
    selectionNote.textContent=row?`Selected occurrence ${row.r.fields.index} · value ${row.r.fields.value}${p?' · '+m.axes.map((a,i)=>`${a}=${p[i]}`).join(', '):''}${p&&!m.visible(p)?' · hidden by the view slice':''}`:'Tap a mark or use this list to reach overlapping and hidden occurrences.';
  }
  function chooseRow(name,ref){
    if(locked())return;chosen={name,ref};if(active!==name)select(name);draw();inspect(name,ref);
  }
  function update(next,selectionName){
    if(next===state&&selectionName===active&&initialized)return;
    state=next;active=selectionName;ensureLayout();
    if(chosen&&!state.objects.find(o=>o.name===chosen.name)?.rows?.some(r=>refKey(r.ref)===refKey(chosen.ref)))chosen=null;
    syncTools();syncSettings();connectionText();
    if(!initialized&&state.objects.length){initialized=true;if(state.objects.some(o=>o.dimension===3||o.axes?.length>=3))[view.yaw,view.pitch]=planes.space;draw();fit();if(canvas.getBoundingClientRect().width<500)centerSelected()}
    else draw();
  }
  function cancel(){
    if(drag){clearTimeout(drag.timer);if(drag.name&&drag.origin)layout.get(drag.name).pose=drag.origin;view={...drag.view};drag=null;draw()}
  }
  canvas.onpointerdown=e=>{
    if(e.button!==0||locked())return;e.preventDefault();pointers.add(e.pointerId);canvas.setPointerCapture(e.pointerId);if(pointers.size!==1){cancel();return}
    const name=nameAt(e),handle=!!e.target.closest('[data-workspace-object]'),p=point(e),mark=e.target.closest('[data-scene-mark]');
    if(name)select(name);
    drag={id:e.pointerId,name:handle?name:null,subject:name,ref:mark?JSON.parse(mark.dataset.sceneMark):null,start:p,last:p,client:{x:e.clientX,y:e.clientY},origin:handle?[...layout.get(name).pose]:null,view:{...view},moved:false};
    if(name&&e.pointerType!=='mouse')drag.timer=setTimeout(()=>{cancel();holdClick=true;options(name)},480);
  };
  canvas.onpointermove=e=>{
    if(!drag||drag.id!==e.pointerId)return;const p=point(e);drag.last=p;
    if(Math.hypot(e.clientX-drag.client.x,e.clientY-drag.client.y)>9){drag.moved=true;clearTimeout(drag.timer)}if(!drag.moved)return;
    if(tool==='orbit'){view.yaw=drag.view.yaw+(e.clientX-drag.client.x)*.007;view.pitch=Math.max(-Math.PI,Math.min(Math.PI,drag.view.pitch+(e.clientY-drag.client.y)*.007));}
    else if(drag.name){if(tool==='move')layout.get(drag.name).pose=plus(drag.origin,projection(view.yaw,view.pitch).shift(p.x-drag.start.x,p.y-drag.start.y));}
    else{view.x-=p.x-drag.start.x;view.y-=p.y-drag.start.y;}
    draw();
  };
  canvas.onpointerup=e=>{
    pointers.delete(e.pointerId);if(!drag||drag.id!==e.pointerId)return;clearTimeout(drag.timer);
    const old=drag,target=old.name&&old.moved&&tool==='connect'?targetAt(point(e),old.name):null;drag=null;draw();
    if(target)combine(old.name,target);else if(!old.moved&&old.ref)chooseRow(old.subject,old.ref);else if(old.moved)status('View changed. Mathematical coordinates and history are unchanged.');
  };
  canvas.onpointercancel=e=>{pointers.delete(e.pointerId);cancel()};canvas.onlostpointercapture=e=>{pointers.delete(e.pointerId);if(drag?.id===e.pointerId)cancel()};
  canvas.oncontextmenu=e=>{e.preventDefault();cancel();if(!locked()&&(nameAt(e)||active))options(nameAt(e)||active)};
  canvas.ondblclick=e=>{if(locked())return;const name=nameAt(e);if(name)focus(name);else create()};
  canvas.onkeydown=e=>{
    const name=nameAt(e)||active;
    if(e.key==='Escape'){e.preventDefault();cancel();return}if(locked()||!name)return;
    if(e.key===' '){e.preventDefault();select(name)}if(e.key==='Enter'){e.preventDefault();focus(name)}
    if(e.key==='ContextMenu'||(e.shiftKey&&e.key==='F10')){e.preventDefault();options(name)}
    if(tool==='move'&&['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)){
      e.preventDefault();if(active!==name)select(name);const s=layout.get(name),dx=e.key==='ArrowLeft'?-20:e.key==='ArrowRight'?20:0,dy=e.key==='ArrowUp'?-20:e.key==='ArrowDown'?20:0;s.pose=plus(s.pose,projection(view.yaw,view.pitch).shift(dx,dy));draw();
    }
  };
  canvas.addEventListener('wheel',e=>{if(locked())return;e.preventDefault();zoom(Math.exp(-e.deltaY*.002))},{passive:false});
  document.addEventListener('pointerdown',()=>{holdClick=false},true);document.addEventListener('pointercancel',()=>{holdClick=false},true);
  document.addEventListener('click',e=>{const block=holdClick&&e.detail>0;holdClick=false;if(block){e.preventDefault();e.stopImmediatePropagation()}},true);
  window.addEventListener('blur',()=>{cancel();pointers.clear()});document.addEventListener('keydown',e=>{if(e.key==='Escape')cancel()});
  function save(){return {version:1,camera:{...view},objects:[...layout.values()].map(s=>({...s,pose:[...s.pose],axes:[...s.axes],slice:s.slice?{...s.slice}:null})),selected:active?{name:active,ref:chosen?.name===active?chosen.ref:null}:null,tool}}
  function load(scene){
    cancel();layout.clear();for(const s of scene.objects)if(state.objects.some(o=>o.name===s.name))layout.set(s.name,{...s,pose:[...s.pose],axes:[...s.axes]});
    ensureLayout();view={...scene.camera};tool=scene.tool;chosen=scene.selected?.ref?scene.selected:null;
    if(chosen&&!state.objects.find(o=>o.name===chosen.name)?.rows?.some(r=>refKey(r.ref)===refKey(chosen.ref)))chosen=null;
    initialized=true;syncTools();syncSettings();connectionText();draw();
  }
  new ResizeObserver(()=>{if(!drag)draw()}).observe(canvas);
  return {update,cancel,save,load,fit,center:centerSelected,refresh:draw,
    remember:()=>({camera:{...view},tool,inputsOpen:list.open,chosen}),
    restore(saved){cancel();view={...saved.camera};tool=saved.tool;chosen=saved.chosen;list.open=saved.inputsOpen;syncTools();syncSettings();draw()},
    reset(){cancel();layout.clear();models.clear();chosen=null;initialized=false;view=initialCamera()},
  };
}
