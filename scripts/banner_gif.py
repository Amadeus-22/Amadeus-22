#!/usr/bin/env python3
"""Banner em GIF. A foto do laboratório ganha vida quadro a quadro: os robôs
viram a cabeça, digitam, soldam e apontam; os LEDs dos racks piscam, pacotes
andam pelo roadmap e o ponteiro vermelho pulsa no mapa.

O movimento é uma deformação da própria foto: cada parte gira em torno de um
pivô, e o deslocamento cai a zero numa faixa em volta dela. Nada é recortado e
colado nem misturado com a imagem parada, então não há fantasma nem borrão.

Tudo tem período que divide o laço de 4 s, então o GIF recomeça sem salto.

    python3 scripts/banner_gif.py            # gera assets/profile-banner.gif
    python3 scripts/banner_gif.py 960        # largura menor, arquivo menor
"""
import math
import pathlib
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

RAIZ = pathlib.Path(__file__).resolve().parent.parent
FOTO = RAIZ / 'assets' / 'profile-banner.jpg'
SAIDA = RAIZ / 'assets' / 'profile-banner.gif'
W, H = 1280, 633
LACO = 4.0      # segundos
FPS = 15
N = int(LACO * FPS)

TELAS = {
    'arq':     [(360, 240), (545, 229), (547, 478), (362, 497)],
    'codigo':  [(549, 226), (772, 213), (772, 392), (549, 404)],
    'rede':    [(779, 212), (962, 204), (964, 372), (781, 386)],
    'roadmap': [(902, 42), (1254, 18), (1250, 288), (1112, 278), (1112, 168), (1006, 168), (1006, 268), (906, 262)],
    'calib':   [(259, 331), (361, 323), (361, 441), (262, 452)],
    'rack1':   [(163, 43), (268, 49), (268, 205), (163, 200)],
    'rack2':   [(410, 63), (487, 67), (487, 205), (410, 203)],
}

VERDE, AMBAR, AZUL = (73, 255, 157), (255, 182, 72), (111, 211, 255)
# (x, y, cor, fase em s, período em s)
LEDS = [
    (22, 78, VERDE, 0.0, 1.0), (22, 118, VERDE, 0.6, 2.0), (22, 158, AMBAR, 1.1, 4.0),
    (22, 196, VERDE, 1.7, 4.0), (22, 236, VERDE, 0.3, 2.0), (22, 318, AZUL, 0.9, 4.0),
    (22, 398, VERDE, 1.4, 2.0), (22, 438, AMBAR, 0.2, 4.0), (138, 96, VERDE, 0.5, 4.0),
    (300, 92, VERDE, 0.8, 2.0), (300, 132, AZUL, 0.1, 4.0), (300, 170, VERDE, 1.5, 2.0),
    (452, 222, VERDE, 1.0, 1.0), (470, 236, AMBAR, 0.4, 4.0), (512, 84, VERDE, 0.7, 2.0),
    (560, 100, VERDE, 1.6, 4.0), (596, 96, AZUL, 0.2, 2.0), (652, 110, VERDE, 1.2, 1.0),
    (652, 168, AMBAR, 0.5, 4.0), (716, 118, VERDE, 0.9, 2.0),
]
LUZES = [(197, 291, 8, 0.0), (1052, 214, 10, 1.0), (826, 458, 7, 2.0), (124, 108, 6, 0.5)]
ROTA = [(934, 104), (1004, 110), (1006, 134), (1070, 132), (1072, 160), (1140, 158), (1142, 206), (1206, 204)]

