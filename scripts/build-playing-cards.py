#!/usr/bin/env python3
# Timestamp: 2026-11-01
# Version: 2.1.0
# Author & Credits: https://www.alawise.es/1-s
"""Draw original suit engravings with exact, inspectable pip counts."""

import html
import json
import math
from pathlib import Path

sys_rad = Path(__file__).resolve().parents[1]
dat_pos = {
    1: [(150, 225)], 2: [(150, 113), (150, 337)],
    3: [(150, 94), (150, 225), (150, 356)],
    4: [(92, 110), (208, 110), (92, 340), (208, 340)],
    5: [(92, 100), (208, 100), (150, 225), (92, 350), (208, 350)],
    6: [(x, y) for y in (100, 225, 350) for x in (92, 208)],
    7: [(x, y) for y in (94, 225, 356) for x in (87, 213)] + [(150, 157)],
    8: [(x, y) for y in (94, 225, 356) for x in (87, 213)] + [(150, 157), (150, 293)],
    9: [(x, y) for y in (94, 181, 269, 356) for x in (88, 212)] + [(150, 225)],
    10: [(x, y) for y in (88, 179, 271, 362) for x in (88, 212)] + [(150, 134), (150, 316)]
}


def crt_oro():
    txt_pag = '<circle r="34" fill="#d9a636"/><circle r="31" fill="none" stroke-width=".7"/>'
    for sys_idx in range(28):
        ang_rad = 2 * math.pi * sys_idx / 28
        txt_pag += f'<circle cx="{math.sin(ang_rad) * 28:.3f}" cy="{math.cos(ang_rad) * 28:.3f}" r=".85" fill="#292321" stroke="none"/>'
    txt_pag += '<circle r="25.5" fill="none" stroke-width=".7"/>'
    for sys_idx in range(12):
        ang_rad = 2 * math.pi * sys_idx / 12
        cnt_x, cnt_y = math.sin(ang_rad)*21, math.cos(ang_rad)*21
        txt_pag += f'<ellipse cx="{cnt_x:.3f}" cy="{cnt_y:.3f}" rx="2.2" ry="4.8" transform="rotate({-30*sys_idx} {cnt_x:.3f} {cnt_y:.3f})" fill="#f7eedb" stroke-width=".65"/>'
    return txt_pag + '<circle r="13" fill="#244b69"/><path d="M0-11C3-5 8-8 9-3C10 2 4 3 6 8C2 7 1 10 0 11C-1 10-2 7-6 8C-4 3-10 2-9-3C-8-8-3-5 0-11Z" fill="#d9a636" stroke-width=".8"/><circle r="3.5" fill="#ad332b" stroke-width=".7"/>'


def crt_cop():
    return '''<path d="M-23-24C-43-37-43 0-20-1M23-24C43-37 43 0 20-1" fill="none" stroke="#d9a636" stroke-width="6"/>
<path d="M-23-24C-43-37-43 0-20-1M23-24C43-37 43 0 20-1" fill="none" stroke-width="1.15"/>
<path d="M-29-30Q-26 2-6 10L-5 23L-17 30L-23 33L-23 39H23V33L17 30L5 23L6 10Q26 2 29-30Z" fill="#d9a636"/>
<ellipse cy="-30" rx="29" ry="8" fill="#d9a636"/><ellipse cy="-30" rx="24" ry="4" fill="#ad332b" stroke-width=".8"/>
<path d="M-23-18Q0-5 23-18L20-6Q0 4-20-6Z" fill="#244b69" stroke-width=".85"/>
<path d="M-18-15Q0-6 18-15M-13-1Q0 9 13-1M-21 34H21M-13 30H13M-5 14H5M-5 20H5" fill="none" stroke-width=".8"/>
<path d="M0-17L4-11L0-7L-4-11Z" fill="#ad332b" stroke="#d9a636" stroke-width=".7"/>
<path d="M-15-26L-12-20M-5-25L-4-16M5-25L4-16M15-26L12-20M-8 5L-6 9M8 5L6 9" fill="none" stroke-width=".65"/>
<path d="M-18 36H18M-10 32H10" fill="none" stroke="#f7eedb" stroke-width=".6"/>'''


