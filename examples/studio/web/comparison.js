import {fieldKeys} from './groups.js';
import {caseLabel} from './cases.js';

// Declares a finite equality question. Python owns alignment, arithmetic, and witnesses.
const el=(tag,text,attrs={})=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);return n};
export function comparisonInspector({source,objects,initial,remember,run,check,inspect,link,clearLink,chooseLink}){
  const ready=objects.filter(o=>o.status==='ready'&&o.kind!=='incidence');
  const box=el('div',undefined,{id:'comparison-tool'}),choices=el('details'),heading=el('summary','Comparison inputs');choices.open=true;choices.append(heading);
  const labeled=(parent,text,control)=>{const label=el('label',text);label.append(control);parent.append(label);return control};
  function picker(parent,label,values,selected='',id){
    const select=el('select',undefined,id?{id}:{});
    if(!values.includes(selected))select.append(el('option','Choose…',{value:''}));
    for(const value of values)select.append(el('option',value,{value}));select.value=selected;
    return labeled(parent,label,select);
  }
  const seed=initial?.name===source.name?initial:{};
  box.append(el('span','DECLARE / COMPARE / INSPECT',{class:'eyebrow'}),el('h2','Compare integer fields'),el('p','Require equal values and exactly the expected keys. Each key must identify one occurrence; equal labels or coincident points do not establish a match.',{class:'help'}),choices);
  choices.append(el('p',`Left object · ${source.name}`));
  const leftValue=picker(choices,'Left value field',source.fields,seed.left_value||'value','comparison-left-value');
  const leftKeys=fieldKeys(source.fields,seed.left_by||[],'Left key fields','Choose a unique key');choices.append(leftKeys.box);
  function other(role){
    const select=picker(choices,role==='right'?'Right object':'Expected domain',ready.map(o=>o.name),seed[role]||'',`comparison-${role}`);
    const slot=el('div');choices.append(slot);let keys=null,value=null;
    function rebuild(first=false){
      slot.replaceChildren();const obj=ready.find(o=>o.name===select.value);keys=null;value=null;
      if(!obj)return;
      if(role==='right')value=picker(slot,'Right value field',obj.fields,first?seed.right_value||'value':'value','comparison-right-value');
      keys=fieldKeys(obj.fields,first?seed[`${role}_by`]||[]:[],role==='right'?'Right key fields':'Expected key fields','Choose a unique key');slot.append(keys.box);
    }
    select.onchange=()=>{rebuild();invalidate()};rebuild(true);
    return {name:()=>select.value,keys:()=>keys?.read()||[],value:()=>value?.value};
  }
  const right=other('right'),expected=other('expected');
  choices.append(el('p','Match key components in the same order. The expected domain is a separate choice so a key missing from both operands stays visible. Residual means left minus right.',{class:'help'}));
  const test=el('button','Compare captured values',{type:'button',class:'primary',id:'check-comparison'});
  const message=el('p','Choose the two value fields and three key declarations.',{id:'comparison-status',role:'status','aria-live':'polite'}),results=el('div',undefined,{id:'comparison-results'});box.append(test,message,results);
  function spec(){return {name:source.name,left_by:leftKeys.read(),left_value:leftValue.value,right:right.name(),right_by:right.keys(),right_value:right.value(),expected:expected.name(),expected_by:expected.keys()}}
  function invalidate(){clearLink();results.replaceChildren();message.textContent='Choices changed. Compare again.';message.dataset.phase='editing';remember(spec())}
  choices.addEventListener('change',invalidate);
  test.onclick=()=>run(async()=>{
    clearLink();results.replaceChildren();message.textContent='Comparing captured fields…';message.dataset.phase='checking';
    try{
      const declaration=spec();remember(declaration);const report=await check(declaration),s=report.summary;
      message.dataset.phase=report.passed?'passed':'failed';
      message.textContent=`${report.passed?'Finite equality holds.':'Finite equality fails.'} ${s.equal} equal, ${s.different} different; missing left ${s.missing_left}, right ${s.missing_right}; outside left ${s.outside_left}, right ${s.outside_right}.${report.empty?' Empty expected domain: no item equality is asserted.':''}`;
      choices.open=false;heading.textContent=`Inputs · ${report.name}.${report.left_value} ↔ ${report.right}.${report.right_value}`;
      render(report);
    }catch(error){message.dataset.phase='error';message.textContent=`Could not compare: ${error.message}`;choices.open=true}
  });
  function render(report){
    results.append(el('p',`Captured case · ${caseLabel(report.parameters)}`,{class:'help'}),
      el('p',`Left: ${report.name}.${report.left_value} by (${report.left_by.join(', ')}). Right: ${report.right}.${report.right_value} by (${report.right_by.join(', ')}). Expected: ${report.expected} by (${report.expected_by.join(', ')}).`,{class:'help'}));
    const filter=picker(results,'Show comparison keys',['all','different','missing','outside','equal'],report.passed?'all':'different','comparison-filter');
    const keys=labeled(results,'Comparison key',el('select',undefined,{id:'comparison-key'}));
    const witness=el('div',undefined,{id:'comparison-witness'}),together=el('button','View compared occurrences',{type:'button',id:'view-comparison'});results.append(witness,together);
    const rows=report.rows;
    const label=row=>`(${row.key.join(', ')}) · ${row.status}${row.residual!==null?` · residual ${row.residual}`:''}`;
    function populate(){
      keys.replaceChildren();rows.forEach((row,i)=>{if(filter.value==='all'||row.status===filter.value)keys.append(el('option',label(row),{value:String(i)}))});show();
    }
    function show(){
      witness.replaceChildren();together.disabled=keys.value==='';
      if(keys.value===''){witness.append(el('p','No keys in this category.'));clearLink();return}
      const index=Number(keys.value),row=rows[index];chooseLink(index);
      witness.append(el('p',`Left ${report.left_value}: ${row.left??'absent'} · Right ${report.right_value}: ${row.right??'absent'}`));
      witness.append(el('p',row.status==='outside'?'Outside the expected domain; no residual is used in this claim.':row.residual===null?'No residual: a missing value is not zero.':`Residual (left − right): ${row.residual}`));
      for(const [side,text,field] of [['left','Inspect left occurrence',report.left_value],['right','Inspect right occurrence',report.right_value],['expected','Inspect expected key',null]]){
        const ref=row[`${side}_ref`];if(!ref)continue;
        const b=el('button',text,{type:'button'});b.onclick=()=>run(()=>inspect(ref,b,field?`Compared ${side} field ${field} = ${row[side]}. Residual ${row.residual??'unavailable'}.`:'Expected domain occurrence; its label is not a compared value.'));witness.append(b);
      }
    }
    together.onclick=()=>run(()=>link(report,rows,Number(keys.value),index=>{
      if(![...keys.options].some(o=>o.value===String(index))){filter.value='all';populate()}
      keys.value=String(index);show();
    }));
    filter.onchange=populate;keys.onchange=show;
    if(!rows.some(row=>row.status===filter.value))filter.value='all';populate();
    results.append(el('p','A captured finite equality compares the declared fields and domain. It is not a universal identity or a correspondence of geometric structures.',{class:'help'}));
  }
  return box;
}
