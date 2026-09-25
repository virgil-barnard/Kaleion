// Declare the quantity being changed. No geometry, execution or lesson logic here.
const el=(tag,text,attrs={})=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);return n};
const field=name=>({field:name}),zero=()=>({integer:'0'});
const labeled=(box,label,control)=>{const l=el('label',label);l.append(control);box.append(l);return control};
function options(entries,label){const s=el('select',undefined,{'aria-label':label});for(const [v,t,disabled] of entries){const o=el('option',t,{value:v});o.disabled=!!disabled;s.append(o)}return s}

export function transformControls(source,expr,seed={}){
  const box=el('div',undefined,{class:'transform-controls'});
  const mode=labeled(box,'Change',options([
    ['place','Coordinates · set positions'],
    ['move','Displacement · add to positions',!source.placed],
    ['roll','Cyclic shift · move contents between slots',!source.placed||!source.axes.length],
  ],'Transform kind'));mode.id='transform-kind';
  const meaning=el('p',undefined,{class:'help',id:'transform-meaning'});box.append(meaning);
  if(!source.placed)box.append(el('p','Set coordinates first to enable displacement and cyclic shifts.',{class:'help'}));
  const panels={},readers={};
  function coordinate(label,spec,panel){const card=expr(spec,source.fields);card.box.setAttribute('role','group');card.box.setAttribute('aria-label',label);panel.append(el('label',label),card.box);return card}
  for(const kind of ['place','move']){
    const panel=el('div');panels[kind]=panel;box.append(panel);
    const dimension=options([['1','1'],['2','2'],['3','3']],'Number of coordinates');
    dimension.value=String(Math.max(source.dimension||Math.max(2,source.axes.length),kind==='place'?seed.coordinates?.length||0:0));
    if(kind==='place')labeled(panel,'Number of coordinates',dimension);
    const coords=[...'xyz'].map((axis,i)=>coordinate(kind==='place'?`${axis} coordinate`:`${axis} displacement`,
      kind==='move'?(i===0&&seed.driver?seed.driver:zero()):seed.coordinates?.[i]||(source.placed&&i<source.dimension?field(axis):source.axes[i]?field(source.axes[i]):i===0?field('key'):zero()),panel));
    const show=()=>coords.forEach((c,i)=>{c.box.hidden=c.box.previousElementSibling.hidden=i>=Number(dimension.value)});
    dimension.onchange=show;show();
    readers[kind]=()=>({source:source.name,[kind==='place'?'coordinates':'displacement']:coords.slice(0,Number(dimension.value)).map(c=>c.read())});
  }
  const cycle=el('div');panels.roll=cycle;box.append(cycle);
  const axis=labeled(cycle,'Cycle along logical axis',options(source.axes.map(a=>[a,a]),'Cycle axis'));
  axis.value=source.axes.at(-1)||'';
  const shift=coordinate('Shift · positive moves toward larger indices',seed.driver||zero(),cycle);
  cycle.append(el('p','The axis length is the period. Give one integer shift per fiber; it may read a keyed measurement. Values, carried fields and identities travel together. Logical indices and positions stay in their slots.',{class:'help'}));
  readers.roll=()=>({source:source.name,axis:axis.value,shift:shift.read()});
  function show(){
    for(const [kind,panel] of Object.entries(panels))panel.hidden=kind!==mode.value;
    meaning.textContent={place:'Give this object exact coordinates and record the change as motion. Identities, values and logical keys stay with each item.',move:'Add a displacement to the current positions. Read a group key to move a whole fiber together, or use individual fields to move each item differently.',roll:'Cycle the existing contents through a declared logical axis. This changes which item occupies each slot; it does not stretch or extend the domain.'}[mode.value];
  }
  mode.onchange=show;show();
  return {box,read:()=>({action:mode.value,args:readers[mode.value]()})};
}
