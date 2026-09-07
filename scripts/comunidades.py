#!/usr/bin/env python3
"""Cards de comunidade como imagem, para fluírem em vez de espremer.

A tabela de duas colunas não quebra em linha: no celular cada célula ficava com
~180px e o navegador hifenizava "QuantConnect" e "organization". Como imagem de
largura fixa num parágrafo, elas fluem — duas por linha no desktop, uma por
linha no telefone.
"""
import base64, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

S = pathlib.Path(__file__).resolve().parent.parent
OUT = S / 'perfil' / 'assets'
MONO = "Consolas, 'DejaVu Sans Mono', 'Courier New', monospace"

TEMAS = {
    "dark":  dict(titulo="#eef4fb", corpo="#a8bcd2", linha="#39506b", acento="#ff3b30"),
    "light": dict(titulo="#111820", corpo="#33414f", linha="#8fa2bb", acento="#c1121f"),
}

def b64(nome):
    dados = (S / 'avatares' / f'{nome}.png').read_bytes()
    return "data:image/png;base64," + base64.b64encode(dados).decode()

def quebrar(t, n):
    ps, ls, cur = t.split(), [], ""
    for w in ps:
        if len(cur) + len(w) + 1 <= n: cur = (cur + " " + w).strip()
        else: ls.append(cur); cur = w
    if cur: ls.append(cur)
    return ls

ORGS = [
    ("QuantConnect", "QuantConnect", "Algorithmic trading research and backtesting, on the platform behind Lean, its open-source engine.", "c-qc"),
    ("AM-TIIX", "TIIX", "Health and services platform at tiix.com.br. Current employer: the PHP portals for clients, professionals and brokers.", "c-tiix"),
    ("NER-ELOHIM", "NER-ELOHIM", "My own organization, where the Go suite and the engineering tooling live. Private by design.", "c-ner"),
    ("instituto-nova-sos", "Instituto Nova SOS", "Contributor to chesed, a Go and TypeScript project for a social institute.", "c-sos"),
]

def card(avatar, titulo, corpo, arq, tema, movel):
    T = TEMAS[tema]
    if movel:
        w, h, av, ft, fc, cols = 560, 300, 64, 27, 22, 33
    else:
        w, h, av, ft, fc, cols = 628, 250, 56, 24, 18, 42
    linhas = quebrar(corpo, cols)
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t">',
         f'  <title id="t">{titulo} — {corpo}</title>',
         f'''  <defs><linearGradient id="r" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{T['acento']}" stop-opacity="0.25"/>
    <stop offset="0.5" stop-color="{T['acento']}"/>
    <stop offset="1" stop-color="{T['acento']}" stop-opacity="0.25"/></linearGradient>
    <clipPath id="c"><rect x="34" y="30" width="{av}" height="{av}" rx="8"/></clipPath></defs>''',
         f'  <rect x="0" y="0" width="{w}" height="3" fill="url(#r)"/>']
    m, n = 10, 18
    p.append(f'''  <g stroke="{T['acento']}" stroke-width="2" fill="none" opacity="0.9">
    <path d="M{m} {m+n} L{m} {m} L{m+n} {m}"/><path d="M{w-m-n} {m} L{w-m} {m} L{w-m} {m+n}"/>
    <path d="M{m} {h-m-n} L{m} {h-m} L{m+n} {h-m}"/><path d="M{w-m-n} {h-m} L{w-m} {h-m} L{w-m} {h-m-n}"/></g>''')
    p.append(f'  <image x="34" y="30" width="{av}" height="{av}" clip-path="url(#c)" href="{b64(avatar)}"/>')
    tx = 34 + av + 20
    for i, l in enumerate(quebrar(titulo, 20)):
        p.append(f'  <text x="{tx}" y="{58 + i*(ft+6)}" font-family="{MONO}" font-size="{ft}" '
                 f'font-weight="700" fill="{T["titulo"]}" letter-spacing="1">{l}</text>')
    y0 = 30 + av + 26
    p.append(f'  <line x1="34" y1="{y0}" x2="{w-34}" y2="{y0}" stroke="{T["linha"]}" stroke-width="1.2" opacity="0.75"/>')
    for i, l in enumerate(linhas[:6]):
        p.append(f'  <text x="34" y="{y0 + 30 + i*(fc+8)}" font-family="{MONO}" font-size="{fc}" '
                 f'fill="{T["corpo"]}">{l}</text>')
    p.append('</svg>')
    suf = ("-m" if movel else "") + ("" if tema == "dark" else "-light")
    (OUT / f'{arq}{suf}.svg').write_text('\n'.join(p))

n = 0
for av, tit, cor, arq in ORGS:
    for tema in TEMAS:
        for movel in (False, True):
            card(av, tit, cor, arq, tema, movel); n += 1
print(f"  {n} cards de comunidade gerados")
