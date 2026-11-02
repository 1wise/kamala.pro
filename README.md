# kamala.pro — Artes Mánticos

Timestamp: 2026-11-02 | Version: 2.1.1
Author and Credits: https://www.alawise.es/1-s

Kamala is an observatory and comparative field guide with a black and indigo
visual system. The homepage retains its full original observatory window,
solar imagery, weather and planetary view, framed by identical menus.

## Field guide and lexicon

The five scales distinguish matter, manipulated objects, human experience,
Earth and the solar system. The 28 original technique pages are joined by
46 complete arts/variant pages. The glossary preserves every named subterm,
English and Spanish labels, definitions and references to each field note.
The glossary is rendered as complete HTML with optional local search and
scale filtering. It does not depend on a remote search service.

Source data: src/techniques.json, src/glossary.json, src/traditions.json
and src/shamanic.json. The previous proposal list remains in src/further-arts.json
for coverage checks. scripts/glossary_pages.py renders the full set and all
photo guidance. Original summaries are preserved in the new editorial data.

## AstroApp

Version 2.1.1 treats calculation completion and image loading as separate
events. The SDK callback no longer reports a loaded image prematurely.
src/astroapp-image.mjs watches the returned PNG, retries transient failures
twice and offers an explicit image-only reload plus a direct image link.
Changing or clearing a chart cancels that image's listeners and timers.
The retry never repeats the chart calculation or sends the form again.

The chart form separates Western natal, Jyotisha Rasi / D1 and divisional
methods. Each has its own zodiac and diagram choices. Natal and Rasi requests
retain the SDK's standard calculation; only a divisional request calls setVarga.
The observed SDK drops the division number from getData(), so incomplete
divisional requests are stopped with an explicit message before submission.
The chart renders directly into
the astrology page's astroappDiv. Only the chart workspace loads the SDK;
ordinary pages do not request it. The head loader exposes a ready promise;
the Excalibur installer inserts the parser-time SDK tag into that workspace's
head using the host's existing astroapp-config.json. No active access code belongs
in source control or the archive.

Version 2.0.2 repaired the global SDK tags introduced in 2.0.0/2.0.1.
deploy/astroapp/repair_astroapp_loading.py supplies a small repair package for
an installed Excalibur site, with backups and no key replacement. Read
deploy/astroapp/REPARAR.md for the verified origin behavior and installation.

Version 2.0.3 sends YYYY/MM/DD dates: the current provider rejects the colon
form from its older guide. Synthetic Western natal and Jyotisha Rasi requests returned HTTP 200
with chart images and calculation XML after that correction.

Western, Jyotisha, Chinese, Maya, Nahua, Dine, Mesopotamian and contemporary
calendar entries have separate navigation and field notes. The complete lexicon
is retained. Further Chinese/Maya integrations require their exact provider
contracts; the public REST examples do not identify those calls. The public
JavaScript access code is not substituted for REST authentication.

deploy/astroapp/CHARTS.md records request modes, current limits and sources.
scripts/package-astroapp.py creates the compact public-only update package.

## Chance and local laboratory

The six-sided dice use original inline SVG artwork: warm ivory, beveled
edges and recessed indigo pips. Faces and history contain pip drawings
instead of printed numerals. src/dice-core.mjs shares the exact six layouts
with scripts/build-dice.mjs; the build also exports six standalone SVG faces.
The sampler and rejection-sampling logic are unchanged.

Cards support Spanish 40/48, American 52 and Marseille 78 with matrix or cross
spreads. Rune sets are Younger Futhark 16 and Elder Futhark 24, with conventional
names, Latin transliteration and modern Finnish glosses. Coins use the supplied
identity as a centered bronze relief and a matching bronze Maltese cross reverse. The three-coin
I Ching method builds six lines from the bottom.

The Marseille deck now has 78 original image files: 22 major arcana and 16
court illustrations made with the built-in image generator, plus 40 ornamental
SVG pip cards with exact suit counts. The complete gallery is at
/apps/cards/tarot/. A card opens in a larger native dialog from the gallery or
from a matrix/cross spread. src/tarot.json stores the mapping and art prompts;
scripts/build-tarot.py recreates the numeral cards. ASSETS.md records provenance.

All three decks now have their own complete artwork. Spanish 48 includes the
40-card subset; American 52 uses individual reversible courts. The catalogue at
/apps/cards/decks/ links every gallery. src/playing-cards.json maps 100 cards;
src/playing-cards-art.json preserves the 24 court-generation briefs.
scripts/build-playing-cards.py draws exact pips, ornamental frames and aces.
The Marseille numeral compositions now include curved swords and crossed batons.

