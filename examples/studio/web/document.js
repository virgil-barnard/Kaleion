// The mathematical capture stays a string: parsing/re-encoding it in JavaScript
// would round exact integers. Envelopes attach views or a finite question;
// neither supplies arithmetic or a trusted verdict.
import {validateColor} from './colors.js';
import {validateComparison} from './comparison-record.js';
const record=v=>v!==null&&typeof v==='object'&&!Array.isArray(v);
const keys=(v,names)=>record(v)&&Object.keys(v).every(k=>names.includes(k));
const bounded=(v,b=1e9)=>typeof v==='number'&&Number.isFinite(v)&&Math.abs(v)<=b;
// View offsets and fitted cameras need headroom beyond a chart's 1e9-unit extent.
const vector=v=>Array.isArray(v)&&v.length===3&&v.every(x=>bounded(x,1e12));
export function validateScene(scene){
  if(!keys(scene,['version','camera','objects','selected','tool',...(scene?.version===2?['theme']:[])])||![1,2].includes(scene.version))throw Error('Unsupported canvas view version.');
  if(scene.version===2&&!['system','light','dark'].includes(scene.theme))throw Error('Invalid saved theme.');
  const c=scene.camera;
  if(!keys(c,['x','y','w','h','yaw','pitch'])||!['x','y','w','h','yaw','pitch'].every(k=>bounded(c[k],1e15))||c.w<1||c.h<1||Math.abs(c.yaw)>100||Math.abs(c.pitch)>100)throw Error('Invalid saved camera.');
  if(!['move','connect','orbit'].includes(scene.tool))throw Error('Invalid saved canvas tool.');
  if(!Array.isArray(scene.objects)||scene.objects.length>60)throw Error('Invalid saved object views.');
  const names=new Set();
  for(const o of scene.objects){
    if(!keys(o,['name','pose','marks','chart','axes','slice',...(scene.version===2?['color']:[])])||typeof o.name!=='string'||!o.name||o.name.length>80||names.has(o.name)||!vector(o.pose))throw Error('Invalid or repeated saved object view.');
    if(o.color!==undefined)validateColor(o.color);
    names.add(o.name);
    if(!['cells','points'].includes(o.marks)||!['logical','placement'].includes(o.chart)||!Array.isArray(o.axes)||o.axes.length<1||o.axes.length>3||o.axes.some(a=>typeof a!=='string'||a.length>80)||new Set(o.axes).size!==o.axes.length)throw Error('Invalid saved chart.');
    if(o.slice!==null&&(!keys(o.slice,['axis','value'])||typeof o.slice.axis!=='string'||!bounded(o.slice.value)))throw Error('Invalid saved slice.');
  }
  if(scene.selected!==null&&(!keys(scene.selected,['name','ref'])||!names.has(scene.selected.name)||!(scene.selected.ref===null||(Array.isArray(scene.selected.ref)&&scene.selected.ref.length===2&&scene.selected.ref.every(x=>typeof x==='string'&&x.length<=200)))))throw Error('Invalid saved selection.');
  return scene;
}
export function canvasDocument(workspace,scene){
  if(typeof workspace!=='string')throw Error('Save the original mathematical capture text.');
  validateScene(scene);
  return JSON.stringify({format:'kaleion-studio',version:scene.version,workspace,scene},null,2);
}
export function comparisonDocument(workspace,scene,comparison){
  if(typeof workspace!=='string')throw Error('Save the original mathematical capture text.');
  validateScene(scene);validateComparison(comparison);
  return JSON.stringify({format:'kaleion-comparison',version:1,workspace,scene,comparison},null,2);
}
export function readDocument(text){
  const data=JSON.parse(text);
  if(data?.format==='kaleion-comparison'){
    if(!keys(data,['format','version','workspace','scene','comparison'])||data.version!==1||typeof data.workspace!=='string')throw Error('Unsupported comparison document version.');
    return {workspace:data.workspace,scene:validateScene(data.scene),comparison:validateComparison(data.comparison)};
  }
  if(data?.format==='kaleion-studio'){
    if(!keys(data,['format','version','workspace','scene'])||![1,2].includes(data.version)||data.scene?.version!==data.version||typeof data.workspace!=='string')throw Error('Unsupported canvas document version.');
    return {workspace:data.workspace,scene:validateScene(data.scene)};
  }
  // Return the original bytes for ordinary schema-1 workspaces.
  return {workspace:text,scene:null};
}
