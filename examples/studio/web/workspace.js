// Spatial presentation of captured roots. Layout and wires never become inputs.
import {viewPositions, projectionLabel} from './views.js';
import {cameraControls} from './camera.js';

const NS='http://www.w3.org/2000/svg', W=228, H=168, LIMIT=180;
const svgNode=(tag,attrs={},text)=>{
  const node=document.createElementNS(NS,tag);
  for(const [key,value] of Object.entries(attrs))node.setAttribute(key,value);
  if(text!==undefined)node.textContent=text;
  return node;
};

export function spatialWorkspace(host,{select,focus,options,combine,locked,status}){
  const canvas=host.querySelector('svg'),world=svgNode('g'),wires=svgNode('g',{'aria-hidden':'true'}),objects=svgNode('g');
  const layout=new Map(),cards=new Map(),pointers=new Set();
  let state={objects:[]},active=null,tool='move',drag=null,view={x:0,y:0,w:900,h:600},initialized=false,holdClick=false;
  world.append(wires,objects);canvas.append(world);
  const help=host.querySelector('[data-spatial-help]'),list=host.querySelector('[data-connection-list]');
  const caption=()=>{help.textContent=tool==='move'
    ?'Drag objects to organize this view. Double-click to focus. Right-click or use Options for tools.'
    :'Arrows follow named definition inputs. Dashed arrows pass through reads. Drag a source to a destination, or choose Combine…';};
  const controls=cameraControls({name:'workspace',fit,zoom:factor=>zoom(factor),pan:(x,y)=>{view.x-=x*view.w/700;view.y-=y*view.h/450;camera()}});
  const center=document.createElement('button');center.textContent='Selected';center.setAttribute('aria-label','Center selected object');center.onclick=centerSelected;controls.prepend(center);
  host.querySelector('[data-spatial-camera]').append(controls);
  host.querySelector('[data-combine]').onclick=()=>{if(active&&!locked())combine(active,null)};
  for(const b of host.querySelectorAll('[data-workspace-tool]'))b.onclick=()=>{
    cancel();tool=b.dataset.workspaceTool;
    host.querySelectorAll('[data-workspace-tool]').forEach(n=>n.setAttribute('aria-pressed',String(n===b)));
    caption();connections();
  };
  function camera(){canvas.setAttribute('viewBox',`${view.x} ${view.y} ${view.w} ${view.h}`)}
  function zoom(factor){cancel();const w=Math.max(300,Math.min(9000,view.w/factor)),h=w*2/3;view={x:view.x+(view.w-w)/2,y:view.y+(view.h-h)/2,w,h};camera()}
  function fit(){
    cancel();const positions=state.objects.map(o=>layout.get(o.name));
    const left=Math.min(0,...positions.map(p=>p.x-40)),top=Math.min(0,...positions.map(p=>p.y-40));
    const right=Math.max(600,...positions.map(p=>p.x+W+40)),bottom=Math.max(400,...positions.map(p=>p.y+H+40));
    const w=Math.max(right-left,(bottom-top)*1.5);view={x:left-(w-(right-left))/2,y:top,w,h:w*2/3};camera();
  }
  function centerSelected(){
    cancel();const p=layout.get(active);if(!p)return;
    const w=Math.max(320,Math.min(800,canvas.getBoundingClientRect().width));view={x:p.x+W/2-w/2,y:p.y+H/2-w/3,w,h:w*2/3};camera();
  }
  function point(event){const p=canvas.createSVGPoint();p.x=event.clientX;p.y=event.clientY;return p.matrixTransform(canvas.getScreenCTM().inverse())}
  function at(p,except=null){return [...state.objects].reverse().find(o=>{const q=layout.get(o.name);return o.name!==except&&p.x>=q.x&&p.x<=q.x+W&&p.y>=q.y&&p.y<=q.y+H})?.name}
  function nodeName(event){return event.target.closest('[data-workspace-object]')?.dataset.workspaceObject}
  function positionCards(){for(const [name,card] of cards){const p=layout.get(name);card.setAttribute('transform',`translate(${p.x} ${p.y})`)}connections()}
  function connections(){
    wires.replaceChildren();list.hidden=tool!=='connect';
    if(tool!=='connect')return;
    const edges=state.connections?.edges||[];
    for(const edge of edges){
      const a=layout.get(edge.source),b=layout.get(edge.target);if(!a||!b)continue;
      const right=b.x>=a.x,x1=a.x+(right?W:0),y1=a.y+H/2,x2=b.x+(right?0:W),y2=b.y+H/2;
      const path=svgNode('path',{d:`M${x1},${y1} C${x1+(right?55:-55)},${y1} ${x2+(right?-55:55)},${y2} ${x2},${y2}`,class:`workspace-wire ${edge.kind==='read'?'read':''} ${[edge.source,edge.target].includes(active)?'related':''}`,'data-connection-source':edge.source,'data-connection-target':edge.target,'marker-end':'url(#workspace-arrow)'});
      path.append(svgNode('title',{},`${edge.source} → ${edge.target} · ${edge.kind==='read'?'read path':'input path'}`));wires.append(path);
    }
    if(drag?.moved&&drag.name){const p=layout.get(drag.name);wires.append(svgNode('path',{d:`M${p.x+W/2},${p.y+H/2} L${drag.last.x},${drag.last.y}`,class:'workspace-proposal'}))}
  }
  function connectionText(){
    list.replaceChildren();
    const summary=document.createElement('summary');summary.textContent=`Inputs of ${active||'selected object'}`;list.append(summary);
    const incoming=(state.connections?.edges||[]).filter(e=>e.target===active),boundaries=(state.connections?.boundaries||[]).filter(e=>e.target===active);
    for(const edge of incoming){const button=document.createElement('button');button.textContent=`${edge.source} → ${edge.target} · ${edge.kind==='read'?'read path':'input path'}`;button.onclick=()=>{if(!locked())select(edge.source)};list.append(button)}
    const p=document.createElement('p');p.className='help';
    p.textContent=(incoming.length?'':'No named input in this view. ')+(boundaries.length?`${boundaries.length} unshown input boundaries: ${[...new Set(boundaries.map(b=>b.reason))].join(', ')}. `:'')+'These are definition paths, not editable live cables. Focus → Occurrences follows actual captured values and keys.';list.append(p);
  }
  function preview(card,obj){
    const points=viewPositions(obj),finite=points.every(p=>p.every(Number.isFinite));
    if(!points.length||!finite){card.append(svgNode('text',{x:W/2,y:80,'text-anchor':'middle',class:'workspace-empty'},obj.status==='failed'?'Evaluation failed':!finite?'Exact values in Focus':'Empty domain'));return}
    const xmin=Math.min(...points.map(p=>p[0])),xmax=Math.max(...points.map(p=>p[0])),ymin=Math.min(...points.map(p=>p[1])),ymax=Math.max(...points.map(p=>p[1]));
    if(!Number.isFinite(xmax-xmin)||!Number.isFinite(ymax-ymin)){card.append(svgNode('text',{x:W/2,y:80,'text-anchor':'middle'},'Exact values in Focus'));return}
    const scale=Math.min(180/Math.max(1,xmax-xmin),88/Math.max(1,ymax-ymin));
    points.slice(0,LIMIT).forEach((p,i)=>card.append(svgNode('circle',{cx:W/2+(p[0]-(xmin+xmax)/2)*scale,cy:64-(p[1]-(ymin+ymax)/2)*scale,r:3.1,class:obj.rows[i].match===false?'workspace-point outside':'workspace-point'})));
  }
  function update(next,selection){
    if(next===state&&selection===active&&initialized)return;
    const focused=document.activeElement?.dataset.workspaceObject;
    state=next;active=selection;
    state.objects.forEach((obj,i)=>{if(!layout.has(obj.name))layout.set(obj.name,{x:40+(i%3)*300,y:40+Math.floor(i/3)*220})});
    objects.replaceChildren();cards.clear();
    for(const obj of state.objects){
      const group=svgNode('g',{'data-workspace-object':obj.name,class:`workspace-object ${obj.name===active?'selected':''}`,role:'button',tabindex:'0','aria-label':`${obj.name}, ${obj.status==='failed'?'evaluation failed':obj.kind}. Space to select, Enter to focus, Shift F10 for options.`,'aria-pressed':String(obj.name===active)});
      group.append(svgNode('rect',{width:W,height:H,rx:16,class:'workspace-outline'}));preview(group,obj);
      const title=obj.name.length>26?obj.name.slice(0,24)+'…':obj.name;
      group.append(svgNode('text',{x:14,y:132,class:'workspace-name'},title),svgNode('text',{x:14,y:152,class:'workspace-meta'},obj.status==='failed'?'Failed · inspect in Focus':`${obj.rows.length} occurrences${obj.rows.length>LIMIT?` · first ${LIMIT} shown`:''}`),svgNode('title',{},`${obj.name}. ${projectionLabel(obj)}. Each object is independently scaled.`));
      objects.append(group);cards.set(obj.name,group);
    }
    if(!state.objects.length)objects.append(svgNode('text',{x:450,y:260,'text-anchor':'middle',class:'workspace-welcome'},'Start with + Add, or Open a saved canvas.'));
    positionCards();connectionText();caption();if(!initialized&&state.objects.length){initialized=true;fit();const width=canvas.getBoundingClientRect().width;if(width>0&&width<500)centerSelected()}camera();
    if(focused)cards.get(focused)?.focus({preventScroll:true});
  }
  function cancel(){
    if(drag){clearTimeout(drag.timer);if(drag.name&&tool==='move')layout.set(drag.name,drag.origin);if(!drag.name)view=drag.view;drag=null;positionCards();camera()}
    cards.forEach(c=>c.classList.remove('drop-target'));
  }
  canvas.onpointerdown=e=>{
    if(e.button!==0||locked())return;e.preventDefault();pointers.add(e.pointerId);canvas.setPointerCapture(e.pointerId);
    if(pointers.size!==1){cancel();return}
    const name=nodeName(e),p=point(e);if(name)select(name);
    drag={id:e.pointerId,name,start:p,last:p,client:{x:e.clientX,y:e.clientY},origin:name?{...layout.get(name)}:null,view:{...view},moved:false};
    if(name&&e.pointerType!=='mouse')drag.timer=setTimeout(()=>{cancel();holdClick=true;options(name)},480);
  };
  canvas.onpointermove=e=>{
    if(!drag||e.pointerId!==drag.id)return;
    const p=point(e);drag.last=p;
    if(Math.hypot(e.clientX-drag.client.x,e.clientY-drag.client.y)>9){drag.moved=true;clearTimeout(drag.timer)}
    if(!drag.moved)return;
    if(!drag.name){view.x-=p.x-drag.start.x;view.y-=p.y-drag.start.y;camera();return}
    if(tool==='move')layout.set(drag.name,{x:drag.origin.x+p.x-drag.start.x,y:drag.origin.y+p.y-drag.start.y});
    const target=tool==='connect'?at(p,drag.name):null;
    cards.forEach((c,name)=>c.classList.toggle('drop-target',name===target));positionCards();
  };
  canvas.onpointerup=e=>{
    pointers.delete(e.pointerId);if(!drag||drag.id!==e.pointerId)return;
    clearTimeout(drag.timer);const old=drag,target=old.name&&old.moved&&tool==='connect'?at(point(e),old.name):null;drag=null;cards.forEach(c=>c.classList.remove('drop-target'));connections();
    if(target)combine(old.name,target);else if(old.moved&&old.name)status(tool==='move'?'View organized. Mathematical coordinates and history are unchanged.':'Choose a destination object, or use Combine…');
  };
  canvas.onpointercancel=e=>{pointers.delete(e.pointerId);cancel()};
  canvas.onlostpointercapture=e=>{pointers.delete(e.pointerId);if(drag?.id===e.pointerId)cancel()};
  canvas.oncontextmenu=e=>{e.preventDefault();cancel();if(locked())return;const name=nodeName(e)||active;if(name)options(name)};
  canvas.ondblclick=e=>{if(locked())return;const name=nodeName(e);if(name)focus(name)};
  canvas.onkeydown=e=>{
    const name=nodeName(e)||active;
    if(e.key==='Escape'){e.preventDefault();cancel();return}
    if(locked()||!name)return;
    if(e.key===' '){e.preventDefault();select(name)}
    if(e.key==='Enter'){e.preventDefault();focus(name)}
    if(e.key==='ContextMenu'||(e.shiftKey&&e.key==='F10')){e.preventDefault();options(name)}
    if(tool==='move'&&['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)){
      e.preventDefault();if(active!==name)select(name);const p=layout.get(name);p.x+=e.key==='ArrowLeft'?-20:e.key==='ArrowRight'?20:0;p.y+=e.key==='ArrowUp'?-20:e.key==='ArrowDown'?20:0;positionCards();
    }
  };
  canvas.addEventListener('wheel',e=>{if(locked())return;e.preventDefault();zoom(Math.exp(-e.deltaY*.002))},{passive:false});
  // A modal can appear under a held finger. Its release must not choose a tool.
  // A fresh pointer gesture or keyboard activation remains an intentional action.
  document.addEventListener('pointerdown',()=>{holdClick=false},true);
  document.addEventListener('pointercancel',()=>{holdClick=false},true);
  document.addEventListener('click',e=>{const block=holdClick&&e.detail>0;holdClick=false;if(block){e.preventDefault();e.stopImmediatePropagation()}},true);
  window.addEventListener('blur',()=>{cancel();pointers.clear()});
  document.addEventListener('keydown',e=>{if(e.key==='Escape')cancel()});
  return {update,cancel,reset(){cancel();layout.clear();initialized=false;view={x:0,y:0,w:900,h:600}}};
}
