// Two syntax views of one relation. Parsing belongs to the adapter; neither
// switching views nor formatting a rule evaluates or commits mathematics.
import {inspectField} from './field-guide.js';
const el=(tag,text,attrs={})=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);return n};
const symbols={'+':'+','-':'-','*':'*','//':'//','%':'%','=':'=','≠':'!=','<':'<','≤':'<=','>':'>','≥':'>=',and:'and',or:'or'};
const precedence={or:1,and:2,'=':3,'≠':3,'<':3,'≤':3,'>':3,'≥':3,'+':4,'-':4,'*':5,'//':5,'%':5};
const reserved=new Set('False None True and as assert async await break class continue def del elif else except finally for from global if import in is lambda nonlocal not or pass raise return try while with yield'.split(' '));
export function formulaText(spec,fields,parameters,{relation=true}={}){
  function condition(node){
    if(['and','or'].includes(node.op)){node.args.forEach(condition);return}
    if(!['=','≠','<','≤','>','≥'].includes(node.op))throw Error('Write a rule needs comparisons joined with and/or. Keep this rule in controls.');
  }
  if(relation)condition(spec);
  function visit(node){
    if('integer'in node){
      if(typeof node.integer!=='string'||! /^-?(0|[1-9][0-9]*)$/.test(node.integer))throw Error('Finish the exact integer in controls before writing this rule.');
      return {text:node.integer,level:6};
    }
    if('field'in node||'parameter'in node){
      const name=node.field??node.parameter;
      if(!('field'in node?fields:parameters).includes(name)
          ||!/^[A-Za-z_][A-Za-z0-9_]*$/.test(name)||reserved.has(name)
          ||(fields.includes(name)&&parameters.includes(name)))throw Error('This name needs the explicit field/parameter controls.');
      return {text:name,level:6};
    }
    if('op'in node&&Object.hasOwn(symbols,node.op)){
      const level=precedence[node.op];
      const args=node.args.map((arg,i)=>{const child=visit(arg);return child.level<level||(child.level===level&&(i===1||level===3))?`(${child.text})`:child.text});
      return {text:`${args[0]} ${symbols[node.op]} ${args[1]}`,level};
    }
    throw Error('This rule uses a keyed read or tuple. Keep editing it with controls.');
  }
  const text=visit(spec).text;
  if(text.length>256)throw Error('This rule is longer than the short notation. Keep editing it with controls.');
  return text;
}

export function relationNotation(initial,fields,parameters,expr,parse){
  return formulaNotation(initial,fields,parameters,expr,parse,true);
}
export function scalarNotation(initial,fields,parameters,expr,parse){
  return formulaNotation(initial,fields,parameters,expr,parse,false);
}
function formulaNotation(initial,fields,parameters,expr,parse,relation){
  const box=el('div',undefined,{class:'relation-notation'}),toolbar=el('div',undefined,{class:'row'});
  const controls=el('button','Use controls',{type:'button','data-rule-controls':'','aria-pressed':'true'});
  const write=el('button',relation?'Write a rule':'Write a formula',{type:'button','data-rule-write':'','aria-pressed':'false'});
  toolbar.append(controls,write);box.append(toolbar);
  let editor=expr(initial,fields),mode='controls',pending=false,generation=0;
  const graphical=el('div');graphical.append(editor.box);
  const written=el('div'),label=el('label',relation?'Match when':'Formula'),input=el('textarea',undefined,{rows:'2',maxlength:'256','aria-label':relation?'Relation rule':'Arithmetic formula',spellcheck:'false',autocomplete:'off',autocapitalize:'off'});
  label.append(input);written.append(label,el('p',relation?'Use =, !=, <, <=, >, >=; join conditions with and / or. Arithmetic: + - * // %. For example: 0 <= i < 4 and i != j.':'Use fields, parameters, + − * // % and parentheses. Use controls for keyed reads from other objects.',{class:'help'}));
  const names=el('div',undefined,{class:'field-names'});names.append(el('p','Explore a field on the canvas:',{class:'help'}));
  for(const name of fields){const b=el('button',name,{type:'button','aria-label':`Explore field ${name}`});b.onclick=()=>inspectField(box,name);names.append(b)}
  names.append(el('p',`Parameters: ${parameters.join(', ')||'none'}.`,{class:'help'}));
  written.append(names);written.hidden=true;
  const feedback=el('p',undefined,{class:'help',role:'status','aria-live':'polite','data-rule-status':''});
  box.append(graphical,written,feedback);
  function changed(){box.dispatchEvent(new Event('change',{bubbles:true}))}
  function show(next){mode=next;graphical.hidden=mode!=='controls';written.hidden=mode!=='text';controls.setAttribute('aria-pressed',String(mode==='controls'));write.setAttribute('aria-pressed',String(mode==='text'))}
  input.oninput=()=>{generation++;feedback.textContent='Draft expression. Preview checks its result.'};
  write.onclick=()=>{
    if(mode==='text'||pending)return;
    try{input.value=formulaText(editor.read(),fields,parameters,{relation});show('text');feedback.textContent='The same expression, written as text.';changed();input.focus({preventScroll:true});input.scrollIntoView({block:'center'})}
    catch(error){feedback.textContent=error.message}
  };
  controls.onclick=async()=>{
    if(mode==='controls'||pending)return;
    const token=++generation,text=input.value;pending=true;controls.disabled=write.disabled=true;changed();feedback.textContent='Reading the expression…';
    try{
      const spec=await parse(text);
      if(token!==generation){feedback.textContent='The text changed while reading it. Choose Use controls again.';return}
      editor=expr(spec,fields);graphical.replaceChildren(editor.box);show('controls');
      feedback.textContent='Expression translated to controls. Preview still checks its result.';
      graphical.querySelector('button')?.focus({preventScroll:true});
    }catch(error){if(token===generation)feedback.textContent=`${error.message}. Your written rule is kept.`}
    finally{pending=false;controls.disabled=write.disabled=false;changed()}
  };
  return {box,read:()=>{if(pending)throw Error('Wait for the rule to finish reading.');return mode==='text'?{formula:input.value}:editor.read()}};
}
