// Read-only field exploration. Groups come from captured data; this component
// never evaluates expressions, changes a declaration, or chooses correspondence.
const el=(tag,text,attrs={})=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);return n};
export const inspectField=(host,field,object=null)=>host.dispatchEvent(new CustomEvent('inspect-field',{bubbles:true,detail:{field,object}}));

export function fieldGuide({source,objects,revision,query,highlight,current}){
  const box=el('details',undefined,{class:'field-guide','data-field-guide':''}),title=el('summary','See a field on the canvas');
  const body=el('div'),scope=el('p',undefined,{class:'help','data-field-scope':''});
  const field=el('select',undefined,{'aria-label':'Field to explore'}),values=el('select',undefined,{'aria-label':'Captured field value'});
  const label=el('label','Field');label.append(field);
  const choices=el('div'),valueLabel=el('label','Value in this saved object');valueLabel.append(values);
  const row=el('div',undefined,{class:'row'}),previous=el('button','Previous value',{type:'button'}),next=el('button','Next value',{type:'button'});
  row.append(previous,next);choices.append(valueLabel,row);
  const result=el('p',undefined,{'data-field-result':'',role:'status','aria-live':'polite'});
  body.append(scope,label,result,choices);box.append(title,body);
  let owner=source,report=null,index=0,generation=0,suspended=false,loading=false;
  function available(){field.replaceChildren(...(owner?.fields||[]).map(f=>el('option',f,{value:f})));field.disabled=!owner}
  available();field.value=source.axes[0]||source.fields[0]||'';
  function valid(){return !suspended&&box.isConnected&&current()}
  function paint(){
    if(!valid()||!box.open||!report){highlight(null);return}
    const group=report.groups[index];values.value=String(index);
    previous.disabled=index<=0;next.disabled=index>=report.groups.length-1;
    if(!group){
      result.textContent='No observed values in this field. This does not declare any missing value to be zero.';
      highlight(null);return;
    }
    const key=group.key_types[0]==='text'?JSON.stringify(group.key[0]):String(group.key[0]);
    const incidence=owner.kind==='incidence';
    result.textContent=`${field.value} = ${key}: ${incidence?`${group.count} matches among `:''}${group.population} ${group.population==='1'?'item':'items'}.`
      +(group.population==='0'?' This declared group has no items.':incidence&&group.count==='0'?' The items exist; none match the relation.':'')
      +` Outlines show this group.${incidence?' Dashed outlines mean outside the relation.':''}`;
    const shown=highlight({name:owner.name,capture:report.capture,field:field.value,label:`${field.value} = ${key}`,members:group.members,matches:group.matches});
    if(shown===false)result.textContent+=' The saved source is hidden by a different preview capture; no outline is transferred to it.';
  }
  async function read(){
    const token=++generation,target=owner,key=field.value;report=null;loading=false;choices.hidden=true;highlight(null);
    if(!valid())return;
    if(!target){scope.textContent='';result.textContent='This source is unavailable. Choose a field from a saved object.';return}
    const role=target.axes.includes(key)?'Logical axis':key==='value'?'Contents field':'Saved field';
    scope.textContent=`${role} ${key} on ${target.name}. Saved object, not the draft. Counts include any items hidden by the view.`;
    if(!target.fields.includes(key)){result.textContent='This field is unavailable in the named object. No other source is substituted.';return}
    result.textContent='Reading saved groups…';loading=true;
    try{
      const data=await query({name:target.name,by:[key],revision});
      if(token!==generation||!valid()||!box.open)return;
      if(data.revision!==revision||data.name!==target.name||data.capture!==target.capture)throw Error('This field belongs to an earlier capture. Reopen the tool.');
      report=data;index=0;values.replaceChildren(...data.groups.map((g,i)=>{
        const key=g.key_types[0]==='text'?JSON.stringify(g.key[0]):String(g.key[0]);
        return el('option',`${key} · ${target.kind==='incidence'?`${g.count} matches / `:''}${g.population} items`,{value:String(i)});
      }));
      choices.hidden=!report.groups.length;paint();
    }catch(error){if(token===generation&&valid()){result.textContent=`Cannot inspect this field: ${error.message}`;highlight(null)}}
    finally{if(token===generation)loading=false}
  }
  field.onchange=read;values.onchange=()=>{index=Number(values.value);paint()};
  previous.onclick=()=>{if(index>0){index--;paint()}};next.onclick=()=>{if(report&&index+1<report.groups.length){index++;paint()}};
  // Browsing must not dirty the enclosing construction or invalidate its preview.
  for(const event of ['input','change'])box.addEventListener(event,e=>e.stopPropagation());
  box.ontoggle=()=>{if(!box.open){generation++;loading=false;highlight(null)}else if(report)paint();else if(!loading)read()};
  return {box,refresh:paint,
    show({field:key,object}){
      suspended=false;owner=object?objects.find(o=>o.name===object&&o.status==='ready'):source;
      available();
      if(!owner?.fields.includes(key))field.append(el('option',`${key} (unavailable)`,{value:key}));
      field.value=key;box.open=true;read();
    },
    suspend(){suspended=true;generation++;loading=false;highlight(null)},
    resume(){suspended=false;if(report)paint();else if(box.open)read()},
    clear(){suspended=true;generation++;loading=false;report=null;highlight(null)},
  };
}
