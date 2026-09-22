// Owns the lifetime of one unfinished editor. No commands, arithmetic, or persistence.
// Keeping the actual controls also preserves local expression undo and exact text.
export function draftSession(){
  let current=null;
  return {
    get current(){return current},
    begin(context,panel,invalidate){
      if(current)throw Error('Finish or discard the current draft first.');
      current={context,panel,nodes:[...panel.childNodes],invalidate,parked:false};
    },
    park(){
      if(!current||current.parked)return;
      current.invalidate();
      current.nodes.forEach(node=>node.remove());
      current.parked=true;
    },
    resume(revision){
      if(!current)return null;
      if(current.context.revision!==revision)throw Error('This draft belongs to an earlier workspace. Discard it before starting another.');
      current.panel.replaceChildren(...current.nodes);
      current.parked=false;
      return current.context;
    },
    clear(){current=null},
  };
}
