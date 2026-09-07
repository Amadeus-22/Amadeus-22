#!/usr/bin/env python3
"""Converte texto em traçado SVG.

Fonte declarada por nome depende do que existe na máquina de quem visita, e o
GitHub é lido de Windows, Mac, Linux e celular. Em traçado o desenho é o mesmo
em todos.
"""
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

_cache = {}

def _carregar(caminho):
    if caminho not in _cache:
        f = TTFont(caminho)
        _cache[caminho] = (f, f.getGlyphSet(), f['head'].unitsPerEm,
                           f.getBestCmap(), f['hmtx'])
    return _cache[caminho]

def traçar(texto, fonte, tamanho, tracking=0.0):
    """Devolve (path_d, largura_total). tracking em fração do tamanho."""
    f, gs, upem, cmap, hmtx = _carregar(fonte)
    esc = tamanho / upem
    partes, x = [], 0.0
    for ch in texto:
        nome = cmap.get(ord(ch))
        if nome is None:
            x += tamanho * 0.5 + tamanho * tracking
            continue
        pen = SVGPathPen(gs)
        gs[nome].draw(pen)
        d = pen.getCommands()
        if d:
            # y invertido: no SVG cresce para baixo, na fonte para cima
            partes.append(f'<path transform="translate({x:.2f},0) scale({esc:.6f},{-esc:.6f})" d="{d}"/>')
        x += hmtx[nome][0] * esc + tamanho * tracking
    largura = x - tamanho * tracking if texto else 0
    return "".join(partes), largura

def bloco(texto, fonte, tamanho, cor, cx, y, tracking=0.0, opacidade=1.0):
    """Grupo centrado em cx, linha de base em y."""
    d, larg = traçar(texto, fonte, tamanho, tracking)
    return (f'<g transform="translate({cx - larg/2:.2f},{y})" fill="{cor}" '
            f'opacity="{opacidade}">{d}</g>'), larg
