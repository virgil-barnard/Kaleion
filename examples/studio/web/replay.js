// Presentation-only samples. No requests, definitions, or parameter evaluation.
export function replayControls(root,{draw,restore,onPresentation}){
  const range=root.querySelector('input'),readout=root.querySelector('output');
  let frames=[],bounds=[],name=null;
  function reset(paint=true){range.value=String(Math.max(0,frames.length-1));readout.textContent='Applied result';onPresentation(false);if(paint)restore()}
  function show(index){
    if(!frames.length)return;
    range.value=String(index);readout.textContent=`Replay ${Math.round(100*index/(frames.length-1))}% · presentation only`;
    onPresentation(true);draw(frames[index],bounds);
  }
  range.oninput=()=>show(Number(range.value));
  root.querySelector('[data-replay-result]').onclick=()=>reset();
  return {
    reset,
    clear(){frames=[];bounds=[];name=null;root.hidden=true;reset(false)},
    select(active){if(active!==name)this.clear();else reset(false)},
    record(samples,active){
      frames=samples||[];name=active;bounds=frames.flatMap(f=>f.positions);
      root.hidden=frames.length<2;range.max=String(Math.max(0,frames.length-1));reset();
    },
    async play(){
      if(frames.length<2)return;
      let start;
      await new Promise(resolve=>{function tick(t){start??=t;const progress=Math.min(1,(t-start)/550);show(Math.round(progress*(frames.length-1)));if(progress<1)requestAnimationFrame(tick);else resolve()}requestAnimationFrame(tick)});
      reset();
    },
  };
}