def crt_esp():
    return '''<path d="M0-56L9-38L5 17H-5L-9-38Z" fill="#c4ccd0"/>
<path d="M0-50V17M0-42L6-35M0-31L6-25M0-20L5-15M0-9L5-4" fill="none" stroke-width=".65"/>
<path d="M-25 17C-25 8-17 8-15 14Q0 20 15 14C17 8 25 8 25 17L23 24Q0 18-23 24Z" fill="#d9a636"/>
<path d="M-5 21H5L6 40H-6Z" fill="#ad332b"/>
<path d="M-5 24L5 28M-5 29L5 33M-5 34L5 38" fill="none" stroke="#d9a636" stroke-width="1.5"/>
<circle cy="46" r="8" fill="#d9a636"/><circle cy="46" r="4" fill="#244b69" stroke-width=".7"/>
<path d="M-20 18Q0 13 20 18M-6 45H6M0 40V51" fill="none" stroke-width=".7"/>'''


def crt_bas():
    return '''<path d="M-7 49L-9 30L-7 4L-12-17L-9-42L-5-51L8-48L10-32L7-15L11 10L7 31L8 49Z" fill="#a97735"/>
<path d="M-3-47L0-32L-3-12L2 10L-2 31L1 46M5-41L2-24L6-9L3 10L5 25M-7-30L6-27M-8 7L7 10M-5 35L5 37" fill="none" stroke-width=".8"/>
<path d="M-9-21C-24-39-33-23-16-17L-7-14M8 0C28-18 36 5 18 8L9 12M-7 24C-28 12-31 33-15 33L-7 30" fill="#3c7151" stroke-width="1"/>
<path d="M-25-26L-9-17M26 0L10 9M-25 26L-8 28" fill="none" stroke="#d9a636" stroke-width=".8"/>
<path d="M-7-39L7-36M-5 44L6 44" fill="none" stroke="#f7eedb" stroke-width="1"/>'''


def crt_sig(clv_pal):
    dat_sig = {
        'Spades': '<path d="M0-30C-8-17-31-8-28 9C-25 27-7 26-2 13L-7 32H7L2 13C7 26 25 27 28 9C31-8 8-17 0-30Z"/>',
        'Hearts': '<path d="M0-17C-12-35-35-19-27-1C-20 12-6 20 0 30C6 20 20 12 27-1C35-19 12-35 0-17Z"/>',
        'Diamonds': '<path d="M0-34L24 0L0 34L-24 0Z"/>',
        'Clubs': '<circle cy="-17" r="14"/><circle cx="-17" cy="6" r="14"/><circle cx="17" cy="6" r="14"/><path d="M-4-6H4V12L9 32H-9L-4 12Z"/>'
    }
    return dat_sig[clv_pal]


def crt_fol(cnt_x, cnt_y, ang_deg=0, val_esc=1):
    return f'''<g transform="translate({cnt_x} {cnt_y}) rotate({ang_deg}) scale({val_esc})" stroke="#292321" stroke-width=".9">
<path d="M0 0C-28-24-17-43-4-25C-4-45 15-49 14-28C29-36 37-16 14-14C34-1 26 14 7 1C3 17-12 18-9 5C-24 18-34 3-16-4C-37-6-31-24-12-15Z" fill="#3c7151"/>
<path d="M-18-19L-1-2M7-30L1-4M20-18L4-3M20 4L5-1M-17 7L-2 1" fill="none" stroke="#f7eedb" stroke-width=".7"/>
<path d="M0 1C-13-10-9-20 0-14C9-20 13-10 0 1Z" fill="#ad332b"/><circle cy="-9" r="2" fill="#d9a636"/></g>'''


def crt_mar(clv_est='spanish'):
    if clv_est == 'american':
        return '''<rect x="18" y="18" width="264" height="414" rx="11" fill="none" stroke="#b5a07a" stroke-width=".65"/>
<path d="M30 68V42Q30 30 42 30H68M232 30H258Q270 30 270 42V68M270 382V408Q270 420 258 420H232M68 420H42Q30 420 30 408V382" fill="none" stroke="#244b69" stroke-width="1"/>
<path d="M39 56V43H56M244 43H257V56M257 394V407H244M56 407H43V394" fill="none" stroke="#b5a07a" stroke-width=".6"/>'''
    return '''<rect x="17" y="17" width="266" height="416" rx="3" fill="none" stroke="#292321" stroke-width="1"/>
<rect x="21" y="21" width="258" height="408" rx="2" fill="none" stroke="#bc953c" stroke-width=".7"/>
<path d="M38 30H262M38 420H262M30 42V408M270 42V408" fill="none" stroke="#292321" stroke-width=".4"/>
<path d="M38 34C48 35 50 31 54 29C50 42 38 42 38 34M262 34C252 35 250 31 246 29C250 42 262 42 262 34M38 416C48 415 50 419 54 421C50 408 38 408 38 416M262 416C252 415 250 419 246 421C250 408 262 408 262 416" fill="#d9a636" stroke="#292321" stroke-width=".6"/>'''


