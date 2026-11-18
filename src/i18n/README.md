# Kamala language editions

Timestamp: 2026-11-18 | Version: 2.5.2
Author & Credits: https://www.alawise.es/1-s

English remains at the existing routes. Spanish is generated below /es/.
The Calo edition below /calo/ was approved by the project owner on 2026-11-18.
It combines documented public Calo vocabulary with Spanish explanations.
It is published without draft notices or a locale-wide noindex restriction.
Public Calo routes and the lexicon are included in the sitemap. The HTML uses
BCP 47 git-ES; search hreflang stays on the supported English/Spanish pair,
without assigning Calo an unrelated language code.
Reference: https://developers.google.com/search/docs/specialty/international/localized-versions

The Spanish catalog was prepared with local translation models and editorial
corrections. No model runs in the visitor's browser. No translation API receives
visitor input. es.overrides.json carries reviewed labels, terminology and
critical scientific qualifications; es.json is the retained general catalog.
The shared runtime translates subsequent app-generated labels without changing
IDs, form values, sensor values, GET contracts or media source URLs.

Model assistance: Helsinki-NLP/opus-mt-en-es (Apache-2.0), and
Xenova/nllb-200-distilled-600M, based on Meta NLLB (CC-BY-NC-4.0).
The source remains available for editorial review. Model weights and development
runtimes are not distributed with the website.

Calo vocabulary: Gamella and colleagues, Gazeta de Antropologia (2011), appendix:
https://www.ugr.es/~pwlac/G27_39Juan_Gamella-y-otros.html
The source documents variants and usage; it does not establish a single norm.
The site documents each adopted equivalent at /calo/lengua/.

Version 2.5.1 expands the selection to 84 entries with documented variants,
context notes, eight categories and a local-only search. It also cites the
Fundacion Secretariado Gitano public glossary and the BNE dictionary guide.
The selection describes the site's current coverage, not the extent of Calo.
Navigation uses more documented vocabulary, with Spanish technical explanations.
Flags are the visible locale controls, with accessible names.

Rebuild with npm run build. To list translatable English units after editing a
page, run python3 scripts/build-i18n.py --extract. Add reviewed translations to
the catalogs. Building and publishing do not download a language model.

External frames and third-party applications retain their provider's language.
The portable standalone laboratory download currently retains English.
