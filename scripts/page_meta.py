#!/usr/bin/env python3
# Timestamp: 2026-10-29
# Version: 2.0.0
# Author and Credits: https://www.alawise.es/1-s
"""Keep canonical and social identities consistent across the generated site."""

import json
from html import escape as esc_htm
from pathlib import Path

dat_met = json.loads((Path(__file__).resolve().parents[1] / 'src/site.json').read_text())


def crt_met(pth_pag, tit_pag, des_pag):
    tit_pag = dat_met['title'] if pth_pag == '/' else tit_pag + ' · ' + dat_met['title']
    url_can = dat_met['origin'] + pth_pag
    txt_met = [
        '<!-- KAMALA META START -->',
        '<title>' + esc_htm(tit_pag) + '</title>',
        '<meta name="description" content="' + esc_htm(des_pag) + '">',
        '<link rel="canonical" href="' + esc_htm(url_can) + '">',
    ]
    for clv_esc, txt_val in [
        ('og:type', 'article' if pth_pag.startswith('/techniques/') or (pth_pag.startswith('/arts/') and pth_pag != '/arts/') else 'website'),
        ('og:site_name', dat_met['title']),
        ('og:title', tit_pag),
        ('og:description', des_pag),
        ('og:url', url_can),
        ('og:locale', 'en_US'),
        ('og:image', dat_met['origin'] + dat_met['share_image']),
        ('og:image:secure_url', dat_met['origin'] + dat_met['share_image']),
        ('og:image:type', 'image/png'),
        ('og:image:width', '1200'),
        ('og:image:height', '630'),
        ('og:image:alt', dat_met['share_alt']),
    ]:
        txt_met.append('<meta property="' + clv_esc + '" content="' + esc_htm(txt_val) + '">')
    for clv_esc, txt_val in [
        ('twitter:card', 'summary_large_image'),
        ('twitter:title', tit_pag),
        ('twitter:description', des_pag),
        ('twitter:url', url_can),
        ('twitter:image', dat_met['origin'] + dat_met['share_image']),
        ('twitter:image:alt', dat_met['share_alt']),
        ('kamala:release', dat_met['release']),
    ]:
        txt_met.append('<meta name="' + clv_esc + '" content="' + esc_htm(txt_val) + '">')
    return '\n'.join(txt_met + ['<!-- KAMALA META END -->'])
