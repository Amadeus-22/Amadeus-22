# Asset generators

Every image in this profile is generated, not drawn by hand in an editor. These
scripts are what produce them, so the design can be regenerated when a colour,
a size or a piece of text changes.

| script | produces |
|---|---|
| `texto.py` | shared helper: converts text to SVG outlines with fontTools |
| `gerar3.py` | section headers, work cards, the at-a-glance strip |
| `nameplate.py` | the AMADEUS wordmark plate |
| `comunidades.py` | the community cards, with avatars embedded as base64 |
| `stack.py` | the technology strip, logos in their official brand colours |

Run them from the repository root:

    python3 scripts/gerar3.py
    python3 scripts/nameplate.py
    python3 scripts/comunidades.py
    python3 scripts/stack.py

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
