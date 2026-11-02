// Timestamp: 2026-11-01
// Version: 2.1.0
// Author & Credits: https://www.alawise.es/1-s
import { rnd_ent } from './entropy-core.mjs';

export const dat_mon = {portrait:'/assets/coin-relief-v2.png', cross:'/assets/coin-cross-relief-v2.png'};
export const pos_crz = [
  {row:2,col:2,label:'Center'}, {row:1,col:2,label:'Above'},
  {row:3,col:2,label:'Below'}, {row:2,col:1,label:'Left'}, {row:2,col:3,label:'Right'}
];
const cfg_apl = {
  majors:['Le Mat','Le Bateleur','La Papesse',"L’Imperatrice","L’Empereur",'Le Pape',"L’Amoureux",'Le Chariot','La Justice',"L’Hermite",'La Roue de Fortune','La Force','Le Pendu','Arcane XIII','Temperance','Le Diable','La Maison Dieu',"L’Etoile",'La Lune','Le Soleil','Le Jugement','Le Monde'],
  romans:['','I','II','III','IIII','V','VI','VII','VIII','VIIII','X','XI','XII','XIII','XIIII','XV','XVI','XVII','XVIII','XVIIII','XX','XXI'],
  suits:{spanish:['Oros','Copas','Espadas','Bastos'],marseille:['Deniers','Coupes','Epees','Batons']}
};

export function crt_bar(clv_bar = 'spanish', cnt_tot = 40) {
  if (!['spanish','american','marseille'].includes(clv_bar)) throw new RangeError('Unknown deck');
  if (clv_bar === 'spanish' && ![40,48].includes(cnt_tot)) throw new RangeError('Spanish decks have 40 or 48 cards');
  if (clv_bar === 'american') return ['Spades','Hearts','Diamonds','Clubs'].flatMap((txt_val,sys_idx)=>
    ['A','2','3','4','5','6','7','8','9','10','J','Q','K'].map(txt_cmt=>({
      id:'a-'+sys_idx+'-'+txt_cmt, label:txt_cmt+' of '+txt_val, rank:txt_cmt,
      suit:txt_val,symbol:['♠','♥','♦','♣'][sys_idx],red:sys_idx===1||sys_idx===2,deck:'Kamala · American · 52',
      art:'/assets/playing-cards/american-'+sys_idx+'-'+txt_cmt.toLowerCase()+(['J','Q','K'].includes(txt_cmt)?'.webp':'.svg')
    })));
  const dat_bar = clv_bar === 'marseille' ? cfg_apl.majors.map((txt_val,sys_idx)=>({
    id:'m-'+sys_idx,label:txt_val,rank:sys_idx ? cfg_apl.romans[sys_idx] : '—',suit:'Major arcana',symbol:'✦',deck:'Kamala · Marseille · 78',art:'/assets/tarot/m-'+sys_idx+'.webp'
  })) : [];
  for (const [sys_idx,txt_val] of cfg_apl.suits[clv_bar].entries()) {
    const dat_env = clv_bar === 'spanish'
      ? (cnt_tot===40 ? ['1','2','3','4','5','6','7','Sota','Caballo','Rey'] : ['1','2','3','4','5','6','7','8','9','Sota','Caballo','Rey'])
      : ['As','2','3','4','5','6','7','8','9','10','Valet','Cavalier','Reine','Roi'];
    for (const txt_cmt of dat_env) dat_bar.push({
      id:clv_bar+'-'+sys_idx+'-'+txt_cmt,label:txt_cmt+' · '+txt_val,
      rank:clv_bar==='spanish' ? ({Sota:'10',Caballo:'11',Rey:'12'}[txt_cmt]||txt_cmt) : txt_cmt,
      suit:txt_val,icon:['coins','cups','swords','batons'][sys_idx],deck:clv_bar==='spanish' ? 'Spanish · '+cnt_tot : 'Kamala · Marseille · 78',
      art:clv_bar==='marseille'
        ? '/assets/tarot/marseille-'+sys_idx+'-'+txt_cmt.toLowerCase()+(['Valet','Cavalier','Reine','Roi'].includes(txt_cmt)?'.webp':'.svg')
        : '/assets/playing-cards/spanish-'+sys_idx+'-'+txt_cmt.toLowerCase()+(['Sota','Caballo','Rey'].includes(txt_cmt)?'.webp':'.svg')
    });
  }
  return dat_bar;
}

