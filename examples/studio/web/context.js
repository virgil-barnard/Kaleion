// One owner per intent: background creates; an object exposes its details and
// a short tool shelf; specialist operations live in one secondary disclosure.
export const creationActions=['vector','grid','cube'];
export function advancedActions(object){
  if(object?.status!=='ready')return [];
  return object.kind==='incidence'
    ? ['select','measure','group_options','coverage']
    : ['values','field','measure','group_options','coverage','compare'];
}
export const labels={
  vector:'Vector',grid:'Grid',cube:'Cube',shape:'Create a shape',
  integers:'Type values',sequence:'Arithmetic sequence',field:'Add a named field',values:'Set values from a formula',
  lens:'Make a relation',measure:'Measure with keys and order',place:'Arrange / move',
  reuse_lens:'Reuse this rule',total:'Sum or count',product:'Make every pair',select:'Keep matches',
  explain:'Explain this item',fit:'Fit view',group_options:'Browse groups',group_lens:'Make a group relation',
  coverage:'Check coverage',assignment:'Use unique matches',compare:'Compare exact fields',
};