# Partes que se mexem. Cada uma gira em torno de um pivô e pode se deslocar.
#   forma, pivô (px, py), graus, (dx, dy) em px, período do giro em s, fase em s
# forma: ('cabeca', cx, cy, rx, ry, limiar) recorta a cabeça clara do fundo
# escuro pelo limiar de luminância (None usa a elipse, para a cabeça diante do
# quadro claro, onde o brilho não separa nada); ('elipse', cx, cy, rx, ry)
# é a própria elipse. O aceno (dy) das cabeças corre no dobro do ritmo do giro.
PARTES = [
    # cabeças: robô em pé à direita, sentado, grande à esquerda e a fila do fundo
    (('cabeca', 1058, 213, 48, 57, None), (1080, 286), 7.0, (0, 1.8), 4.0, 0.0),
    (('cabeca', 222, 286, 50, 56, 105), (230, 354), 8.0, (0, 2.0), 4.0, 1.5),
    (('cabeca', 105, 126, 33, 40, 105), (106, 180), 9.0, (0, 1.8), 4.0, 0.5),
    (('cabeca', 372, 122, 30, 36, 105), (373, 170), 10.0, (0, 1.8), 4.0, 2.5),
    (('cabeca', 512, 126, 27, 33, 105), (513, 172), 10.0, (0, 1.6), 4.0, 1.2),
    (('cabeca', 605, 130, 25, 31, 105), (606, 174), 10.0, (0, 1.6), 4.0, 3.3),
    (('cabeca', 687, 136, 23, 29, 105), (688, 178), 10.0, (0, 1.4), 4.0, 0.4),
    (('cabeca', 748, 141, 21, 27, 105), (749, 180), 10.0, (0, 1.4), 4.0, 2.0),
    (('cabeca', 802, 144, 20, 26, 105), (803, 182), 10.0, (0, 1.4), 4.0, 3.0),
    # braços e mãos
    (('elipse', 962, 298, 70, 30), (1034, 326), 3.0, (0, 0), 2.0, 0.4),      # antebraço que aponta o mapa
    (('elipse', 925, 398, 34, 24), (960, 410), 1.6, (0, 1.2), 4.0, 1.5),     # tablet na mão
    (('elipse', 250, 462, 42, 24), (205, 455), 0.0, (3.2, 1.6), 1.0, 0.0),   # mão com o ferro de solda
    (('elipse', 308, 466, 26, 18), (308, 466), 0.0, (1.4, 1.2), 1.0, 0.5),   # a outra mão, na placa
    (('elipse', 650, 512, 36, 20), (650, 512), 0.0, (0, 3.2), 0.5, 0.00),    # mãos digitando, em contratempo
    (('elipse', 736, 482, 32, 18), (736, 482), 0.0, (0, 3.2), 0.5, 0.25),
]
QUEDA = 9       # largura, em px, da faixa onde o deslocamento cai a zero


def mascara_poligono(p):
    m = Image.new('L', (W, H), 0)
    ImageDraw.Draw(m).polygon(p, fill=255)
    return np.asarray(m, dtype=np.float32) / 255.0


def caixa(p):
    xs, ys = [x for x, _ in p], [y for _, y in p]
    return min(xs), min(ys), max(xs), max(ys)


def onda(t, periodo, fase=0.0):
    """0..1..0 suave, com o período dado."""
    return 0.5 - 0.5 * math.cos(2 * math.pi * (t + fase) / periodo)


