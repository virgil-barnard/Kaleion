// Presentation policy only. Exact integers are normalized before conversion to
// a bounded floating color fraction; no mathematical field is modified.
export const palettes={
  ocean:{label:'Ocean',stops:['#153b66','#238b9b','#9cdbca','#f0f9dc']},
  violet:{label:'Violet',stops:['#351451','#7852a1','#c89acc','#fff0df']},
  ember:{label:'Ember',stops:['#481a46','#aa355c','#ed8152','#fff0b0']},
  balance:{label:'Blue · white · red',stops:['#245ca1','#d2e5ef','#faf6ed','#e5b4a0','#ae3548']},
};
export const colorDefaults=()=>({mode:'uniform',solid:'#e4b97e',field:'value',palette:'ocean',range:'auto',min:'0',max:'1',reverse:false});
const integer=v=>typeof v==='string'&&/^-?\d+$/.test(v);
export function validateColor(c){
  if(!c||typeof c!=='object'||Array.isArray(c)||Object.keys(c).sort().join(',')!==Object.keys(colorDefaults()).sort().join(',')||
     !['uniform','field'].includes(c.mode)||!/^#[0-9a-f]{6}$/i.test(c.solid)||
     typeof c.field!=='string'||!c.field||c.field.length>80||!Object.hasOwn(palettes,c.palette)||
     !['auto','fixed'].includes(c.range)||typeof c.reverse!=='boolean'||!integer(c.min)||!integer(c.max)||c.min.length>4301||c.max.length>4301||BigInt(c.min)>BigInt(c.max))
    throw Error('Choose a color, an integer field, and minimum ≤ maximum.');
  return c;
}
const rgb=hex=>[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16));
const hex=channels=>'#'+channels.map(v=>Math.round(v).toString(16).padStart(2,'0')).join('');
export function paletteColor(palette,t,reverse=false){
  const stops=palettes[palette].stops,p=(reverse?1-t:t)*(stops.length-1),i=Math.min(stops.length-2,Math.floor(p)),f=p-i;
  const a=rgb(stops[i]),b=rgb(stops[i+1]);return hex(a.map((v,k)=>v+(b[k]-v)*f));
}
export function markColors(fill){
  const channels=rgb(fill);
  // WCAG relative luminance selects the more legible black/white label. Color
  // itself never encodes selection or relation membership exclusively.
  const linear=channels.map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4});
  const luminance=linear[0]*.2126+linear[1]*.7152+linear[2]*.0722;
  return {fill,shade:hex(channels.map(v=>v*.82)),light:hex(channels.map(v=>v+(255-v)*.15)),text:luminance>.179?'#000000':'#ffffff'};
}
export function colorScale(obj,config=colorDefaults(),endpointLabels=[]){
  validateColor(config);
  const values=(obj.rows||[]).map(r=>r.fields[config.field]);
  if(config.field==='value')values.push(...endpointLabels.flat());
  const integers=values.filter(integer).map(BigInt);
  let low=null,high=null;
  if(config.range==='fixed'){low=BigInt(config.min);high=BigInt(config.max)}
  else for(const v of integers){if(low===null||v<low)low=v;if(high===null||v>high)high=v}
  const available=(obj.fields||[]).includes(config.field)||values.some(integer);
  const note=config.mode==='uniform'?'Uniform object color.':!available?`Field ${config.field} is unavailable; gray means no integer value.`:
    !integers.length?'No integer values to color.':`${config.field}: ${low} → ${high}${low===high?' · limit value uses midpoint color':''}. ${config.range==='auto'?'Full captured domain; slices do not rescale.':'Fixed range; values outside it use the end colors.'}`;
  function at(value){
    if(config.mode==='uniform')return config.solid;
    if(!integer(value)||low===null||!available)return '#8d9698';
    const v=BigInt(value),t=v<low?0:v>high?1:low===high?.5:Number((v-low)*1000000n/(high-low))/1000000;
    return paletteColor(config.palette,t,config.reverse);
  }
  return {at,note,min:low?.toString()??null,max:high?.toString()??null,available,hasValues:integers.length>0};
}