def crt_svg(txt_tit, cnt_car, txt_cor, txt_def, clv_est='spanish'):
    txt_pap = '#fffdf7' if clv_est == 'american' else '#f7eedb'
    return f'''<!-- Timestamp: 2026-11-01 | Version: 2.1.0 | Author & Credits: https://www.alawise.es/1-s -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 450" role="img" aria-labelledby="title" data-pip-count="{cnt_car}" data-deck-style="{clv_est}">
<title id="title">{html.escape(txt_tit)}</title><defs>{txt_def}<pattern id="paper-grain" width="17" height="23" patternUnits="userSpaceOnUse"><path d="M3 4L5 4M12 16L13 16M7 21L8 21" stroke="#756047" stroke-width=".4" opacity=".13"/></pattern></defs>
<rect width="300" height="450" rx="6" fill="{txt_pap}"/><rect width="300" height="450" fill="url(#paper-grain)"/>
{crt_mar(clv_est)}{txt_cor}</svg>
'''


def crt_es(dat_itm, clv_est='spanish'):
    cnt_car = dat_itm['count']
    txt_pip = {'Oros': crt_oro, 'Copas': crt_cop, 'Espadas': crt_esp, 'Bastos': crt_bas}[dat_itm['suit']]()
    txt_def = '<g id="pip" stroke="#292321" stroke-width="1.35" stroke-linejoin="round" stroke-linecap="round">' + txt_pip + '</g>'
    dat_esc = {1: 2.25, 2: 1.32, 3: 1.04, 4: 1.08, 5: 1, 6: .94, 7: .8, 8: .78, 9: .7, 10: .66}
    txt_pag = ''
    if cnt_car == 1:
        txt_pag += '<g stroke="#bc953c" stroke-width=".8" fill="none"><ellipse cx="150" cy="225" rx="92" ry="147"/><ellipse cx="150" cy="225" rx="88" ry="143"/><path d="M150 64V47M150 386V403M42 225H32M258 225H268M83 99L74 88M217 99L226 88M83 351L74 362M217 351L226 362"/></g>'
        txt_pag += crt_fol(150, 80, 0, .64) + crt_fol(150, 370, 180, .64)
    else:
        txt_pag += '<g stroke="#3c7151" fill="none" stroke-width="1"><path d="M49 371C42 285 48 160 46 79M251 371C258 285 252 160 254 79"/></g>'
        for cnt_y in (92, 178, 273, 358):
            txt_pag += crt_fol(46, cnt_y, -25, .26) + crt_fol(254, 450-cnt_y, 155, .26)
    dat_esp = dict(dat_pos)
    dat_esp[7] = [(x, y) for y in (94, 225, 356) for x in (87, 213)] + [(150, 225)]
    dat_esp[8] = [(x, y) for y in (90, 180, 270, 360) for x in (88, 212)]
    dat_esp[9] = [(x, y) for y in (100, 225, 350) for x in (78, 150, 222)]
    for cnt_x, cnt_y in dat_esp[cnt_car]:
        # Spanish suit symbols stay upright, as on traditional Iberian decks.
        txt_pag += f'<use data-pip="1" href="#pip" transform="translate({cnt_x} {cnt_y}) scale({dat_esc[cnt_car]})"/>'
    return crt_svg(dat_itm['name'], cnt_car, txt_pag, txt_def, clv_est)


def crt_us(dat_itm):
    cnt_car = dat_itm['count']
    txt_col = '#ad2336' if dat_itm['suit'] in ('Hearts', 'Diamonds') else '#182633'
    txt_def = '<g id="pip" fill="' + txt_col + '">' + crt_sig(dat_itm['suit']) + '</g>'
    txt_pag = ''
    if cnt_car == 1:
        # The ace receives engraving without adding an uncounted suit symbol.
        txt_pag += '<g fill="none" stroke="#bc953c" stroke-width=".8"><ellipse cx="150" cy="225" rx="105" ry="148"/><ellipse cx="150" cy="225" rx="99" ry="141"/><path d="M150 62V45M150 388V405M38 225H26M262 225H274"/></g>'
        txt_pag += '<use data-pip="1" href="#pip" transform="translate(150 225) scale(2.8)"/>'
        txt_pag += '<g transform="translate(150 226)" stroke="#fffdf7" fill="none" stroke-width="1"><path d="M0 44V-43M0-34C-23-45-30-23 0-12C30-23 23-45 0-34M0-5C-29-22-37 1 0 16C37 1 29-22 0-5M0 22C-20 11-26 32 0 39C26 32 20 11 0 22"/><path d="M0-39V-48M0 45V52" stroke="#bc953c"/></g>'
        txt_pag += '<g stroke="#bc953c" fill="none" stroke-width=".8"><path d="M88 113C61 144 54 176 54 202M212 113C239 144 246 176 246 202M88 337C61 306 54 274 54 248M212 337C239 306 246 274 246 248"/></g>'
    else:
        val_esc = 1.06 if cnt_car < 7 else .83
        for cnt_x, cnt_y in dat_pos[cnt_car]:
            ang_deg = 180 if cnt_y > 225 else 0
            txt_pag += f'<use data-pip="1" href="#pip" transform="translate({cnt_x} {cnt_y}) rotate({ang_deg}) scale({val_esc})"/>'
    return crt_svg(dat_itm['name'], cnt_car, txt_pag, txt_def, 'american')