def preparar_partes(base):
    """Para cada parte: a região da foto, o peso do movimento e a grade de pixels."""
    lum = np.asarray(base.convert('L'), dtype=np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    prontas = []
    for forma, (px, py), graus, desloc, periodo, fase in PARTES:
        tipo, cx, cy, rx, ry = forma[:5]
        dentro = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1.0
        rigido = dentro
        if tipo == 'cabeca':
            limiar = forma[5]
            if limiar is not None:
                # A parte clara dá o contorno; o casco convexo dela traz junto o
                # que é escuro mas faz parte da cabeça (orelha, sombra, nuca).
                claro = dentro & (lum > limiar)
                claro = ndimage.binary_closing(claro, iterations=4)
                rotulos, n = ndimage.label(claro)
                if n > 1:
                    tam = ndimage.sum(claro, rotulos, range(1, n + 1))
                    claro = rotulos == (1 + int(np.argmax(tam)))
                casco = np.zeros((H, W), dtype=np.uint8)
                cv2.fillConvexPoly(casco, cv2.convexHull(cv2.findNonZero(claro.astype(np.uint8))), 1)
                rigido = casco.astype(bool)
            # O pescoço entra junto: perto do pivô o giro quase não desloca nada.
            queixo = cy + ry * 0.8
            u = np.clip((yy - queixo) / max(py - queixo, 1.0), 0, 1)
            rigido = rigido | ((yy >= queixo) & (yy <= py) & (np.abs(xx - (cx + (px - cx) * u)) <= rx * 0.6))
            rigido = ndimage.binary_dilation(rigido, iterations=2)
        # Peso 1 dentro da parte, caindo suave até 0 a QUEDA pixels dela.
        dist = ndimage.distance_transform_edt(~rigido)
        peso = np.clip(1 - dist / QUEDA, 0, 1)
        peso = (peso * peso * (3 - 2 * peso)).astype(np.float32)
        ys, xs = np.nonzero(peso > 0)
        x0, x1 = max(xs.min() - 4, 0), min(xs.max() + 5, W)
        y0, y1 = max(ys.min() - 4, 0), min(ys.max() + 5, H)
        prontas.append((slice(y0, y1), slice(x0, x1), peso[y0:y1, x0:x1], xx[y0:y1, x0:x1], yy[y0:y1, x0:x1],
                        (px, py), graus, desloc, periodo, fase, tipo))
    return prontas


def mover(base_arr, partes, t):
    """Deforma a foto: cada parte no seu ângulo, com o entorno acompanhando de leve."""
    arr = base_arr.copy()
    for sy, sx, peso, gx, gy, (px, py), graus, (ax, ay), periodo, fase, tipo in partes:
        s = math.sin(2 * math.pi * (t + fase) / periodo)
        ang = math.radians(graus) * s
        if tipo == 'cabeca':
            dx, dy = 0.0, ay * math.sin(2 * math.pi * (t + fase) / (periodo / 2))
        else:
            dx, dy = ax * s, (ay * math.cos(2 * math.pi * (t + fase) / periodo) if ax and ay else ay * s)
        # De onde vem cada pixel se a parte fosse rígida: giro inverso em torno do pivô.
        ca, sa = math.cos(ang), math.sin(ang)
        rx_, ry_ = gx - px - dx, gy - py - dy
        ox = ca * rx_ + sa * ry_ + px
        oy = -sa * rx_ + ca * ry_ + py
        # O peso mistura a posição de origem com a própria posição: é isso que
        # estica o entorno em vez de sobrepor duas imagens.
        mapa_x = (gx + peso * (ox - gx)).astype(np.float32)
        mapa_y = (gy + peso * (oy - gy)).astype(np.float32)
        arr[sy, sx] = cv2.remap(arr, mapa_x, mapa_y, cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    return arr


def luzes(t, mascaras):
    """Camada RGBA com tudo o que é luz: telas, LEDs, pulsos, pacotes."""
    cam = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(cam, 'RGBA')

    # ponteiro vermelho
    for k in range(2):
        f = ((t + k * 1.0) % 2.0) / 2.0
        r = 5 + 17 * f
        d.ellipse((889 - r, 272 - r, 889 + r, 272 + r), outline=(255, 89, 100, int(230 * (1 - f))), width=2)
    d.ellipse((886.4, 269.4, 891.6, 274.6), fill=(255, 217, 220, 255))

    # pacotes no roadmap
    comp = [math.dist(a, b) for a, b in zip(ROTA, ROTA[1:])]
    total = sum(comp)
    for k in range(3):
        f = ((t + k * LACO / 3) % LACO) / LACO
        alfa = int(255 * min(f / 0.08, 1.0, (1 - f) / 0.1))
        alvo, i = f * total, 0
        while i < len(comp) - 1 and alvo > comp[i]:
            alvo -= comp[i]
            i += 1
        (xa, ya), (xb, yb) = ROTA[i], ROTA[i + 1]
        u = alvo / comp[i]
        x, y = xa + (xb - xa) * u, ya + (yb - ya) * u
        d.ellipse((x - 3.4, y - 3.4, x + 3.4, y + 3.4), fill=(230, 248, 255, alfa))

    # LEDs
    for x, y, cor, fase, periodo in LEDS:
        aceso = ((t + fase) % periodo) < periodo * 0.55
        d.rounded_rectangle((x, y, x + 5, y + 2.6), radius=1, fill=cor + (245 if aceso else 40,))

    # faísca do ferro de solda
    f = (t % 1.0)
    if f < 0.2 or 0.5 <= f < 0.7:
        d.ellipse((265, 466, 279, 480), fill=(255, 182, 72, 90))
        d.ellipse((269.8, 470.8, 274.2, 475.2), fill=(255, 243, 196, 255))

    arr = np.asarray(cam, dtype=np.float32)

    extra = np.zeros((H, W, 4), dtype=np.float32)

    # halos nos robôs
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    for x, y, r, fase in LUZES:
        forca = 0.15 + 0.6 * onda(t, 2.0, fase)
        raio = r * (0.8 + 0.45 * onda(t, 2.0, fase))
        a = np.clip(1 - np.hypot(xx - x, yy - y) / raio, 0, 1) * forca
        extra[..., 0] = np.where(a > extra[..., 3] / 255, 143, extra[..., 0])
        extra[..., 1] = np.where(a > extra[..., 3] / 255, 224, extra[..., 1])
        extra[..., 2] = np.where(a > extra[..., 3] / 255, 255, extra[..., 2])
        extra[..., 3] = np.maximum(extra[..., 3], a * 255)

    return extra, arr


def compor(fundo, camada):
    a = camada[..., 3:4] / 255.0
    return fundo * (1 - a) + camada[..., :3] * a


def gerar(largura):
    base = Image.open(FOTO).convert('RGB')
    mascaras = {n: mascara_poligono(p) for n, p in TELAS.items()}
    partes = preparar_partes(base)
    base_arr = np.asarray(base, dtype=np.float32)
    escala = largura / W
    tam = (largura, round(H * escala))

    quadros = []
    for k in range(N):
        t = k / FPS
        arr = mover(base_arr, partes, t)
        extra, desenho = luzes(t, mascaras)
        arr = compor(compor(arr, extra), desenho)
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
        if tam != (W, H):
            img = img.resize(tam, Image.LANCZOS)
        quadros.append(img)

    # Uma paleta só para todos os quadros, tirada de uma amostra do laço, e sem
    # pontilhado: o pontilhado muda de quadro para quadro e a foto "ferve".
    amostra = Image.new('RGB', (tam[0], tam[1] * 4))
    for i, k in enumerate((0, N // 4, N // 2, 3 * N // 4)):
        amostra.paste(quadros[k], (0, tam[1] * i))
    paleta = amostra.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    indexados = [np.asarray(q.quantize(palette=paleta, dither=Image.Dither.NONE)) for q in quadros]

    # Do segundo quadro em diante só vai o que mudou; o resto fica transparente
    # (índice 255) e o quadro anterior continua na tela.
    TRANSP = 255
    saida = [Image.fromarray(indexados[0], 'P')]
    for ant, atual in zip(indexados, indexados[1:]):
        delta = np.where(atual == ant, TRANSP, atual).astype(np.uint8)
        saida.append(Image.fromarray(delta, 'P'))
    pal = paleta.getpalette()[:255 * 3] + [0, 0, 0]
    for q in saida:
        q.putpalette(pal)

    saida[0].save(SAIDA, save_all=True, append_images=saida[1:], duration=int(1000 / FPS), loop=0,
                  transparency=TRANSP, disposal=1, optimize=False)
    print(f'{SAIDA.relative_to(RAIZ)}: {tam[0]}x{tam[1]}, {N} quadros, {SAIDA.stat().st_size / 1e6:.2f} MB')


if __name__ == '__main__':
    gerar(int(sys.argv[1]) if len(sys.argv) > 1 else W)
