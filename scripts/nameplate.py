#!/usr/bin/env python3
"""Placa de nome. AMADEUS em traçado vetorial, fino e com entreletra larga."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from texto import bloco

OUT = pathlib.Path(__file__).resolve().parent.parent / 'assets'
F = '/home/p/miniconda3/fonts/'
MONO = "Consolas, 'DejaVu Sans Mono', 'Courier New', monospace"

TEMAS = {
    "dark":  dict(nome="#f2f7fd", sub="#8ea3bb", papel="#ff3b30", txt="#9fb2c8", linha="#39506b"),
    "light": dict(nome="#0d141c", sub="#54637a", papel="#c1121f", txt="#33414f", linha="#8fa2bb"),
}

def placa(tema, movel=False):
    T = TEMAS[tema]
    w, h = (560, 240) if movel else (1280, 236)
    cx = w / 2
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t">',
         '  <title id="t">AMADEUS — Pedro Barbosa — Quantitative Developer and Systems Engineer</title>',
         f'''  <defs><linearGradient id="r{tema[0]}{int(movel)}" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{T['papel']}" stop-opacity="0"/>
    <stop offset="0.5" stop-color="{T['papel']}"/>
    <stop offset="1" stop-color="{T['papel']}" stop-opacity="0"/></linearGradient></defs>''']

    # AMADEUS: Ubuntu Thin, entreletra bem aberta. É a entreletra que dá a
    # elegância; peso fino sozinho fica só apagado.
    t_nome = 62 if movel else 96
    g, larg = bloco("AMADEUS", F + "Ubuntu-Th.ttf", t_nome, T["nome"], cx,
                    (72 if movel else 96), tracking=0.40)
    p.append("  " + g)

    # filete curto sob o nome, na largura dele
    y1 = (92 if movel else 122)
    p.append(f'  <rect x="{cx-larg/2:.1f}" y="{y1}" width="{larg:.1f}" height="1" '
             f'fill="{T["linha"]}" opacity="0.55"/>')

    g2, _ = bloco("PEDRO BARBOSA", F + "Ubuntu-L.ttf", (15 if movel else 19),
                  T["sub"], cx, y1 + (26 if movel else 32), tracking=0.52)
    p.append("  " + g2)

    y2 = y1 + (52 if movel else 64)
    p.append(f'  <rect x="{cx-(180 if movel else 320)}" y="{y2}" '
             f'width="{360 if movel else 640}" height="2" fill="url(#r{tema[0]}{int(movel)})"/>')

    if movel:
        for i, l in enumerate(["QUANTITATIVE DEVELOPER", "SYSTEMS ENGINEER"]):
            p.append(f'  <text x="{cx}" y="{y2+28+i*24}" text-anchor="middle" font-family="{MONO}" '
                     f'font-size="16" font-weight="700" fill="{T["papel"]}" letter-spacing="1.8">{l}</text>')
        y3 = y2 + 82
        p.append(f'  <text x="{cx}" y="{y3}" text-anchor="middle" font-family="{MONO}" font-size="14" '
                 f'fill="{T["txt"]}">Python &#183; R &#183; Go &#183; PHP</text>')
        y4 = y3 + 28
    else:
        p.append(f'  <text x="{cx}" y="{y2+34}" text-anchor="middle" font-family="{MONO}" '
                 f'font-size="22" font-weight="700" fill="{T["papel"]}" letter-spacing="4.5">'
                 f'QUANTITATIVE DEVELOPER // SYSTEMS ENGINEER</text>')
        y3 = y2 + 68
        p.append(f'  <text x="{cx}" y="{y3}" text-anchor="middle" font-family="{MONO}" font-size="17" '
                 f'fill="{T["txt"]}">Quantitative research in Python and R &#183; production systems in Go and PHP</text>')
        y4 = y3 + 34

    p.append(f'  <text x="{cx}" y="{y4}" text-anchor="middle" font-family="{MONO}" '
             f'font-size="{12 if movel else 14}" fill="{T["sub"]}" letter-spacing="2.8">'
             f'RIO DE JANEIRO &#8212; UTC&#8722;3 &#8212; EN &amp; PT &#8212; REMOTE</text>')
    p.append('</svg>')
    suf = ("-m" if movel else "") + ("" if tema == "dark" else "-light")
    (OUT / f'nameplate{suf}.svg').write_text('\n'.join(p))

for t in TEMAS:
    for m in (False, True):
        placa(t, m)
print("  4 placas regeradas")
