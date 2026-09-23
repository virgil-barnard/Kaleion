// Single-pointer and keyboard alternatives; callbacks modify view state only.
export function cameraControls({name,fit,zoom,pan,fitId}){
  const box=document.createElement('div');box.className='camera-controls';box.setAttribute('role','group');box.setAttribute('aria-label',`${name} view controls`);
  function button(text,label,action){const b=document.createElement('button');b.type='button';b.textContent=text;b.setAttribute('aria-label',label);b.onclick=action;return b}
  const fitButton=button('Fit',`Fit ${name} view`,fit);if(fitId)fitButton.id=fitId;
  box.append(fitButton,button('−',`Zoom out ${name} view`,()=>zoom(1/1.4)),button('+',`Zoom in ${name} view`,()=>zoom(1.4)));
  const directions=document.createElement('details'),summary=document.createElement('summary'),row=document.createElement('div');summary.textContent='Pan';row.className='row';
  for(const [label,x,y] of [['left',-60,0],['right',60,0],['up',0,-60],['down',0,60]])row.append(button(label,`Pan ${name} view ${label}`,()=>pan(x,y)));
  directions.append(summary,row);box.append(directions);return box;
}
