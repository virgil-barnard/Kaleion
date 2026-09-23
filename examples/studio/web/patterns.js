// Small pattern starters and axis totals. These produce declarations, not results.
const el=(tag,text,attrs={})=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);return n};
const field=name=>({field:name}),integer=value=>({integer:String(value)}),op=(name,...args)=>({op:name,args});
const select=(values,current,label)=>{const s=el('select',undefined,{'aria-label':label});for(const [value,text] of values)s.append(el('option',text,{value}));s.value=current;return s};
const labeled=(box,text,input)=>{const label=el('label',text);label.append(input);box.append(label);return input};
const presets={1:[['even','Even numbers'],['at_least','At least…'],['at_most','At most…']],2:[['equal','Equal inputs'],['less','First is smaller'],['sum','Sum is…']],3:[['add','First + second = third'],['ordered','Inputs in order'],['sum','Total is…']]};
export function pattern(kind,fields,limit='3'){
  const [a,b,c]=fields.map(field),n=integer(limit);
  if(kind==='even')return op('=',op('%',a,integer(2)),integer(0));
  if(kind==='at_least')return op('≥',a,n);
  if(kind==='at_most')return op('≤',a,n);
  if(kind==='equal')return op('=',a,b);
  if(kind==='less')return op('<',a,b);
  if(kind==='add')return op('=',op('+',a,b),c);
  if(kind==='ordered')return op('and',op('≤',a,b),op('≤',b,c));
  return op('=',fields.map(field).reduce((a,b)=>op('+',a,b)),n);
}

export function lensControls(source,expr){
  const box=el('div',undefined,{class:'pattern-controls'}),arity=select([['1','One input'],['2','Two inputs'],['3','Three inputs']],String(Math.min(3,source.axes.length||1)),'Number of lens inputs');
  labeled(box,'Start a pattern with',arity);
  const simple=el('div'),detail=el('details'),summary=el('summary','Customize the formula'),formula=el('div'),custom=el('p','Custom formula. Changing a starter choice replaces it.',{class:'help'});custom.hidden=true;detail.append(summary,formula);box.append(simple,custom,detail);
  let rule;
  function rebuild(){
    const count=Number(arity.value);simple.replaceChildren();
    const kind=select(presets[count],presets[count][0][0],'Pattern');labeled(simple,'Pattern starter',kind);
    const mapping=[],inputs=el('div',undefined,{class:'pattern-inputs'});simple.append(inputs);
    for(let i=0;i<count;i++){
      const choices=source.fields.map(f=>[f,f]);
      mapping.push(labeled(inputs,count===1?'Input field':['First','Second','Third'][i],select(choices,count===1?(source.fields.includes('value')?'value':source.axes[0]||'index'):source.axes[i]||'index',`Lens input ${i+1}`)));
    }
    const limit=el('input',undefined,{type:'text',inputmode:'numeric','aria-label':'Pattern number',value:'3'}),limitLabel=el('label','Number');limitLabel.append(limit);simple.append(limitLabel);
    function update(){
      limitLabel.hidden=!['sum','at_least','at_most'].includes(kind.value);
      rule=expr(pattern(kind.value,mapping.map(s=>s.value),limit.value),source.fields);
      formula.replaceChildren(rule.box);
      custom.hidden=true;summary.textContent='Customize the formula';
      rule.box.addEventListener('change',()=>{custom.hidden=false;summary.textContent='Custom formula'});
    }
    kind.onchange=update;mapping.forEach(s=>s.onchange=update);limit.oninput=update;update();
  }
  arity.onchange=rebuild;rebuild();
  const hint=el('p','The lens highlights matches and keeps every other item in its domain.',{class:'help'});box.append(hint);
  return {box,read:()=>rule.read()};
}

export function totalControls(source,expr){
  const box=el('div',undefined,{class:'pattern-controls'}),fields=source.total_fields||source.axes,reducer=select([['count','Count matches'],['sum','Sum weights']],source.kind==='incidence'||!source.fields.includes('value')?'count':'sum','Total operation');
  labeled(box,'Total',reducer);
  const axes=el('fieldset',undefined,{class:'axis-totals'});axes.append(el('legend',source.axes.length?'Along these axes':'Along these retained keys'));box.append(axes);
  const checks=fields.map((name,i)=>{const c=el('input',undefined,{type:'checkbox',value:name,'aria-label':`Total along ${name}`});c.checked=i===fields.length-1;const label=el('label',name);label.prepend(c);axes.append(label);return c});
  if(!checks.length)axes.append(el('p','This object has no logical axes: make one total.'));
  const meaning=el('p',undefined,{class:'help',id:'axis-total-meaning'});box.append(meaning);
  const weight=expr(field(source.fields.includes('value')?'value':source.axes[0]||'index'),source.fields),detail=el('details');detail.append(el('summary','Weight formula'),weight.box);box.append(detail);
  function update(){const retained=fields.filter((_,i)=>!checks[i].checked);detail.hidden=reducer.value!=='sum';meaning.textContent=`${retained.length?'Keep '+retained.join(', ')+' as result keys.':'Make one total.'} Empty fibers stay as zero. The new object can supply values to another construction.`}
  checks.forEach(c=>c.onchange=update);reducer.onchange=update;update();
  return {box,read:()=>({axes:checks.filter(c=>c.checked).map(c=>c.value),reducer:reducer.value,weight:weight.read()})};
}

export function reuseControls(source,objects,destination){
  const box=el('div',undefined,{class:'pattern-controls'}),rule=source.reusable_rule;
  if(!rule?.available){box.append(el('p',rule?.reason||'No reusable predicate is available.'));return {box,read:()=>{throw Error(rule?.reason||'No reusable predicate')}}}
  box.append(el('p',rule.formula,{class:'lens-formula'}));
  const targets=objects.filter(o=>o.status==='ready'&&o.kind!=='incidence');
  const target=select(targets.map(o=>[o.name,o.name]),destination||targets[0]?.name||'','Lens destination');labeled(box,'Use this lens on',target);
  const mappings=el('div');box.append(mappings);let fields=[];
  function update(){
    mappings.replaceChildren();const obj=targets.find(o=>o.name===target.value);
    fields=rule.fields.map(name=>[name,labeled(mappings,`Rule input ${name} →`,select([['','Choose a field'],...(obj?.fields||[]).map(f=>[f,f])],obj?.fields.includes(name)?name:'',`Map rule input ${name}`))]);
  }
  target.onchange=update;update();
  const bindings=Object.entries(rule.parameters).map(([k,v])=>`${k} = ${v}`).join(', ');
  box.append(el('p',bindings?`Captured constants: ${bindings}. These stay fixed in the copy; the destination keeps its own parameters.`:'This copies the predicate. The original lens and its domain remain available.',{class:'help'}));
  return {box,read:()=>({target:target.value,mapping:Object.fromEntries(fields.map(([k,v])=>[k,v.value])),capture:rule.capture})};
}
