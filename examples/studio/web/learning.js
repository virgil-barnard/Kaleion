// Discovery and tutorial presentation only. All mathematical edits remain in
// the existing controls; tutorial navigation does not issue commands.
const el=(tag,text,attrs={})=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);return n};
const steps=[
  ['Begin with a blank canvas','Save any work you want to keep. Open → Blank canvas → Load example. Starting or advancing this guide never changes your mathematics.','The walkthrough builds Numbers, Triangle, Counts, Formula, and Markers using the ordinary controls.'],
  ['Declare a size','Parameters → Declare parameter. Name it n, value 4. Preview, then Keep results.','Sizes and formulas can now use n. A new parameter case is a calculation, not a playback frame.'],
  ['Give a grid values','Create → Grid. Name: Numbers. Set both sizes to n + 1. Choose Values from a formula and enter i + j. Create.','There are 25 locations, with indices 0 through 4 on each axis.'],
  ['Make a triangular relation','Numbers → Details → Relation. Name: Triangle. Customize the formula → Write a rule: value < n. Preview, then Apply.','Ten locations match. The other fifteen still belong to the source domain.'],
  ['Turn counts into an object','Triangle → Details → Sum / count. Name: Counts. Choose Count matches and total along j only, keeping i. Preview, then Apply.','Counts are 4, 3, 2, 1, 0. The last group exists even though no item matches there.'],
  ['Give those counts something to move','Create → Vector. Name: Markers. Size: n + 1. Choose Values from a formula: 0. Create.','Five distinct markers start in a line. Their numeric labels are zero; positions are separate.'],
  ['Create your first motion','Counts → Details → Combine. Destination: Markers. Choose Drive a transformation and keep Coordinates. The y coordinate reads Counts. Keep source key ↔ target key as key ↔ key and the supplied value as value. Preview, then Apply.','Applying new coordinates records a movement. Dragging an object name only moves its view; it does not record mathematical motion.'],
  ['Play and reverse it','With Markers selected, use Replay saved movement, Play, or drag the scrubber. Undo reverses the recorded move; Redo restores it. Show result returns to the exact endpoint.','If you changed selection, select Markers and use Undo then Redo to recover replay. Save → Canvas and view preserves the captured history.'],
  ['Follow a height to its cause','Tap a moved marker, or use Appearance → Choose an item. Follow keyed read, then View measurement and contributors. Try the marker at height 2 and the zero-height marker.','The height 2 reads a count with two contributors. The marker label stays zero; its position is driven by the measurement.'],
  ['Build an independent prediction','Create → Vector. Name: Formula. Size: n + 1. Choose Values from a formula: n - i. Create.','This independently produces 4, 3, 2, 1, 0. A similar-looking graph alone does not declare equality.'],
  ['Ask an exact finite question','Counts → Details → More tools → Compare exact fields. Left value: value; add left key i. Right object: Formula, value: value, right key i. Expected domain: Formula, expected key i. Compare captured values.','All five keys agree. This checks the saved case. The formula, key correspondence and expected domain are explicit.'],
  ['Vary, save, and continue','Parameters: change n to 6, Preview and Keep results. Reopen Compare on Counts and compare again. Save → Canvas and view. Try n = 0 next: one retained zero remains.','Next load Pack a triangle for ranks and prefixes, Three measurements lift a plane for 3D motion, then A box of ones and its counterexample. General proofs remain a later layer.'],
];

export function learningShelf({dialog,guide,load,chooseFile,allowed,status,returnFocus}){
  const list=dialog.querySelector('[data-example-list]'),detail=dialog.querySelector('[data-example-detail]');
  const confirm=dialog.querySelector('[data-example-load]'),message=dialog.querySelector('[data-example-status]');
  let entries=null,selected=null,step=0;
  function renderGuide(){
    guide.replaceChildren();
    const summary=el('summary',`Walkthrough · ${step+1}/${steps.length} · ${steps[step][0]}`);
    const body=el('div',undefined,{class:'tutorial-body'}),action=el('p',steps[step][1]),expect=el('p',steps[step][2],{class:'help'});
    const row=el('div',undefined,{class:'row'}),previous=el('button','Previous',{type:'button','data-tutorial-previous':''}),next=el('button','Next',{type:'button','data-tutorial-next':''}),close=el('button','End guide',{type:'button'});
    previous.disabled=step===0;next.disabled=step===steps.length-1;
    function turn(delta){step+=delta;renderGuide();const target=guide.querySelector(delta>0?'[data-tutorial-next]':'[data-tutorial-previous]');(target.disabled?guide.querySelector('summary'):target).focus({preventScroll:true})}
    previous.onclick=()=>turn(-1);next.onclick=()=>turn(1);close.onclick=()=>{guide.hidden=true;returnFocus();status('Guide closed. Your construction is unchanged.')};
    row.append(previous,next,close);body.append(action,expect,row);guide.append(summary,body);
  }
  dialog.querySelector('[data-open-file]').onclick=()=>{if(!allowed())return;dialog.close();chooseFile()};
  dialog.querySelector('[data-close-library]').onclick=()=>dialog.close();
  dialog.querySelector('[data-start-tutorial]').onclick=()=>{dialog.close();step=0;renderGuide();guide.hidden=false;guide.open=true;guide.querySelector('summary').focus();status('Walkthrough opened. Follow the steps with the ordinary canvas tools.')};
  confirm.onclick=async()=>{
    if(!selected||!allowed())return;
    const entry=selected;
    try{
      await load(entry);
      dialog.close();status(entry.next);
    }catch(error){message.textContent=`Could not open example: ${error.message}. Your previous canvas is retained.`}
  };
  function choose(entry){
    selected=entry;detail.replaceChildren(el('h3',entry.title),el('p',entry.description),el('p',entry.next,{class:'help'}));confirm.disabled=!allowed();
    list.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.example===entry.id)));message.textContent='Loading replaces the current canvas. Save first if you want to keep your work.';
  }
  return {async open(){
    if(!allowed())return;
    dialog.showModal();confirm.disabled=true;selected=null;detail.replaceChildren();message.textContent='Choose a saved file, an example, or the walkthrough.';
    try{
      if(!entries){const r=await fetch('/api/examples');if(!r.ok)throw Error('Example list unavailable');entries=await r.json()}
      if(!dialog.open)return;
      list.replaceChildren(...entries.map(entry=>{const b=el('button',entry.title,{type:'button','data-example':entry.id,'aria-pressed':'false'});b.onclick=()=>choose(entry);return b}));
    }catch(error){message.textContent=error.message+' You can still choose a local file.'}
  }};
}
