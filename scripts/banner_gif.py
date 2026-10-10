#!/usr/bin/env python3
"""Banner em GIF. A foto do laboratório ganha vida quadro a quadro: os robôs
se mexem de leve (mãos digitando, ferro de solda, braço apontando, cabeças),
as telas têm varredura e brilho, os LEDs dos racks piscam, pacotes andam pelo
roadmap e o ponteiro vermelho pulsa no mapa.

Tudo tem período que divide o laço de 4 s, então o GIF recomeça sem salto.

    python3 scripts/banner_gif.py            # gera assets/profile-banner.gif
    python3 scripts/banner_gif.py 960        # largura menor, arquivo menor
"""
import math
import pathlib
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
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

# Cabeças. Cada uma é recortada da foto como um sprite, o lugar onde ela estava
# é reconstruído (inpainting) e o sprite gira em torno do pescoço por cima desse
# fundo limpo. Sem isso, a cabeça original fica parada atrás da que se move e o
# resultado é um fantasma em vez de um movimento.
#   elipse (cx, cy, rx, ry), pivô no pescoço (px, py), graus, aceno em px, fase, recorte
# recorte: limiar de luminância para separar a cabeça clara do fundo escuro, ou
# None quando o fundo também é claro e a própria elipse serve de contorno.
CABECAS = [
    ((1057, 212, 47, 58), (1080, 284), 9.0, 2.6, 0.0, None),    # robô em pé à direita
    ((222, 286, 50, 56), (230, 352), 9.0, 2.6, 1.5, 105),       # robô sentado
    ((105, 126, 33, 40), (106, 178), 11.0, 2.4, 0.5, 105),      # robô grande à esquerda
    ((372, 122, 30, 36), (373, 168), 12.0, 2.4, 2.5, 105),      # fila do fundo
    ((512, 126, 27, 33), (513, 170), 12.0, 2.2, 1.2, 105),
    ((605, 130, 25, 31), (606, 172), 12.0, 2.0, 3.3, 105),
    ((687, 136, 23, 29), (688, 176), 12.0, 2.0, 0.4, 105),
    ((748, 141, 21, 27), (749, 178), 12.0, 1.8, 2.0, 105),
    ((802, 144, 20, 26), (803, 180), 12.0, 1.8, 3.0, 105),
]
MARGEM = 26

# Mãos, braços e ombros: deslocamentos pequenos dentro de uma máscara esfumada.
#   elipse (cx, cy, rx, ry), pivô (px, py), graus, (dx, dy), período em s, fase em s
MOVIMENTOS = [
    ((968, 300, 84, 40), (1034, 326), 3.4, (0, 0), 2.0, 0.4),     # antebraço que aponta o mapa
    ((925, 398, 40, 30), (960, 410), 1.8, (0, 1.4), 4.0, 1.5),    # tablet na mão
    ((250, 462, 50, 30), (205, 455), 0.0, (3.6, 1.8), 1.0, 0.0),  # mão com o ferro de solda
    ((308, 466, 32, 24), (308, 466), 0.0, (1.6, 1.4), 1.0, 0.5),  # a outra mão, segurando a placa
    ((650, 512, 44, 26), (650, 512), 0.0, (0, 3.6), 0.5, 0.00),   # mãos digitando, em contratempo
    ((736, 482, 40, 24), (736, 482), 0.0, (0, 3.6), 0.5, 0.25),
    ((856, 448, 54, 50), (864, 528), 3.0, (0, 0), 2.0, 0.75),     # cabeça e ombros de quem digita
]