## Contemplation rooms

/contemplation/ opens the candle and crystal rooms at /apps/candle/ and
/apps/crystal/. The local Canvas paintings use incoming traffic for brightness,
outgoing traffic for sway/color, packet rates for fine movement and new logged
firewall notices for gentle amber flares/rings. These are artistic mappings,
not cryptographic randomness or a firewall severity display.

The rooms read same-origin /telemetry/contemplation.json. deploy/contemplation/
contains the optional non-root Excalibur collector, systemd unit, installer and
nginx cache snippet. The collector reads enp6s0 counters and matching new kernel
firewall records; it publishes aggregate counters only. Install it on Excalibur
to enable live mode. No sample JSON is deployed and Sites cannot read Excalibur's
sysfs or journal. Missing/stale signals stay explicit; Demo is separately labeled.
Focus view, fullscreen, pause, glow and reduced-motion support are available.
URL settings: src_mode=live|demo and int_lvl=0.4..1.4. They do not generate keys,
change firewall rules or modify the shared entropy source.

Every draw and the key laboratory share src/entropy-core.mjs. Fresh browser
randomness is always included, and the interface labels the sources actually
used. The laboratory is an exhibition of working possibilities: SSH
public/private pairs, hexadecimal, Base64, Base64url, Base32, UUID v4,
TOTP setups, QR exports and independent ASCII seed art. Private SSH keys
download as files with passphrase protection selected by default. SSH QR
exports contain the public key; secret and TOTP QR exports contain their
labeled values. The portable HTML includes every generator and uses the
same libraries and a restricted content policy. It does not load AstroApp.

GET api_act=configure fills controls; an explicit api_act=draw requests a fresh
Chance result. The local laboratory accepts configuration only; generation
requires a button. /api/ documents parameter names, ranges and examples.

## Potpourri and Excalibur

Potpourri provides photo instructions for every technique and art. The upload
handler is packaged separately from static Sites assets and runs on Excalibur
with PHP GD, fileinfo and the existing private Send transport. It validates
CSRF, topic, dimensions, sizes and actual image formats, re-encodes photos,
sends a fixed-destination private email, and removes temporary files. There is
no permanent image gallery. Mailbox copies remain available for the human reply.

The installer preserves original biorhythm apps, active AstroApp configuration,
the existing contact form and private mail credentials. It updates shared
navigation and metadata and creates a rollback backup. Nginx and PHP upload
limits are documented in the release.

## Build, verify and package

    npm ci
    npm run build
    python3 tests/page-contracts.py
    node tests/dice-art.mjs
    node tests/astroapp-image.mjs
    node tests/tarot-assets.mjs
    node tests/playing-card-assets.mjs
    node tests/contemplation-core.mjs
    python3 tests/test_contemplation_feed.py
    node tests/astroapp-core.mjs
    node tests/astroapp-head.mjs
    python3 tests/contact-shell.py
    python3 tests/install-v2.py
    python3 tests/potpourri-endpoint.py
    python3 scripts/package-excalibur.py
    python3 scripts/package-downloads.py

The upload test needs PHP CLI with GD and fileinfo. It uses a non-sending mail
double. Other focused checks cover the shared random source, complete decks,
exact spread positions, rune sets, I Ching probabilities, key containers and QR
decoding. No live AstroApp key or outgoing email is used by the local tests.

Sites hosts the static UI. Excalibur hosts the existing PHP applications,
mail transport, public camera sampler and private photo submissions.
The download packager creates a hosted /downloads/ page with the Excalibur
ZIP and source ZIP, checksums and the portable tool. Generated download bundles
are excluded from the Excalibur overlay and source ZIP to avoid nesting.
The stable portable path is /assets/keys-lab.html; earlier portable paths
remain compatibility copies of the complete current application.

## Git handoff

GIT.md explains the source archive, build, deployment package and first push
to an existing empty Git repository. ASSETS.md records the matching bronze
coin assets and the reverse-side generation brief. The archive contains the
source tree and baseline built pages. Run npm ci and npm run build before
deployment; generated copies of source assets are omitted from the source ZIP.

legacy/bior preserves a sanitized reference copy of the owner's Drive apps,
including the biorhythm generator, compositor and solar simulator. It is not
deployed by the builder or installer; existing Excalibur apps remain in place.
See legacy/README.md for provenance, configuration and known legacy behavior.
