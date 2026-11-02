#!/usr/bin/env python3
# Timestamp: 2026-10-30
# Version: 2.0.0
# Author and Credits: https://www.alawise.es/1-s
"""Render every retained lexical entry and its connected field note."""

import html
import re
import unicodedata
from collections import defaultdict
from urllib.parse import quote

def esc_htm(txt_val):
    return html.escape(str(txt_val), quote=True)

def clv_lex(txt_val):
    txt_val = unicodedata.normalize('NFKD', txt_val).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+','-',txt_val).strip('-') or 'term'

def crt_gls_lst(dat_gls, dat_esc, clv_esc=None):
    return '<div class="cards lexicon-cards">' + ''.join(
        '<a class="card" href="/arts/'+dat_itm['slug']+'/"><div class="art" aria-hidden="true">'+esc_htm(dat_itm['symbol'])+'</div><span class="tag">'+esc_htm(dat_esc[dat_itm['scale']][1])+' / '+esc_htm(dat_itm['family'])+'</span><h3>'+esc_htm(dat_itm['title'])+' <span>↗</span></h3><p>'+esc_htm(dat_itm['definition'])+'</p></a>'
        for dat_itm in dat_gls if clv_esc is None or dat_itm['scale']==clv_esc or clv_esc in dat_itm['secondary_scales']) + '</div>'

def crt_pot_lnk(clv_esc, tit_pag='Share a photograph or a record.'):
    return '<section class="section pot-invitation"><div><span class="eyebrow">POTPOURRI / PERSONAL INTERPRETATION</span><h2>'+esc_htm(tit_pag)+'</h2><p>A photograph, drawing or dated record can be sent privately for a personal reading. Include the procedure and the question.</p></div><a class="button" href="/potpourri/?art='+quote(clv_esc)+'">Photo instructions & submission ↗</a></section>'

