// Owns parameter declarations and the finite-case report, never arithmetic or history.
const el=(tag,text,attrs={})=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);return n};
export const caseLabel=parameters=>Object.entries(parameters||{}).map(([name,value])=>`${name} = ${value}`).join(' · ')||'No declared parameters';

export function caseFields(parameters){
  const box=el('div'),rows=el('div'),entries=[];
  const add=el('button','Declare parameter',{type:'button',id:'declare-parameter'});
  function row(name='',value='0',existing=false){
    const item=el('div',undefined,{class:'parameter-row'});
    const key=el('input',undefined,{type:'text','aria-label':'Parameter name',maxlength:'32'});key.value=name;key.readOnly=existing;
    const input=el('input',undefined,{type:'text',inputmode:'numeric','aria-label':name?`Value of ${name}`:'Parameter value'});input.value=value;
    const keyLabel=el('label','Name'),valueLabel=el('label','Exact integer');keyLabel.append(key);valueLabel.append(input);item.append(keyLabel,valueLabel);
    entries.push({key,input});rows.append(item);add.disabled=entries.length>=16;
    if(!existing)key.focus({preventScroll:true});
  }
  box.append(el('p','Declare an integer once, then choose Parameter in formulas or axis lengths. Editing these values proposes a new case. Apply keeps the evaluated results, including any failures.',{class:'help'}),rows,add);
  for(const [name,value] of Object.entries(parameters||{}))row(name,value,true);
  add.onclick=()=>{row();box.dispatchEvent(new Event('change',{bubbles:true}))};
  return {box,read:()=>{
    const values=Object.create(null);
    for(const {key,input} of entries){
      if(!key.value.trim())throw Error('Give every declared parameter a name.');
      if(Object.hasOwn(values,key.value.trim()))throw Error('Parameter names must be distinct.');
      values[key.value.trim()]=input.value.trim();
    }
    return values;
  }};
}

export function caseReport(preview,{applied=false}={}){
  const box=el('div',undefined,{id:'case-report'});
  box.append(el('h3',applied?'Captured results':`Preview case · ${caseLabel(preview.parameters)}`));
  const failures=preview.objects.filter(o=>o.status==='failed');
  const ready=preview.objects.filter(o=>o.status==='ready');
  box.append(el('p',`${ready.length} ready · ${failures.length} failed. ${applied?'Select an object to inspect its captured evidence. Undo restores the previous capture.':'Apply to inspect this case; Cancel keeps the applied case.'}`,{class:'help'}));
  if(failures.length){const list=el('ul');for(const obj of failures)list.append(el('li',`${obj.name}: ${obj.error}`));box.append(list)}
  if(ready.length){
    const details=el('details'),list=el('ul');details.append(el('summary',`Ready objects · ${ready.length}`));
    for(const obj of ready)list.append(el('li',`${obj.name}: ${obj.rows.length} occurrences`));
    details.append(list);box.append(details);
  }
  return box;
}
