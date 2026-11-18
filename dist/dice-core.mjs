// Timestamp: 2026-11-02
// Version: 2.1.1
// Author & Credits: https://www.alawise.es/1-s
// Inline vector faces keep their exact pip counts and work without image requests.
export const dat_dad = [
  null,
  {label:'One pip',pips:[[120,114]]},
  {label:'Two pips',pips:[[70,64],[170,164]]},
  {label:'Three pips',pips:[[70,64],[120,114],[170,164]]},
  {label:'Four pips',pips:[[70,64],[170,64],[70,164],[170,164]]},
  {label:'Five pips',pips:[[70,64],[170,64],[120,114],[70,164],[170,164]]},
  {label:'Six pips',pips:[[70,64],[170,64],[70,114],[170,114],[70,164],[170,164]]}
];
let idx_dad=0;

export function svg_dad(cnt_val) {
  if (!Number.isInteger(cnt_val) || cnt_val<1 || cnt_val>6) throw new RangeError('A die face must contain one to six pips');
  const dat_itm=dat_dad[cnt_val];
  return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 246" role="img" aria-label="'+dat_itm.label+'" data-pip-count="'+cnt_val+'">'+
    '<defs><linearGradient id="ivory" x1="0" y1="0" x2=".8" y2="1"><stop stop-color="#fffef1"/><stop offset=".42" stop-color="#f0e6ce"/><stop offset="1" stop-color="#c5b38e"/></linearGradient>'+
    '<linearGradient id="bevel" x1="0" y1="0" x2=".3" y2="1"><stop stop-color="#c4aa73"/><stop offset=".45" stop-color="#827054"/><stop offset=".76" stop-color="#c5ab77"/><stop offset="1" stop-color="#62503d"/></linearGradient>'+
    '<radialGradient id="pip" cx=".35" cy=".25" r=".9"><stop stop-color="#423557"/><stop offset=".55" stop-color="#211b32"/><stop offset="1" stop-color="#0d0c16"/></radialGradient>'+
    '<linearGradient id="rim" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#77694f"/><stop offset=".4" stop-color="#b8a378"/><stop offset="1" stop-color="#fff7df"/></linearGradient></defs>'+
    '<rect x="24" y="26" width="203" height="207" rx="32" fill="url(#bevel)"/>'+
    '<path d="M219 59V188Q219 219 187 223H65Q38 223 27 204Q44 215 69 215H182Q213 215 213 184V56Z" fill="#4d3d33" opacity=".5"/>'+
    '<rect x="14" y="9" width="205" height="210" rx="33" fill="url(#ivory)" stroke="#dfc997" stroke-width="1.1"/>'+
    '<rect x="20" y="15" width="193" height="198" rx="28" fill="none" stroke="#fffcec" stroke-width="1.5" opacity=".8"/>'+
    '<rect x="25" y="20" width="183" height="188" rx="24" fill="none" stroke="#b59b68" stroke-width=".55" opacity=".62"/>'+
    '<path d="M44 22H184Q207 22 207 46M29 45V172" stroke="#fffef5" stroke-width="2" fill="none" opacity=".68"/>'+
    dat_itm.pips.map(([cnt_x,cnt_y])=>'<circle cx="'+cnt_x+'" cy="'+(cnt_y+1)+'" r="16.4" fill="url(#rim)"/><circle data-pip="1" cx="'+cnt_x+'" cy="'+cnt_y+'" r="13.7" fill="url(#pip)"/><path d="M'+(cnt_x-9)+' '+(cnt_y+11)+'Q'+cnt_x+' '+(cnt_y+17)+' '+(cnt_x+10)+' '+(cnt_y+10)+'" stroke="#fff4d1" stroke-width="1.1" fill="none" opacity=".65"/>').join('')+
    '</svg>';
}

export function crt_dad(cnt_val, sys_idx=0) {
  const dmn_itm=document.createElement('figure');
  dmn_itm.className='pip-die';
  dmn_itm.dataset.face=String(cnt_val);
  dmn_itm.setAttribute('aria-label','Die · '+dat_dad[cnt_val]?.label);
  dmn_itm.style.setProperty('--die-tilt',[-5,4,-2,6,1,-4][sys_idx%6]+'deg');
  // The markup is generated solely from the fixed, validated six-face catalogue.
  const txt_id='die-'+(++idx_dad);
  dmn_itm.innerHTML=svg_dad(cnt_val).replaceAll('id="','id="'+txt_id+'-').replaceAll('url(#','url(#'+txt_id+'-');
  dmn_itm.firstElementChild.setAttribute('aria-hidden','true');
  return dmn_itm;
}
