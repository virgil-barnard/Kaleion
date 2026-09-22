import {viewPositions,projectionLabel,refKey} from './views.js';

// This renderer knows scoped links, never how coverage, weights, or bindings were computed.
// Each card owns its camera. Selection, cameras, and lifetime are tab-local only.
const el=(tag,text,attrs={})=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);return n};
const svgEl=(tag,attrs={})=>{const n=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);return n};
export function linkedViews(host,{load,inspect,onVisibility}){
  let session=null,generation=0,cleanups=[];
  function close(){generation++;for(const clean of cleanups)clean();cleanups=[];session=null;host.replaceChildren();host.hidden=true;onVisibility(false)}
  async function open(spec){
    const ticket=++generation;
    const [left,right]=await Promise.all([load(spec.left.capture),load(spec.right.capture)]);
    if(ticket!==generation)return;
    // Validate before replacing the visible pair; an unavailable link is not empty evidence.
    for(const [side,view] of [['left',left],['right',right]]){
      const refs=new Set(view.rows.map(r=>refKey(r.ref)));
      for(const link of spec.links)for(const item of link[side])if(!refs.has(refKey(item.ref)))throw Error('A linked occurrence is absent from its captured view.');
    }
    close();host.hidden=false;onVisibility(true);
    const header=el('div',undefined,{class:'linked-header'}),title=el('h2',spec.title),done=el('button','Close linked views',{type:'button',id:'close-linked'});
    done.onclick=()=>{close();document.getElementById('options').focus({preventScroll:true})};header.append(title,done);
    const help=el('p',spec.detail,{class:'help'}),label=el('label','Evidence link'),choice=el('select',undefined,{id:'linked-choice'});
    spec.links.forEach((link,i)=>choice.append(el('option',link.label,{value:String(i)})));label.append(choice);
    const cards=el('div',undefined,{class:'linked-cards'}),message=el('p','Tap a linked item or use its occurrence list. Drag to pan; each view has its own zoom.',{class:'help',role:'status',id:'linked-status'});
    host.append(header,help,label,cards,message);
    const controllers=[card(left,spec.left,'left'),card(right,spec.right,'right')];
    session={spec,choice,controllers};
    choice.onchange=()=>choose(Number(choice.value));choose(spec.index||0,false);
    function card(view,descriptor,side){
      const box=el('section',undefined,{class:'linked-card','data-side':side,'aria-label':descriptor.label});
      const name=view.roots.length?`Current capture · ${view.roots.join(', ')}`:'Captured dependency · may differ from a current object';
      box.append(el('h3',descriptor.label),el('p',name,{class:'help','data-capture-label':''}));
      const svg=svgEl('svg',{viewBox:'0 0 420 260',role:'img','aria-label':descriptor.label}),marks=svgEl('g');svg.append(marks);
      const projection=el('p',projectionLabel(view),{class:'help'}),toolbar=el('div',undefined,{class:'row'});
      const fit=el('button','Fit',{type:'button','aria-label':`Fit ${side} view`}),minus=el('button','−',{type:'button','aria-label':`Zoom out ${side} view`}),plus=el('button','+',{type:'button','aria-label':`Zoom in ${side} view`});toolbar.append(fit,minus,plus);
      const selection=el('label',`${descriptor.label} occurrence`),select=el('select',undefined,{'data-linked-occurrence':side});selection.append(select);
      const detail=el('p','',{class:'linked-detail',role:'status'}),follow=el('button','Inspect selected occurrence',{type:'button','data-linked-inspect':side});
      box.append(svg,projection,toolbar,selection,detail,follow);cards.append(box);
      const context=new Map(view.rows.map(r=>[refKey(r.ref),r])),positions=viewPositions(view),valid=positions.every(p=>p.every(Number.isFinite));
      let items=[],selected=null,camera={x:0,y:0,zoom:1},points=[],gesture=null;
      const short=v=>{const s=String(v);return s.length>13?s.slice(0,10)+'…':s};
      const coordinates=e=>{const p=svg.createSVGPoint();p.x=e.clientX;p.y=e.clientY;return p.matrixTransform(svg.getScreenCTM().inverse())};
      function draw(){
        marks.replaceChildren();points=[];if(!valid){projection.textContent='Coordinates exceed floating range. Exact values remain in the occurrence list.';return}
        const xs=positions.map(p=>p[0]),ys=positions.map(p=>p[1]),xmin=Math.min(0,...xs),xmax=Math.max(1,...xs),ymin=Math.min(0,...ys),ymax=Math.max(1,...ys);
        const scale=Math.min(340/(xmax-xmin),190/(ymax-ymin))*camera.zoom,unit=420/Math.max(200,svg.getBoundingClientRect().width);
        const members=new Map(items.map(item=>[refKey(item.ref),item]));
        positions.forEach((p,i)=>{
          const row=view.rows[i],key=refKey(row.ref),item=members.get(key),chosen=key===selected;
          const x=210+(p[0]-(xmin+xmax)/2)*scale+camera.x,y=130-(p[1]-(ymin+ymax)/2)*scale+camera.y;
          const circle=svgEl('circle',{cx:x,cy:y,r:(chosen?7:4)*unit,fill:item?.emphasis===false?'#a9b6ad':'#b96429',opacity:item?1:.12,stroke:chosen?'#235d48':'none','stroke-width':3,'data-linked-ref':key,'data-linked-member':String(!!item),'data-linked-selected':String(chosen)});
          marks.append(circle);points.push({x,y,key});
          if(item&&items.length<=16){const text=svgEl('text',{x:x+9*unit,y:y-8*unit});text.style.fontSize=`${12*unit}px`;text.textContent=short(row.fields.value);marks.append(text)}
        });
      }
      function selectItem(key){
        selected=key;select.value=key||'';const row=context.get(key),item=items.find(i=>refKey(i.ref)===key);
        detail.textContent=row?`Value ${row.fields.value}${item?.note?` · ${item.note}`:''}`:'';follow.disabled=!row;draw();
      }
      function update(link){
        items=link[side];select.replaceChildren();
        for(const item of items){const row=context.get(refKey(item.ref));select.append(el('option',`${row.fields.index} · value ${row.fields.value}${item.note?` · ${item.note}`:''}`,{value:refKey(item.ref)}))}
        select.disabled=!items.length;
        selectItem(items.some(i=>refKey(i.ref)===selected)?selected:items.length?refKey((items.find(i=>i.emphasis!==false)||items[0]).ref):null);
        if(!items.length)detail.textContent=link[side==='left'?'emptyLeft':'emptyRight']||'No linked occurrences. Faint points show context only.';
      }
      select.onchange=()=>selectItem(select.value);
      follow.onclick=()=>inspect(context.get(selected).ref,follow);
      fit.onclick=()=>{camera={x:0,y:0,zoom:1};draw()};minus.onclick=()=>{camera.zoom=Math.max(.2,camera.zoom/1.4);draw()};plus.onclick=()=>{camera.zoom=Math.min(12,camera.zoom*1.4);draw()};
      svg.onpointerdown=e=>{if(!e.isPrimary||e.button>0){gesture=null;return}e.preventDefault();svg.setPointerCapture(e.pointerId);const p=coordinates(e);gesture={id:e.pointerId,start:p,last:p,moved:false}};
      svg.onpointermove=e=>{if(!gesture||e.pointerId!==gesture.id)return;const p=coordinates(e);if(Math.hypot(p.x-gesture.start.x,p.y-gesture.start.y)*svg.getScreenCTM().a>9)gesture.moved=true;if(gesture.moved){camera.x+=p.x-gesture.last.x;camera.y+=p.y-gesture.last.y;draw()}gesture.last=p};
      svg.onpointerup=e=>{
        if(!gesture||e.pointerId!==gesture.id)return;const tap=!gesture.moved;gesture=null;if(!tap)return;
        const p=coordinates(e),near=points.map(d=>({...d,d:Math.hypot(d.x-p.x,d.y-p.y)})).filter(d=>d.d<24/svg.getScreenCTM().a).sort((a,b)=>a.d-b.d);
        if(!near.length)return;
        const point=near[0],indices=spec.links.flatMap((link,i)=>link[side].some(item=>refKey(item.ref)===point.key)?[i]:[]);
        if(!indices.length){message.textContent='No link in this evidence for that occurrence. Faint points provide context only.';return}
        const current=Number(choice.value),index=indices.includes(current)?current:indices.length===1?indices[0]:null;
        if(index===null){message.textContent='This occurrence belongs to several links. Choose an evidence link from the list.';return}
        choose(index);selectItem(point.key);message.textContent=near.length>1?'Several points are close or coincident. Use the occurrence list to choose exactly.':'Selection follows captured evidence; no construction was changed.';
      };
      svg.onpointercancel=()=>{gesture=null};const blur=()=>{gesture=null};window.addEventListener('blur',blur);
      const observer=new ResizeObserver(draw);observer.observe(svg);cleanups.push(()=>{observer.disconnect();window.removeEventListener('blur',blur)});
      return {update};
    }
  }
  function choose(index,notify=true){
    if(!session||!session.spec.links[index])return;
    session.choice.value=String(index);for(const c of session.controllers)c.update(session.spec.links[index]);
    if(notify)session.spec.onChoose?.(index);
  }
  return {open,choose,close};
}