def crt_epc(cnt_car):
    txt_def = '<g id="straight" stroke="#292321" stroke-width="1.3" stroke-linejoin="round" stroke-linecap="round">' + crt_esp() + '</g>'
    txt_pag = ''
    for sys_idx in range(cnt_car // 2):
        cnt_top, cnt_bot = 65 + 12*sys_idx, 369 - 12*sys_idx
        cnt_lat, cnt_ini = 14 + 17*sys_idx, 144 - 3*sys_idx
        txt_id = 'blade-' + str(sys_idx)
        txt_def += f'''<g id="{txt_id}" stroke="#292321" stroke-width="1.1" stroke-linejoin="round"><path d="M{cnt_ini} {cnt_top}C{cnt_lat-8} {cnt_top+34} {cnt_lat-8} {cnt_bot-60} 121 {cnt_bot}L126 {cnt_bot-8}C{cnt_lat+15} {cnt_bot-75} {cnt_lat+15} {cnt_top+54} {cnt_ini} {cnt_top}Z" fill="#c6ccd0"/>
<path d="M{cnt_ini-14} {cnt_top+14}C{cnt_lat+3} {cnt_top+62} {cnt_lat+3} {cnt_bot-83} 119 {cnt_bot-12}" fill="none" stroke-width=".55"/>
<g transform="translate(124 {cnt_bot-2}) rotate(-38)"><path d="M-16 0Q0-10 16 0V5Q0-1-16 5Z" fill="#d9a636"/><path d="M-4 4H4V22H-4Z" fill="#ad332b"/><path d="M-4 8L4 12M-4 14L4 18" stroke="#d9a636" stroke-width="1.5"/><circle cy="26" r="5" fill="#d9a636"/></g></g>'''
        txt_pag += f'<use data-pip="1" href="#{txt_id}"/><use data-pip="1" href="#{txt_id}" transform="translate(300 450) rotate(180)"/>'
    if cnt_car % 2:
        txt_pag += '<use data-pip="1" href="#straight" transform="translate(150 225) scale(' + ('2.45' if cnt_car == 1 else '1.75') + ')"/>'
    else:
        txt_pag += crt_fol(150, 225, 0, 1.0)
        txt_pag += '<path d="M150 206C135 185 125 165 137 153C151 164 150 179 150 206M150 244C165 265 175 285 163 297C149 286 150 271 150 244" fill="#ad332b" stroke="#292321" stroke-width="1.1"/>'
    for cnt_x, cnt_y, ang_deg in ((59, 68, -40), (241, 382, 140)):
        txt_pag += crt_fol(cnt_x, cnt_y, ang_deg, .6)
    return txt_pag, txt_def


def crt_btc(cnt_car):
    txt_def = '''<g id="crossed-baton" stroke="#292321" stroke-width="1.2" stroke-linejoin="round"><path d="M-7-158H7L6 158H-6Z" fill="#244b69"/>
<path d="M-7-130H7V-103H-7ZM-7-69H7V-40H-7ZM-7 0H7V29H-7ZM-7 64H7V94H-7ZM-7 129H7V151H-7Z" fill="#ad332b"/>
<path d="M-10-158H10V-148H-10ZM-10 148H10V158H-10Z" fill="#d9a636"/>
<path d="M-3-142V-134M-3-98V-76M-3-36V-6M-3 34V59M-3 99V122" fill="none" stroke="#f7eedb" stroke-width=".9"/>
<path d="M-7-116L7-108M-7-54L7-46M-7 13L7 21M-7 79L7 87M-7 140L7 148" fill="none" stroke="#d9a636" stroke-width="1"/></g>'''
    if cnt_car == 1:
        txt_pag = '<use data-pip="1" href="#crossed-baton" transform="translate(150 225) scale(1.65 1)"/>'
        return txt_pag + crt_fol(93, 175, -60, .88) + crt_fol(207, 275, 120, .88), txt_def
    txt_pag = ''
    cnt_par = cnt_car // 2
    for sys_idx in range(cnt_par):
        cnt_off = (sys_idx - (cnt_par-1)/2) * 18
        for ang_deg in (-29, 29):
            txt_pag += f'<use data-pip="1" href="#crossed-baton" transform="translate({150+cnt_off} 225) rotate({ang_deg})"/>'
    if cnt_car % 2:
        txt_pag += '<use data-pip="1" href="#crossed-baton" transform="translate(150 225)"/>'
    txt_pag += crt_fol(150, 61, 0, .61) + crt_fol(150, 389, 180, .61)
    txt_pag += crt_fol(50, 225, -90, .48) + crt_fol(250, 225, 90, .48)
    return txt_pag, txt_def


def crt_tar(dat_itm):
    dat_pal = {'Deniers': 'Oros', 'Coupes': 'Copas', 'Epees': 'Espadas', 'Batons': 'Bastos'}
    if dat_itm['suit'] == 'Epees':
        txt_pag, txt_def = crt_epc(dat_itm['count'])
    elif dat_itm['suit'] == 'Batons':
        txt_pag, txt_def = crt_btc(dat_itm['count'])
    else:
        return crt_es(dict(dat_itm, suit=dat_pal[dat_itm['suit']]), 'marseille')
    return crt_svg(dat_itm['name'], dat_itm['count'], txt_pag, txt_def, 'marseille')


def crt_bar():
    dat_bar = []
    for sys_idx, txt_pal in enumerate(('Oros', 'Copas', 'Espadas', 'Bastos')):
        for txt_ran in [str(cnt_ran) for cnt_ran in range(1, 10)] + ['Sota', 'Caballo', 'Rey']:
            est_fig = txt_ran in ('Sota', 'Caballo', 'Rey')
            dat_itm = {'id': f'spanish-{sys_idx}-{txt_ran}', 'name': txt_ran+' · '+txt_pal,
                       'label': txt_ran+' · '+txt_pal, 'rank': {'Sota': '10', 'Caballo': '11', 'Rey': '12'}.get(txt_ran, txt_ran),
                       'suit': txt_pal, 'deck': 'spanish', 'kind': 'illustration' if est_fig else 'pip',
                       'art': f'/assets/playing-cards/spanish-{sys_idx}-{txt_ran.lower()}.' + ('webp' if est_fig else 'svg')}
            if not est_fig:
                dat_itm['count'] = int(txt_ran)
            dat_bar.append(dat_itm)
    for sys_idx, txt_pal in enumerate(('Spades', 'Hearts', 'Diamonds', 'Clubs')):
        for txt_ran in ['A'] + [str(cnt_ran) for cnt_ran in range(2, 11)] + ['J', 'Q', 'K']:
            est_fig = txt_ran in ('J', 'Q', 'K')
            dat_itm = {'id': f'a-{sys_idx}-{txt_ran}', 'name': txt_ran+' of '+txt_pal,
                       'label': txt_ran+' of '+txt_pal, 'rank': txt_ran, 'suit': txt_pal,
                       'deck': 'american', 'kind': 'illustration' if est_fig else 'pip',
                       'art': f'/assets/playing-cards/american-{sys_idx}-{txt_ran.lower()}.' + ('webp' if est_fig else 'svg')}
            if not est_fig:
                dat_itm['count'] = 1 if txt_ran == 'A' else int(txt_ran)
            dat_bar.append(dat_itm)
    return dat_bar


def main():
    dat_bar = crt_bar()
    pth_dst = sys_rad / 'src/assets/playing-cards'
    pth_dst.mkdir(parents=True, exist_ok=True)
    for dat_itm in dat_bar:
        if dat_itm['kind'] != 'pip':
            continue
        txt_pag = crt_es(dat_itm) if dat_itm['deck'] == 'spanish' else crt_us(dat_itm)
        (sys_rad / 'src' / dat_itm['art'].lstrip('/')).write_text(txt_pag)
    dat_met = {'timestamp': '2026-11-01', 'release': '2.1.0',
               'author_credits': 'https://www.alawise.es/1-s', 'title': 'Kamala · Spanish and American playing cards',
               'method': 'Original engraved SVG suit compositions with exact pip counts and individually illustrated courts. The Spanish 40-card variant omits eights and nines.',
               'cards': dat_bar}
    (sys_rad / 'src/playing-cards.json').write_text(json.dumps(dat_met, ensure_ascii=False, indent=2) + '\n')
    print('Built 76 engraved pip images and the 100-card Spanish/American artwork map.')


if __name__ == '__main__':
    main()
