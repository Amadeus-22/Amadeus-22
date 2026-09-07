#!/usr/bin/env python3
"""Faixa de stack: logos nas cores oficiais, com o nome embaixo de cada um.

Precisa ser asset próprio: o <picture> do GitHub só troca tema em imagem que
ele mesmo serve. Um <source srcset> apontando para o skillicons é bloqueado
pela CSP, que é por que a seção aparecia vazia.
"""
import json, re, pathlib

S = pathlib.Path(__file__).resolve().parent.parent
OUT = S / 'perfil' / 'assets'
MONO = "Consolas, 'DejaVu Sans Mono', 'Courier New', monospace"

dados = json.load(open(S / 'si.json'))
icons = dados['icons'] if isinstance(dados, dict) else dados
por_titulo = {i['title']: i for i in icons}

# (arquivo simple-icons, título no catálogo, rótulo na tela)
GRUPOS = [
    ("LANGUAGES", [("go","Go","Go"),("python","Python","Python"),("php","PHP","PHP"),
                   ("javascript","JavaScript","JavaScript"),("typescript","TypeScript","TypeScript"),
                   ("r","R","R"),("gnubash","GNU Bash","Bash")]),
    ("DATA &amp; ANALYSIS", [("sqlite","SQLite","SQLite"),("postgresql","PostgreSQL","PostgreSQL"),
                             ("mongodb","MongoDB","MongoDB"),("scikitlearn","scikit-learn","scikit-learn")]),
    ("RUNTIME &amp; TOOLING", [("linux","Linux","Linux"),("docker","Docker","Docker"),
                               ("git","Git","Git"),("github","GitHub","GitHub"),
                               ("nodedotjs","Node.js","Node.js"),("react","React","React"),
                               ("flask","Flask","Flask")]),
]

def traco(arq):
    t = (S / 'icons' / f'{arq}.svg').read_text()
    m = re.search(r'<path[^>]*\sd="([^"]+)"', t)
    return m.group(1)

TEMAS = {
    "dark":  dict(bg1="#0b0f16", bg2="#070a10", bg3="#0d1219", rot="#8ea3bb",
                  nome="#c8d6e6", linha="#39506b", acento="#ff3b30", escuro_min=0.30),
    "light": dict(bg1="#eef1f5", bg2="#e6eaf0", bg3="#dfe4ec", rot="#4a5a6b",
                  nome="#22303e", linha="#8fa2bb", acento="#c1121f", escuro_min=0.0),
}

def clarear(hexa, tema):
    """Logos quase pretos somem no fundo escuro; clareia só esses."""
    if tema != "dark":
        return "#" + hexa
    r, g, b = (int(hexa[i:i+2], 16) for i in (0, 2, 4))
    lum = (0.299*r + 0.587*g + 0.114*b) / 255
    if lum >= 0.30:
        return "#" + hexa
    f = 0.30 / max(lum, 0.02)
    return "#%02x%02x%02x" % tuple(min(255, int(c*f) + 40) for c in (r, g, b))

def faixa(tema):
    T = TEMAS[tema]
    w, lin_h, topo = 1280, 168, 30
    h = topo + lin_h*len(GRUPOS) + 16
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t">',
         '  <title id="t">Go, Python, PHP, JavaScript, TypeScript, R, Bash. SQLite, PostgreSQL, MongoDB, scikit-learn. Linux, Docker, Git, GitHub, Node.js, React, Flask.</title>',
         f'''  <defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{T['bg1']}"/><stop offset="0.55" stop-color="{T['bg2']}"/>
      <stop offset="1" stop-color="{T['bg3']}"/></linearGradient>
    <linearGradient id="red" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{T['acento']}" stop-opacity="0.25"/>
      <stop offset="0.5" stop-color="{T['acento']}"/>
      <stop offset="1" stop-color="{T['acento']}" stop-opacity="0.25"/></linearGradient></defs>
  <rect width="{w}" height="{h}" fill="url(#bg)"/>
  <rect x="0" y="0" width="{w}" height="3" fill="url(#red)"/>''']
    m, n = 10, 22
    p.append(f'''  <g stroke="{T['acento']}" stroke-width="2" fill="none" opacity="0.9">
    <path d="M{m} {m+n} L{m} {m} L{m+n} {m}"/><path d="M{w-m-n} {m} L{w-m} {m} L{w-m} {m+n}"/>
    <path d="M{m} {h-m-n} L{m} {h-m} L{m+n} {h-m}"/><path d="M{w-m-n} {h-m} L{w-m} {h-m} L{w-m} {h-m-n}"/></g>''')

    ICO = 56
    for gi, (rot, itens) in enumerate(GRUPOS):
        y = topo + gi*lin_h
        p.append(f'  <text x="{w//2}" y="{y+26}" text-anchor="middle" font-family="{MONO}" '
                 f'font-size="19" font-weight="700" fill="{T["rot"]}" letter-spacing="5">{rot}</text>')
        p.append(f'  <line x1="{w//2-300}" y1="{y+40}" x2="{w//2+300}" y2="{y+40}" '
                 f'stroke="{T["linha"]}" stroke-width="1.2" opacity="0.7"/>')
        nq = len(itens)
        larg = min(1140, nq*172)
        passo = larg/nq
        x0 = (w-larg)/2 + passo/2
        for i, (arq, titulo, rotulo) in enumerate(itens):
            cx = x0 + i*passo
            cor = clarear(por_titulo[titulo]['hex'], tema)
            esc = ICO/24
            p.append(f'  <g transform="translate({cx-ICO/2:.1f},{y+58}) scale({esc:.4f})">'
                     f'<path d="{traco(arq)}" fill="{cor}"/></g>')
            p.append(f'  <text x="{cx:.1f}" y="{y+142}" text-anchor="middle" font-family="{MONO}" '
                     f'font-size="17" fill="{T["nome"]}">{rotulo}</text>')
    p.append('</svg>')
    suf = "" if tema == "dark" else "-light"
    (OUT / f'stack{suf}.svg').write_text('\n'.join(p))

for t in TEMAS: faixa(t)
print("stack.svg e stack-light.svg gerados")
