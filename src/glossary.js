// Timestamp: 2026-10-30
// Version: 2.0.0
// Author and Credits: https://www.alawise.es/1-s
const dmn_itm = document.querySelector('[data-glossary]');
if (dmn_itm) {
  const fmt_lex = txt_val => txt_val.normalize('NFD').replace(/\p{Diacritic}/gu,'').toLowerCase();
  const dat_lex = [...dmn_itm.querySelectorAll('[data-lexicon-entry]')];
  const act_lex = () => {
    const qry_flt = fmt_lex(dmn_itm.querySelector('[data-lexicon-search]').value.trim());
    const clv_esc = dmn_itm.querySelector('[data-lexicon-scale]').value;
    let cnt_tot = 0;
    for (const dmn_det of dat_lex) {
      dmn_det.hidden = Boolean(clv_esc && dmn_det.dataset.scale !== clv_esc) || !fmt_lex(dmn_det.textContent).includes(qry_flt);
      if (!dmn_det.hidden) cnt_tot++;
    }
    for (const dmn_det of dmn_itm.querySelectorAll('.lexicon-letter')) dmn_det.hidden = !dmn_det.querySelector('[data-lexicon-entry]:not([hidden])');
    dmn_itm.querySelector('[data-lexicon-count]').textContent = cnt_tot+' of '+dat_lex.length+' lexical entries';
    dmn_itm.querySelector('[data-lexicon-empty]').hidden = cnt_tot > 0;
  };
  dmn_itm.querySelector('[data-lexicon-search]').addEventListener('input',act_lex);
  dmn_itm.querySelector('[data-lexicon-scale]').addEventListener('change',act_lex);
}
