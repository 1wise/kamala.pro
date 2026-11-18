/* Timestamp: 2026-10-28 | Version: 1.5.0 | Author and Credits: https://www.alawise.es/1-s */
'use strict';

// Fit the original fixed-width app without changing its canvas or calculations.
for (const dmn_itm of document.querySelectorAll('.planetary-media')) {
  const dmn_vis = dmn_itm.querySelector('iframe');
  const ob_tam = new ResizeObserver((dat_itm) => {
    const fac_esc = Math.min(1, dat_itm[0].contentRect.width / 380);
    dmn_vis.style.width = '380px';
    dmn_vis.style.height = '750px';
    dmn_vis.style.transform = `scale(${fac_esc})`;
    dmn_vis.style.left = `${(dat_itm[0].contentRect.width - 380 * fac_esc) / 2}px`;
    dmn_itm.style.height = `${750 * fac_esc}px`;
  });
  ob_tam.observe(dmn_itm);
}
