// Timestamp: 2026-11-02
// Version: 2.1.1
// Author & Credits: https://www.alawise.es/1-s
import { crt_azr, rnd_ent } from './entropy-core.mjs?v=2.1.0';
import { crt_bar, crt_tir, cfg_tir, pos_crz, dat_run, dat_mon, crt_lin, crt_hex } from './chance-core.mjs?v=2.1.0';
import {crt_dad} from './dice-core.mjs?v=2.1.1';

for (const dmn_itm of document.querySelectorAll('[data-chance-app]')) {
  const clv_esc = dmn_itm.dataset.chanceApp;
  const btn_env = dmn_itm.querySelector('[data-draw]');
  const dmn_vis = dmn_itm.querySelector('[data-result]');
  const dat_hst = [];
  let dat_bar = [], dat_res = [], dat_lin = [], url_fot = null;
  const cfg_apl = {portrait:dat_mon.portrait,job:0};
  const act_lab = txt_val=>{dmn_itm.querySelector('[data-source-status]').textContent=txt_val;};
  const est_ich = ()=>dmn_itm.querySelector('[data-coin-mode]')?.value==='iching';

  function crt_mon(rnd_bit) {
    const dmn_det = document.createElement('figure'); dmn_det.className='coin-result';
    dmn_det.setAttribute('aria-label',rnd_bit ? 'Heads' : 'Maltese cross / tails');
    const dmn_itm = document.createElement('span'); dmn_itm.className='coin-face '+(rnd_bit ? 'is-heads' : 'is-tails');
    if (!rnd_bit || cfg_apl.portrait === dat_mon.portrait) dmn_itm.classList.add('is-relief');
    if (!rnd_bit || cfg_apl.portrait) {
      const dmn_vis = document.createElement('img'); dmn_vis.alt='';
      dmn_vis.src=rnd_bit ? cfg_apl.portrait : dat_mon.cross;
      dmn_vis.addEventListener('error',()=>{dmn_vis.remove();dmn_itm.textContent=rnd_bit ? 'H' : '✠';},{once:true});
      dmn_itm.append(dmn_vis);
    } else { dmn_itm.textContent='H'; dmn_itm.classList.add('portrait-pending'); }
    const dmn_nav = document.createElement('figcaption');
    dmn_nav.textContent=rnd_bit ? (cfg_apl.portrait ? 'Portrait · heads' : 'Heads · portrait pending') : 'Maltese cross · tails';
    dmn_det.append(dmn_itm,dmn_nav); return dmn_det;
  }

  function crt_crd(dat_itm, sys_idx) {
    const dmn_det = document.createElement('article'); dmn_det.className='playing-card'+(dat_itm.red ? ' red-card' : '');
    dmn_det.dataset.cardId=dat_itm.id; dmn_det.dataset.position=String(sys_idx+1);
    const dmn_itm = document.createElement('span'); dmn_itm.className='card-position';
    // Position is numbered in draw order, independently of the visual grid.
    dmn_itm.textContent=String(sys_idx+1);
    const dmn_nav = document.createElement('b'); dmn_nav.className='card-rank'; dmn_nav.textContent=dat_itm.rank;
    const dmn_vis = document.createElement(dat_itm.art ? 'a' : dat_itm.icon ? 'img' : 'span'); dmn_vis.className='card-pip';
    if (dat_itm.art) {
      dmn_det.classList.add('illustrated-card'); dmn_vis.className='tarot-art';
      dmn_vis.href=dat_itm.art+'?v=2.1.0'; dmn_vis.dataset.tarotOpen=''; dmn_vis.dataset.cardName=dat_itm.label;
      dmn_vis.setAttribute('aria-label','View larger image: '+dat_itm.label);
      const dmn_img=document.createElement('img'); dmn_img.src=dmn_vis.href;
      dmn_img.alt=dat_itm.label; dmn_img.width=300; dmn_img.height=450;
      dmn_img.loading='lazy'; dmn_img.decoding='async'; dmn_vis.append(dmn_img);
      if (!dat_itm.id.startsWith('m-') && !dat_itm.id.startsWith('marseille-')) {
        dmn_vis.classList.add('indexed-card',dat_itm.id.startsWith('a-')?'american-card':'spanish-card');
        for (const txt_pos of ['top','bottom']) {
          const dmn_idx=document.createElement('span');dmn_idx.className='card-index index-'+txt_pos;dmn_idx.setAttribute('aria-hidden','true');
          const dmn_ran=document.createElement('b');dmn_ran.textContent=dat_itm.rank;
          const dmn_pal=document.createElement(dat_itm.icon?'img':'span');
          if (dat_itm.icon) {dmn_pal.src='/assets/suit-'+dat_itm.icon+'.svg';dmn_pal.alt='';}
          else dmn_pal.textContent=dat_itm.symbol+'\uFE0E';
          dmn_idx.append(dmn_ran,dmn_pal);dmn_vis.append(dmn_idx);
        }
      }
    }
    else if (dat_itm.icon) { dmn_vis.src='/assets/suit-'+dat_itm.icon+'.svg'; dmn_vis.alt=''; }
    else { dmn_vis.textContent=dat_itm.symbol+'\uFE0E'; dmn_vis.setAttribute('aria-hidden','true'); }
    const txt_val = document.createElement('strong'); txt_val.className='card-name'; txt_val.textContent=dat_itm.label;
    const txt_note = document.createElement('small'); txt_note.textContent=dat_itm.deck;
    dmn_det.append(dmn_itm,dmn_nav,dmn_vis,txt_val,txt_note); return dmn_det;
  }

  function crt_run(dat_itm, sys_idx) {
    const dmn_det = document.createElement('article'); dmn_det.className='rune-tile'; dmn_det.dataset.runeId=dat_itm.id;
    const dmn_vis = document.createElement('span'); dmn_vis.className='rune-glyph'; dmn_vis.textContent=dat_itm.glyph;
    const dmn_nav = document.createElement('strong');
    const idi_run = dmn_itm.querySelector('[data-rune-label]').value;
    dmn_nav.textContent=idi_run==='fi' ? dat_itm.fi : idi_run==='latin' ? dat_itm.latin : dat_itm.name;
    if (idi_run==='fi') dmn_nav.lang='fi';
    const txt_note = document.createElement('small'); txt_note.textContent=(sys_idx+1)+' / '+dat_itm.name+' · '+dat_itm.latin;
    dmn_det.append(dmn_vis,dmn_nav,txt_note);return dmn_det;
  }

  function act_ich() {
    const dmn_nav = dmn_itm.querySelector('[data-iching-lines]');
    const dmn_det = dmn_itm.querySelector('[data-hexagrams]');
    dmn_nav.replaceChildren(); dmn_det.replaceChildren();
    for (const [sys_idx,dat_itm] of dat_lin.entries()) {
      const dmn_vis = document.createElement('li'); dmn_vis.className='iching-record';
      const txt_val = document.createElement('strong'); txt_val.textContent='Line '+(sys_idx+1)+' · '+dat_itm.value;
      const txt_note = document.createElement('span');
      txt_note.textContent=({6:'Changing yin',7:'Stable yang',8:'Stable yin',9:'Changing yang'})[dat_itm.value];
      const txt_art = document.createElement('div'); txt_art.className='line-coins';txt_art.append(...dat_itm.coins.map(crt_mon));
      const txt_ext = document.createElement('small');txt_ext.className='line-source';txt_ext.textContent=dat_itm.source;
      dmn_vis.append(txt_val,txt_art,txt_note,txt_ext);dmn_nav.append(dmn_vis);
    }
    if (dat_lin.length===6) {
      const dat_hex = crt_hex(dat_lin.map(dat_itm=>dat_itm.value));
      for (const [txt_val,dat_env,cnt_tot] of [['Primary',dat_hex.primary,dat_hex.number],['Relating',dat_hex.related,dat_hex.relatedNumber]]) {
        const dmn_vis = document.createElement('figure');dmn_vis.className='hexagram';
        const txt_note = document.createElement('figcaption');txt_note.textContent=txt_val+' · Hexagram '+cnt_tot+' '+String.fromCodePoint(0x4dc0+cnt_tot-1);
        const txt_art = document.createElement('div');txt_art.className='hexagram-lines';
        for (let sys_idx=5;sys_idx>=0;sys_idx--) {
          const dmn_det = document.createElement('div');dmn_det.className='hex-line '+(dat_env[sys_idx] ? 'yang' : 'yin');
          dmn_det.setAttribute('aria-label','Line '+(sys_idx+1)+': '+(dat_env[sys_idx] ? 'yang' : 'yin'));
          if (txt_val==='Primary' && dat_hex.changing.includes(sys_idx+1)) dmn_det.classList.add('changing');
          dmn_det.append(document.createElement('i'),document.createElement('i'));txt_art.append(dmn_det);
        }
        dmn_vis.append(txt_note,txt_art);dmn_det.append(dmn_vis);
      }
      const txt_note = document.createElement('p');txt_note.className='hex-change-note';
      txt_note.textContent=dat_hex.changing.length ? 'Changing lines (counted from the bottom): '+dat_hex.changing.join(', ') : 'No changing lines. The relating figure is identical.';
      dmn_det.append(txt_note);
    }
    btn_env.textContent=dat_lin.length===6 ? 'Hexagram complete · reset to begin' : 'Cast line '+(dat_lin.length+1)+' of 6 ↗';
    btn_env.disabled=dat_lin.length===6;
    dmn_itm.querySelector('[data-cast-all]').disabled=dat_lin.length>0;
  }

  function crt_res() {
    dmn_vis.replaceChildren();
    if (clv_esc==='cards') {
      const clv_dis=dmn_itm.querySelector('[data-layout]').value;
      const cnt_col=clv_dis==='cross' ? 3 : Number(dmn_itm.querySelector('[data-cols]').value);
      dmn_vis.className='chance-results card-spread '+(clv_dis==='cross' ? 'cross-spread' : 'matrix-spread');
      dmn_vis.style.setProperty('--spread-cols',String(cnt_col));
      for (const [sys_idx,dat_itm] of dat_res.entries()) {
        const dmn_det=crt_crd(dat_itm,sys_idx);
        if (clv_dis==='cross') {
          dmn_det.style.gridRow=String(pos_crz[sys_idx].row);dmn_det.style.gridColumn=String(pos_crz[sys_idx].col);
          dmn_det.querySelector('.card-position').textContent=(sys_idx+1)+' · '+pos_crz[sys_idx].label;
        }
        dmn_vis.append(dmn_det);
      }
    } else if (clv_esc==='dice') {dmn_vis.className='chance-results dice-table';dmn_vis.append(...dat_res.map(crt_dad));}
    else if (clv_esc==='runes') dmn_vis.append(...dat_res.map(crt_run));
    else if (clv_esc==='coins'||clv_esc==='yijing') { dmn_vis.append(...dat_res.map(crt_mon));act_ich(); }
    else for (const txt_val of dat_res) { const dmn_det=document.createElement('span');dmn_det.className='chance-token';dmn_det.textContent=String(txt_val);dmn_vis.append(dmn_det); }
    if (dmn_itm.querySelector('[data-portrait-note]')) dmn_itm.querySelector('[data-portrait-note]').textContent='The site portrait and Maltese cross are the defaults. Local photos stay in this tab and are not uploaded or saved.';
    if (dmn_itm.querySelector('[data-portrait-preview]')) {
      const dmn_det=dmn_itm.querySelector('[data-portrait-preview]');dmn_det.replaceChildren(crt_mon(1),crt_mon(0));
    }
  }

  function act_cnt() {
    dmn_itm.querySelector('[data-remaining]').textContent=clv_esc==='cards'||clv_esc==='runes'
      ? dat_bar.length+' remaining · no replacement' : est_ich() ? dat_lin.length+' of 6 lines · first cast is the bottom line' : 'Each toss is independent.';
    if (clv_esc==='cards') {
      const clv_dis=dmn_itm.querySelector('[data-layout]').value;
      for (const dmn_det of dmn_itm.querySelectorAll('[data-rows],[data-cols]')) dmn_det.disabled=clv_dis==='cross';
      dmn_itm.querySelector('[data-spanish-size]').hidden=dmn_itm.querySelector('[data-deck]').value!=='spanish';
    }
    if (clv_esc==='coins'||clv_esc==='yijing') {
      dmn_itm.querySelector('[data-iching]').hidden=!est_ich();
      dmn_itm.querySelector('[data-count]').disabled=est_ich();
      dmn_itm.querySelector('[data-cast-all]').hidden=!est_ich();
      if (!est_ich()) btn_env.textContent='Toss coins ↗';
      else act_ich();
    }
  }

  function act_azr() {
    cfg_apl.job++;
    for (const dmn_det of dmn_itm.querySelectorAll('input,select,button')) dmn_det.disabled=false;
    dat_bar=clv_esc==='cards' ? crt_bar(dmn_itm.querySelector('[data-deck]').value,Number(dmn_itm.querySelector('[data-spanish-size] select').value))
      : clv_esc==='runes' ? [...dat_run[dmn_itm.querySelector('[data-rune-set]').value]] : [];
    if (clv_esc==='runes') { const dmn_det=dmn_itm.querySelector('[data-count]');dmn_det.max=String(dat_bar.length);if(Number(dmn_det.value)>dat_bar.length)dmn_det.value=String(dat_bar.length); }
    dat_res=[];dat_lin=[];dat_hst.length=0;
    dmn_itm.querySelector('[data-history]').replaceChildren();
    btn_env.disabled=false;
    crt_res();act_cnt();act_lab('Ready. A new shared-source sample is requested for every action. Changing a deck, alphabet, layout or coin mode resets its session.');
  }

  async function act_fot(evt_ui) {
    const dat_itm=evt_ui.target.files[0];if(!dat_itm)return;
    if(!['image/jpeg','image/png','image/webp'].includes(dat_itm.type)||dat_itm.size>8*1024*1024){act_lab('Choose a JPEG, PNG or WebP no larger than 8 MB.');evt_ui.target.value='';return;}
    const sys_idx=++cfg_apl.job;
    const url_app=URL.createObjectURL(dat_itm);
    try {
      const dmn_det=new Image();dmn_det.src=url_app;await dmn_det.decode();
      if(dmn_det.naturalWidth*dmn_det.naturalHeight>25000000)throw new Error('Image too large');
      if(sys_idx!==cfg_apl.job){URL.revokeObjectURL(url_app);return;}
      if(url_fot)URL.revokeObjectURL(url_fot);url_fot=url_app;cfg_apl.portrait=url_fot;
      crt_res();act_lab('Portrait set for this page only. The photo is not uploaded or saved.');
    } catch { URL.revokeObjectURL(url_app);act_lab('The photo could not be opened. Use a JPEG, PNG or WebP up to 25 megapixels.'); }
    finally { evt_ui.target.value=''; }
  }
  function clr_fot() {
    cfg_apl.job++;
    if(url_fot)URL.revokeObjectURL(url_fot);url_fot=null;cfg_apl.portrait=dat_mon.portrait;crt_res();
  }
  dmn_itm.querySelector('[data-portrait-file]')?.addEventListener('change',act_fot);
  dmn_itm.querySelector('[data-clear-photo]')?.addEventListener('click',()=>{clr_fot();act_lab('Site portrait restored.');});

  async function act_tir(est_env=false) {
    let cnt_tot=Number(dmn_itm.querySelector('[data-count]')?.value||1);
    try {
      if(clv_esc==='cards')cnt_tot=cfg_tir(dmn_itm.querySelector('[data-layout]').value,Number(dmn_itm.querySelector('[data-rows]').value),Number(dmn_itm.querySelector('[data-cols]').value),dat_bar.length).count;
      else if(est_ich()) { if(dat_lin.length===6||est_env&&dat_lin.length)throw new Error('Reset the hexagram before beginning a new cast.');cnt_tot=3; }
      else if(!Number.isInteger(cnt_tot)||cnt_tot<1||cnt_tot>Number(dmn_itm.querySelector('[data-count]').max))throw new Error('Choose a whole number within the stated range.');
      if(clv_esc==='runes'&&cnt_tot>dat_bar.length)throw new Error('Not enough runes remain. Reset the set or choose fewer.');
    } catch(err_env){act_lab(err_env.message);return;}
    const sys_idx=++cfg_apl.job;
    for(const dmn_det of dmn_itm.querySelectorAll('input,select,button'))dmn_det.disabled=true;
    act_lab('Sampling…');
    try {
      const dat_azr=await crt_azr(dmn_itm.querySelector('[data-source]').value);
      if(sys_idx!==cfg_apl.job){dat_azr.seed.fill(0);return;}
      if(clv_esc==='cards'||clv_esc==='runes')dat_res=crt_tir(dat_bar,cnt_tot,dat_azr);
      else if(est_ich()) {
        for(let idx_act=0;idx_act<(est_env?6:1);idx_act++){const dat_itm=crt_lin(dat_azr);dat_itm.source=dat_azr.label;dat_lin.push(dat_itm);dat_res=dat_itm.coins;}
      } else {
        dat_res=Array.from({length:cnt_tot},()=>clv_esc==='dice' ? rnd_ent(dat_azr,6)+1 : clv_esc==='coins'||clv_esc==='yijing' ? rnd_ent(dat_azr,2) : rnd_ent(dat_azr,256).toString(16).padStart(2,'0'));
        if(clv_esc==='entropy')dat_res=[dat_res.join('')];
      }
      dat_azr.seed.fill(0);crt_res();
      const txt_val=est_ich() ? 'I Ching · bottom to top: '+dat_lin.map(dat_itm=>dat_itm.value).join(' / ')
        : dat_res.map(dat_itm=>clv_esc==='cards' ? dat_itm.label : clv_esc==='runes' ? dat_itm.glyph+' '+dat_itm.fi+' / '+dat_itm.name : clv_esc==='coins'||clv_esc==='yijing' ? dat_itm ? 'Heads' : 'Maltese cross' : dat_itm).join(' · ');
      dat_hst.unshift(clv_esc==='dice'?{time:new Date().toLocaleTimeString(),dice:[...dat_res],source:dat_azr.label}:new Date().toLocaleTimeString()+' — '+txt_val+' / '+dat_azr.label);dat_hst.splice(10);
      dmn_itm.querySelector('[data-history]').replaceChildren(...dat_hst.map(dat_itm=>{
        const dmn_det=document.createElement('li');
        if(typeof dat_itm==='string') dmn_det.textContent=dat_itm;
        else {
          dmn_det.className='dice-history';
          const dmn_tim=document.createElement('time');dmn_tim.textContent=dat_itm.time;
          const dmn_dad=document.createElement('span');dmn_dad.className='dice-mini';dmn_dad.append(...dat_itm.dice.map(crt_dad));
          const dmn_fnt=document.createElement('small');dmn_fnt.textContent=dat_itm.source;
          dmn_det.append(dmn_tim,dmn_dad,dmn_fnt);
        }
        return dmn_det;
      }));
      act_lab(dat_azr.label);
    }catch {act_lab('The draw could not be completed. Reset and try again in a current browser.');}
    finally {
      if(sys_idx===cfg_apl.job){for(const dmn_det of dmn_itm.querySelectorAll('input,select,button'))dmn_det.disabled=false;act_cnt();}
    }
  }
  btn_env.addEventListener('click',()=>act_tir());
  dmn_itm.querySelector('[data-cast-all]')?.addEventListener('click',()=>act_tir(true));
  dmn_itm.querySelector('[data-reset]').addEventListener('click',act_azr);
  for(const dmn_det of dmn_itm.querySelectorAll('[data-deck],[data-spanish-size] select,[data-layout],[data-rune-set],[data-coin-mode]'))dmn_det.addEventListener('change',act_azr);
  // Commit dimensions while editing. Disabling a focused field can trigger
  // change after a draw starts; that late event must not cancel the new draw.
  for(const dmn_det of dmn_itm.querySelectorAll('[data-rows],[data-cols]'))dmn_det.addEventListener('input',act_azr);
  dmn_itm.querySelector('[data-rune-label]')?.addEventListener('change',crt_res);
  window.addEventListener('pagehide',()=>{cfg_apl.job++;if(url_fot)URL.revokeObjectURL(url_fot);url_fot=null;cfg_apl.portrait=dat_mon.portrait;dat_res=[];dat_lin=[];dat_bar=[];dat_hst.length=0;});
  window.addEventListener('pageshow',evt_ui=>{if(evt_ui.persisted)act_azr();});
  const api_qry = new URLSearchParams(location.search);
  let txt_val = '';
  let est_drw = false;
  if (location.search.length > 1) {
    const api_ver = api_qry.get('api_ver') || '1';
    const api_act = api_qry.get('api_act') || 'configure';
    const vw_mod = api_qry.get('vw_mod');
    if (api_ver !== '1' || !['configure','draw'].includes(api_act) || (vw_mod && vw_mod !== clv_esc)) {
      txt_val = 'URL settings were ignored. Use API v1, a supported action and a module matching this page.';
    } else {
      const src_cam = api_qry.get('src_cam');
      if (['auto','cam1','cam2','cam3','cam4','browser'].includes(src_cam)) dmn_itm.querySelector('[data-source]').value = src_cam;
      if (clv_esc === 'cards') {
        const deck_typ = api_qry.get('deck_typ');
        if (['spanish','american','marseille'].includes(deck_typ)) dmn_itm.querySelector('[data-deck]').value = deck_typ;
        const deck_cnt = api_qry.get('deck_cnt');
        if (['40','48'].includes(deck_cnt) && dmn_itm.querySelector('[data-deck]').value === 'spanish') dmn_itm.querySelector('[data-spanish-size] select').value = deck_cnt;
        const lay_mod = api_qry.get('lay_mod');
        if (['matrix','cross'].includes(lay_mod)) dmn_itm.querySelector('[data-layout]').value = lay_mod;
        const cnt_itm = Number(api_qry.get('cnt_itm'));
        const cnt_lin = Number(api_qry.get('cnt_lin'));
        const cnt_col = Number(api_qry.get('cnt_col'));
        const cnt_max = deck_typ === 'american' ? 52 : deck_typ === 'marseille' ? 78 : Number(dmn_itm.querySelector('[data-spanish-size] select').value);
        if (dmn_itm.querySelector('[data-layout]').value === 'matrix') {
          const cnt_rows = api_qry.has('cnt_lin') ? cnt_lin : api_qry.has('cnt_itm') && !api_qry.has('cnt_col') ? 1 : 0;
          const cnt_cols = api_qry.has('cnt_col') ? cnt_col : api_qry.has('cnt_itm') && !api_qry.has('cnt_lin') ? cnt_itm : 0;
          if ([cnt_rows,cnt_cols].every(cnt_tot => Number.isInteger(cnt_tot) && cnt_tot >= 1 && cnt_tot <= 78) && cnt_rows * cnt_cols <= cnt_max) {
            dmn_itm.querySelector('[data-rows]').value = String(cnt_rows);
            dmn_itm.querySelector('[data-cols]').value = String(cnt_cols);
          }
        }
      }
      if (clv_esc === 'runes') {
        const rune_set = api_qry.get('rune_set');
        if (['16','24'].includes(rune_set)) dmn_itm.querySelector('[data-rune-set]').value = rune_set;
        const label_fmt = api_qry.get('label_fmt');
        if (['fi','name','latin'].includes(label_fmt)) dmn_itm.querySelector('[data-rune-label]').value = label_fmt;
      }
      if (clv_esc === 'coins' || clv_esc === 'yijing') {
        const coin_mod = api_qry.get('coin_mod');
        if (['free','iching'].includes(coin_mod)) dmn_itm.querySelector('[data-coin-mode]').value = coin_mod;
      }
      const dmn_cnt = dmn_itm.querySelector('[data-count]');
      const cnt_itm = Number(api_qry.get('cnt_itm'));
      if (dmn_cnt && api_qry.has('cnt_itm') && !est_ich() && Number.isInteger(cnt_itm) && cnt_itm >= 1 && cnt_itm <= Number(dmn_cnt.max)) dmn_cnt.value = String(cnt_itm);
      est_drw = api_act === 'draw';
      txt_val = 'GET settings are prefilled. Review them and press the draw button when you are ready; no result was generated.';
    }
  }
  act_azr();
  if (txt_val) act_lab(txt_val);
  if (est_drw) queueMicrotask(() => act_tir(est_ich()));
}