def crt_v2(crt_pag, crt_hdr, crt_fnt, dat_gls, dat_tec, dat_esc, pth_src, pth_dst):
    dat_lex = []
    dat_top = {}
    dat_nom = dict(zip(
        ['pendulum','crystallization','dice','coins','grounds','runes','cards','entropy-streams','weather','sun','planets','horoscope','contemplative-observation','naam-listening','breath-observation','ritual-sound','yijing','crystal-gazing','candle-gazing','handreading','automatic-writing','automatic-painting','tracking','kinesthesia','radiesthesia','molybdomancy','clairvoyance','lucid-dreaming'],
        ['Péndulo','Cristalización','Dados','Monedas','Lectura de posos de té y café','Runas','Cartas / cartomancia','Flujos de entropía','Meteorología','Sol','Planetas','Horóscopo','Observación contemplativa','Naam / escucha atenta','Observación de la respiración','Sonido y ritmo ritual','I Ching / Yijing','Observación del cristal','Contemplación de la vela','Quiromancia / lectura de manos','Escritura automática','Pintura y dibujo automáticos','Rastreo / huellas y señales','Kinestesia / conciencia corporal','Radiestesia','Molibdomancia','Clarividencia','Sueños lúcidos']))
    for dat_itm in dat_tec:
        dat_top[dat_itm['slug']] = {'title':dat_itm['title'], 'photo':[
            'Include one full view and one closer detail of the observation.',
            'Describe the preparation, time, arrangement and question. Keep the original sequence visible.'
        ]}
        dat_lex.append({'term':dat_itm['title'],'term_es':dat_nom.get(dat_itm['slug'],''),'definition':dat_itm['description'],'scale':dat_itm['scale'],'url':'/techniques/'+dat_itm['slug']+'/'})
    for clv_esc, dat_env in {
        'grounds':['Photograph the cup from above and from several sides in soft light; include the handle as an orientation reference.','Include the saucer separately and describe how the drink was prepared and the cup turned.'],
        'handreading':['Photograph both palms with fingers relaxed and the full hand in view.','Add a sharp close view of the palm lines and indicate left/right and the dominant hand.'],
        'cards':['Use one overhead photograph showing the complete spread in its original order.','Include card positions, deck name and any reversals; add a close detail if text is unreadable.'],
        'dice':['Photograph every die from above with its result unobstructed.','Number successive throws and keep the original order in the accompanying note.'],
        'coins':['Photograph the complete arrangement from above so each side is visible.','For I Ching, include all six line totals in bottom-to-top order.'],
        'runes':['Show the entire layout with each rune in its drawn orientation.','State whether the set contains 16 or 24 runes and number their draw order.'],
        'tracking':['Take a wide landscape view and a sharp overhead photograph of the trace with a ruler.','Add a side view, direction and location context without disturbing the track.'],
        'pendulum':['Include the suspension point, weight and a stationary reference in a full view.','Add a sequence or dated drawing and record string length, timing and nearby movement.'],
        'crystallization':['Include a full sample view and a focused microscope detail with magnification or scale.','Record ingredients, preparation, illumination and time since drying.']
    }.items():
        dat_top[clv_esc]['photo'] = dat_env
    for dat_itm in dat_gls:
        dat_top[dat_itm['slug']] = {'title':dat_itm['title'], 'photo':dat_itm['photo']}
        txt_pag = crt_hdr(esc_htm(dat_itm['title'])+'.',esc_htm(dat_itm['definition']),dat_esc[dat_itm['scale']][1].upper()+' / '+esc_htm(dat_itm['family']))
        txt_pag += '<section class="section reading"><div><span class="eyebrow">LEXICON / LANGUAGE & MEANING</span><h2>Names in context.</h2><dl class="term-definitions">'
        for idx_tec, dat_fnt in enumerate(dat_itm['lexicon']):
            clv_esc = clv_lex(dat_fnt['term'])
            txt_pag += '<div id="term-'+clv_esc+'"><dt>'+esc_htm(dat_fnt['term'])+'</dt><dd><span lang="es">'+esc_htm(dat_fnt['term_es'])+'</span><p>'+esc_htm(dat_fnt['definition'])+'</p></dd></div>'
            dat_lex.append({**dat_fnt,'scale':dat_itm['scale'],'url':'/arts/'+dat_itm['slug']+'/#term-'+clv_esc})
        txt_pag += '</dl></div><div><span class="eyebrow">PROVENANCE & INTERPRETATION</span><h2>A practice,<br>a setting.</h2><p>'+esc_htm(dat_itm['context'])+'</p><div class="practice-tags">'+''.join('<a href="/scales/'+clv_esc+'/">'+esc_htm(dat_esc[clv_esc][1])+'</a>' for clv_esc in [dat_itm['scale']]+dat_itm['secondary_scales'])+'</div>'+crt_fnt(dat_itm['sources'])+'</div></section>'
        txt_pag += '<section class="section reading field-method"><div><span class="eyebrow">FIELD NOTE / METHOD</span><h2>Keep a record.</h2><ol>'+''.join('<li>'+esc_htm(txt_val)+'</li>' for txt_val in dat_itm['method'])+'</ol></div><div><span class="eyebrow">POTPOURRI / PHOTO GUIDE</span><h2>What to include.</h2><ul>'+''.join('<li>'+esc_htm(txt_val)+'</li>' for txt_val in dat_itm['photo'])+'</ul></div></section>'
        if dat_itm['related']:
            txt_pag += '<section class="section related"><span class="eyebrow">CONNECTED FIELD NOTES</span><div class="actions">'+''.join('<a class="text-link" href="/techniques/'+clv_esc+'/">'+esc_htm(next(dat_fnt['title'] for dat_fnt in dat_tec if dat_fnt['slug']==clv_esc))+' ↗</a>' for clv_esc in dat_itm['related'])+'</div></section>'
        txt_pag += crt_pot_lnk(dat_itm['slug'])+'<section class="section next-page"><a class="text-link" href="/glossary/">Full glossary ↗</a><a class="text-link" href="/arts/">All arts & variants ↗</a></section>'
        crt_pag('/arts/'+dat_itm['slug']+'/',dat_itm['title'],txt_pag,dat_itm['definition'])
    txt_pag = crt_hdr('Arts, names<br>& connections.','The complete field guide: practices, historical vocabulary and variants, connected to their sources and scales.','KAMALA / ARTS & VARIANTS')
    txt_pag += '<section class="section"><p class="scale-explainer">Each name has a definition and a context. A term can identify a symbolic system, a reported experience, a contemplative practice or a historical custom. Related names retain their own entries.</p><div class="actions"><a class="button" href="/glossary/">Search the full lexicon ↗</a><a class="text-link" href="/scales/">Choose a scale ↗</a></div></section>'
    for txt_val in dict.fromkeys(dat_itm['family'] for dat_itm in dat_gls):
        txt_pag += '<section class="section"><span class="eyebrow">LEXICON / FIELD GUIDE</span><h2>'+esc_htm(txt_val)+'</h2>'+crt_gls_lst([dat_itm for dat_itm in dat_gls if dat_itm['family']==txt_val],dat_esc)+'</section>'
    crt_pag('/arts/','Arts & variants',txt_pag,'All retained mantic arts and variants, with definitions, cultural context, observation notes, sources and private photo submission.')
    # Keep the prior astrology vocabulary available when its long API panel is removed.
    for dat_itm in [
        ('Traditional / classical astrology','Astrología tradicional / clásica','Labels used for historical astrological schools; name the period, authors and rules followed in a particular reading.'),
        ('Mayan planetary horoscope','Horóscopo planetario maya','The planetary horoscope described by AstroApp using synodic ages and twenty trecenas; identify its method separately from calendrical conversions.'),
        ('Transit','Tránsito','A planetary position considered for a selected time, often compared with a reference chart.'),
        ('Progression','Progresión','An astrological timing technique deriving symbolic positions through a stated time correspondence.'),
        ('Planetary return','Retorno planetario','An astrological chart for a planet returning to a specified reference position.'),
        ('Synastry','Sinastría','An astrological comparison between two charts.'),
        ('Tropical zodiac','Zodíaco tropical','A zodiac referenced to the equinoxes through twelve equal divisions.'),
        ('Sidereal zodiac','Zodíaco sideral','A zodiac using a specified stellar reference and its chosen ayanamsa convention.'),
        ('House system','Sistema de casas','A convention for dividing a chart into astrological houses.'),
        ('Geocentric coordinates','Coordenadas geocéntricas','Positions expressed relative to an Earth-centered reference frame.'),
        ('Heliocentric coordinates','Coordenadas heliocéntricas','Positions expressed relative to a Sun-centered reference frame.'),
        ('Rāśi / D1','Carta rāśi','The principal sign-based chart used in Jyotish.'),
        ('Varga','Carta divisional','A zodiac division used to construct a divisional chart in Jyotish.'),
        ('Nakshatra','Nakshatra','A lunar mansion used within Indian astrological systems.'),
        ('Daśā','Daśā','An astrological period system used for timing in Jyotish.'),
        ('Pañcāṅga','Pañcāṅga','A five-part Hindu calendrical almanac.'),
        ('Muhūrta','Muhūrta','The selection of an intended time through Indian electional astrology.'),
        ('Tzolk’in','Tzolk’in','The 260-day sacred count in Maya calendrical traditions.'),
        ('Haab’','Haab’','The 365-day Maya calendar.'),
        ('Long Count','Cuenta Larga','A Mesoamerican system for recording elapsed days from a calendrical starting point.'),
        ('Tonalpohualli','Tonalpohualli','The 260-day ritual count in Nahua calendrical traditions.'),
        ('Dreamspell','Dreamspell','A modern calendar system, presented separately from historical Maya counts.'),
        ('Ayanamsa','Ayanamsa','The angular offset used by a specified convention to relate tropical and sidereal zodiac positions.'),
        ('BaZi / Four Pillars','BaZi / Cuatro Pilares','A Chinese calendrical system organizing birth information into four pillars.'),
        ('Zi Wei Dou Shu','Zi Wei Dou Shu','A Chinese astrological chart system with its own stars, palaces and interpretive rules.'),
        ('Jyotish / Vedic astrology','Jyotish / astrología védica','A name for Indian astrological traditions with distinct calculations, texts and schools.'),
        ('Hellenistic astrology','Astrología helenística','Astrological traditions developed in the Hellenistic Mediterranean and their later study.'),
        ('Babylonian astrology','Astrología babilónica','Mesopotamian traditions of celestial omens and later horoscopic practice.'),
        ('Diné / Navajo sky traditions','Tradiciones celestes diné / navajo','Community-specific sky knowledge and narratives, documented in the cultural atlas.')
    ]:
        dat_lex.append({'term':dat_itm[0],'term_es':dat_itm[1],'definition':dat_itm[2],'scale':'solar','url':'/traditions/shamanic/dine-navajo/' if dat_itm[0].startswith('Diné') else '/astrology/'})
    dat_lex.sort(key=lambda dat_itm:clv_lex(dat_itm['term']))
    dat_grp = defaultdict(list)
    for dat_itm in dat_lex:
        dat_grp[clv_lex(dat_itm['term'])[0].upper()].append(dat_itm)
    txt_pag = crt_hdr('A lexicon.<br>Room for every name.','Names, synonyms and definitions across traditions. Search in English or Spanish, then follow a term to its practice and context.','KAMALA / COMPLETE GLOSSARY')
    txt_pag += '<section class="section lexicon-shell" data-glossary><div class="lexicon-toolbar"><label>Find a term<input type="search" data-lexicon-search placeholder="e.g. geomancy, sueños, wax" autocomplete="off"></label><label>Observation scale<select data-lexicon-scale><option value="">All scales</option>'+''.join('<option value="'+clv_esc+'">'+esc_htm(dat_itm[1])+'</option>' for clv_esc,dat_itm in dat_esc.items())+'</select></label><p data-lexicon-count role="status" aria-live="polite">'+str(len(dat_lex))+' lexical entries</p></div><nav class="lexicon-alphabet" aria-label="Glossary letters">'+''.join('<a href="#letter-'+clv_esc+'">'+clv_esc+'</a>' for clv_esc in dat_grp)+'</nav>'
    for clv_esc,dat_env in dat_grp.items():
        txt_pag += '<section class="lexicon-letter" id="letter-'+clv_esc+'"><h2>'+clv_esc+'</h2><div class="lexicon-grid">'
        for dat_itm in dat_env:
            txt_pag += '<article class="lexicon-entry" data-lexicon-entry data-scale="'+dat_itm['scale']+'"><span class="eyebrow">'+esc_htm(dat_esc[dat_itm['scale']][1])+'</span><h3><a href="'+dat_itm['url']+'">'+esc_htm(dat_itm['term'])+' ↗</a></h3>'+('<span class="lexicon-es" lang="es">'+esc_htm(dat_itm['term_es'])+'</span>' if dat_itm['term_es'] else '')+'<p>'+esc_htm(dat_itm['definition'])+'</p></article>'
        txt_pag += '</div></section>'
    txt_pag += '<p class="lexicon-empty" data-lexicon-empty hidden>No matching terms. Try another spelling or clear the scale filter.</p></section>'
    crt_pag('/glossary/','Complete glossary',txt_pag,'A complete searchable lexicon of mantic arts, contemplative practices, historical vocabulary and astrological terms, with English and Spanish names.')
    dat_top['other'] = {'title':'Other / a name or practice to identify','photo':['Include a clear full view and a close detail.','Describe the material, place, preparation and question.']}
    txt_pag = (pth_src/'potpourri.html').read_text().replace('<!-- POTPOURRI OPTIONS -->',''.join('<option value="'+clv_esc+'">'+esc_htm(dat_itm['title'])+'</option>' for clv_esc,dat_itm in sorted(dat_top.items(),key=lambda dat_env:dat_env[1]['title'].casefold())))
    crt_pag('/potpourri/','Potpourri — personal interpretation',txt_pag,'Photo guides and private submissions for personal readings of cards, hands, grounds, coins, tracks, dreams and all arts in the Kamala field guide.')
    (pth_dst/'potpourri/topics.json').write_text(__import__('json').dumps(dat_top,ensure_ascii=False,indent=2))
    return len(dat_lex)
