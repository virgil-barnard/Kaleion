// A shape and its contents are independent authoring choices. Decimal strings
// and formula text reach the server unchanged; no JS arithmetic supplies values.
const el=(tag,text,attrs={})=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);return n};
const label=(box,text,input)=>{const n=el('label',text);n.append(input);box.append(n);return input};
export const shapes={vector:{rank:1,title:'Vector',lengths:['6']},grid:{rank:2,title:'Grid',lengths:['5','5']},cube:{rank:3,title:'Cube',lengths:['4','4','4']}};
export function shapeControls(kind,parameters){
  const shape=shapes[kind],box=el('section',undefined,{class:'shape-controls'}),axes=['i','j','k'].slice(0,shape.rank);
  const diagram=el('div',undefined,{class:`shape-diagram ${kind}`,'aria-hidden':'true'});
  for(let i=0;i<(kind==='vector'?6:kind==='grid'?15:9);i++)diagram.append(el('span'));
  const dimensions=el('div',undefined,{class:'shape-dimensions'});box.append(diagram,dimensions);
  const sizes=axes.map((axis,i)=>label(dimensions,`${axis} · ${['length','rows','layers'][i]}`,el('input',undefined,{type:'text',inputmode:'numeric',value:shape.lengths[i],'aria-label':`Size ${axis}`})));
  const mode=label(box,'At each location',el('select',undefined,{id:'shape-contents'}));
  mode.append(el('option','Tuples only · no values',{value:'tuples'}),el('option','Values from a formula',{value:'formula'}));
  if(kind==='vector')mode.append(el('option','Values I type',{value:'list'}));
  const formulaBox=el('div'),formula=label(formulaBox,`Value(${axes.join(', ')}) =`,el('input',undefined,{id:'shape-formula',type:'text',value:axes.join(' + '),spellcheck:'false',autocomplete:'off'}));
  formulaBox.append(el('p','Use +, −, *, //, %, and parentheses. For example: '+(kind==='vector'?'2*i + 1':kind==='grid'?'10*i + j':'100*i + 10*j + k'),{class:'help'}));
  const listBox=el('div'),list=label(listBox,'Values · separated by commas',el('input',undefined,{id:'shape-list',type:'text',value:'0, 1, 2, 3, 4, 5'}));
  listBox.append(el('p','The list determines the length; repeated values stay separate.',{class:'help'}));
  const meaning=el('p',undefined,{class:'shape-meaning',id:'shape-meaning'});box.append(formulaBox,listBox,meaning);
  const advanced=el('details'),names=[];advanced.append(el('summary','Index names and sizes'));
  axes.forEach(axis=>names.push(label(advanced,`Name for ${axis}`,el('input',undefined,{type:'text',value:axis,'aria-label':`Index name ${axis}`}))));
  advanced.append(el('p','Sizes can be integer parameters or formulas such as n + 1. In value formulas, use your index names; index is the flat position.',{class:'help'}));box.append(advanced);
  function sync(){
    formulaBox.hidden=mode.value!=='formula';listBox.hidden=mode.value!=='list';dimensions.hidden=mode.value==='list';
    meaning.textContent=mode.value==='tuples'?`Each location is a tuple (${axes.join(', ')}). No numeric value is assigned.`:mode.value==='formula'?'The formula gives one exact integer to each location.':'One location per value.';
    meaning.textContent+=' Indices start at 0. Shapes are finite; zero length is allowed.';
  }
  mode.onchange=sync;sync();
  return {box,read:()=>mode.value==='list'?{action:'integers',args:{values:list.value.trim()?list.value.split(',').map(s=>s.trim()):[]}}:{action:'grid',args:{shape:sizes.map(input=>/^-?(0|[1-9][0-9]*)$/.test(input.value.trim())?input.value.trim():{formula:input.value.trim()}),axes:names.map(n=>n.value.trim()),value:mode.value==='tuples'?null:{formula:formula.value}}}};
}
