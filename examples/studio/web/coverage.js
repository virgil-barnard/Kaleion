import {fieldKeys} from './groups.js';

// Chooses a claim and presents captured evidence. Counts and guards belong to Python.
export function coverageInspector({source,objects,initialBy=[],run,check,inspect,showGroup,adopt,canAdopt}){
  const el=(tag,text,attrs={})=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);return n};
  const labeled=(parent,text,control)=>{const label=el('label',text);label.append(control);parent.append(label);return control};
  const box=el('div',undefined,{id:'coverage-tool'});
  box.append(el('span','DECLARE / CHECK / INSPECT',{class:'eyebrow'}),el('h2','Check coverage'),el('p',`${source.name}: exactly one match per expected key; no outside matches.`));
  const by=fieldKeys(source.fields,initialBy,'Source group keys','Choose fields that identify the receiving item');box.append(by.box);
  const expected=labeled(box,'Expected domain',el('select',undefined,{id:'coverage-expected'}));
  expected.append(el('option','Choose a collection…',{value:''}));
  for(const obj of objects.filter(o=>o.status==='ready'&&o.kind!=='incidence'))expected.append(el('option',obj.name,{value:obj.name}));
  const keySlot=el('div',undefined,{id:'coverage-expected-keys'});box.append(keySlot);let expectedKeys=null;
  box.append(el('p','Pair key fields in the same order. Choose expected items independently; duplicate matches still count separately.',{class:'help'}));
  const test=el('button','Check coverage',{type:'button',id:'check-coverage',class:'primary'});
  const message=el('p','Choose both key declarations, then check.',{id:'coverage-status',role:'status','aria-live':'polite','aria-atomic':'true'});
  const results=el('div',undefined,{id:'coverage-results'});box.append(test,message,results);
  const spec=()=>({name:source.name,by:by.read(),expected:expected.value,expected_by:expectedKeys?.read()||[]});
  function invalidate(){results.replaceChildren();message.textContent='Choices changed. Check coverage again.';message.dataset.phase='editing'}
  by.box.addEventListener('change',invalidate);
  expected.onchange=()=>{
    const target=objects.find(o=>o.name===expected.value);
    expectedKeys=target?fieldKeys(target.fields,[],'Expected key fields','Choose a unique key for each expected occurrence'):null;
    keySlot.replaceChildren(...(expectedKeys?[expectedKeys.box]:[]));
    expectedKeys?.box.addEventListener('change',invalidate);invalidate();
  };
  test.onclick=()=>run(async()=>{
    results.replaceChildren();message.textContent='Checking captured memberships…';message.dataset.phase='checking';
    try{
      const report=await check(spec()),s=report.summary;
      message.dataset.phase=report.passed?'passed':'failed';
      message.textContent=`${report.passed?'Requirement holds.':'Requirement fails.'} ${s.unique} of ${s.expected} expected keys have one match; ${s.missing} missing, ${s.multiple} multiple, ${s.outside} outside keys.${report.empty?' The expected domain is empty; this makes no claim about any item.':''}`;
      render(report);
    }catch(error){message.dataset.phase='error';message.textContent=`Could not check: ${error.message}`}
  });
  function render(report){
    const filter=labeled(results,'Show keys',el('select',undefined,{id:'coverage-filter'}));
    for(const [value,text] of [['all','All keys'],['missing','Missing matches'],['multiple','Multiple matches'],['outside','Outside expected domain'],['unique','Exactly one match']])filter.append(el('option',text,{value}));
    const keys=labeled(results,'Coverage key',el('select',undefined,{id:'coverage-key'}));
    const witness=el('div',undefined,{id:'coverage-witness'});results.append(witness);
    const rows=[...report.rows.map(r=>({...r,outside:false})),...report.unexpected.map(r=>({...r,outside:true}))];
    const keyText=row=>row.key.map((k,i)=>row.key_types[i]==='text'?JSON.stringify(k):String(k)).join(', ');
    const matchText=row=>`${row.count} ${row.count==='1'?'match':'matches'}`;
    function populate(){
      keys.replaceChildren();
      rows.forEach((row,i)=>{if(filter.value==='all'||(filter.value==='outside'?row.outside:!row.outside&&row.status===filter.value))keys.append(el('option',`${keyText(row)} · ${matchText(row)}${row.outside?' · outside':''}`,{value:String(i)}))});
      show();
    }
    function show(){
      witness.replaceChildren();if(keys.value===''){witness.append(el('p','No keys in this category.'));return}
      const row=rows[Number(keys.value)];
      witness.append(el('p',row.present?`${matchText(row)} among ${row.population} ${row.population==='1'?'candidate':'candidates'}.`:'No candidate group exists for this expected key. Its match count is zero.'));
      if(row.group!==null){const b=el('button','Show candidate group',{type:'button'});b.onclick=()=>run(()=>showGroup(report,row.group));witness.append(b)}
      if(row.expected_ref){const b=el('button','Inspect expected occurrence',{type:'button'});b.onclick=()=>run(()=>inspect(row.expected_ref,b));witness.append(b)}
      if(row.matches.length){
        let choice=null;
        if(row.matches.length>1){
          choice=labeled(witness,'Matching occurrence',el('select',undefined,{id:'coverage-match'}));
          row.matches.forEach((_,i)=>choice.append(el('option',`Match ${i+1}`,{value:String(i)})));
        }
        const b=el('button',choice?'Inspect selected match':'Inspect match',{type:'button'});
        b.onclick=()=>run(()=>inspect(row.matches[choice?Number(choice.value):0],b));witness.append(b);
      }
    }
    filter.onchange=populate;keys.onchange=show;populate();
    const adoptButton=el('button','Use unique matches…',{type:'button',id:'coverage-adopt',class:'primary'});
    adoptButton.disabled=!report.passed||!canAdopt();
    adoptButton.onclick=()=>adopt({source:report.name,by:report.by,expected:report.expected,expected_by:report.expected_by,capture:report.capture,expected_capture:report.expected_capture});
    results.append(adoptButton,el('p',!canAdopt()?'Resume or discard the parked draft before creating an assignment.':'Choose which value the sole match supplies next. Preview and Apply attach it as a new field on the expected occurrences.',{class:'help'}));
    const detail=el('details');detail.append(el('summary','Read the coverage declaration'),el('pre',JSON.stringify({...spec(),requirement:'exactly one',outside_matches:'reject'},null,2)));results.append(detail);
  }
  return box;
}
