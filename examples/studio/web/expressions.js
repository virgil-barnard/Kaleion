// A structured formula editor. This module edits syntax; it never calculates it.
const symbols={'+':'+','-':'−','*':'×','//':'div','%':'mod','=':'=','≠':'≠','<':'<','≤':'≤','>':'>','≥':'≥',and:'∧',or:'∨'};
const clone=value=>structuredClone(value);
const field=name=>({field:name}), number=value=>({integer:String(value)});
const node=(tag,text,attrs={})=>{
  const element=document.createElement(tag);if(text!==undefined)element.textContent=text;
  for(const [key,value] of Object.entries(attrs))element.setAttribute(key,value);
  return element;
};

export function formatExpression(spec){
  if('field' in spec)return spec.field;
  if('integer' in spec)return spec.integer;
  if('parameter' in spec)return `$${spec.parameter}`;
  if('tuple' in spec)return `(${spec.tuple.map(formatExpression).join(', ')})`;
  if('op' in spec)return `(${formatExpression(spec.args[0])} ${symbols[spec.op]} ${formatExpression(spec.args[1])})`;
  const r=spec.read;
  return `read ${r.object}(${formatExpression(r.value)}; source ${formatExpression(r.key)} ↔ target ${formatExpression(r.on)})`;
}

function at(tree,path){return path.reduce((part,key)=>part[key],tree)}
function replaced(tree,path,replacement){
  if(!path.length)return clone(replacement);
  const next=clone(tree);at(next,path.slice(0,-1))[path.at(-1)]=clone(replacement);return next;
}
function contextAt(tree,path,fields,sources){
  let part=tree, context=fields;
  for(let i=0;i<path.length;i++){
    const key=path[i];
    if(key==='read'&&['key','value'].includes(path[i+1])){
      context=sources.find(source=>source.name===part.read.object)?.fields||[];
    }
    part=part[key];
  }
  return context;
}

