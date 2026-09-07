#!/usr/bin/env python3
"""Placas do README em dois temas. Fontes dimensionadas para o tamanho RENDERIZADO.

O GitHub exibe o README a ~756px de largura. Uma placa de 1280px é reduzida a
0,59; uma de 628px (meia coluna) a 0,29. Uma fonte de 13,5 no SVG chegava ao
olho como 8px. Os tamanhos aqui são escolhidos pelo resultado final, não pelo
número no arquivo.
"""
import pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / 'assets'
MONO = "Consolas, 'DejaVu Sans Mono', 'Courier New', monospace"
VERM = "#ff3b30"
VERM_CLARO = "#c1121f"

TEMAS = {
    "dark":  dict(bg1="#0b0f16", bg2="#070a10", bg3="#0d1219", grade="#39506b", grade_op=0.20,
                  scan="#8fc7ff", scan_op=0.045, titulo="#eef4fb", corpo="#a8bcd2",
                  fraco="#8ea3bb", linha="#39506b", acento=VERM),
    "light": dict(bg1="#eef1f5", bg2="#e6eaf0", bg3="#dfe4ec", grade="#8fa2bb", grade_op=0.30,
                  scan="#39506b", scan_op=0.030, titulo="#111820", corpo="#33414f",
                  fraco="#4a5a6b", linha="#8fa2bb", acento=VERM_CLARO),
}

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def base(w, h, T, idp, seed=1):
    return f'''  <defs>
    <linearGradient id="red{idp}" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{T['acento']}" stop-opacity="0.25"/>
      <stop offset="0.5" stop-color="{T['acento']}"/>
      <stop offset="1" stop-color="{T['acento']}" stop-opacity="0.25"/>
    </linearGradient>
  </defs>
'''

def cantos(w, h, T, n=26, sw=2.2):
    m = 10
    return f'''  <g stroke="{T['acento']}" stroke-width="{sw}" fill="none" opacity="0.9">
    <path d="M{m} {m+n} L{m} {m} L{m+n} {m}"/><path d="M{w-m-n} {m} L{w-m} {m} L{w-m} {m+n}"/>
    <path d="M{m} {h-m-n} L{m} {h-m} L{m+n} {h-m}"/><path d="M{w-m-n} {h-m} L{w-m} {h-m} L{w-m} {h-m-n}"/>
  </g>
'''

def titulo(txt, arq, idp, tema):
    T = TEMAS[tema]
    w, h = 1280, 104          # mais alto: a fonte cresceu
    s = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t">
  <title id="t">{esc(txt)}</title>
{base(w, h, T, idp)}{cantos(w, h, T, n=22, sw=2.2)}  <rect x="0" y="0" width="{w}" height="3" fill="url(#red{idp})"/>
  <rect x="0" y="{h-3}" width="{w}" height="3" fill="url(#red{idp})" opacity="0.6"/>
  <g fill="{T['acento']}"><rect x="62" y="{h//2-15}" width="6" height="30"/><rect x="78" y="{h//2-8}" width="6" height="16"/></g>
  <text x="106" y="{h//2+13}" font-family="{MONO}" font-size="38" font-weight="700"
        fill="{T['titulo']}" letter-spacing="9">{esc(txt.upper())}</text>
