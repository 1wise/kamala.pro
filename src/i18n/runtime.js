// Timestamp: 2026-11-18 | Version: 2.5.0
// Author & Credits: https://www.alawise.es/1-s
// Localize newly rendered UI text while leaving app data and protocols intact.
(async()=>{
  const loc_act=document.body.dataset.siteLocale;
  if(!['es','calo'].includes(loc_act))return;
  const ver_loc=new URL(document.currentScript?.src??location.href).searchParams.get('v')??'';
  const url_ver='?v='+encodeURIComponent(ver_loc);
  let dat_loc;
  try{
    const res=await fetch('/i18n/es.json'+url_ver);if(!res.ok)return;dat_loc=await res.json();
    if(loc_act==='calo'){const extra=await fetch('/i18n/calo.json'+url_ver);if(extra.ok)Object.assign(dat_loc,await extra.json());}
  }catch{return;}
  const norm_txt=txt=>txt.replace(/\s+/g,' ').trim();
  const txt_loc=txt=>{
    const key=norm_txt(txt),val=dat_loc[key];
    if(typeof val!=='string'){
      if(key.startsWith('Download ZIP ·'))return txt.replace('Download ZIP','Descargar ZIP');
      const prefixes=['Source bell alarm:','Last source alarm:','Source alarm:','Source:','State:','Mode:'];
      for(const prefix of prefixes)if(key.startsWith(prefix)&&dat_loc[prefix])return dat_loc[prefix]+' '+txt_loc(key.slice(prefix.length).trim());
      if(key.includes(' · ')){
        const next=key.split(' · ').map(part=>txt_loc(part)).join(' · ');
        if(next!==key)return next;
      }
      if(/^Event \d+/.test(key))return key.replace(/^Event /,'Evento ');
      const graph=key.match(/^(Displacement|Windchime dissociation|Z depth change|Axis displacement|Axis velocity) (in ([a-z/]+)|\(unitless\)) over the last (\d+) seconds\.$/);
      if(graph){const name=dat_loc[graph[1]]??graph[1];return name+' '+(graph[3]?'en '+graph[3]:'sin unidades')+' durante los últimos '+graph[4]+' segundos.';}
      return txt;
    }
    if(val===key)return txt;
    return txt.replace(/\S(?:[\s\S]*\S)?/,()=>val);
  };
  const is_skip=el=>el?.closest('script,style,code,pre,kbd,samp,[data-no-translate],.language-menu');
  function act_loc(root){
    if(root.nodeType===Node.TEXT_NODE){if(!is_skip(root.parentElement)){const next=txt_loc(root.nodeValue);if(next!==root.nodeValue)root.nodeValue=next;}return;}
    if(root.nodeType!==Node.ELEMENT_NODE||is_skip(root))return;
    for(const name of ['aria-label','title','alt','placeholder']){
      const old=root.getAttribute(name);if(old){const next=txt_loc(old);if(next!==old)root.setAttribute(name,next);}
    }
    for(const child of [...root.childNodes])act_loc(child);
  }
  globalThis.kamalaLocale={text:txt_loc};
  act_loc(document.body);
  const obs_loc=new MutationObserver(records=>{
    for(const record of records){
      if(record.type==='childList'){for(const child of record.addedNodes)act_loc(child);}
      else act_loc(record.target);
    }
  });
  obs_loc.observe(document.body,{childList:true,subtree:true,characterData:true,attributes:true,attributeFilter:['aria-label','title','alt','placeholder']});
})();