export function expressionEditor(initial,fields,sources=[],parameters=[]){
  let tree=clone(initial), selected=null, past=[], returnPath=null;
  const box=node('div',undefined,{class:'expression'});
  const formula=node('div',undefined,{class:'formula','aria-label':'Structured expression'});
  const toolbar=node('div',undefined,{class:'formula-tools'});
  const edit=node('button','Edit whole expression',{type:'button','data-edit-root':''});
  const undo=node('button','Undo expression edit',{type:'button','data-expression-undo':''});
  const sheet=node('div',undefined,{class:'expression-sheet'});sheet.hidden=true;
  toolbar.append(edit,undo);box.append(formula,toolbar,sheet);

  function update(replacement){
    if(selected===null)return;
    const next=replaced(tree,selected,replacement);
    if(JSON.stringify(next)!==JSON.stringify(tree)){
      past.push(clone(tree));if(past.length>32)past.shift();tree=next;
      box.dispatchEvent(new Event('change',{bubbles:true}));
    }
    renderFormula();
  }
  function optionList(values,value,label){
    const select=node('select',undefined,{'aria-label':label});
    if(value!==undefined&&!values.includes(value))values=[value,...values];
    for(const item of values)select.append(node('option',item,{value:item}));
    if(value!==undefined)select.value=value;
    return select;
  }
  function labeled(label,control){const wrapper=node('label',label);wrapper.append(control);sheet.append(wrapper);return control}
  function focusPart(){
    const target=[...formula.querySelectorAll('[data-path]')].find(button=>button.dataset.path===returnPath);
    (target||edit).focus({preventScroll:true});
  }
  function close(){selected=null;sheet.hidden=true;renderFormula();focusPart()}
  function focusEditor(label){
    const inputs=[...sheet.querySelectorAll('input,select')];
    (inputs.find(input=>input.getAttribute('aria-label')===label)||inputs.at(-1))?.focus({preventScroll:true});
  }
  function open(path,fromRoot=false){selected=path;returnPath=fromRoot?null:path.join('/');sheet.hidden=false;renderSheet();renderFormula();focusEditor()}
  function renderFormula(){
    formula.replaceChildren();
    function token(text,path,label){
      const button=node('button',text,{type:'button',class:'formula-token','data-path':path.join('/'),'aria-label':label});
      button.setAttribute('aria-pressed',String(JSON.stringify(path)===JSON.stringify(selected)));
      button.onclick=()=>open(path);return button;
    }
    function render(spec,path,parent){
      if('field' in spec){parent.append(token(spec.field,path,`Edit field ${spec.field}`));return}
      if('integer' in spec){parent.append(token(spec.integer,path,`Edit integer ${spec.integer}`));return}
      if('parameter' in spec){parent.append(token(`$${spec.parameter}`,path,`Edit parameter ${spec.parameter}`));return}
      if('op' in spec){
        parent.append(node('span','('));render(spec.args[0],[...path,'args',0],parent);
        parent.append(token(symbols[spec.op],path,`Edit operation ${symbols[spec.op]}`));
        render(spec.args[1],[...path,'args',1],parent);parent.append(node('span',')'));return;
      }
      if('tuple' in spec){
        parent.append(token('(',path,'Edit key tuple'));
        spec.tuple.forEach((part,i)=>{if(i)parent.append(node('span',','));render(part,[...path,'tuple',i],parent)});
        parent.append(node('span',')'));return;
      }
      const r=spec.read;
      parent.append(token(`read ${r.object}`,path,`Edit keyed read from ${r.object}`),node('span','('));
      render(r.value,[...path,'read','value'],parent);parent.append(node('span','; source'));
      render(r.key,[...path,'read','key'],parent);parent.append(node('span','↔ target'));
      render(r.on,[...path,'read','on'],parent);parent.append(node('span',')'));
    }
    render(tree,[],formula);formula.setAttribute('aria-label',formatExpression(tree));
    undo.disabled=!past.length;
  }
  function renderSheet(){
    sheet.replaceChildren();const spec=at(tree,selected), available=contextAt(tree,selected,fields,sources);
    const heading=node('div',undefined,{class:'row'}),done=node('button','Done',{type:'button','data-expression-done':''});
    heading.append(node('strong','Edit selected part'),done);sheet.append(heading);
    done.onclick=close;
    const kind='field'in spec?'Field':'integer'in spec?'Number':'parameter'in spec?'Parameter':'op'in spec?'Operation':'tuple'in spec?'Key tuple':'Keyed read';
    const type=labeled('Replace with',optionList(['Field','Number','Parameter','Operation','Key tuple','Keyed read'],kind,'Expression type'));
    type.onchange=()=>{
      if(selected.length>30){sheet.append(node('p','Expression nesting exceeds the editor budget.'));type.value=kind;return}
      let replacement;
      if(type.value==='Field')replacement=field(available[0]||'value');
      else if(type.value==='Number')replacement=number(0);
      else if(type.value==='Parameter'){
        if(!parameters.length){sheet.append(node('p','Declare a parameter in Parameters before starting this construction.'));type.value=kind;return}
        replacement={parameter:parameters[0]};
      }
      else if(type.value==='Operation')replacement={op:'+',args:[clone(at(tree,selected)),number(1)]};
      else if(type.value==='Key tuple')replacement={tuple:[clone(at(tree,selected)),field(available[0]||'value')]};
      else{
        if(!sources.length){sheet.append(node('p','Create a source or measurement to read first.'));type.value=kind;return}
        replacement={read:{object:sources[0].name,on:field(available.includes('key')?'key':available[0]),key:field('key'),value:field('value')}};
      }
      update(replacement);renderSheet();focusEditor('Expression type');
    };
    if(kind==='Field'){
      const value=labeled('Field in this context',optionList(available,spec.field,'Field'));
      if(!available.includes(spec.field))sheet.append(node('p','This field is unavailable in the selected context. Choose another field.',{class:'help'}));
      value.onchange=()=>update(field(value.value));
    }else if(kind==='Number'){
      const value=node('input',undefined,{type:'text',inputmode:'numeric','aria-label':'Exact integer'});value.value=spec.integer;
      labeled('Exact integer',value);value.oninput=()=>update(number(value.value));
    }else if(kind==='Parameter'){
      const value=labeled('Declared parameter',optionList(parameters,spec.parameter,'Parameter'));
      value.onchange=()=>update({parameter:value.value});
      sheet.append(node('p','This name reads the saved parameter value. Use Parameters to change its exact value across the construction.',{class:'help'}));
    }else if(kind==='Operation'){
      const value=labeled('Operation',optionList(Object.keys(symbols),spec.op,'Operation'));
      value.onchange=()=>update({...at(tree,selected),op:value.value});
      sheet.append(node('p','Tap either operand in the formula to edit it. “div” is floor integer division; “mod” requires a positive modulus.',{class:'help'}));
      const row=node('div',undefined,{class:'row'});
      for(const [index,label] of [[0,'Keep left operand'],[1,'Keep right operand']]){
        const keep=node('button',label,{type:'button'});keep.onclick=()=>{update(at(tree,selected).args[index]);renderSheet();focusEditor()};row.append(keep);
      }
      sheet.append(row);
    }else if(kind==='Key tuple'){
      sheet.append(node('p','Match components in the same order on both sides of a read. Each component is a scalar field or expression; tap it to edit.',{class:'help'}));
      const row=node('div',undefined,{class:'row'}),add=node('button','Add component',{type:'button'}),remove=node('button','Remove last component',{type:'button'});
      add.disabled=spec.tuple.length>=8;remove.disabled=spec.tuple.length<=2;
      add.onclick=()=>{update({tuple:[...at(tree,selected).tuple,field(available[0]||'value')]});renderSheet();focusEditor('Expression type')};
      remove.onclick=()=>{update({tuple:at(tree,selected).tuple.slice(0,-1)});renderSheet();focusEditor('Expression type')};
      row.append(add,remove);sheet.append(row);
    }else{
      const source=labeled('Read from',optionList(sources.map(s=>s.name),spec.read.object,'Read from'));
      source.onchange=()=>{update({read:{...at(tree,selected).read,object:source.value}});renderSheet();focusEditor('Read from')};
      sheet.append(node('p','The source key and value belong to the driver. The target key belongs to the object receiving the read. Tap each part in the formula to edit it.',{class:'help'}));
    }
  }
  edit.onclick=()=>open([],true);
  box.addEventListener('keydown',event=>{
    if(event.key==='Escape'&&selected!==null){event.stopPropagation();event.preventDefault();close()}
  });
  undo.onclick=()=>{if(!past.length)return;tree=past.pop();selected=null;sheet.hidden=true;renderFormula();box.dispatchEvent(new Event('change',{bubbles:true}));(undo.disabled?edit:undo).focus({preventScroll:true})};
  renderFormula();
  return {box,read:()=>clone(tree)};
}
