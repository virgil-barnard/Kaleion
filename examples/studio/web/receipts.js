// Receipt navigation owns the meaning of reads and contributions. The paired
// renderer receives scoped links and opaque selection context, never formulas to run.
const el=(tag,text,attrs={})=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);return n};
const measurementName=reducer=>reducer==='prefix_sum'?'prefix sum':reducer;
export function receiptInspector({panel,run,query,linked,beforeShow}){
  function show(receipt,{heading='Value',back=null,contribution=null}={}){
    beforeShow();
    panel.replaceChildren(el('span','CAPTURED EVIDENCE',{class:'eyebrow'}),el('h2',receipt.item.value===null?'Tuple · no value':`${heading} ${receipt.item.value}`));
    if(back){const button=el('button',back.label,{type:'button',id:'receipt-back'});button.onclick=()=>run(back.restore);panel.append(button);button.focus({preventScroll:true})}
    panel.append(el('pre',JSON.stringify(receipt.item.fields,null,2)));
    function returnHere(label){
      const view=linked.remember();
      return {label,restore:async()=>{
        if(view)await linked.open(view.spec,view);else linked.close();
        show(receipt,{heading,back,contribution});
      }};
    }
    function readButton(read,{weight=false}={}){
      const button=el('button',`${weight?'Follow weight read':'Follow keyed read'} · ${read.value}`,{type:'button'});
      button.onclick=()=>run(async()=>{
        const previous=returnHere(weight?'Back to contribution':'Back to read origin');
        const driver=await query('inspect-driver',{ref:read.driver});
        const spec={title:weight?'A contribution and its weight source':'An item and its keyed driver',
          detail:`Key ${read.key.join(', ')} · read ${read.read} = ${read.value}. ${weight?'This read participates in the weight expression; the full weight may combine several reads.':'This is the captured read, including an earlier input version when needed.'}`,
          left:{capture:receipt.item.ref[0],label:weight?'Contributor':'Driven item'},right:{capture:read.driver[0],label:weight?'Weight source':'Driver'},
          links:[{label:`Key ${read.key.join(', ')}`,left:[{ref:receipt.item.ref,note:weight?`Weight ${contribution.item.weight}`:'Inspected output'}],right:[{ref:read.driver,note:`Read ${read.value}`}]}],
          inspect:ref=>run(async()=>show(await query('inspect-driver',{ref}),{back:previous}))};
        await linked.open(spec);show(driver,{heading:weight?'Weight source value':'Driver value',back:previous});
      });
      const group=el('div',undefined,{class:'receipt-read','data-read-site':read.site});
      group.append(el('p',`Read at ${read.site} · ${read.read}`,{class:'help'}),button);
      return group;
    }
    if(contribution){
      const {item,measurement}=contribution;
      const section=el('section',undefined,{id:'contribution-evidence'});
      section.append(el('h2',`Contribution to ${measurementName(measurement.reducer)}`),
        el('p',`${item.item.value===null?'Tuple without a value':`Source value ${item.item.value}`} · weight ${item.weight}`),
        el('p',`Measured result ${measurement.item.value} · retained key (${measurement.key.join(', ')})`),
        el('p',measurement.formula,{class:'help'}));
      for(const read of item.reads)section.append(readButton(read,{weight:true}));
      if(!item.reads.length)section.append(el('p','No keyed reads in this contribution weight. Its exact weight remains part of the captured receipt.',{class:'help'}));
      panel.append(section);
    }
    const m=receipt.measurement;
    if(m.unavailable)panel.append(el('p','No active measurement receipt at this item.',{class:'quiet'}));
    else{
      panel.append(el('h2',`${measurementName(m.reducer)} · ${m.contributor_count} contributors`),el('p',m.formula));
      const together=el('button','View measurement and contributors',{type:'button',id:'view-contributors'});
      together.onclick=()=>run(async()=>{
        const evidence=await query('contributors',{ref:receipt.item.ref}),full=evidence.measurement;
        await linked.open({title:'A measurement and its contributors',
          detail:`${measurementName(full.reducer)} · ${full.contributor_count} contributors in a candidate population of ${full.population}. Weights and values are distinct. Faint points are context only.`,
          left:{capture:receipt.item.ref[0],label:'Measurement'},right:{capture:evidence.universe,label:'Contributors'},
          links:[{label:`Key ${full.key.join(', ')} · value ${receipt.item.value}`,
            left:[{ref:receipt.item.ref,note:`${full.contributor_count} contributors`}],
            right:full.contributors.map(c=>({ref:c.item.ref,note:`weight ${c.weight}`,contribution:c})),
            emptyRight:'Zero contributors. The captured source remains visible; its faint points did not contribute.'}],
          inspect:(ref,trigger,selected)=>run(async()=>{
            const previous=returnHere('Back to measurement');
            show(await query('inspect-driver',{ref}),{back:previous,
              contribution:selected.contribution?{item:selected.contribution,measurement:full}:null});
          })});
      });panel.append(together);
      for(const c of m.contributors)panel.append(el('p',`${c.item.value===null?'Tuple':`Value ${c.item.value}`} · weight ${c.weight}`,{class:'receipt-item'}));
      if(m.truncated)panel.append(el('p','Showing the first 32 contributors. Open the paired view for complete evidence within the studio budget.'));
    }
    if(Array.isArray(receipt.bindings))for(const b of receipt.bindings)panel.append(readButton(b));
    const details=el('details');details.append(el('summary','Scoped references and receipt'),el('pre',JSON.stringify(contribution?{...receipt,contribution}:receipt,null,2)));panel.append(details);
  }
  return {show};
}
