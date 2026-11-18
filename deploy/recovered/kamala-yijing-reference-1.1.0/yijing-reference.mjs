// Timestamp: 2026-11-07
// Version: 1.1.0
// Author & Credits: https://www.alawise.es/1-s
import { obt_gua } from './yijing-readings.mjs?v=1.1.0';

function crt_txt(txt_tag, txt_cls, txt_val) {
  const dmn_itm = document.createElement(txt_tag);
  if (txt_cls) dmn_itm.className = txt_cls;
  dmn_itm.textContent = txt_val;
  return dmn_itm;
}

function obt_num(dmn_fig) {
  const txt_cap = dmn_fig.querySelector('figcaption')?.textContent || '';
  // The existing renderer encodes King Wen order in the Unicode hexagram glyph.
  // Reading that glyph avoids tying the notes to the caption's English wording.
  for (const txt_chr of txt_cap) {
    const cnt_uni = txt_chr.codePointAt(0);
    if (cnt_uni >= 0x4dc0 && cnt_uni <= 0x4dff) return cnt_uni - 0x4dc0 + 1;
  }
  return null;
}

function crt_nota(dat_gua, txt_rol) {
  const dmn_tar = document.createElement('article');
  dmn_tar.className = 'yijing-reading';
  const dmn_tit = crt_txt('h4', 'yijing-reading-title',
    txt_rol + ' · ' + dat_gua.number + ' ');
  const dmn_nom = crt_txt('span', '', dat_gua.name_zh);
  dmn_nom.lang = 'lzh-Hant';
  dmn_tit.append(dmn_nom);
  const dmn_lab = crt_txt('p', 'yijing-reading-label', 'Classical Chinese · 卦辭');
  const dmn_ori = crt_txt('blockquote', 'yijing-original', dat_gua.original);
  dmn_ori.lang = 'lzh-Hant';
  const dmn_eng = crt_txt('p', 'yijing-reading-label', 'Brief English rendering · Kamala');
  const dmn_not = crt_txt('p', 'yijing-brief', dat_gua.note_en);
  const dmn_src = crt_txt('a', 'text-link', 'Chinese text · Wikisource ↗');
  dmn_src.href = dat_gua.source_zh;
  dmn_src.target = '_blank';
  dmn_src.rel = 'noopener noreferrer';
  dmn_tar.append(dmn_tit, dmn_lab, dmn_ori, dmn_eng, dmn_not, dmn_src);
  return dmn_tar;
}

for (const dmn_sec of document.querySelectorAll('[data-iching]')) {
  const dmn_ref = dmn_sec.querySelector('[data-iching-reference]');
  const dmn_lin = dmn_sec.querySelector('[data-iching-lines]');
  const dmn_hex = dmn_sec.querySelector('[data-hexagrams]');
  if (!dmn_ref) continue;
  dmn_ref.hidden = true;
  if (!dmn_lin || !dmn_hex) continue;

  const dmn_not = document.createElement('section');
  dmn_not.className = 'yijing-notes';
  dmn_not.dataset.yijingNotes = '';
  dmn_not.hidden = true;
  dmn_not.setAttribute('aria-label', 'Book of Changes · completed cast');
  dmn_not.setAttribute('aria-live', 'polite');
  const dmn_tit = crt_txt('h3', 'yijing-notes-title', 'Zhouyi 周易 · Book of Changes');
  const dmn_exp = crt_txt('p', 'yijing-notes-intro',
    'Hexagram statements (卦辭) from the received classical text. The brief English renderings are Kamala editorial notes.');
  const dmn_dat = document.createElement('div');
  dmn_dat.className = 'yijing-readings';
  const dmn_atr = crt_txt('p', 'yijing-notes-source',
    'Chinese text: Wikisource contributors. Brief renderings: Kamala. ');
  const dmn_lic = crt_txt('a', '', 'CC BY-SA 4.0 ↗');
  dmn_lic.href = 'https://creativecommons.org/licenses/by-sa/4.0/';
  dmn_lic.target = '_blank';
  dmn_lic.rel = 'noopener noreferrer';
  dmn_atr.append(dmn_lic);
  dmn_not.append(dmn_tit, dmn_exp, dmn_dat, dmn_atr, dmn_ref);
  dmn_hex.after(dmn_not);
  let clv_act = '';

  const act_ref = () => {
    const cnt_lin = [...dmn_lin.children].filter(dmn_itm => dmn_itm.matches('li.iching-record')).length;
    const dat_fig = [...dmn_hex.querySelectorAll('figure.hexagram')];
    const dat_num = dat_fig.map(obt_num);
    const est_fin = !dmn_sec.hidden && cnt_lin === 6 && dat_num.length === 2
      && dat_num.every(cnt_hex => obt_gua(cnt_hex));
    dmn_not.hidden = !est_fin;
    dmn_ref.hidden = !est_fin;
    if (!est_fin) {
      if (clv_act) dmn_dat.replaceChildren();
      clv_act = '';
      return;
    }
    const clv_nva = dat_num.join(':');
    if (clv_nva === clv_act) return;
    if (dat_num[0] === dat_num[1]) {
      dmn_dat.replaceChildren(crt_nota(obt_gua(dat_num[0]), 'Primary and relating'));
    } else {
      dmn_dat.replaceChildren(crt_nota(obt_gua(dat_num[0]), 'Primary'),
        crt_nota(obt_gua(dat_num[1]), 'Relating'));
    }
    clv_act = clv_nva;
  };
  // Keep the observer away from the notes it renders, avoiding mutation loops.
  const sys_obs = new MutationObserver(act_ref);
  sys_obs.observe(dmn_lin, { childList: true });
  sys_obs.observe(dmn_hex, { childList: true });
  sys_obs.observe(dmn_sec, { attributes: true, attributeFilter: ['hidden'] });
  act_ref();
}
