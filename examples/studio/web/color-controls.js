import {palettes,colorDefaults,validateColor} from './colors.js';

const el=(tag,text,attrs={})=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);return n};
export function colorControls(change){
  const box=el('details',undefined,{class:'color-controls'});box.append(el('summary','Color'));
  function select(label,options){const node=el('select',undefined,{'aria-label':label});for(const [value,text] of options)node.append(el('option',text,{value}));return input(label,node)}
  function input(label,node){const wrap=el('label',label);wrap.append(node);box.append(wrap);return node}
  const mode=select('Color by',[['uniform','Uniform color'],['field','Integer field']]);
  const solid=input('Object color',el('input',undefined,{type:'color','aria-label':'Object color'}));
  const field=select('Color field',[]),palette=select('Palette',Object.entries(palettes).map(([k,v])=>[k,v.label]));
  const reverse=input('Reverse palette',el('input',undefined,{type:'checkbox','aria-label':'Reverse palette'}));
  const range=select('Color range',[['auto','Automatic min–max'],['fixed','Fixed min–max']]);
  const min=input('Minimum',el('input',undefined,{type:'text',inputmode:'text','aria-label':'Color minimum'}));
  const max=input('Maximum',el('input',undefined,{type:'text',inputmode:'text','aria-label':'Color maximum'}));
  const use=el('button','Use current limits',{type:'button'}),apply=el('button','Apply colors',{type:'button'}),row=el('div',undefined,{class:'row'});row.append(use,apply);
  const gradient=el('div',undefined,{class:'color-gradient','aria-hidden':'true'}),note=el('p',undefined,{class:'help','data-color-note':''}),error=el('p',undefined,{role:'status','data-color-status':''});
  box.append(gradient,note,row,error,el('p','Colors change the picture only. Nonmatches remain faint with dashed edges. Fixed limits make different objects or cases comparable.',{class:'help'}));
  let current=null;
  function visibility(){solid.parentNode.hidden=mode.value!=='uniform';for(const n of [field,palette,reverse,range])n.parentNode.hidden=mode.value!=='field';for(const n of [min,max])n.parentNode.hidden=mode.value!=='field'||range.value!=='fixed';use.hidden=mode.value!=='field';gradient.hidden=mode.value!=='field';use.disabled=current?.min==null}
  mode.onchange=range.onchange=()=>{error.textContent='Apply colors to use these choices.';visibility()};
  use.onclick=()=>{if(current?.min!=null){range.value='fixed';min.value=current.min;max.value=current.max;visibility();error.textContent='Current limits copied. Apply colors to fix the scale.'}};
  apply.onclick=()=>{try{const settings=validateColor({mode:mode.value,solid:solid.value,field:field.value,palette:palette.value,range:range.value,min:min.value.trim(),max:max.value.trim(),reverse:reverse.checked});change(settings);error.textContent='Colors applied. Mathematics and history are unchanged.'}catch(e){error.textContent=e.message}};
  return {box,sync(obj,settings=colorDefaults(),scale){
    mode.value=settings.mode;solid.value=settings.solid;palette.value=settings.palette;range.value=settings.range;reverse.checked=settings.reverse;min.value=settings.min;max.value=settings.max;
    const names=[...new Set([...(obj.fields||[]),settings.field])];field.replaceChildren(...names.map(n=>el('option',n,{value:n})));field.value=settings.field;error.textContent='';visibility();this.legend(settings,scale);
  },legend(settings,scale,replaying=false){
    current=scale;note.textContent=scale.note+(replaying?' Replay uses captured endpoint values, never interpolated values. Other fields belong to the current capture.':'');
    const stops=[...palettes[settings.palette].stops];if(settings.reverse)stops.reverse();
    gradient.hidden=settings.mode!=='field'||!scale.hasValues;
    gradient.style.background=settings.range==='auto'&&scale.min!==null&&scale.min===scale.max?scale.at(scale.min):`linear-gradient(to right,${stops.join(',')})`;
    use.disabled=current.min==null;
  }};
}
