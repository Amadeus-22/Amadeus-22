#!/usr/bin/env python3
"""Banner em GIF. A foto do laboratório ganha vida quadro a quadro: os robôs
viram a cabeça, digitam, soldam e apontam; os LEDs dos racks piscam, pacotes
andam pelo roadmap e o ponteiro vermelho pulsa no mapa.

Cada parte que se mexe é recortada da foto pelo seu contorno real (GrabCut), e
só ela gira, em torno da junta: o pescoço para as cabeças, o pulso para as mãos.
O fundo fica parado. Onde a parte estava, a foto é reconstruída, mas essa área
fica quase toda coberta e só aparece numa lasca de poucos pixels.

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

# Partes que se mexem.
#   elipse em volta da parte (cx, cy, rx, ry): é só o ponto de partida do recorte
#   junta (px, py): onde ela gira; None usa o meio da base do recorte (pescoço)
#   graus do giro, período em s, fase em s
PARTES = [
    # cabeças: robô em pé à direita, sentado, grande à esquerda e a fila do fundo
    ((1058, 213, 50, 60), (1072, 262), 7.0, 4.0, 0.0),
    ((222, 286, 52, 58), (228, 340), 7.0, 4.0, 1.5),
    ((105, 126, 34, 42), None, 8.0, 4.0, 0.5),
    ((372, 122, 31, 38), None, 9.0, 4.0, 2.5),
    ((512, 126, 28, 35), None, 9.0, 4.0, 1.2),
    ((605, 130, 26, 33), None, 9.0, 4.0, 3.3),
    ((687, 136, 24, 31), None, 9.0, 4.0, 0.4),
    ((748, 141, 22, 29), None, 9.0, 4.0, 2.0),
    ((802, 144, 21, 28), None, 9.0, 4.0, 3.0),
    # mãos, girando no pulso
    ((650, 512, 40, 24), (679, 523), 5.0, 0.5, 0.00),     # mão esquerda digitando
    ((736, 482, 36, 22), (756, 479), 5.0, 0.5, 0.25),     # mão direita, em contratempo
    ((250, 462, 46, 28), (202, 470), 2.5, 1.0, 0.0),      # mão com o ferro de solda
    ((940, 290, 52, 26), (975, 305), 3.5, 2.0, 0.4),      # mão que aponta o mapa
]
MARGEM = 20


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
    """Recorta cada parte e devolve a foto sem elas mais a lista de sprites."""
    bgr = cv2.cvtColor(np.asarray(base, dtype=np.uint8), cv2.COLOR_RGB2BGR)
    limpa = bgr.copy()
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    sprites = []
    for (cx, cy, rx, ry), junta, graus, periodo, fase in PARTES:
        x0, y0 = max(int(cx - rx - MARGEM), 0), max(int(cy - ry - MARGEM), 0)
        x1, y1 = min(int(cx + rx + MARGEM), W), min(int(cy + ry + MARGEM), H)
        e = ((xx[y0:y1, x0:x1] - cx) / rx) ** 2 + ((yy[y0:y1, x0:x1] - cy) / ry) ** 2
        # GrabCut: o miolo da elipse é a parte com certeza, a borda é "talvez",
        # e o algoritmo acha o contorno real pelas cores.
        marca = np.full(e.shape, cv2.GC_BGD, np.uint8)
        marca[e <= 1.25 ** 2] = cv2.GC_PR_BGD
        marca[e <= 1.0] = cv2.GC_PR_FGD
        marca[e <= 0.45 ** 2] = cv2.GC_FGD
        cv2.grabCut(bgr[y0:y1, x0:x1], marca, None, np.zeros((1, 65)), np.zeros((1, 65)), 6, cv2.GC_INIT_WITH_MASK)
        frente = (marca == cv2.GC_FGD) | (marca == cv2.GC_PR_FGD)
        rotulos, n = ndimage.label(frente)
        if n > 1:   # só a maior mancha
            frente = rotulos == (1 + int(np.argmax(ndimage.sum(frente, rotulos, range(1, n + 1)))))
        frente = ndimage.binary_fill_holes(frente)

        if junta is None:   # meio da base do recorte
            ys, xs = np.nonzero(frente)
            base_y = ys.max()
            junta = (x0 + float(xs[ys >= base_y - 3].mean()), y0 + float(base_y))

        # Borda de um pixel só de transição: nítida, sem serrilhado.
        alfa = cv2.GaussianBlur(frente.astype(np.float32), (0, 0), 0.7)
        rgb = cv2.cvtColor(bgr[y0:y1, x0:x1], cv2.COLOR_BGR2RGB).astype(np.float32)
        premult = np.dstack([rgb * alfa[..., None], alfa])   # alfa pré-multiplicado: sem franja escura ao girar
        sprites.append((premult, (x0, y0, x1, y1), junta, graus, periodo, fase))

        buraco = (ndimage.binary_dilation(frente, iterations=7)).astype(np.uint8) * 255
        limpa[y0:y1, x0:x1] = cv2.inpaint(limpa[y0:y1, x0:x1], buraco, 5, cv2.INPAINT_NS)
    return cv2.cvtColor(limpa, cv2.COLOR_BGR2RGB).astype(np.float32), sprites


def mover(limpa, sprites, t):
    """Cola cada parte, no seu ângulo, por cima do fundo parado."""
    arr = limpa.copy()
    for premult, (x0, y0, x1, y1), (px, py), graus, periodo, fase in sprites:
        ang = graus * math.sin(2 * math.pi * (t + fase) / periodo)
        m = cv2.getRotationMatrix2D((px - x0, py - y0), ang, 1.0)
        girado = cv2.warpAffine(premult, m, (x1 - x0, y1 - y0), flags=cv2.INTER_LANCZOS4,
                                borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        a = np.clip(girado[..., 3:4], 0, 1)
        arr[y0:y1, x0:x1] = arr[y0:y1, x0:x1] * (1 - a) + np.clip(girado[..., :3], 0, 255)
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
    limpa, sprites = preparar_partes(base)
    escala = largura / W
    tam = (largura, round(H * escala))

    quadros = []
    for k in range(N):
        t = k / FPS
        arr = mover(limpa, sprites, t)
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
