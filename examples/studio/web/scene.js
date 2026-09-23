// Geometry for a shared orthographic scene. No expressions or mathematical edits.
export const UNIT=28;
export const refKey=ref=>JSON.stringify(ref);
export const planes={xy:[0,0],xz:[0,-Math.PI/2],yz:[-Math.PI/2,-Math.PI/2],space:[.65,.8]};
export function projection(yaw,pitch){
  const c=Math.cos(yaw),s=Math.sin(yaw),p=Math.cos(pitch),q=Math.sin(pitch);
  const right=[c,-s,0],up=[p*s,p*c,-q],front=[q*s,q*c,p];
  const dot=(a,b)=>a.reduce((v,x,i)=>v+x*b[i],0);
  return {
    point:v=>[UNIT*dot(v,right),-UNIT*dot(v,up),dot(v,front)],
    shift:(x,y)=>right.map((v,i)=>(v*x-up[i]*y)/UNIT),front,
  };
}
export function chartDefaults(obj){
  return {marks:'cells',chart:obj.placed?'placement':'logical',axes:(obj.axes?.length?obj.axes:['index']).slice(0,3),slice:null};
}
export function geometry(obj,settings){
  const axes=settings.chart==='placement'?['x','y','z'].slice(0,obj.dimension||0):settings.axes;
  const rows=obj.rows||[],coords=rows.map(row=>settings.chart==='placement'?row.position:axes.map(a=>Number(row.fields[a])));
  let valid=obj.status==='ready'&&axes.length>0&&coords.every(p=>Array.isArray(p)&&p.every(v=>Number.isFinite(v)&&Math.abs(v)<=1e9));
  let positions=valid?coords.map(p=>[p[0]||0,p[1]||0,p[2]||0]):[];
  let low=[0,0,0],high=[0,0,0];
  if(positions.length)for(let i=0;i<3;i++){low[i]=Math.min(...positions.map(p=>p[i]));high[i]=Math.max(...positions.map(p=>p[i]));}
  // Fitting includes the declared logical domain, even when it has zero items.
  if(settings.chart==='logical'&&obj.shape)axes.forEach((a,i)=>{
    const index=obj.axes.indexOf(a),length=Number(obj.shape[index]);
    if(index>=0){
      if(!Number.isFinite(length)||length>1e9)valid=false;
      else{low[i]=Math.min(0,low[i]);high[i]=Math.max(high[i],length-1,0)}
    }
  });
  if(!valid){positions=[];low=[0,0,0];high=[0,0,0]}
  const values=settings.slice&&axes.includes(settings.slice.axis)?[...new Set(positions.map(p=>p[axes.indexOf(settings.slice.axis)]))].sort((a,b)=>a-b):[];
  const visible=p=>!settings.slice||!axes.includes(settings.slice.axis)||p[axes.indexOf(settings.slice.axis)]===settings.slice.value;
  return {axes,positions,low,high,valid,values,visible,dimension:axes.length};
}
export function corners(low,high,pad=.5){
  return Array.from({length:8},(_,n)=>low.map((v,i)=>(n&(1<<i)?high[i]+pad:v-pad)));
}
export function projectedBounds(points){
  return {left:Math.min(...points.map(p=>p[0])),right:Math.max(...points.map(p=>p[0])),top:Math.min(...points.map(p=>p[1])),bottom:Math.max(...points.map(p=>p[1]))};
}
export function cellFaces(position,dimension,project){
  if(dimension<3){
    const [x,y,z]=position;
    return [[[-.46,-.46],[.46,-.46],[.46,.46],[-.46,.46]].map(([a,b])=>project.point([x+a,y+b,z]))];
  }
  const vertices=corners(position,position,.46),faces=[];
  for(let axis=0;axis<3;axis++){
    const side=project.front[axis]>=0?1:0,others=[0,1,2].filter(i=>i!==axis);
    const indices=[[0,0],[1,0],[1,1],[0,1]].map(bits=>(side<<axis)|(bits[0]<<others[0])|(bits[1]<<others[1]));
    faces.push(indices.map(i=>project.point(vertices[i])));
  }
  return faces;
}
