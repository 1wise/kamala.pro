#!/usr/bin/env python3
# Timestamp: 2026-11-02
# Version: 2.1.1
# Author & Credits: https://www.alawise.es/1-s
"""Render the same experiment inside its article and its standalone workspace."""

dat_prb = {
    'entropy': ('Entropy lab', 'Generate hexadecimal bytes from the shared sampler.', 16, 32, 'Generate bytes', 'Bytes', 'entropy-streams'),
    'dice': ('Dice', 'Roll standard six-sided dice.', 2, 12, 'Roll dice', 'Dice', 'dice'),
    'coins': ('Coins', 'Toss independent digital coins.', 3, 12, 'Toss coins', 'Coins', 'coins'),
    'cards': ('Cards', 'Spanish cards, American playing cards or Tarot de Marseille. Arrange a matrix or a five-card cross.', 3, 78, 'Draw spread', 'Cards', 'cards'),
    'runes': ('Runes', 'Choose 16 or 24 runes, with Finnish glosses and conventional transliteration.', 3, 24, 'Draw runes', 'Runes', 'runes'),
    'yijing': ('I Ching', 'Cast six lines with three coins, from bottom to top, and identify the changing figure.', 3, 3, 'Cast line 1 of 6', 'Coins', 'yijing'),
}


def crt_prb(clv_esc):
    tit_pag, sub_pag, cnt_car, cnt_tot, tit_lnk, txt_note, pth_pag = dat_prb[clv_esc]
    txt_ext = ''
    txt_art = ''
    txt_sig = ''
    if clv_esc == 'cards':
        txt_ext = '''<label>Deck<select data-deck><option value="spanish">Spanish deck</option><option value="american">American playing cards · 52</option><option value="marseille">Tarot de Marseille · 78</option></select></label><label data-spanish-size>Spanish deck size<select><option value="40">40 cards · no 8 or 9</option><option value="48">48 cards · includes 8 and 9</option></select></label><label>Layout<select data-layout><option value="matrix">Rows × columns</option><option value="cross">Five-card cross</option></select></label><label>Rows<input data-rows type="number" min="1" max="78" step="1" value="1" required></label><label>Columns<input data-cols type="number" min="1" max="78" step="1" value="3" required></label>'''
        txt_art = '<p class="quiet-note">Matrix: one card per cell, in row order. Cross: 1 center, 2 above, 3 below, 4 left, 5 right. Changing a deck or layout begins a fresh deck and clears its record. Wide matrices scroll horizontally.</p><p class="quiet-note">No jokers. Marseille includes 22 major and 56 minor arcana, with Justice VIII and Strength XI. Every deck uses original Kamala artwork. Open a card image for a larger view. <a href="/apps/cards/decks/">Browse all three illustrated decks ↗</a></p>'
    else:
        txt_ext = f'<label>{txt_note}<input data-count type="number" min="1" max="{cnt_tot}" step="1" value="{cnt_car}" required></label>'
    if clv_esc == 'runes':
        txt_ext = '''<label>Rune alphabet<select data-rune-set><option value="16">16 · Younger Futhark</option><option value="24">24 · Elder Futhark</option></select></label><label>Labels<select data-rune-label><option value="fi">Finnish · suomi</option><option value="name">Conventional rune names</option><option value="latin">Latin transliteration</option></select></label>''' + txt_ext
        txt_art = '<p class="quiet-note">The 24-rune alphabet is historically older than the 16-rune alphabet. Finnish is the Finno-Ugric language used for the modern glosses here; the alphabets themselves are Germanic. Conventional rune names and transliterations remain visible. Several reconstructed names and meanings are debated; Perthro is marked uncertain.</p>'
    if clv_esc in ('coins', 'yijing'):
        txt_ext = '<label>Coin mode<select data-coin-mode><option value="free"' + (' selected' if clv_esc == 'coins' else '') + '>Free toss</option><option value="iching"' + (' selected' if clv_esc == 'yijing' else '') + '>I Ching · three coins</option></select></label>' + txt_ext
        txt_sig = '<button class="button button-secondary" type="button" data-cast-all hidden>Cast all six lines ↗</button>'
        txt_art = '''<details class="portrait-settings"><summary>Coin portrait</summary><div class="coin-preview" data-portrait-preview></div><p class="quiet-note" data-portrait-note>The site portrait and Maltese cross are the defaults. Choose a local photo for this page only; it stays in this tab and is not uploaded or saved.</p><div class="chance-controls"><label>Local portrait · JPEG / PNG / WebP<input type="file" data-portrait-file accept="image/jpeg,image/png,image/webp"></label><button type="button" class="reset" data-clear-photo>Restore site portrait</button></div></details><section class="iching-workspace" data-iching hidden aria-label="I Ching cast"><h3>Three coins. Six lines.</h3><p class="quiet-note">Portrait / heads = 3. Maltese cross / tails = 2. Totals: 6 changing yin, 7 stable yang, 8 stable yin, 9 changing yang. The first cast is line 1 at the bottom. This is the three-coin method, with probabilities 1:3:3:1 for 6, 7, 8 and 9. Each action requests one camera sample; Cast all six lines shares that sample across its 18 tosses, with fresh browser randomness for every toss.</p><div class="hexagrams" data-hexagrams></div><ol class="iching-lines" data-iching-lines aria-label="Cast lines, numbered from the bottom"></ol><a class="text-link" href="https://ctext.org/book-of-changes" target="_blank" rel="noopener">Read the Book of Changes ↗</a></section>'''
    return f'''<section class="chance-workspace section article-experiment" id="experiment" data-chance-app="{clv_esc}" aria-labelledby="experiment-title">
<div class="eyebrow">TRY THE EXPERIMENT / {tit_pag.upper()}</div><h2 id="experiment-title">Make a draw. Keep a record.</h2><p>{sub_pag}</p>
<div class="chance-controls"><label>Sample source<select data-source><option value="auto">Camera mix · one source per draw</option><option value="cam1">Camera 1</option><option value="cam2">Camera 2</option><option value="cam3">Camera 3</option><option value="cam4">Microscope / Camera 4</option><option value="browser">Browser only</option></select></label>{txt_ext}<button class="button" type="button" data-draw>{tit_lnk} ↗</button>{txt_sig}<button class="reset" type="button" data-reset>Reset{' deck' if clv_esc == 'cards' else ' set' if clv_esc == 'runes' else ''}</button></div>
<div class="spread-viewport" tabindex="0" aria-label="Draw results; wide layouts scroll horizontally"><div class="chance-results" data-result role="status" aria-live="polite" aria-label="Draw result"></div></div><p data-remaining class="quiet-note"></p><p data-source-status role="status" aria-live="polite"></p>{txt_art}
<details class="chance-method"><summary>How this draw works</summary><p>The server takes up to 128 KiB of JPEG image data from one fixed stream, with a two-second timeout, and mixes it with fresh system randomness using SHA-512. The browser uses the same source module as the standalone key tool and mixes this response with its own random seed and uses fresh browser random words for each result. Rejection sampling avoids modulo bias. If the sampler is unavailable, results use browser randomness and the status says so.</p><p>Samples are experimental: no physical entropy rate has been established. Camera delays and repeated frames are possible. No predictive meaning is assigned to results. History stays in this page and clears when you leave or reset.</p></details>
<h3>Recent draws</h3><ol class="chance-history" data-history></ol><noscript>Enable JavaScript to use this experiment.</noscript></section>'''
