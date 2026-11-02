#!/usr/bin/env python3
# Timestamp: 2026-11-02
# Version: 2.1.1
# Author & Credits: https://www.alawise.es/1-s
"""Build complete static pages with shared navigation and independent app routes."""

import html
import json
import math
import re
import shutil
from pathlib import Path
from urllib.parse import quote

from page_meta import crt_met, dat_met
from chance_widgets import crt_prb, dat_prb
from glossary_pages import crt_gls_lst, crt_pot_lnk, crt_v2
from contemplation_pages import crt_cnp

sys_rad = Path(__file__).resolve().parents[1]
pth_src = sys_rad / "src"
pth_dst = sys_rad / "dist"
pth_img = pth_src / 'assets/coin-portrait.png'
if pth_img.is_file():
    (pth_dst / 'assets').mkdir(parents=True, exist_ok=True)
    shutil.copyfile(pth_img, pth_dst / 'assets/coin-portrait.png')
dat_tec = json.loads((pth_src / "techniques.json").read_text())
dat_trd = json.loads((pth_src / "traditions.json").read_text())
dat_chm = json.loads((pth_src / "shamanic.json").read_text())
dat_obs = json.loads((pth_src / "observatory.json").read_text())
dat_cam = json.loads((pth_src / "cameras.json").read_text())
dat_pdt = json.loads((pth_src / "further-arts.json").read_text())
dat_gls = json.loads((pth_src / "glossary.json").read_text())["entries"]
for pth_fil in (pth_src / "assets").rglob('*'):
    if pth_fil.is_file():
        pth_rel = pth_fil.relative_to(pth_src / 'assets')
        (pth_dst / 'assets' / pth_rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(pth_fil, pth_dst / 'assets' / pth_rel)
dat_reg = {
    "northern-europe": "Northern Europe",
    "siberia-inner-asia": "Siberia & Inner Asia",
    "americas": "The Americas",
    "arctic": "The Arctic",
    "east-asia": "East Asia",
}
dat_esc = {
    "matter": ("01", "Matter", "Material scale", "Crystals, surfaces, cast forms and their shadows.", "Observe material structure and the conditions under which it changes. The scale refers to the object being observed, rather than the size of the equipment."),
    "hand": ("02", "Hand scale", "Objects & manipulation", "Cards, coins, runes and objects arranged or moved by hand.", "Follow what is held, cast, arranged or marked by hand. This scale groups manipulated objects and tools; body awareness, dreams and perception remain in Human scale."),
    "human": ("03", "Human scale", "Body, perception & dreams", "The body, attention, dreams, clairvoyance accounts and personal cycles.", "Explore body awareness, handreading, breath, listening, lucid dreams and clairvoyance accounts. Document the physical procedure and keep any symbolic interpretation alongside the observation."),
    "earth": ("04", "Earth", "Terrestrial scale", "Wildlife tracks, atmosphere, cameras and changing signals.", "Follow wildlife tracks, the local environment and the streams produced by instruments. Source, location, sampling interval and units make observations easier to compare."),
    "solar": ("05", "Solar system", "Celestial scale", "The Sun, planets, gravity and astrology.", "Study the sky through observation, calculation and cultural interpretation. Identify which approach each record uses and retain its time and reference frame."),
}

# Cardinal spokes are indigo; each quadrant then follows green, yellow and red.
txt_est = '''<svg class="brand-star" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" aria-hidden="true"><g fill="none" stroke-width="1.8" stroke-linecap="round">'''
txt_est += ''.join('''<g transform="rotate(''' + str(ang_sig) + ''' 32 32)"><path stroke="#7367e8" d="M32 25V6"/><path stroke="#45bc7b" d="M34.68 25.53L41.95 7.98"/><path stroke="#eac84c" d="M36.95 27.05L50.38 13.62"/><path stroke="#df5d70" d="M38.47 29.32L56.02 22.05"/></g>''' for ang_sig in (0, 90, 180, 270))
txt_est += '</g></svg>'


def esc_htm(txt_val):
    return html.escape(str(txt_val), quote=True)


def crt_nav(pth_pag, clv_nav='top'):
    def crt_lnk(pth_lnk, tit_lnk):
        cls_lnk = ' aria-current="page"' if pth_pag == pth_lnk else ""
        return f'<a href="{pth_lnk}"{cls_lnk}>{tit_lnk}</a>'

    txt_esc = "".join(crt_lnk(f"/scales/{clv_esc}/", f"<span>{dat_itm[0]}</span> {dat_itm[1]}") for clv_esc, dat_itm in dat_esc.items())
    return f'''{'<a class="skip" href="#main">Skip to content</a>' if clv_nav == 'top' else ''}
<header class="site-menu{' menu-bottom' if clv_nav == 'bottom' else ''}"><a class="brand" href="/" aria-label="kamala.pro home">{txt_est}<span class="brand-copy"><span>kamala<span class="dot">.</span>pro</span><small lang="es">Artes Mánticos</small></span></a>
<button class="menu-toggle" aria-controls="main-nav-{clv_nav}" aria-expanded="false">Menu <span>＋</span></button>
<nav id="main-nav-{clv_nav}" class="site-navigation" aria-label="{'Main navigation' if clv_nav == 'top' else 'Bottom navigation'}">
{crt_lnk('/', 'Home')}
<details class="nav-scales"><summary>Scales <span>⌄</span></summary><div class="nav-drop">{crt_lnk('/scales/', 'Explore all scales ↗')}{txt_esc}</div></details>
{crt_lnk('/arts/', 'Arts')}{crt_lnk('/glossary/', 'Glossary')}{crt_lnk('/traditions/', 'Traditions')}<details class="nav-scales nav-astrology"><summary>Astrology <span>⌄</span></summary><div class="nav-drop">{crt_lnk('/astrology/', 'Charts & traditions ↗')}{crt_lnk('/astrology/#western', 'Western astrology')}{crt_lnk('/astrology/#jyotish', 'Jyotisha · Indian astrology')}{crt_lnk('/astrology/#chinese', 'Chinese astrology')}{crt_lnk('/astrology/#maya', 'Maya calendars')}{crt_lnk('/astrology/#nahua', 'Nahua calendars')}{crt_lnk('/astrology/#dine', 'Diné sky traditions')}{crt_lnk('/astrology/#modern-calendars', 'Dreamspell · modern system')}{crt_lnk('/astrology/#mesopotamian', 'Mesopotamian traditions')}</div></details>{crt_lnk('/biorritmos/', 'Biorhythms')}{crt_lnk('/gravitacional/', 'Planetary gravity')}{crt_lnk('/observatory/', 'Observatory')}{crt_lnk('/potpourri/', 'Potpourri')}{crt_lnk('/contact/', 'Contact')}
{crt_lnk('/stream/', 'Cameras')}{crt_lnk('/apps/', 'Chance apps')}{crt_lnk('/contemplation/', 'Contemplation')}{crt_lnk('/api/', 'URL & API')}
</nav></header>'''


def crt_crd(dat_itm, idx_tec):
    dat_itm_esc = dat_esc[dat_itm["scale"]]
    return f'''<a class="card" data-cat="{dat_itm['scale']}" href="/techniques/{dat_itm['slug']}/"><div class="art" aria-hidden="true">{dat_itm['symbol']}</div><span class="tag">{idx_tec + 1:02} / {dat_itm_esc[1]}</span><h3>{esc_htm(dat_itm['title'])} <span>↗</span></h3><p>{esc_htm(dat_itm['summary'])}</p></a>'''


def crt_lst(clv_esc=None):
    return '<div class="cards">' + "".join(crt_crd(dat_itm, idx_tec) for idx_tec, dat_itm in enumerate(dat_tec) if not clv_esc or dat_itm["scale"] == clv_esc) + '</div>' + crt_gls_lst(dat_gls, dat_esc, clv_esc)


def crt_esc():
    return '<div class="scale-grid">' + "".join(f'''<a class="scale-card" href="/scales/{clv_esc}/"><span class="eyebrow">{dat_itm[0]} / {dat_itm[2]}</span><h3>{dat_itm[1]} <span>↗</span></h3><p>{dat_itm[3]}</p></a>''' for clv_esc, dat_itm in dat_esc.items()) + '</div>'


def crt_trd():
    return '<div class="tradition-grid">' + ''.join(f'''<a class="tradition-card" href="/traditions/{dat_itm['slug']}/"><h3>{esc_htm(dat_itm['title'])}<span>↗</span></h3><p>{esc_htm(dat_itm['summary'])}</p><div class="practice-tags">{''.join('<span>' + esc_htm(txt_val) + '</span>' for txt_val in dat_itm['practices'])}</div></a>''' for dat_itm in dat_trd if dat_itm['slug'] != 'shamanic') + '</div>'


def crt_chm(clv_reg=None):
    return '<div class="atlas-grid">' + ''.join(f'''<a class="atlas-card" href="/traditions/shamanic/{dat_itm['slug']}/"><span class="eyebrow">{esc_htm(dat_itm['area'])}</span><h3>{esc_htm(dat_itm['title'])}<span aria-hidden="true">↗</span></h3><p>{esc_htm(dat_itm['summary'])}</p><div class="practice-tags">{''.join('<span>' + esc_htm(txt_val) + '</span>' for txt_val in dat_itm['practices'])}</div></a>''' for dat_itm in dat_chm if clv_reg is None or dat_itm['region'] == clv_reg) + '</div>'


def crt_cam():
    # Camera cards do not open media connections; only a selected screen does.
    return '<div class="camera-grid">' + ''.join(f'''<a class="camera-card" href="/stream/{dat_itm['id']}/"><div class="camera-art" aria-hidden="true"><span>{idx_tec + 1:02}</span><i></i></div><span class="eyebrow">{esc_htm(dat_itm['label'])}</span><h2>{esc_htm(dat_itm['title'])}<span aria-hidden="true">↗</span></h2><p>{esc_htm(dat_itm['summary'])}</p><span class="camera-open">OPEN CAMERA SCREEN ↗</span></a>''' for idx_tec, dat_itm in enumerate(dat_cam)) + '</div>'


def crt_obs():
    return f'''<section class="home-streams" aria-labelledby="streams-title"><div class="stream-heading"><div><div class="eyebrow">THE OBSERVATORY / SUN · EARTH · PLANETS</div><h2 id="streams-title">Three windows.<br>One unfolding world.</h2></div><p>Solar imagery, the changing atmosphere<br>and the planetary view, side by side.</p></div><div class="stream-grid">
<article class="stream-card" id="solar"><div class="stream-label"><span class="eyebrow">01 / SOLAR IMAGERY</span><span class="source-badge">NASA / SDO</span></div><h3>The Sun</h3><div class="stream-media solar-media"><video controls muted playsinline loop preload="none" poster="{esc_htm(dat_obs['solar_image'])}" aria-label="Latest published SDO AIA 171 solar sequence"><source src="{esc_htm(dat_obs['solar_video'])}" type="video/mp4">Your browser cannot play this sequence. Use the source link below.</video></div><p class="stream-caption">AIA 171 Å · latest published sequence. Dates appear in the imagery; this is a time-lapse, not a continuous live camera.</p><div class="stream-links"><a href="{esc_htm(dat_obs['solar_video'])}" target="_blank" rel="noopener">Open solar sequence ↗</a><a href="{esc_htm(dat_obs['solar_source'])}" target="_blank" rel="noopener">NASA source ↗</a></div></article>
<article class="stream-card" id="weather"><div class="stream-label"><span class="eyebrow">02 / METEO</span><span class="source-badge">WINDY / ECMWF</span></div><h3>Andorra & the Pyrenees</h3><div class="stream-media"><iframe src="{esc_htm(dat_obs['weather_embed'])}" title="Windy animated weather map centered on Andorra and the Pyrenees" loading="lazy" referrerpolicy="no-referrer" allowfullscreen></iframe></div><p class="stream-caption">Animated wind forecast · the model and selected time are shown in the map. Forecast data are distinct from local station measurements.</p><div class="stream-links"><a href="{esc_htm(dat_obs['weather_source'])}" target="_blank" rel="noopener">Open weather map ↗</a><a href="/techniques/weather/">Weather field notes ↗</a></div></article>
<article class="stream-card" id="alignment"><div class="stream-label"><span class="eyebrow">03 / PLANETARY ALIGNMENT</span><span class="source-badge">KAMALA / ORIGINAL APP</span></div><h3>The planetary view</h3><div class="stream-media planetary-media"><iframe src="{esc_htm(dat_obs['planetary_app'])}" title="Kamala SolarSimulator: planetary positions and experimental gravity model" loading="lazy" referrerpolicy="no-referrer"></iframe></div><p class="stream-caption">The existing SolarSimulator, with its time and speed controls. Display distances are adjusted; its gravity model remains experimental.</p><div class="stream-links"><a href="{esc_htm(dat_obs['planetary_app'])}" target="_blank" rel="noopener">Open original application ↗</a><a href="/gravitacional/">Full workspace ↗</a></div></article>
</div></section>'''


def crt_fnt(dat_fnt):
    return '<aside class="context-sources"><div class="eyebrow">SOURCES & CONTEXT</div>' + ''.join(f'''<a href="{esc_htm(dat_itm['url'])}" target="_blank" rel="noopener">{esc_htm(dat_itm['title'])} ↗</a>''' for dat_itm in dat_fnt) + '</aside>'


def crt_zod():
    # This wheel is an editorial illustration, with no date-dependent positions.
    txt_sig = ""
    for idx_sig, sig_zod in enumerate("♈♉♊♋♌♍♎♏♐♑♒♓"):
        ang_sig = math.radians(idx_sig * 30 - 75)
        txt_sig += f'<text x="{250 + 178 * math.cos(ang_sig):.1f}" y="{250 + 178 * math.sin(ang_sig):.1f}">{sig_zod}\ufe0e</text>'
        ang_sig = math.radians(idx_sig * 30)
        txt_sig += f'<line x1="{250 + 146 * math.cos(ang_sig):.1f}" y1="{250 + 146 * math.sin(ang_sig):.1f}" x2="{250 + 210 * math.cos(ang_sig):.1f}" y2="{250 + 210 * math.sin(ang_sig):.1f}"/>'
    return f'''<svg class="zodiac" viewBox="0 0 500 500" role="img" aria-label="Illustrated zodiac wheel; not a calculated chart"><g fill="none" stroke="currentColor"><circle cx="250" cy="250" r="233" opacity=".15"/><circle cx="250" cy="250" r="211" opacity=".65"/><circle cx="250" cy="250" r="146" opacity=".5"/><circle cx="250" cy="250" r="135" stroke-dasharray="1 7"/><circle cx="250" cy="250" r="70" opacity=".2"/>{txt_sig}</g><g stroke="currentColor" fill="none" opacity=".35"><path d="M250 115L367 317 133 317ZM250 385L133 183 367 183Z"/><path d="M250 38V462M38 250H462" opacity=".25"/></g><circle cx="250" cy="250" r="10" fill="currentColor"/><circle cx="250" cy="250" r="22" fill="none" stroke="currentColor"/><text class="wheel-label" x="250" y="487">SYMBOLIC MAP · ILLUSTRATION</text></svg>'''


txt_ftr = f'''<footer><a class="brand" href="/">{txt_est}<span>kamala.pro</span></a><span>OBSERVATION IS A BEGINNING.</span><a href="/approach/">Our approach</a><a href="https://www.alawise.es/1-s" target="_blank" rel="noopener">1wise / OpenMind ↗</a><span>© 2026 · kamala.pro</span></footer>'''


def crt_pag(pth_pag, tit_pag, txt_pag, des_pag):
    pth_fil = pth_dst / pth_pag.strip("/") / "index.html"
    pth_fil.parent.mkdir(parents=True, exist_ok=True)
    txt_met = '<meta http-equiv="Content-Security-Policy" content="default-src &apos;none&apos;; script-src &apos;self&apos;; style-src &apos;self&apos;; img-src data: blob:; connect-src https://www.kamala.pro/api/entropy.php; worker-src &apos;none&apos;; object-src &apos;none&apos;; base-uri &apos;none&apos;; form-action &apos;none&apos;">'
    # The provider validates the SDK during load. Keep it within its workspace.
    txt_sdk = '<!-- ASTROAPP SDK START --><!-- ASTROAPP SDK END --><script src="/astroapp-head.js?v=' + dat_met["release"] + '"></script>' if 'data-astroapp' in txt_pag and 'id="astroappDiv"' in txt_pag else ''
    txt_v2 = '<link rel="stylesheet" href="/v2.css?v=' + dat_met["release"] + '">'
    if 'data-contemplation=' in txt_pag or pth_pag == '/contemplation/':
        txt_v2 += '<link rel="stylesheet" href="/contemplation.css?v=' + dat_met["release"] + '">'
    if 'data-contemplation=' in txt_pag:
        txt_v2 += '<script type="module" src="/contemplation.mjs?v=' + dat_met["release"] + '"></script>'
    txt_tar = '<script src="/tarot-viewer.js?v=' + dat_met['release'] + '" defer></script>' if 'data-tarot-gallery' in txt_pag or 'data-chance-app="cards"' in txt_pag else ''
    txt_ctl = ('<script src="/glossary.js?v=' + dat_met["release"] + '" defer></script>') if 'data-glossary' in txt_pag else ('<script src="/potpourri.js?v=' + dat_met["release"] + '" defer></script>') if 'data-potpourri' in txt_pag else ''
    pth_fil.write_text(f'''<!doctype html>
<!-- Timestamp: 2026-11-02 | Version: 2.1.1 | Author & Credits: https://www.alawise.es/1-s -->
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#06060c">{txt_met if 'data-keys-lab' in txt_pag else ''}{crt_met(pth_pag, tit_pag, des_pag)}<link rel="icon" type="image/svg+xml" href="{'data:image/svg+xml,' + quote(txt_est) if 'data-keys-lab' in txt_pag else '/favicon.svg'}"><link rel="stylesheet" href="/style.css?v={dat_met['release']}">{('<link rel="stylesheet" href="/lab.css?v=' + dat_met['release'] + '">') if 'data-keys-lab' in txt_pag else ''}{txt_v2}{txt_sdk}{txt_ctl}{txt_tar}{('<link rel="stylesheet" href="/astroapp.css?v=' + dat_met['release'] + '"><script type="module" src="/astroapp.js?v=' + dat_met['release'] + '"></script>') if 'data-astroapp' in txt_pag else ''}</head><body{' class="home-shell"' if pth_pag == '/' else ' class="cam-shell"' if pth_pag.startswith('/stream/cam') else ''}>{crt_nav(pth_pag)}<main id="main">{txt_pag}</main>{crt_nav(pth_pag, 'bottom') if pth_pag == '/' else '' if pth_pag.startswith('/stream/cam') else txt_ftr}{('<script src="/lab.js?v=' + dat_met['release'] + '" defer></script>') if 'data-keys-lab' in txt_pag else ('<script src="/app.js?v=' + dat_met['release'] + '" defer></script>')}{('<script src="/observatory.js?v=' + dat_met['release'] + '" defer></script>') if pth_pag in ('/', '/observatory/') else ''}{('<script src="/camera.js?v=' + dat_met['release'] + '" defer></script>') if pth_pag.startswith('/stream/cam') else ''}{('<script type="module" src="/entropy.js?v=' + dat_met['release'] + '"></script>') if 'data-chance-app=' in txt_pag else ''}</body></html>''')


def crt_hdr(tit_pag, sub_pag, clv_esc="FIELD GUIDE", txt_art=""):
    return f'''<section class="page-hero {'has-art' if txt_art else ''}"><div><a class="back-link" href="/">KAMALA / HOME</a><div class="eyebrow">{clv_esc}</div><h1>{tit_pag}</h1><p>{sub_pag}</p></div>{txt_art}</section>'''


txt_hom = (pth_src / "home.html").read_text()
txt_hom = re.sub(r'<div class="filters".*?</div><div class="cards" id="cards"></div>', '''<div class="filters" role="group" aria-label="Filter techniques by scale"><button class="active" data-filter="all" aria-pressed="true">All scales <sup>12</sup></button><button data-filter="matter" aria-pressed="false">Matter</button><button data-filter="hand" aria-pressed="false">Hand scale</button><button data-filter="human" aria-pressed="false">Human scale</button><button data-filter="earth" aria-pressed="false">Earth</button><button data-filter="solar" aria-pressed="false">Solar system</button></div>''' + crt_lst(), txt_hom, flags=re.S)
txt_hom = txt_hom.replace('All scales <sup>12</sup>', f'All scales <sup>{len(dat_tec)}</sup>')
txt_hom = txt_hom.replace('Explore by technique. Keep the observation,<br>the method and the interpretation in view.', 'Explore by scale, from matter to the solar system.<br>Follow each technique to its own field notes.')
txt_hom = txt_hom.replace('THE FIELD GUIDE / 01', 'THE FIELD GUIDE / FIVE SCALES')
txt_hom = txt_hom.replace('href="#techniques"', 'href="/scales/"')
txt_hom = txt_hom.replace('Explore the techniques', 'Explore the scales')
txt_trd = '<section id="traditions" class="section tradition-overview"><div class="section-head"><div><div class="eyebrow">TRADITIONS & TECHNIQUES</div><h2>Different roots.<br>An open field of inquiry.</h2></div><p>Explore named practices in their own context.<br>Each pathway leads to methods and sources.</p></div>' + crt_trd() + '<div class="tradition-footer"><p>An initial set of pathways, open to further traditions and contributions.</p><a class="text-link" href="/traditions/">Explore the traditions ↗</a></div></section>'
txt_ast = f'''<section class="astrology-feature"><div><div class="eyebrow">CELESTIAL SCALE / ASTROLOGY</div><h2>The sky as<br>a symbolic language.</h2><p>Western astrology and Jyotisha chart methods, with separate field notes for Chinese, Maya, Nahua, Diné and other sky traditions.</p><div class="actions"><a class="button" href="/astrology/">Explore astrology <span>↗</span></a><a class="text-link" href="/gravitacional/">Planetary gravity ↗</a></div><span class="feature-note">CHART METHODS / TRADITIONS / FIELD NOTES</span></div><div class="wheel-wrap">{crt_zod()}</div></section>'''
txt_hom = txt_hom.replace('<section id="techniques"', txt_trd + txt_ast + '<section id="techniques"', 1)
txt_hom = txt_hom.replace('<section id="observatory"', '''<section class="app-links section"><div class="section-head"><div><div class="eyebrow">INDEPENDENT APPLICATIONS</div><h2>Two instruments. Their own space.</h2></div><p>Open the existing applications<br>from their dedicated pages.</p></div><div class="app-grid"><a href="/biorritmos/" class="app-card"><span class="eyebrow">HUMAN SCALE / 01</span><span class="app-symbol">∿</span><h3>Biorhythms <span>↗</span></h3><p>Individual studies and combined views.</p><span class="tag">ORIGINAL APPLICATION</span></a><a href="/gravitacional/" class="app-card"><span class="eyebrow">CELESTIAL SCALE / 02</span><span class="app-symbol">☉</span><h3>Planetary gravity <span>↗</span></h3><p>SolarSimulator: orbital alignment and gravitational variation.</p><span class="tag">ORIGINAL APPLICATION</span></a></div></section><section id="observatory"''', 1)
txt_chm = f'''<section class="shamanic-feature" aria-labelledby="atlas-feature-title"><div class="atlas-mark" aria-hidden="true"><span>{len(dat_chm):02}</span><small>PEOPLES & PATHWAYS</small></div><div><div class="eyebrow">FEATURED ATLAS / SHAMANIC & INDIGENOUS TRADITIONS</div><h2 id="atlas-feature-title">Many peoples.<br>Living knowledge.</h2><p>From Karelia and Sápmi to the Siberian taiga, the steppe and the Amazon. Explore distinct communities through their own names, places and sources.</p><a class="button" href="/traditions/shamanic/">Explore the cultural atlas ↗</a></div><div class="atlas-feature-links"><a href="/traditions/shamanic/#northern-europe">Karelia & Sápmi <span>↗</span></a><a href="/traditions/shamanic/#siberia-inner-asia">Siberia & the steppe <span>↗</span></a><a href="/traditions/shamanic/#americas">The Americas & Amazonia <span>↗</span></a><a href="/traditions/shamanic/#arctic">The Arctic <span>↗</span></a><a href="/traditions/shamanic/#east-asia">East Asia <span>↗</span></a></div></section>'''
txt_cam = '<section class="camera-home"><div class="camera-intro"><div><div class="eyebrow">KAMALA / FOUR CAMERA WINDOWS</div><h1>The observatory.<br>One window at a time.</h1></div><p>Three cameras and a microscope.<br>Choose a screen and follow its signal.</p></div>' + crt_cam() + '<p class="camera-directory-note">Each camera opens on its own page. Feed availability and delay depend on the original source.</p></section>'
crt_pag('/', 'Observatory', '<h1 class="sr-only">kamala.pro — Artes Mánticos</h1><section class="home-stage" aria-label="Kamala observatory"><iframe class="home-control" src="https://go.1-s.es/" title="Kamala observatory" allow="autoplay; fullscreen" referrerpolicy="no-referrer"></iframe></section>' + crt_obs() + txt_chm, 'Mantic arts, cultural traditions and experiments across five scales. Camera streams, the Sun, weather, astrology and planetary alignment at kamala.pro.')
crt_pag('/stream/', 'Camera screens', txt_cam, 'Choose Camera 1, Camera 2, Camera 3 or the microscope. Each opens on its own dedicated screen.')
for dat_itm in dat_cam:
    clv_cam = dat_itm['id']
    txt_cam = f'''<section class="cam-player" data-source="{esc_htm(dat_itm['source'])}"><div class="cam-toolbar"><div class="cam-title"><span class="eyebrow">KAMALA / {clv_cam.upper()}</span><h1>{esc_htm(dat_itm['title'])}</h1></div><nav class="cam-switcher" aria-label="Camera screens">{''.join('<a href="/stream/' + dat_fnt['id'] + '/"' + (' aria-current="page"' if dat_fnt['id'] == clv_cam else '') + '>' + ('Mic 4' if dat_fnt['id'] == 'cam4' else dat_fnt['title'].replace('Camera', 'Cam')) + '</a>' for dat_fnt in dat_cam)}</nav><div class="cam-actions"><button type="button" data-camera-toggle>Stop feed</button><button type="button" data-fullscreen aria-pressed="false">Fullscreen</button><a href="{esc_htm(dat_itm['source'])}" target="_blank" rel="noopener">Source ↗</a></div></div><figure class="cam-frame"><img class="cam-feed" src="{esc_htm(dat_itm['source'])}" alt="{esc_htm(dat_itm['title'])} camera feed" decoding="async" referrerpolicy="no-referrer"><figcaption class="cam-message" role="status" aria-live="polite">Connecting to {esc_htm(dat_itm['title'])}…</figcaption></figure><div class="cam-footnote"><span>ONE CAMERA / ONE SCREEN</span><span>Image timing and availability depend on the source.</span></div></section>'''
    crt_pag('/stream/' + clv_cam + '/', dat_itm['title'], txt_cam, dat_itm['summary'])

txt_pag = crt_hdr('Different roots.<br>Shared curiosity.', 'Explore named traditions through their texts, practices and cultural context. An initial set of pathways for an open, agnostic field guide.', 'TRADITIONS & TECHNIQUES')
txt_pag += txt_chm + '<section class="section"><div class="eyebrow">MORE TRADITIONS & APPROACHES</div>' + crt_trd() + '<div class="detail-note">A shared interest in attention or interpretation does not make traditions equivalent. Each pathway retains its own sources, vocabulary and method.</div></section><section class="section next-page"><div><div class="eyebrow">ANOTHER WAY TO EXPLORE</div><h2>Follow the scale of observation.</h2></div><a class="button" href="/scales/">Explore the scales ↗</a></section>'
crt_pag('/traditions/', 'Traditions & techniques', txt_pag, 'Christian, Sikh, yogic, Buddhist, shamanic, Yijing, runic, tarot and anthroposophical pathways, with their methods and sources.')
for dat_itm in dat_trd:
    if dat_itm['slug'] == 'shamanic':
        continue
    txt_pag = crt_hdr(esc_htm(dat_itm['title']) + '.', esc_htm(dat_itm['summary']), 'TRADITIONS / CULTURAL CONTEXT')
    txt_pag += '<section class="section reading"><div><div class="eyebrow">THE CONTEXT</div><h2>A named point of entry.</h2><p>' + esc_htm(dat_itm['description']) + '</p><div class="practice-tags">' + ''.join('<span>' + esc_htm(txt_val) + '</span>' for txt_val in dat_itm['practices']) + '</div></div><div><div class="eyebrow">A WAY TO STUDY</div><h2>Keep the source in view.</h2><p>' + esc_htm(dat_itm['method']) + '</p>' + crt_fnt(dat_itm['sources']) + '</div></section>'
    txt_pag += '<section class="section tradition-methods"><div class="eyebrow">TECHNIQUES IN THIS PATHWAY</div><h2>Explore the field notes.</h2><div class="cards">' + ''.join(crt_crd(dat_fnt, idx_tec) for idx_tec, dat_fnt in enumerate(dat_tec) if dat_fnt['slug'] in dat_itm['techniques']) + '</div><a class="back-link" href="/traditions/">← ALL TRADITIONS</a></section>'
    crt_pag('/traditions/' + dat_itm['slug'] + '/', dat_itm['title'], txt_pag, dat_itm['summary'])

txt_pag = crt_hdr('Across lands.<br>Across languages.', 'A cultural atlas of shamanic and related Indigenous traditions. Thirteen situated pathways, with community names and public sources.', 'SHAMANIC & INDIGENOUS TRADITIONS / CULTURAL ATLAS')
txt_pag += '<section class="atlas-intro"><p>These are distinct living and historical traditions, not branches of one universal culture. “Shamanism” is a comparative term whose meaning and acceptance vary; the names used by each community guide the individual entries.</p><nav class="region-nav" aria-label="Atlas regions">' + ''.join(f'<a href="#{clv_reg}">{esc_htm(txt_val)}</a>' for clv_reg, txt_val in dat_reg.items()) + '</nav></section>'
for clv_reg, txt_val in dat_reg.items():
    txt_pag += f'<section class="atlas-region" id="{clv_reg}"><div class="eyebrow">PEOPLES, PLACES & PUBLIC SOURCES</div><h2>{esc_htm(txt_val)}</h2>' + crt_chm(clv_reg) + '</section>'
txt_pag += '<section class="section next-page"><div><div class="eyebrow">FOLLOW THE PRACTICE</div><h2>Sound, attention and field notes.</h2></div><div class="actions"><a class="button" href="/techniques/ritual-sound/">Ritual sound ↗</a><a class="text-link" href="/techniques/tracking/">Tracking & signs ↗</a></div></section>'
crt_pag('/traditions/shamanic/', 'Shamanic & Indigenous cultural atlas', txt_pag, 'Diné, Karelian, Sámi, Evenki, Sakha, Buryat, Tuvan, Mongolian, Shipibo-Konibo-Xetebo, Yanomami, Mapuche, Inuit and Jeju pathways.')
for dat_itm in dat_chm:
    txt_pag = crt_hdr(esc_htm(dat_itm['title']) + '.', esc_htm(dat_itm['summary']), esc_htm(dat_reg[dat_itm['region']]) + ' / ' + esc_htm(dat_itm['area']))
    txt_pag += '<section class="section reading"><div><div class="eyebrow">PEOPLE & CONTEXT</div><h2>A place, a name,<br>a living history.</h2><p>' + esc_htm(dat_itm['description']) + '</p><div class="practice-tags">' + ''.join('<span>' + esc_htm(txt_val) + '</span>' for txt_val in dat_itm['practices']) + '</div></div><div><div class="eyebrow">A WAY TO STUDY</div><h2>Begin with the source.</h2><p>' + esc_htm(dat_itm['method']) + '</p>' + crt_fnt(dat_itm['sources']) + '</div></section>'
    txt_pag += '<section class="section next-page"><div><div class="eyebrow">CONTINUE THE ATLAS</div><h2>Other places.<br>Other vocabularies.</h2></div><a class="button" href="/traditions/shamanic/#' + dat_itm['region'] + '">Return to ' + esc_htm(dat_reg[dat_itm['region']]) + ' ↗</a></section>'
    crt_pag('/traditions/shamanic/' + dat_itm['slug'] + '/', dat_itm['title'], txt_pag, dat_itm['summary'])

crt_pag('/scales/', 'Five scales of observation', crt_hdr('From crystal<br>to cosmos.', 'Five ways to enter the same observatory. Choose the scale of the object being observed.', 'THE FIELD GUIDE / SCALES') + '<section class="section scale-intro">' + crt_esc() + '<p class="quiet-note">Scale is a navigation guide. Several techniques cross these boundaries; each page states its method and context.</p></section><section class="section"><div class="eyebrow">ALL TECHNIQUES</div><h2>A closer look.</h2><a class="text-link" href="/arts/">Arts & variants ↗</a>' + crt_lst() + '</section>', 'Navigate techniques by the scale of observation, from matter and human practices to Earth and the solar system.')
crt_v2(crt_pag, crt_hdr, crt_fnt, dat_gls, dat_tec, dat_esc, pth_src, pth_dst)

for clv_esc, dat_itm in dat_esc.items():
    txt_ext = '<aside class="related"><span class="eyebrow">COMPLETE LEXICON</span><h3>Names & connections</h3><p>Definitions, synonyms and cultural context for every retained art.</p><a class="text-link" href="/arts/">Explore the list ↗</a></aside>'
    if clv_esc == 'human':
        txt_ext += '<aside class="related"><span class="eyebrow">INDEPENDENT APPLICATION</span><h3>Biorhythms</h3><p>Open the original individual and combined study tools on their own page.</p><a class="text-link" href="/biorritmos/">Open biorhythms ↗</a></aside>'
    if clv_esc == 'solar':
        txt_ext += '<aside class="related"><span class="eyebrow">EXPLORE FURTHER</span><h3>Astrology & planetary gravity</h3><p>Two dedicated spaces for symbolic interpretation and the existing gravitational simulator.</p><div class="actions"><a class="button" href="/astrology/">Astrology ↗</a><a class="text-link" href="/gravitacional/">Planetary gravity ↗</a></div></aside>'
    if clv_esc in ('hand', 'earth'):
        txt_ext += '<aside class="scale-experiments related"><span class="eyebrow">TRY THE FIELD NOTES</span><h3>Experiments within the articles.</h3><div class="actions">' + ''.join('<a class="text-link" href="/techniques/' + dat_fnt['slug'] + '/#experiment">' + esc_htm(dat_fnt['title']) + ' ↗</a>' for dat_fnt in dat_tec if dat_fnt['scale'] == clv_esc and dat_fnt['slug'] in ('dice', 'coins', 'cards', 'runes', 'yijing', 'entropy-streams')) + '</div></aside>'
    crt_pag(f'/scales/{clv_esc}/', dat_itm[1], crt_hdr(dat_itm[1] + '.', dat_itm[3], dat_itm[0] + ' / ' + dat_itm[2]) + f'<section class="section scale-intro"><p class="scale-explainer">{dat_itm[4]}</p>{crt_lst(clv_esc)}{txt_ext}<a class="back-link" href="/scales/">← ALL FIVE SCALES</a></section>', dat_itm[3])

for idx_tec, dat_itm in enumerate(dat_tec):
    clv_esc = dat_itm['scale']
    txt_art = f'<div class="specimen" aria-hidden="true"><span>{dat_itm["symbol"]}</span><small>FIELD NOTE / {idx_tec + 1:02}</small></div>'
    txt_pag = crt_hdr(esc_htm(dat_itm['title']) + '.', esc_htm(dat_itm['summary']), dat_esc[clv_esc][1].upper() + ' / TECHNIQUE', txt_art)
    txt_pag += f'''<section class="section reading"><div><div class="eyebrow">THE OBSERVATION</div><h2>Look closely.</h2><p>{esc_htm(dat_itm['description'])}</p><a class="text-link" href="/scales/{clv_esc}/">Explore {dat_esc[clv_esc][1].lower()} ↗</a></div><div><div class="eyebrow">A STARTING PROTOCOL</div><h2>Make a record.</h2><p>{esc_htm(dat_itm['method'])}</p><div class="detail-note">Keep the original observation, the method and any interpretation together in the record.</div></div></section>'''
    if dat_itm.get('sources'):
        txt_pag += '<section class="section technique-context">' + crt_fnt(dat_itm['sources']) + '</section>'
    if dat_itm.get('related'):
        txt_pag += '<section class="section technique-context"><a class="text-link" href="/arts/">Arts & variants ↗</a><div class="eyebrow">RELATED FIELD NOTES</div><div class="actions">' + ''.join(f'''<a class="text-link" href="/techniques/{dat_fnt['slug']}/">{esc_htm(dat_fnt['title'])} ↗</a>''' for dat_fnt in dat_tec if dat_fnt['slug'] in dat_itm['related']) + '</div></section>'
    if dat_itm.get('stream'):
        txt_pag += '<section class="section technique-context"><div class="eyebrow">OBSERVATORY VIEW / INSTALLATION IN PROGRESS</div><p>Pendulum setups are being installed. The framing and visible instruments may change.</p><a class="text-link" href="/stream/' + dat_itm['stream'] + '/">Open the camera screen ↗</a></section>'
    txt_ext = ''.join(f'''<a class="text-link" href="/traditions/{dat_fnt['slug']}/">{esc_htm(dat_fnt['title'])} ↗</a>''' for dat_fnt in dat_trd if dat_itm['slug'] in dat_fnt['techniques'])
    if txt_ext:
        txt_pag += '<section class="section technique-context"><div class="eyebrow">TRADITIONS & CONTEXT</div><div class="actions">' + txt_ext + '</div></section>'
    if dat_itm['slug'] in ('coins', 'dice', 'cards', 'runes', 'yijing', 'entropy-streams'):
        txt_pag += crt_prb('entropy' if dat_itm['slug'] == 'entropy-streams' else dat_itm['slug'])
    if dat_itm['slug'] == 'entropy-streams':
        txt_pag += '<section class="section technique-context"><div class="eyebrow">LOCAL GENERATORS</div><h2>One source, many possibilities.</h2><p>Explore SSH pairs, hexadecimal and other secret encodings, UUIDs, TOTP setups, QR codes and ASCII seed art using the shared camera and browser source.</p><a class="button" href="/apps/entropy/">Open the local laboratory ↗</a></section>'
    if dat_itm['slug'] == 'horoscope':
        txt_pag += '<section class="section next-page"><div><div class="eyebrow">ASTROLOGY</div><h2>A wider celestial context.</h2></div><a class="button" href="/astrology/">Enter astrology ↗</a></section>'
    if dat_itm['slug'] in ('candle-gazing', 'crystal-gazing'):
        clv_cnp = 'candle' if dat_itm['slug'] == 'candle-gazing' else 'crystal'
        txt_pag += '<section class="section technique-context"><div class="eyebrow">CONTEMPLATION ROOM</div><h2>Hold the attention.</h2><p>A digital ' + ('candle' if clv_cnp == 'candle' else 'crystal sphere') + ' shaped by enp6s0 traffic and logged firewall notices from Excalibur.</p><a class="button" href="/apps/' + clv_cnp + '/">Open the room ↗</a></section>'
    txt_pag += crt_pot_lnk(dat_itm['slug'])
    crt_pag('/techniques/' + dat_itm['slug'] + '/', dat_itm['title'], txt_pag, dat_itm['summary'])

txt_pag = crt_hdr('Reading<br>the sky.', 'A dedicated space for astrology: charts, cycles, symbols and the traditions that give them meaning.', 'CELESTIAL SCALE / ASTROLOGY', '<div class="wheel-wrap">' + crt_zod() + '</div>')
txt_pag = txt_pag.replace('</p>', '</p><div class="actions"><a class="button" href="#chart">Prepare a chart ↘</a><a class="text-link" href="/glossary/">Names & definitions ↗</a></div>', 1)
txt_pag += '''<section class="section astrology-paths"><div class="section-head"><div><div class="eyebrow">THREE POINTS OF ENTRY</div><h2>Context before interpretation.</h2></div><p>A symbolic reading and a physical calculation<br>answer different questions.</p></div><div class="path-grid"><a href="/techniques/horoscope/"><span class="eyebrow">01 / SYMBOLIC READING</span><h3>Horoscope ↗</h3><p>State the tradition, zodiac system and assumptions behind a reading.</p></a><a href="/techniques/planets/"><span class="eyebrow">02 / OBSERVATION</span><h3>Planets ↗</h3><p>Record positions and visibility with a source, date, location and time zone.</p></a><a href="/gravitacional/"><span class="eyebrow">03 / PHYSICAL MODEL</span><h3>Planetary gravity ↗</h3><p>Open the existing SolarSimulator as an independent application.</p></a></div></section>'''
txt_pag += (pth_src / 'astroapp.html').read_text()
txt_pag += (pth_src / 'astrology-traditions.html').read_text()
txt_pag += '''<section class="section reading"><div><div class="eyebrow">A PLURAL APPROACH</div><h2>Traditions in context.</h2><p>Compare sources, language and practice while retaining the distinctions between traditions. No religious affiliation is required to explore the material.</p></div><div><div class="eyebrow">FIELD NOTES</div><h2>Room for doubt.</h2><p>Record the chart or observation before its interpretation. Astrology is approached here as a cultural and symbolic practice, rather than an established scientific forecasting method.</p><a class="text-link" href="/approach/">Read the approach ↗</a></div></section>'''
crt_pag('/astrology/', 'Astrology', txt_pag, 'Western and Jyotisha chart methods, with separate field notes for Chinese, Maya, Nahua, Diné, Mesopotamian and modern calendrical traditions.')

txt_pag = (pth_src / 'api.html').read_text()
txt_pag += '<section class="section"><div class="eyebrow">CONTEMPLATION ROOMS</div><h2>Choose the signal and light.</h2><p>The candle and crystal use <code>src_mode=live</code> for same-origin Excalibur telemetry or <code>src_mode=demo</code> for explicitly simulated signals. <code>int_lvl</code> sets initial glow between 0.4 and 1.4.</p><p><a class="text-link" href="/apps/candle/?src_mode=demo&amp;int_lvl=0.85">Candle demonstration ↗</a> · <a class="text-link" href="/apps/crystal/?src_mode=live&amp;int_lvl=0.85">Crystal with the live feed ↗</a></p><p>The rooms do not change firewall rules or generate cryptographic material.</p></section>'
crt_pag('/api/', 'URL & API guide', txt_pag, 'GET query names and definitions for configuring Kamala chance applications and the local entropy laboratory without triggering a draw or generating a key.')

for pth_pag, tit_pag, sub_pag, clv_esc, url_app in [
    ('/biorritmos/', 'Biorhythms', 'The existing biorhythm tools, with individual and combined studies in their own space.', 'HUMAN SCALE / INDEPENDENT APPLICATION', 'https://kamala.pro/bior/bior.php'),
    ('/gravitacional/', 'Planetary gravity', 'The original SolarSimulator: explore date, orbital alignment and the gravitational calculation in a dedicated workspace.', 'CELESTIAL SCALE / INDEPENDENT APPLICATION', 'https://www.kamala.pro:443/bior/SolarSimulator/'),
]:
    txt_tabs = ''
    txt_note = 'This is the existing external application. Its interface, calculations and controls come from the original service.'
    if pth_pag == '/biorritmos/':
        txt_tabs = ''
        txt_note += ' The individual generator and compositor are shown together. Generate a chart, then double-click the copied filename in the compositor.'
        txt_note += ' Biorhythm curves are presented as an exploratory model, not a validated health assessment.'
    else:
        txt_note += ' The numerical model has not been independently validated in this update.'
    txt_pag = crt_hdr(esc_htm(tit_pag) + '.', sub_pag, clv_esc)
    if pth_pag == '/biorritmos/':
        txt_pag += f'''<section class="app-workspace bior-workspace"><div class="workspace-bar"><span class="eyebrow">GENERATOR + COMPOSITOR</span><a class="text-link" href="https://kamala.pro/bior/bior.php" target="_blank" rel="noopener">Open original applications ↗</a></div><div class="bior-tools-grid"><article class="bior-tool"><div class="bior-tool-heading"><span class="eyebrow">01 / GENERATOR</span><h2>Individual study</h2></div><iframe src="https://kamala.pro/bior/bior.php" title="Biorhythm individual chart generator" referrerpolicy="no-referrer" loading="lazy"></iframe></article><article class="bior-tool"><div class="bior-tool-heading"><span class="eyebrow">02 / COMPOSITOR</span><h2>Combined studies</h2></div><iframe src="https://kamala.pro/bior/compose.php" title="Biorhythm chart compositor" referrerpolicy="no-referrer" loading="lazy"></iframe></article></div><p class="quiet-note">{txt_note} If an embedded view is unavailable, open its original application.</p></section>'''
    else:
        txt_pag += f'''<section class="app-workspace"><div class="workspace-bar">{txt_tabs}<a id="open-app" class="text-link" href="{url_app}" target="_blank" rel="noopener">Open original application ↗</a></div><iframe id="original-app" src="{url_app}" title="{tit_pag} original application" referrerpolicy="no-referrer" loading="lazy"></iframe><p class="quiet-note">{txt_note} If the embedded view is unavailable, use “Open original application”.</p></section>'''
    txt_pag += '<section class="section next-page"><div><div class="eyebrow">CONTINUE EXPLORING</div><h2>Return to the field guide.</h2></div><a class="button" href="/scales/">Explore the scales ↗</a></section>'
    crt_pag(pth_pag, tit_pag, txt_pag, sub_pag)

txt_obs = re.search(r'<section id="observatory".*?</section>', txt_hom, re.S).group()
crt_pag('/observatory/', 'Observatory', crt_hdr('The world,<br>in observation.', 'Cameras, solar imagery, weather and the planetary view.', 'TERRESTRIAL SCALE / OBSERVATORY') + crt_obs() + txt_obs + '<section class="section">' + crt_esc() + '</section>', 'Camera streams, solar sequences, weather maps, planetary alignment and time services.')
txt_ctc = re.search(r'<section id="contact".*?</section>', txt_hom, re.S).group()
crt_pag('/contact/', 'Contact', txt_ctc.replace('<h2>', '<h1>', 1).replace('</h2>', '</h1>', 1), 'One contact point for questions, collaboration and academic inquiries.')
txt_apr = re.search(r'<section id="approach".*?</section>', txt_hom, re.S).group()
crt_pag('/approach/', 'Our approach', txt_apr.replace('<h2>', '<h1>', 1).replace('</h2>', '</h1>', 1) + '<section class="section">' + crt_esc() + '</section>', 'Observation, measurement, cultural context and an open approach to interpretation.')
(pth_dst / 'favicon.svg').write_text('<!-- Timestamp: 2026-10-27 | Version: 1.3.0 | Author & Credits: https://www.alawise.es/1-s -->\n' + txt_est)


# Article experiments and independent workspaces share one source of markup.
txt_tabs = '<nav class="chance-tabs" aria-label="Chance applications">' + ''.join('<a href="/apps/' + clv_esc + '/">' + dat_itm[0] + '</a>' for clv_esc, dat_itm in dat_prb.items()) + '</nav>'
crt_pag('/apps/', 'Chance applications', crt_hdr('A moment.<br>A possibility.', 'Decks, layouts, coins, I Ching and runes, with a shared camera and browser source.', 'KAMALA / CHANCE APPLICATIONS') + '<section class="section"><aside class="related"><div class="eyebrow">LOCAL GENERATORS</div><h2>One source, many possibilities.</h2><p>Explore SSH pairs, hexadecimal and other secret encodings, UUIDs, TOTP setups, QR codes and ASCII seed art.</p><a class="button" href="/apps/entropy/">Open the entropy laboratory ↗</a><a class="text-link" href="/api/">Read the GET URL definitions ↗</a></aside>' + txt_tabs + '<div class="path-grid">' + ''.join('<a href="/techniques/' + dat_itm[6] + '/#experiment"><h2>' + dat_itm[0] + ' ↗</h2><p>' + dat_itm[1] + '</p><span class="tag">READ & EXPERIMENT</span></a>' for dat_itm in dat_prb.values()) + '</div><p class="quiet-note">Each experiment is also available in its field note under Scales. Each request can sample one camera, mixed with server and browser randomness. The interface reports the source actually used.</p></section>', 'Dice, cards, coins, I Ching, runes and entropy experiments, integrated with their field notes under Scales.')
for clv_esc, dat_itm in dat_prb.items():
    if clv_esc == 'entropy':
        crt_pag('/apps/entropy/', 'Entropy lab — generators & possibilities', (pth_src / 'lab/lab.html').read_text(), 'SSH public/private pairs, hexadecimal, Base64, Base32, UUIDs, secrets, TOTP, QR and random seed ASCII art. Local tools sharing the camera and browser source, with a portable HTML download.')
        continue
    txt_pag = crt_hdr(dat_itm[0] + '.', dat_itm[1], 'KAMALA / CHANCE APPLICATIONS')
    txt_pag += '<div class="section chance-links">' + txt_tabs + '<a class="text-link" href="/techniques/' + dat_itm[6] + '/#experiment">Read the article & experiment ↗</a></div>' + crt_prb(clv_esc)
    txt_pag += crt_pot_lnk(clv_esc)
    crt_pag('/apps/' + clv_esc + '/', dat_itm[0], txt_pag, dat_itm[1])

crt_cnp(crt_pag, crt_hdr)

# The full illustrated deck is a browsable gallery as well as a draw source.
dat_tar = json.loads((pth_src / 'tarot.json').read_text())['cards']
txt_pag = crt_hdr('Tarot de Marseille.<br>Drawn for Kamala.', 'Seventy-eight original card faces inspired by the Marseille tradition. Open any card for a closer look.', 'KAMALA / THE ILLUSTRATED DECK')
txt_pag += '<section class="section tarot-intro"><p>The 22 major arcana and 16 court cards have individual woodcut-inspired illustrations. The 40 numbered minor cards use ornamental suit compositions with exact pip counts. Justice remains VIII and Strength XI.</p><a class="button" href="/apps/cards/?api_ver=1&amp;api_act=configure&amp;vw_mod=cards&amp;deck_typ=marseille">Use this deck in a draw ↗</a><nav class="tarot-index" aria-label="Deck sections">'
for clv_esc, txt_val in [('major-arcana', 'Major arcana'), ('deniers', 'Deniers'), ('coupes', 'Coupes'), ('epees', 'Epees'), ('batons', 'Batons')]:
    txt_pag += '<a href="#' + clv_esc + '">' + txt_val + '</a>'
txt_pag += '</nav></section><div data-tarot-gallery>'
for clv_esc, txt_val in [('major-arcana', 'Major arcana'), ('deniers', 'Deniers'), ('coupes', 'Coupes'), ('epees', 'Epees'), ('batons', 'Batons')]:
    txt_pag += '<section class="section tarot-section" id="' + clv_esc + '"><div class="eyebrow">KAMALA / TAROT DE MARSEILLE</div><h2>' + txt_val + '</h2><div class="tarot-gallery">'
    for dat_itm in dat_tar:
        if dat_itm['suit'] != txt_val:
            continue
        if not (pth_src / dat_itm['art'].lstrip('/')).is_file():
            raise ValueError('Missing tarot artwork: ' + dat_itm['art'])
        url_art = esc_htm(dat_itm['art']) + '?v=' + dat_met['release']
        txt_pag += '<a class="tarot-catalogue-card" href="' + url_art + '" data-tarot-open data-card-name="' + esc_htm(dat_itm['name']) + '" data-card-id="' + esc_htm(dat_itm['id']) + '" aria-label="View larger image: ' + esc_htm(dat_itm['name']) + '"><img src="' + url_art + '" alt="' + esc_htm(dat_itm['name']) + '" width="300" height="450" loading="lazy" decoding="async"><small>' + esc_htm(dat_itm['rank']) + '</small><strong>' + esc_htm(dat_itm['name']) + '</strong></a>'
    txt_pag += '</div></section>'
txt_pag += '</div>'
crt_pag('/apps/cards/tarot/', 'Tarot de Marseille — 78 illustrated cards', txt_pag, 'The complete original Kamala Marseille-inspired deck: 22 major arcana, 16 court illustrations and 40 ornamental pip cards. Open every image and use the deck in matrix or cross spreads.')

dat_pal = json.loads((pth_src / 'playing-cards.json').read_text())['cards']
txt_pag = crt_hdr('Three decks.<br>Every card.', 'Original Kamala artwork for Spanish cards, American playing cards and Tarot de Marseille.', 'KAMALA / CARD LIBRARY')
txt_pag += '<section class="section"><div class="path-grid">'
for clv_bar, tit_pag, txt_note in [
    ('spanish', 'Spanish cards', '48 original faces. Choose 40 or 48 cards in the draw.'),
    ('american', 'American playing cards', '52 original faces, reversible court illustrations and classic suit layouts.'),
    ('tarot', 'Tarot de Marseille', '78 original faces, including 22 major arcana and ornamental minor suits.')
]:
    txt_pag += '<a href="/apps/cards/' + clv_bar + '/"><h2>' + tit_pag + ' ↗</h2><p>' + txt_note + '</p><span class="tag">COMPLETE DECK</span></a>'
txt_pag += '</div><p class="quiet-note">Original Kamala designs inspired by their respective traditions. Names, ranks and suit identities remain explicit; the collections are not historical facsimiles.</p><a class="button" href="/apps/cards/">Make a draw ↗</a></section>'
crt_pag('/apps/cards/decks/', 'Card library — all three illustrated decks', txt_pag, 'Browse every original Kamala card: Spanish 40/48, American 52 and Marseille tarot 78.')
for clv_bar, tit_pag, dat_suit in [
    ('spanish', 'Spanish cards', ['Oros','Copas','Espadas','Bastos']),
    ('american', 'American playing cards', ['Spades','Hearts','Diamonds','Clubs'])
]:
    txt_pag = crt_hdr(tit_pag + '.', 'Every suit. Every rank. Original court illustrations and exact ornamental pip compositions.', 'KAMALA / THE ILLUSTRATED DECKS')
    txt_pag += '<section class="section tarot-intro"><a class="button" href="/apps/cards/?api_ver=1&amp;api_act=configure&amp;vw_mod=cards&amp;deck_typ=' + clv_bar + '">Use this deck in a draw ↗</a><a class="text-link" href="/apps/cards/decks/">All three decks ↗</a><nav class="tarot-index" aria-label="Deck sections">'
    for txt_val in dat_suit:
        txt_pag += '<a href="#' + txt_val.lower() + '">' + txt_val + '</a>'
    txt_pag += '</nav></section><div data-tarot-gallery>'
    for txt_val in dat_suit:
        txt_pag += '<section class="section tarot-section" id="' + txt_val.lower() + '"><div class="eyebrow">KAMALA / ' + tit_pag.upper() + '</div><h2>' + txt_val + '</h2><div class="tarot-gallery">'
        for dat_itm in dat_pal:
            if dat_itm['deck'] != clv_bar or dat_itm['suit'] != txt_val:
                continue
            if not (pth_src / dat_itm['art'].lstrip('/')).is_file():
                raise ValueError('Missing playing-card artwork: ' + dat_itm['art'])
            url_art = esc_htm(dat_itm['art']) + '?v=' + dat_met['release']
            txt_pag += '<a class="tarot-catalogue-card" href="' + url_art + '" data-tarot-open data-card-name="' + esc_htm(dat_itm['name']) + '" data-card-id="' + esc_htm(dat_itm['id']) + '" aria-label="View larger image: ' + esc_htm(dat_itm['name']) + '"><img src="' + url_art + '" alt="' + esc_htm(dat_itm['name']) + '" width="300" height="450" loading="lazy" decoding="async"><small>' + esc_htm(dat_itm['rank']) + '</small><strong>' + esc_htm(dat_itm['name']) + '</strong></a>'
        txt_pag += '</div></section>'
    txt_pag += '</div>'
    crt_pag('/apps/cards/' + clv_bar + '/', tit_pag + ' — complete illustrated deck', txt_pag, 'A complete original Kamala ' + tit_pag.lower() + ' deck, with individual court illustrations and exact pip counts.')

# Shipping shell fragments lets Excalibur update contact without replacing its form.
pth_fil = sys_rad / 'deploy/site-update/fragments'
pth_fil.mkdir(parents=True, exist_ok=True)
txt_val = '<!-- Timestamp: 2026-11-02 | Version: 2.1.1 | Author & Credits: https://www.alawise.es/1-s -->'
txt_met = crt_met('/contact/', 'Contact', 'One contact point for questions, collaboration and academic inquiries.').replace('<!-- KAMALA META START -->', '<!-- KAMALA META START -->\n' + txt_val)
(pth_fil / 'contact-meta.html').write_text(txt_met)
(pth_fil / 'contact-header.html').write_text(re.search(r'<header.*?</header>', crt_nav('/contact/'), re.S).group().replace('>', '>' + txt_val, 1))
(pth_fil / 'contact-footer.html').write_text(txt_ftr.replace('<footer>', '<footer>' + txt_val))
(pth_dst / 'entropy-core.mjs').write_text((pth_src / 'entropy-core.mjs').read_text())
(pth_dst / 'chance-core.mjs').write_text((pth_src / 'chance-core.mjs').read_text())
(pth_dst / 'entropy.js').write_text((pth_src / 'chance.mjs').read_text())
(pth_dst / 'tarot-viewer.js').write_text((pth_src / 'tarot-viewer.js').read_text())
for pth_fil in ('astroapp-core.mjs', 'astroapp.mjs', 'astroapp-frame.mjs', 'astroapp-image.mjs', 'astroapp.css', 'astroapp-head.js', 'glossary.js', 'potpourri.js', 'v2.css', 'contemplation-core.mjs', 'contemplation.mjs', 'contemplation.css', 'dice-core.mjs'):
    (pth_dst / pth_fil.replace('astroapp.mjs', 'astroapp.js').replace('astroapp-frame.mjs', 'astroapp-frame.js')).write_text((pth_src / pth_fil).read_text())
print(f'Built {sum(pth_fil.parent != pth_dst / "downloads" for pth_fil in pth_dst.rglob("index.html"))} pages with shared metadata and article experiments.')
