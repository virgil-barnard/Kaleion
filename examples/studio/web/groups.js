// Shared key declaration widget. Selection state and backend query policy live elsewhere.
export function fieldKeys(fields,initial=[],label='Group keys',emptyLabel='Whole domain · no retained keys'){
  let keys=[...initial];
  const box=document.createElement('div');box.className='field-keys';box.setAttribute('role','group');box.setAttribute('aria-label',label);
  const chips=document.createElement('div');chips.className='key-chips';
  const add=document.createElement('select');add.setAttribute('aria-label',`Add ${label.toLowerCase()}`);add.dataset.groupAdd='';
  const wrapper=document.createElement('label');wrapper.textContent=label;wrapper.append(add);box.append(chips,wrapper);
  function render(){
    chips.replaceChildren();
    if(!keys.length){const total=document.createElement('span');total.className='quiet';total.textContent=emptyLabel;chips.append(total)}
    for(const [i,key] of keys.entries()){
      const chip=document.createElement('button');chip.type='button';chip.textContent=`${key} ×`;chip.setAttribute('aria-label',`Remove key ${key}`);
      chip.onclick=()=>{keys.splice(i,1);render();box.dispatchEvent(new Event('change',{bubbles:true}));(chips.querySelectorAll('button')[i]||add).focus({preventScroll:true})};chips.append(chip);
    }
    add.replaceChildren(new Option('Add a field…',''));
    for(const field of fields.filter(f=>!keys.includes(f)))add.append(new Option(field,field));
  }
  add.onchange=()=>{if(add.value){keys.push(add.value);render();box.dispatchEvent(new Event('change',{bubbles:true}))}};
  render();return {box,read:()=>[...keys]};
}
