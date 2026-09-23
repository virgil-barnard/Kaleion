// Inspection is a drawer over the continuous canvas, never a camera/surface mode.
// This module owns disclosure and focus only; it cannot evaluate mathematics.
export function canvasShell(root,{onClose}){
  const panel=root.querySelector('#panel'),close=root.querySelector('#close-panel');
  let opener=null;
  function open(section='details',title='Object'){
    if(panel.hidden)opener=document.activeElement;
    panel.hidden=false;panel.dataset.section=section;
    root.querySelector('#panel-title').textContent=title;
    root.querySelector('#construction').classList.toggle('shelved',!['details','construction'].includes(section));
    root.querySelector('#activity').hidden=section==='view';
    root.querySelector('#object-view').hidden=section!=='view';
    root.querySelector('#object-tools').hidden=section!=='details';
    panel.scrollTop=0;
  }
  function hide(){
    onClose();panel.hidden=true;
    (opener?.isConnected?opener:root.querySelector('#workspace-canvas')).focus({preventScroll:true});
  }
  close.onclick=hide;
  // A native dialog, select, or formula popover owns Escape first.
  root.addEventListener('keydown',event=>{
    if(event.key==='Escape'&&!event.defaultPrevented&&!panel.hidden&&panel.contains(event.target)
        &&!root.querySelector('dialog[open]')&&!event.target.closest('select,[data-expression-dialog]')){
      event.preventDefault();hide();
    }
  });
  return {open,hide,get visible(){return !panel.hidden}};
}
