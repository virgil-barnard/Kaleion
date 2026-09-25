// A portable question tied to three captures. It carries no trusted verdict:
// reopening asks the existing exact comparator to check those captures again.
const fields=['name','left_by','left_value','right','right_by','right_value','expected','expected_by'];
const record=v=>v!==null&&typeof v==='object'&&!Array.isArray(v);
const exactKeys=(v,ks)=>record(v)&&Object.keys(v).sort().join(',')===[...ks].sort().join(',');
const text=v=>typeof v==='string'&&v.length>0&&v.length<=80;
const keys=v=>Array.isArray(v)&&v.length>0&&v.length<=16&&v.every(text)&&new Set(v).size===v.length;
export function validateComparison(c){
  if(!exactKeys(c,['version','kind','title','spec','captures'])||c.version!==1||c.kind!=='keyed-integer-equality'||
     typeof c.title!=='string'||c.title.length>160||!exactKeys(c.spec,fields)||
     !['name','left_value','right','right_value','expected'].every(k=>text(c.spec[k]))||
     !['left_by','right_by','expected_by'].every(k=>keys(c.spec[k]))||c.spec.left_by.length!==c.spec.right_by.length||c.spec.left_by.length!==c.spec.expected_by.length||
     !exactKeys(c.captures,['left','right','expected'])||!Object.values(c.captures).every(v=>typeof v==='string'&&v.length>0&&v.length<=200))
    throw Error('Unsupported finite comparison declaration.');
  return c;
}
export function comparisonRecord(report,title=''){
  return validateComparison({version:1,kind:'keyed-integer-equality',title,
    spec:Object.fromEntries(fields.map(k=>[k,Array.isArray(report[k])?[...report[k]]:report[k]])),
    captures:{left:report.left_capture,right:report.right_capture,expected:report.expected_capture}});
}
export function requireComparisonCaptures(declaration,objects){
  validateComparison(declaration);
  for(const [side,name] of [['left',declaration.spec.name],['right',declaration.spec.right],['expected',declaration.spec.expected]])
    if(!objects.some(o=>o.name===name&&o.capture===declaration.captures[side]&&o.status==='ready'))
      throw Error(`Saved ${side} capture does not match this workspace. No equality verdict is available.`);
}
export function finiteStatement(report){
  return `dom(L) = dom(R) = D\n∀ k ∈ D, L(k) = R(k)\n\nL: ${JSON.stringify(report.name)}.${report.left_value} by (${report.left_by.join(', ')})\nR: ${JSON.stringify(report.right)}.${report.right_value} by (${report.right_by.join(', ')})\nD: keys of ${JSON.stringify(report.expected)} by (${report.expected_by.join(', ')})`;
}
