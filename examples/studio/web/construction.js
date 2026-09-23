// Definition browsing owns its navigation stack. It sends no authoring commands.
const el=(tag,text,attrs={})=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);return n};
const key=t=>JSON.stringify([t.root,t.path]);

export function constructionInspector(host,{state,query,beforeNavigate,remember,restore,navigate,view,locked}){
  let current=null,revision=null,generation=0,stack=[],cache=new Map();
  const status=data=>data.status==='ready'?(data.capture?`Captured · ${data.extent} occurrences`:'Result capture unavailable'):data.status==='failed'?'Evaluation failed':'Not captured · definition only';
  function render(data){
    current=data;host.hidden=!data;
    host.replaceChildren();if(!data)return;
    host.dataset.definition=data.definition;host.dataset.root=data.target.root;host.dataset.path=JSON.stringify(data.target.path);
    const header=el('div',undefined,{class:'construction-heading'}),heading=el('h2',data.label,{id:'construction-title'});
    header.append(el('span','CONSTRUCTION',{class:'eyebrow'}),heading);
    if(stack.length){
      const back=el('button',`Back to ${stack.at(-1).data.label}`,{type:'button',id:'construction-back'});
      back.onclick=async()=>{
        if(locked())return;
        const ticket=++generation,previous=stack.pop();
        try{
          await restore(previous.context,()=>ticket===generation);
          if(ticket!==generation)return;
          current=previous.data;host.replaceChildren(...previous.nodes);host.dataset.definition=current.definition;
          host.dataset.root=current.target.root;host.dataset.path=JSON.stringify(current.target.path);
          previous.focus?.focus({preventScroll:true});host.parentElement.scrollTop=previous.scroll;
        }catch(error){if(ticket===generation){stack.push(previous);render(current);host.append(el('p',error.message,{class:'error',role:'status'}))}}
      };header.append(back);
    }
    const summary=el('p',`${data.title} · ${data.kind}`,{class:'construction-summary'});
    const badge=el('p',`${data.context} · ${status(data)}`,{class:'construction-status','data-definition-status':data.status});
    const details=el('details',undefined,{id:'construction-details',open:''});
    details.append(el('summary','How this is made'));
    const formula=el('dl',undefined,{class:'construction-arguments'});
    for(const a of data.arguments)formula.append(el('dt',a.label),el('dd',a.text));
    if(!data.arguments.length)details.append(el('p','This operation is declared by its inputs below.',{class:'help'}));
    else details.append(formula);
    if(data.error)details.append(el('p',data.error,{class:'error construction-error'}));
    const params=data.parameters===null?'Local parameter values were not captured. Follow Back to inspect the case declaration.':Object.entries(data.parameters).map(([k,v])=>`${k} = ${v}`).join(' · ')||'No parameter bindings';
    details.append(el('p',`${data.local_depth?'Local evaluation case':'Evaluation case'} · ${params}`,{class:'help','data-construction-case':''}));
    if(data.inputs.length){
      details.append(el('h3','Inputs'));
      const inputs=el('ol',undefined,{class:'construction-inputs'});
      data.inputs.forEach(input=>{
        const item=el('li'),button=el('button',undefined,{type:'button','data-construction-input':JSON.stringify(input.target),'aria-label':`Inspect ${input.label} · ${input.role}`});
        button.append(el('strong',input.label),el('span',input.role),el('small',`${input.context} · ${input.status==='ready'?'captured':input.status==='failed'?'failed':'not captured'}`));
        button.onclick=()=>follow(input.target,button);item.append(button);
        for(const read of data.reads.filter(r=>key(r.target)===key(input.target))){
          const meaning=el('dl',undefined,{class:'construction-read'});
          if(read.mode==='aligned'&&read.on!==undefined){
            for(const [label,value] of [['At',read.site],['Target key',read.on],['Driver key',read.key],['Field read',read.value]])meaning.append(el('dt',label),el('dd',value));
          }else meaning.append(el('dt',read.site),el('dd',read.mode==='scalar'?'Require one scalar result':'Positional lookup in this input'));
          item.append(meaning);
        }
        inputs.append(item);
      });details.append(inputs);
    }else details.append(el('p','Source constructor · no object inputs.',{class:'help'}));
    for(const note of data.notes)details.append(el('p',note,{class:'help'}));
    const show=el('button','View captured result',{type:'button',id:'construction-view'});
    show.disabled=!data.capture;
    show.onclick=()=>view(data);details.append(show);
    details.append(el('p','Read-only declaration. Inspect an occurrence in the captured result to follow its value and contributors.',{class:'help'}));
    const canonical=el('details',undefined,{class:'construction-canonical'});
    canonical.append(el('summary','Exact operation and scoped references'));
    canonical.append(el('p',`Definition ${data.definition}${data.capture?` · capture ${data.capture}`:''}`,{class:'help'}));
    for(const bindings of data.scope_bindings)canonical.append(el('p','Enclosing local bindings'),el('pre',bindings));
    canonical.append(el('pre',data.canonical));
    if(data.canonical_truncated)canonical.append(el('p','Showing the first 24,000 characters. Save preserves the complete declaration.',{class:'help'}));
    details.append(canonical);host.append(header,summary,badge,details);
  }
  async function follow(target,focus){
    if(locked())return;
    const ticket=++generation;
    host.querySelectorAll('[data-construction-loading]').forEach(node=>node.remove());
    beforeNavigate();
    const previous={data:current,nodes:[...host.childNodes],context:remember(),focus,scroll:host.parentElement.scrollTop};
    host.setAttribute('aria-busy','true');
    const message=el('p','Reading input definition…',{role:'status','data-construction-loading':''});host.append(message);
    try{
      let data=cache.get(key(target));
      if(!data){data=await query(target);if(ticket!==generation)return;cache.set(key(target),data)}
      if(ticket!==generation)return;
      stack.push(previous);render(data);await navigate(data);
      if(ticket===generation){host.querySelector('#construction-back')?.focus({preventScroll:true});host.scrollIntoView({block:'nearest'})}
    }catch(error){if(ticket===generation){message.textContent=error.message;message.className='error';if(!message.isConnected)host.append(message)}}
    finally{if(ticket===generation){host.removeAttribute('aria-busy');if(message.textContent==='Reading input definition…')message.remove()}}
  }
  function select(name){
    generation++;stack=[];host.removeAttribute('aria-busy');
    if(revision!==state().revision){revision=state().revision;cache=new Map()}
    for(const obj of state().objects)if(obj.construction)cache.set(key(obj.construction.target),obj.construction);
    render(state().objects.find(o=>o.name===name)?.construction||null);
  }
  return {select,collapse(){const details=host.querySelector('#construction-details');if(details)details.open=false}};
}
