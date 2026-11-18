// Timestamp: 2026-11-01
// Version: 2.1.0
// Author & Credits: https://www.alawise.es/1-s
// Native image links remain usable when dialog support or JavaScript is absent.
(() => {
const dmn_dlg = document.createElement('dialog');
dmn_dlg.className = 'tarot-dialog';
dmn_dlg.setAttribute('aria-labelledby', 'tarot-dialog-title');
const btn_cer = document.createElement('button');
btn_cer.type = 'button'; btn_cer.className = 'tarot-dialog-close';
btn_cer.textContent = 'Close ×'; btn_cer.autofocus = true;
const dmn_tit = document.createElement('h2'); dmn_tit.id = 'tarot-dialog-title';
const dmn_img = document.createElement('img');
dmn_dlg.append(btn_cer, dmn_tit, dmn_img); document.body.append(dmn_dlg);
btn_cer.addEventListener('click', () => dmn_dlg.close());
dmn_dlg.addEventListener('click', evt_ui => { if (evt_ui.target === dmn_dlg) dmn_dlg.close(); });
document.addEventListener('click', evt_ui => {
  const dmn_lnk = evt_ui.target.closest('a[data-tarot-open]');
  if (!dmn_lnk || evt_ui.button !== 0 || evt_ui.ctrlKey || evt_ui.metaKey || evt_ui.shiftKey || evt_ui.altKey || typeof dmn_dlg.showModal !== 'function') return;
  const url_img = new URL(dmn_lnk.href);
  if (url_img.origin !== location.origin || !['/assets/tarot/','/assets/playing-cards/'].some(pth_src=>url_img.pathname.startsWith(pth_src))) return;
  evt_ui.preventDefault();
  dmn_tit.textContent = dmn_lnk.dataset.cardName;
  dmn_img.alt = dmn_lnk.dataset.cardName;
  dmn_img.src = url_img.href;
  dmn_dlg.showModal();
});
})();