</svg>
'''
    (OUT / arq).write_text(s)

def quebrar(t, n):
    ps, ls, cur = t.split(), [], ""
    for w_ in ps:
        if len(cur) + len(w_) + 1 <= n: cur = (cur + " " + w_).strip()
        else: ls.append(cur); cur = w_
    if cur: ls.append(cur)
    return ls

def card(tit, corpo, arq, idp, tema, w=628, h=300):
    T = TEMAS[tema]
    linhas = quebrar(corpo, 40)          # menos caracteres por linha, fonte maior
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t">',
         f'  <title id="t">{esc(tit)} — {esc(corpo)}</title>',
         base(w, h, T, idp), cantos(w, h, T, n=18, sw=2.0),
         f'  <rect x="0" y="0" width="{w}" height="3" fill="url(#red{idp})"/>',
         f'  <g fill="{T["acento"]}"><rect x="36" y="40" width="6" height="24"/></g>',
         f'  <text x="54" y="60" font-family="{MONO}" font-size="26" font-weight="700" '
         f'fill="{T["titulo"]}" letter-spacing="1.6">{esc(tit.upper())}</text>',
         f'  <line x1="36" y1="82" x2="{w-36}" y2="82" stroke="{T["linha"]}" stroke-width="1.4" opacity="0.8"/>']
    for i, l in enumerate(linhas[:7]):
        p.append(f'  <text x="36" y="{116 + i*30}" font-family="{MONO}" font-size="20" '
                 f'fill="{T["corpo"]}">{esc(l)}</text>')
    p.append('</svg>')
    (OUT / arq).write_text('\n'.join(p))

def glance(arq, idp, tema):
    T = TEMAS[tema]
    w, h = 1280, 150
    cel = [("QUANT","research &amp; backtesting"), ("BACKEND","Go · PHP · Python"),
           ("UTC−3","overlaps US &amp; EU hours"), ("EN · PT","working languages")]
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t">',
         '  <title id="t">Quant research and backtesting. Backend in Go, PHP and Python. UTC minus 3. English and Portugues.</title>',
         base(w, h, T, idp), cantos(w, h, T, n=20, sw=2.0),
         f'  <rect x="0" y="0" width="{w}" height="3" fill="url(#red{idp})"/>']
    for i in range(1, 4):
        x = w * i / 4
        p.append(f'  <line x1="{x}" y1="34" x2="{x}" y2="{h-34}" stroke="{T["linha"]}" stroke-width="1.2" opacity="0.7"/>')
    for i, (a, b) in enumerate(cel):
        cx = w * (i + 0.5) / 4
        p.append(f'  <text x="{cx}" y="72" text-anchor="middle" font-family="{MONO}" font-size="36" '
                 f'font-weight="700" fill="{T["titulo"]}" letter-spacing="3">{a}</text>')
        p.append(f'  <text x="{cx}" y="108" text-anchor="middle" font-family="{MONO}" font-size="19" '
                 f'fill="{T["fraco"]}">{b}</text>')
    p.append('</svg>')
    (OUT / arq).write_text('\n'.join(p))

TITULOS = [("What I work on","h-work"),("Selected work","h-selected"),("Currently","h-currently"),
           ("Stack","h-stack"),("Communities","h-communities"),("Contact","h-contact")]
CARDS = [
    ("Quantitative development","Trading strategy research and backtesting on QuantConnect. Risk modelling and predictive models on financial time series, with evaluation that separates a real edge from a curve that only looks good.","w-quant"),
    ("Backend systems in Go","Services that ship as a single static binary with no runtime dependencies. SQLite with full-text search, subprocess isolation over versioned contracts, systemd deployment.","w-go"),
    ("PHP and legacy modernisation","Working inside established codebases: registration and permission flows, scheduling, payments, and reversible database migrations on systems already carrying users.","w-php"),
    ("Data automation","Collection bots, scraping, pipelines and internal tooling. Linux and systemd, scheduled jobs, and reporting that someone actually reads.","w-data"),
]

n = 0
for tema in ("dark", "light"):
    suf = "" if tema == "dark" else "-light"
    for i, (t, f) in enumerate(TITULOS):
        titulo(t, f + suf + ".svg", f"t{i}{tema[0]}", tema); n += 1
    for i, (t, c, f) in enumerate(CARDS):
        card(t, c, f + suf + ".svg", f"c{i}{tema[0]}", tema); n += 1
    glance("at-a-glance" + suf + ".svg", f"g{tema[0]}", tema); n += 1
print(f"{n} placas geradas nos dois temas")
