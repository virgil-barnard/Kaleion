// Presentation coordinates are deliberately separate from exact field strings.
export const refKey = ref => JSON.stringify(ref);
export function viewPositions(obj){
  if(!obj?.rows)return [];
  if(obj.placed)return obj.rows.map(r=>[r.position[0],r.position[1]||0]);
  const [a,b]=obj.axes.length?obj.axes:['index','value'];
  return obj.rows.map(r=>[Number(r.fields[a]),Number(r.fields[b] || 0)]);
}
export function projectionLabel(obj){
  return obj.placed?`Declared ${obj.dimension}D placement${obj.dimension===3?' · XY projection':''}`:'Approximate table projection · exact labels';
}
