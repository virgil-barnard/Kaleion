// Author choices and statement presentation. Python owns graph expansion and
// exact assumptions. No program text, algebra, or proof runs in the browser.
import {validateExpansion} from './comparison-record.js';
const el=(tag,text,attrs={})=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);return n};
export function statementEditor({parameters,initial=null,run,expand}){
  const seed=initial||{vary:[],assumptions:'',coprime:[]};
  const box=el('details',undefined,{id:'construction-statement'});box.open=Boolean(initial);
  box.append(el('summary','Expand construction'),el('p','Choose which named parameters may vary. Other bindings and local cases stay fixed. Assumptions are choices to investigate; a checked case does not prove them.',{class:'help'}));
  const fields=el('fieldset'),legend=el('legend','Vary over integers');fields.append(legend);box.append(fields);
  const names=Object.keys(parameters),vary=[];
  for(const name of names){
    const input=el('input',undefined,{type:'checkbox',value:name});input.checked=seed.vary.includes(name);
    const label=el('label',`${name} · captured ${parameters[name]}`);label.prepend(input);fields.append(label);vary.push(input);
  }
  if(!names.length)fields.append(el('p','This construction has no named global parameters. Its literal constants remain fixed.',{class:'help'}));
  const assumption=el('textarea',undefined,{rows:'2',maxlength:'256',id:'statement-assumptions',placeholder:'a > 1 and b > 1'});assumption.value=seed.assumptions;
  const label=el('label','Assumptions about parameters');label.append(assumption);box.append(label);
  const pairs=el('div'),coprime=[];box.append(pairs);
  function addPair(pair=[]){
    const row=el('div',undefined,{class:'statement-pair'}),selects=[];
    for(let i=0;i<2;i++){
      const select=el('select',undefined,{'aria-label':i?'Second coprime parameter':'First coprime parameter'});
      for(const name of names)select.append(el('option',name,{value:name}));select.value=pair[i]||names[i]||'';row.append(select);selects.push(select);
    }
    const remove=el('button','Remove coprime assumption',{type:'button'}),entry={row,selects};row.append(remove);coprime.push(entry);pairs.append(row);
    remove.onclick=()=>{coprime.splice(coprime.indexOf(entry),1);row.remove();changed()};
  }
  for(const pair of seed.coprime)addPair(pair);
  const add=el('button','Assume two parameters are coprime',{type:'button'});add.disabled=names.length<2;
  add.onclick=()=>{if(coprime.length>=8){message.textContent='At most eight coprime assumptions.';return}addPair();changed()};box.append(add);
  const button=el('button','Expand statement',{type:'button',id:'expand-statement'}),message=el('p',undefined,{role:'status','aria-live':'polite',id:'statement-status'}),result=el('div',undefined,{id:'statement-result'});box.append(button,message,result);
  let accepted=initial,dirty=false;
  const finiteOnly=el('button','Keep only the finite question',{type:'button'});box.append(finiteOnly);
  finiteOnly.onclick=()=>{
    for(const input of vary)input.checked=false;
    assumption.value='';for(const {row} of coprime)row.remove();coprime.length=0;
    accepted=null;dirty=false;result.replaceChildren();message.textContent='Only the captured finite question will be saved.';
  };
  function read(){return validateExpansion({vary:vary.filter(v=>v.checked).map(v=>v.value),assumptions:assumption.value.trim(),coprime:coprime.map(({selects})=>selects.map(s=>s.value))})}
  function changed(){dirty=true;result.replaceChildren();message.textContent='Choices changed. Expand again before saving this statement.'}
  box.addEventListener('input',changed);box.addEventListener('change',changed);
  function render(report){
    result.replaceChildren();
    if(report.status==='unsupported'){
      message.textContent=`Expansion unavailable at ${report.blocker.operation}: ${report.blocker.reason}. The finite comparison can still be saved and inspected.`;
      result.append(el('p',`Source definition · ${report.blocker.node}`,{class:'help'}));return;
    }
    message.textContent='Expanded from definitions. No proof attempted.';
    result.append(el('pre',report.text));
    const hypothesis=el('div');hypothesis.append(el('h3','Author assumptions'));
    if(!report.hypotheses.length)hypothesis.append(el('p','None declared.'));
    for(const h of report.hypotheses)hypothesis.append(el('p',`${h.text} · captured case: ${h.satisfied===true?'satisfied':h.satisfied===false?'not satisfied':'undefined / unavailable'}`));
    result.append(hypothesis);
    const satisfied=report.hypotheses_defined&&report.hypotheses.every(h=>h.satisfied===true);
    result.append(el('p',!satisfied?'This case does not satisfy all declared assumptions, so a finite failure here does not refute the conditional statement.':report.finite_passed?'The captured case agrees. The statement for other parameter values remains unproved.':'The finite comparison fails under these author assumptions. Inspect its witness; construction obligations also belong to the statement.',{class:'help'}));
    const obligations=el('details');obligations.append(el('summary',`Construction obligations · ${report.obligations.length}`));
    obligations.append(el('p','These conditions must follow from your assumptions. They are goals to establish, not extra assumptions added for you.',{class:'help'}));
    for(const o of report.obligations)obligations.append(el('p',`${o.reason} · captured case: ${o.captured.satisfied===true?'satisfied':o.captured.satisfied===false?'not satisfied':'unavailable'}`),el('pre',o.text));
    if(!report.obligations.length)obligations.append(el('p','No additional conditions in this expansion.'));
    result.append(obligations,el('p',`${report.projection}. Indicators [P] are 1 when P holds and 0 otherwise. All sums retain their bounded integer domains.`,{class:'help'}));
    const receipt=el('details');receipt.append(el('summary','Statement identity'),el('p',report.translator),el('pre',report.fingerprint));result.append(receipt);
  }
  button.onclick=()=>run(async()=>{
    result.replaceChildren();message.textContent='Expanding recorded definitions…';
    try{const options=read();const report=await expand(options);accepted=options;dirty=false;render(report)}
    catch(error){dirty=true;message.textContent=`Could not expand: ${error.message}`}
  });
  if(initial)message.textContent='Saved parameter choices and assumptions restored. Expand to derive the statement again.';
  return {box,read:()=>{if(dirty)throw Error('Expand the changed statement choices before saving.');return accepted}};
}
