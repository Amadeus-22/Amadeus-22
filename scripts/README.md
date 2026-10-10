# Asset generators

Every image in this profile is generated, not drawn by hand in an editor. These
scripts are what produce them, so the design can be regenerated when a colour,
a size or a piece of text changes.

| script | produces |
|---|---|
| `texto.py` | shared helper: converts text to SVG outlines with fontTools |
| `gerar3.py` | section headers, work cards (desktop and mobile), the at-a-glance strip |
| `nameplate.py` | the AMADEUS wordmark plate |
| `comunidades.py` | the community cards, with avatars embedded as base64 |
| `stack.py` | the technology strip, logos in their official brand colours |
| `banner_gif.py` | the animated banner: the lab photo with the robots moving and the screens live, as a 6-second looping GIF |

Run them from the repository root:

    python3 scripts/gerar3.py
    python3 scripts/nameplate.py
    python3 scripts/comunidades.py
    SI_DIR=/path/to/simple-icons python3 scripts/stack.py
    python3 scripts/banner_gif.py 960     # needs Pillow and NumPy; 960 is the width

`stack.py` needs the simple-icons catalogue, which is not kept in this
repository: `SI_DIR` must hold `si.json` (from `data/simple-icons.json`) and
`icons/<slug>.svg`, both from https://cdn.jsdelivr.net/npm/simple-icons@latest/.

Everything writes into `assets/`.

## Why the images carry their own text

GitHub renders a README inside its own theme and strips CSS, so the page
background cannot be styled and layout cannot use media queries. What it does
support is `<picture>`, which accepts any media query — including width. Each
plate therefore ships in four variants: dark, light, mobile-dark, mobile-light.

For the same reason every `<source srcset>` points at a file in this
repository. GitHub proxies `img src` but not `source srcset`, so a `<picture>`
pointing at an external host renders nothing.

## Requirements

Python 3 with `fontTools` and `Pillow`. Fonts are read from the paths declared
at the top of each script; adjust them if yours live elsewhere.
