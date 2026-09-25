// Copy/address decisions only. Execution and occurrence lineage belong to Python.
const el=(tag,text,attrs={})=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);return n};
const labeled=(box,text,node)=>{const label=el('label',text);label.append(node);box.append(label);return node};
function options(entries,id){const s=el('select',undefined,{id});for(const [value,text] of entries)s.append(el('option',text,{value}));return s}

export function reindexControls(source,objects){
  const box=el('div');
  const kind=labeled(box,'Operation',options([['tile','Repeat'],['gather','Take an address list'],['concat','Join another object']],'reindex-kind'));
  const axis=labeled(box,'Along',options([...source.axes.map(a=>[a,`Axis ${a}`]),['','Flattened sequence']],'reindex-axis'));
  axis.value=source.axes[0]||'';
  const placement=labeled(box,'Result placement',options([['indices','Index chart'],['unplaced','Unplaced · arrange later']],'reindex-placement'));
  const explanation=el('p',undefined,{class:'help',id:'reindex-meaning'});box.append(explanation);
  const panels={};for(const mode of ['tile','gather','concat']){panels[mode]=el('div');box.append(panels[mode])}
  const candidates=objects.filter(o=>o.status==='ready'&&o.kind!=='incidence');
  const repeatMode=labeled(panels.tile,'Repeat count from',options([['formula','A number or parameter formula'],['object','A single value from an object']],'reindex-repeat-mode'));
  const formulaBox=el('div'),objectBox=el('div');panels.tile.append(formulaBox,objectBox);
  const times=labeled(formulaBox,'Number of repeats',el('input',undefined,{id:'reindex-times',value:'2',inputmode:'text'}));
  const repeatSource=labeled(objectBox,'Count object',options(candidates.filter(o=>o.fields.includes('value')).map(o=>[o.name,o.name]),'reindex-repeat-source'));
  panels.tile.append(el('p','One nonnegative integer is required. An object must contain exactly one value; that dependency is retained when parameters change. Zero repeats gives an empty domain.',{class:'help'}));
  function repeatChoice(){formulaBox.hidden=repeatMode.value!=='formula';objectBox.hidden=repeatMode.value!=='object'}
  repeatMode.onchange=repeatChoice;repeatChoice();
  const addresses=labeled(panels.gather,'Address object',options(candidates.map(o=>[o.name,o.name]),'reindex-addresses'));
  const fields=labeled(panels.gather,'Read addresses from',options([],'reindex-field'));
  const order=labeled(panels.gather,'Order address rows by',options([],'reindex-order'));
  const claim=labeled(panels.gather,'Coverage requirement',options([['copies','Allow repeats and omissions'],['bijective','Every source slot exactly once']],'reindex-claim'));
  panels.gather.append(el('p','Addresses are zero-based source slots, not labels or keys. One address supplies each destination slot. Order must be unique; ties fail. The same address list applies to every fiber along a chosen axis.',{class:'help'}));
  function addressFields(){const obj=candidates.find(o=>o.name===addresses.value);for(const s of [fields,order]){s.replaceChildren();for(const f of obj?.fields||[])s.append(el('option',f,{value:f}))}fields.value=obj?.fields.includes('value')?'value':obj?.fields[0]||'';order.value='index'}
  addresses.onchange=addressFields;addressFields();
  const other=labeled(panels.concat,'Append this object',options(candidates.map(o=>[o.name,o.name]),'reindex-other'));
  panels.concat.append(el('p','All other axis sizes and attribute names must agree. For zero padding, create a zero-valued grid explicitly, then join it. Tuple-only inputs can join other tuple-only inputs.',{class:'help'}));
  function show(){
    for(const [mode,panel] of Object.entries(panels))panel.hidden=mode!==kind.value;
    const axes=axis.value?[...source.axes].reverse():['index'];
    const dimension=source.dimension||Math.max(2,axes.length);while(axes.length<dimension)axes.push('0');
    explanation.textContent=`New occurrences retain captured source links; a repeated address makes distinct copies. ${placement.value==='indices'?`Index chart: (${axes.join(', ')}).`:'No positions are supplied.'} Use a new Result name to keep the source beside it, or its current name to record this step on the source. Earlier consumers retain their inputs.`;
  }
  kind.onchange=axis.onchange=placement.onchange=show;show();
  return {box,read:()=>({source:source.name,kind:kind.value,axis:axis.value||null,placement:placement.value,
    ...(kind.value==='tile'?{times:repeatMode.value==='object'?{object:repeatSource.value}:{formula:times.value}}:kind.value==='concat'?{other:other.value}:{addresses:addresses.value,field:fields.value,order:order.value,bijective:claim.value==='bijective'})})};
}