def preparar_cabecas(base):
    """Devolve a foto sem as cabeças e, para cada uma, o sprite com alfa."""
    limpa = np.asarray(base, dtype=np.uint8).copy()
    lum = np.asarray(base.convert('L'), dtype=np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    sprites = []
    for (cx, cy, rx, ry), (px, py), graus, aceno, fase, limiar in CABECAS:
        dentro = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1.0
        if limiar is None:
            cabeca = dentro
        else:
            # A parte clara dá o contorno; o casco convexo dela traz junto o que
            # é escuro mas faz parte da cabeça (orelha, sombra do rosto, nuca).
            # Sem o casco, só a parte clara girava e o resto ficava parado.
            claro = dentro & (lum > limiar)
            claro = ndimage.binary_closing(claro, iterations=4)
            rotulos, n = ndimage.label(claro)
            if n > 1:   # fica só a maior mancha: a cabeça, não um reflexo no rack
                tam = ndimage.sum(claro, rotulos, range(1, n + 1))
                claro = rotulos == (1 + int(np.argmax(tam)))
            pts = cv2.findNonZero(claro.astype(np.uint8))
            casco = np.zeros((H, W), dtype=np.uint8)
            cv2.fillConvexPoly(casco, cv2.convexHull(pts), 1)
            cabeca = casco.astype(bool)

        # Pescoço: uma faixa do queixo até o pivô, que acompanha a cabeça cada
        # vez menos conforme desce. No pivô o giro não desloca nada, então é ali
        # que o sprite pode sumir sem deixar degrau.
        queixo = cy + ry * 0.80
        u = np.clip((yy - queixo) / max(py - queixo, 1.0), 0, 1)
        centro = cx + (px - cx) * u
        meia = rx * (0.62 - 0.22 * u)
        pescoco = (yy >= queixo) & (yy <= py) & (np.abs(xx - centro) <= meia)

        alfa = ndimage.gaussian_filter((cabeca | pescoco).astype(np.float32), 1.3)
        alfa *= 1.0 - u ** 1.5

        x0, y0 = max(int(cx - rx - MARGEM), 0), max(int(cy - ry - MARGEM), 0)
        x1, y1 = min(int(cx + rx + MARGEM), W), min(int(max(cy + ry, py) + MARGEM), H)
        rgba = np.dstack([np.asarray(base, dtype=np.uint8)[y0:y1, x0:x1], (alfa[y0:y1, x0:x1] * 255).astype(np.uint8)])
        sprites.append((Image.fromarray(rgba, 'RGBA'), (x0, y0, x1, y1), (px, py), graus, aceno, fase))

        # O fundo só é reconstruído onde a cabeça estava. No pescoço fica a foto
        # original, e o sprite se mistura com ela.
        buraco = ndimage.binary_dilation(cabeca & (yy < queixo + 2), iterations=5).astype(np.uint8) * 255
        limpa[y0:y1, x0:x1] = cv2.inpaint(limpa[y0:y1, x0:x1], buraco[y0:y1, x0:x1], 6, cv2.INPAINT_TELEA)
    return limpa.astype(np.float32), sprites


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


def mover(limpa, sprites, t):
    """Põe cada cabeça no seu ângulo e depois mexe mãos, braços e ombros."""
    arr = limpa.copy()
    for sprite, (x0, y0, x1, y1), (px, py), graus, aceno, fase in sprites:
        # vira devagar de um lado para o outro (4 s) e acena no dobro do ritmo (2 s)
        ang = math.radians(graus) * math.sin(2 * math.pi * (t + fase) / 4.0)
        dy = aceno * math.sin(2 * math.pi * (t + fase) / 2.0)
        ca, sa = math.cos(ang), math.sin(ang)
        qx, qy = px - x0, py - y0
        coef = (ca, sa, qx - ca * qx - sa * (qy + dy),
                -sa, ca, qy + sa * qx - ca * (qy + dy))
        girado = np.asarray(sprite.transform(sprite.size, Image.AFFINE, coef, resample=Image.BICUBIC), dtype=np.float32)
        a = girado[..., 3:4] / 255.0
        arr[y0:y1, x0:x1] = arr[y0:y1, x0:x1] * (1 - a) + girado[..., :3] * a

    for (cx, cy, rx, ry), (px, py), graus, (ax, ay), periodo, fase in MOVIMENTOS:
        s = math.sin(2 * math.pi * (t + fase) / periodo)
        ang = math.radians(graus) * s
        dx, dy = ax * s, ay * math.cos(2 * math.pi * (t + fase) / periodo) if ax and ay else ay * s
        margem = 16
        x0, y0 = max(int(cx - rx - margem), 0), max(int(cy - ry - margem), 0)
        x1, y1 = min(int(cx + rx + margem), W), min(int(cy + ry + margem), H)
        atual = Image.fromarray(np.clip(arr[y0:y1, x0:x1], 0, 255).astype(np.uint8))
        ca, sa = math.cos(ang), math.sin(ang)
        qx, qy = px - x0, py - y0
        coef = (ca, sa, qx - ca * (qx + dx) - sa * (qy + dy),
                -sa, ca, qy + sa * (qx + dx) - ca * (qy + dy))
        movido = atual.transform(atual.size, Image.AFFINE, coef, resample=Image.BICUBIC)
        m = Image.new('L', atual.size, 0)
        ImageDraw.Draw(m).ellipse((cx - x0 - rx * 0.72, cy - y0 - ry * 0.72, cx - x0 + rx * 0.72, cy - y0 + ry * 0.72), fill=255)
        m = np.asarray(m.filter(ImageFilter.GaussianBlur(min(rx, ry) * 0.28)), dtype=np.float32)[..., None] / 255.0
        arr[y0:y1, x0:x1] = arr[y0:y1, x0:x1] * (1 - m) + np.asarray(movido, dtype=np.float32) * m
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

    # brilho e varredura das telas, direto em numpy para respeitar o contorno
    extra = np.zeros((H, W, 4), dtype=np.float32)
    ys = np.arange(H, dtype=np.float32)[:, None]
    for i, (nome, p) in enumerate(TELAS.items()):
        m = mascaras[nome]
        _, y0, _, y1 = caixa(p)
        brilho = 0.07 * onda(t, 2.0, i * 0.5)
        periodo = (4.0, 2.0, 4.0)[i % 3]
        pos = y0 - 60 + ((t + i * 0.9) % periodo) / periodo * (y1 - y0 + 60)
        faixa = np.clip(1 - np.abs(ys - (pos + 30)) / 30, 0, 1) * 0.22
        a = np.clip(brilho + faixa, 0, 1) * m
        extra[..., 0] = np.maximum(extra[..., 0], 175 * (a > 0))
        extra[..., 1] = np.maximum(extra[..., 1], 226 * (a > 0))
        extra[..., 2] = np.maximum(extra[..., 2], 255 * (a > 0))
        extra[..., 3] = np.maximum(extra[..., 3], a * 255)

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
    limpa, sprites = preparar_cabecas(base)
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
