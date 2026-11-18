// Timestamp: 2026-11-18 | Version: 2.5.1
// Author & Credits: https://www.alawise.es/1-s
// Filter public vocabulary locally; no visitor query leaves the page.
const dmn_bus=document.querySelector('[data-calo-search]');
if(dmn_bus){
  const dmn_txt=dmn_bus.querySelector('[data-calo-query]');
  const dmn_cat=dmn_bus.querySelector('[data-calo-category]');
  const dat_fil=[...document.querySelectorAll('[data-calo-entry]')];
  const norm_txt=txt=>txt.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  const act_bus=()=>{
    const txt_bus=norm_txt(dmn_txt.value.trim());let cnt_vis=0;
    for(const dmn_fil of dat_fil){
      const est_vis=(!dmn_cat.value||dmn_fil.dataset.category===dmn_cat.value)&&norm_txt(dmn_fil.textContent).includes(txt_bus);
      dmn_fil.hidden=!est_vis;cnt_vis+=Number(est_vis);
    }
    dmn_bus.querySelector('[data-calo-count]').textContent=cnt_vis+' / '+dat_fil.length+' voces';
    document.querySelector('[data-calo-empty]').hidden=cnt_vis>0;
  };
  dmn_txt.addEventListener('input',act_bus);dmn_cat.addEventListener('change',act_bus);
}
