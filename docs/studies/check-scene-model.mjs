// Optional offline JS contracts for geometry and lossless canvas documents.
import assert from 'node:assert/strict';
import {projection,planes,geometry,chartDefaults,cellFaces,UNIT} from '../../examples/studio/web/scene.js';
import {canvasDocument,readDocument,validateScene} from '../../examples/studio/web/document.js';
const near=(a,b)=>a.forEach((v,i)=>assert.ok(Math.abs(v-b[i])<1e-10,`${a} != ${b}`));
near(projection(...planes.xy).point([2,3,4]),[2*UNIT,-3*UNIT,4]);
near(projection(...planes.xz).point([2,3,4]),[2*UNIT,-4*UNIT,-3]);
near(projection(...planes.yz).point([2,3,4]),[3*UNIT,-4*UNIT,2]);
for(const angles of Object.values(planes)){
  const p=projection(...angles);near(p.point(p.shift(35,-49)),[35,-49,0]);
  assert.equal(cellFaces([2,3,4],3,p).length,3);
}
const obj={name:'A',status:'ready',placed:true,dimension:3,axes:['i','j','k'],shape:['2','2','2'],rows:[
  {ref:['scope','a'],fields:{i:'0',j:'1',k:'0',value:'9007199254740993'},position:[3,0,7],match:true},
  {ref:['scope','b'],fields:{i:'1',j:'0',k:'1',value:'9007199254740993'},position:[3,0,7],match:false},
]};
const original=JSON.stringify(obj),s=chartDefaults(obj),g=geometry(obj,s);
assert.deepEqual(g.positions,[[3,0,7],[3,0,7]]);
s.marks='points';assert.deepEqual(geometry(obj,s).positions,g.positions);
s.chart='logical';s.axes=['k','i','j'];s.slice={axis:'i',value:1};
const logical=geometry(obj,s);assert.deepEqual(logical.positions,[[0,0,1],[1,1,0]]);
assert.deepEqual(logical.positions.filter(logical.visible),[[1,1,0]]);
assert.deepEqual(logical.high,[1,1,1]);assert.equal(JSON.stringify(obj),original);
const empty=geometry({...obj,placed:false,rows:[],shape:['0','3','4']},{...s,axes:['i','j','k'],slice:null});
assert.deepEqual(empty.high,[0,2,3]);assert.deepEqual(empty.positions,[]);
const enormous=geometry({...obj,placed:false,rows:[],shape:['0','1'+'0'.repeat(100),'4']},{...s,axes:['i','j','k'],slice:null});
assert.equal(enormous.valid,false);assert.ok(enormous.high.every(Number.isFinite));
const camera={x:0,y:0,w:900,h:600,yaw:0,pitch:0};
const scene={version:1,camera,objects:[{name:'A',pose:[-2,3,4],...s}],selected:{name:'A',ref:['scope','b']},tool:'orbit'};
const workspace='{"schema":1,"exact":1267650600228229401496703205377}';
const document=canvasDocument(workspace,scene),read=readDocument(document);
assert.equal(read.workspace,workspace);assert.deepEqual(read.scene,scene);
assert.equal(readDocument(workspace).workspace,workspace);
// A supported wide logical domain must remain saveable after Fit and shelf layout.
const wide={...scene,camera:{...camera,w:1e9*UNIT*2,h:1e9*UNIT},objects:[{...scene.objects[0],pose:[1e10,0,0]}]};
assert.deepEqual(readDocument(canvasDocument(workspace,wide)).scene,wide);
for(const invalid of [null,{...scene,version:3},{...scene,objects:[...scene.objects,...scene.objects]},{...scene,camera:{...camera,w:Infinity}},{...scene,objects:[{...scene.objects[0],axes:['i','i']}]}])assert.throws(()=>validateScene(invalid));
assert.throws(()=>readDocument(JSON.stringify({format:'kaleion-studio',version:2,workspace,scene})));
console.log('Scene geometry and document contracts passed.');