// Finnish labels are modern glosses. They are not reconstructed Finnic rune names.
export const dat_run = {
  '16':[
    ['ᚠ','f','Fe','Karja'],['ᚢ','u','Ur','Sade'],['ᚦ','þ','Thurs','Jättiläinen'],['ᚬ','ą','Ass','Jumala'],
    ['ᚱ','r','Reid','Ratsastus'],['ᚴ','k','Kaun','Haava'],['ᚼ','h','Hagall','Rae'],['ᚾ','n','Naudr','Hätä'],
    ['ᛁ','i','Iss','Jää'],['ᛅ','a','Ar','Sato'],['ᛋ','s','Sol','Aurinko'],['ᛏ','t','Tyr','Týr'],
    ['ᛒ','b','Bjarkan','Koivu'],['ᛘ','m','Madr','Ihminen'],['ᛚ','l','Logr','Vesi'],['ᛦ','ʀ','Yr','Marjakuusi']
  ],
  '24':[
    ['ᚠ','f','Fehu','Karja'],['ᚢ','u','Uruz','Alkuhärkä'],['ᚦ','þ','Thurisaz','Jättiläinen'],['ᚨ','a','Ansuz','Jumala'],
    ['ᚱ','r','Raidho','Ratsastus'],['ᚲ','k','Kenaz','Soihtu'],['ᚷ','g','Gebo','Lahja'],['ᚹ','w','Wunjo','Ilo'],
    ['ᚺ','h','Hagalaz','Rae'],['ᚾ','n','Naudiz','Hätä'],['ᛁ','i','Isaz','Jää'],['ᛃ','j','Jera','Vuosi'],
    ['ᛇ','ï','Eihwaz','Marjakuusi'],['ᛈ','p','Perthro','Merkitys epävarma'],['ᛉ','z','Algiz','Hirvi'],['ᛊ','s','Sowilo','Aurinko'],
    ['ᛏ','t','Tiwaz','Týr'],['ᛒ','b','Berkano','Koivu'],['ᛖ','e','Ehwaz','Hevonen'],['ᛗ','m','Mannaz','Ihminen'],
    ['ᛚ','l','Laguz','Vesi'],['ᛜ','ŋ','Ingwaz','Ing'],['ᛞ','d','Dagaz','Päivä'],['ᛟ','o','Othala','Perintö']
  ]
};
for (const [clv_run,dat_env] of Object.entries(dat_run)) dat_run[clv_run] = dat_env.map(([txt_sig,txt_val,txt_cmt,txt_note],sys_idx)=>({
  id:'r'+clv_run+'-'+sys_idx,glyph:txt_sig,latin:txt_val,name:txt_cmt,fi:txt_note
}));

export function crt_tir(dat_bar, cnt_tot, dat_azr) {
  if (!Number.isInteger(cnt_tot) || cnt_tot<1 || cnt_tot>dat_bar.length) throw new RangeError('Not enough symbols remain');
  const dat_env = [];
  for (let sys_idx=0;sys_idx<cnt_tot;sys_idx++) dat_env.push(dat_bar.splice(rnd_ent(dat_azr,dat_bar.length),1)[0]);
  return dat_env;
}

export function cfg_tir(clv_dis, cnt_fil, cnt_col, cnt_tot) {
  if (!['matrix','cross'].includes(clv_dis)) throw new RangeError('Unknown layout');
  if (clv_dis==='cross') { cnt_fil=3;cnt_col=3; }
  if (![cnt_fil,cnt_col].every(cnt_tot=>Number.isInteger(cnt_tot)&&cnt_tot>=1&&cnt_tot<=78)) throw new RangeError('Use 1 to 78 rows and columns');
  const dat_env = {rows:cnt_fil,cols:cnt_col,count:clv_dis==='cross' ? 5 : cnt_fil*cnt_col};
  if (dat_env.count>cnt_tot) throw new RangeError('Not enough cards remain for this layout. Reset the deck or choose fewer positions.');
  return dat_env;
}

export function crt_lin(dat_azr) {
  const dat_env = Array.from({length:3},()=>rnd_ent(dat_azr,2));
  return {coins:dat_env,value:dat_env.reduce((cnt_tot,rnd_bit)=>cnt_tot+2+rnd_bit,0)};
}

// Rows are upper trigrams, columns lower trigrams; bits run bottom to top.
const dat_hex = [
  [1,10,13,25,44,6,33,12],[43,58,49,17,28,47,31,45],
  [14,38,30,21,50,64,56,35],[34,54,55,51,32,40,62,16],
  [9,61,37,42,57,59,53,20],[5,60,63,3,48,29,39,8],
  [26,41,22,27,18,4,52,23],[11,19,36,24,46,7,15,2]
];
export function crt_hex(dat_lin) {
  if (dat_lin.length!==6 || !dat_lin.every(cnt_tot=>[6,7,8,9].includes(cnt_tot))) throw new RangeError('A hexagram needs six coin totals');
  const dat_env = dat_lin.map(cnt_tot=>cnt_tot%2);
  const dat_dst = dat_lin.map((cnt_tot,sys_idx)=>[6,9].includes(cnt_tot) ? 1-dat_env[sys_idx] : dat_env[sys_idx]);
  const dat_par = dat_lin.map((cnt_tot,sys_idx)=>[6,9].includes(cnt_tot) ? sys_idx+1 : 0).filter(Boolean);
  const dat_res = {primary:dat_env,related:dat_dst,changing:dat_par};
  for (const [txt_val,dat_itm] of [['number',dat_env],['relatedNumber',dat_dst]]) {
    const cnt_fil = [7,3,5,1,6,2,4,0].indexOf(dat_itm[3]+2*dat_itm[4]+4*dat_itm[5]);
    const cnt_col = [7,3,5,1,6,2,4,0].indexOf(dat_itm[0]+2*dat_itm[1]+4*dat_itm[2]);
    dat_res[txt_val] = dat_hex[cnt_fil][cnt_col];
  }
  return dat_res;
}
