# -*- coding: utf-8 -*-
"""Ícones e imagens de compartilhamento (Open Graph) do The Love Theory, desenhados com Pillow.
Chamado por build.py. Usa fontes do Windows quando existem; senão, a fonte padrão do Pillow."""
import math, os
from PIL import Image, ImageDraw, ImageFont

PINK_DEEP = (216, 64, 143); MAGENTA = (184, 35, 111); PINK2 = (248, 210, 224); LILAC = (205, 185, 230)
BLUE = (159, 176, 212); BLUE2 = (199, 210, 232); PAPER = (247, 239, 231); DOT = (230, 217, 208); INK = (42, 29, 44); WHITE = (255, 255, 255)
FONTS = "C:/Windows/Fonts"


def font(name, size):
    for n in name if isinstance(name, (list, tuple)) else [name]:
        p = os.path.join(FONTS, n)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def heart(draw, cx, cy, s, fill):
    """Coração paramétrico centrado em (cx, cy) com largura ~ 2*s."""
    pts = []
    for i in range(240):
        t = i / 240 * 2 * math.pi
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + x * s / 16, cy - y * s / 16 - s * 0.08))
    draw.polygon(pts, fill=fill)


def icon(size, maskable=False):
    big = size * 4
    im = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if maskable:
        d.rectangle([0, 0, big, big], fill=PINK_DEEP)
        heart(d, big / 2, big / 2, big * 0.24, WHITE)
    else:
        d.ellipse([0, 0, big - 1, big - 1], fill=PINK_DEEP)
        heart(d, big / 2, big / 2, big * 0.32, WHITE)
    return im.resize((size, size), Image.LANCZOS)


def rounded(d, box, r, fill, outline=None, width=0):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) > maxw and cur:
            lines.append(cur); cur = w
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


def og(path, kicker, title, sub, studio, url="lovetheory.biblioverse.org"):
    W, H, S = 1200, 630, 2
    im = Image.new("RGB", (W * S, H * S), PAPER)
    d = ImageDraw.Draw(im)
    for x in range(20, W * S, 32):
        for y in range(20, H * S, 32):
            d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=DOT)
    k = lambda v: int(v * S)
    # janela principal
    x0, y0, x1, y1 = 56, 56, 760, 574
    rounded(d, [k(x0 + 10), k(y0 + 10), k(x1 + 10), k(y1 + 10)], k(24), INK)
    rounded(d, [k(x0), k(y0), k(x1), k(y1)], k(24), PINK2, INK, k(3))
    d.rounded_rectangle([k(x0), k(y0), k(x1), k(y0 + 52)], radius=k(24), fill=LILAC, corners=(True, True, False, False))
    d.line([k(x0), k(y0 + 52), k(x1), k(y0 + 52)], fill=INK, width=k(3))
    d.rounded_rectangle([k(x0), k(y0), k(x1), k(y0 + 52)], radius=k(24), outline=INK, width=k(3), corners=(True, True, False, False))
    for i, c in enumerate((WHITE, (243, 180, 204), BLUE)):
        cx = x0 + 30 + i * 26
        d.ellipse([k(cx - 8), k(y0 + 18), k(cx + 8), k(y0 + 34)], fill=c, outline=INK, width=k(2))
    fs = font(["segoeuib.ttf", "arialbd.ttf"], k(18))
    d.text((k(x1 - 24), k(y0 + 26)), studio.upper(), font=fs, fill=INK, anchor="rm")
    # textos
    fk = font(["segoescb.ttf", "segoesc.ttf", "Inkfree.ttf"], k(34))
    ft = font(["segoeuib.ttf", "arialbd.ttf"], k(64))
    fsub = font(["segoeuib.ttf", "arialbd.ttf"], k(34))
    tx = x0 + 44
    d.text((k(tx), k(y0 + 92)), kicker, font=fk, fill=MAGENTA)
    y = y0 + 150
    for line in wrap(d, title, ft, k(x1 - tx - 40)):
        d.text((k(tx), k(y)), line, font=ft, fill=INK); y += 74
    d.text((k(tx), k(y + 12)), sub, font=fsub, fill=MAGENTA)
    # rodapé da janela: marca + endereço
    my = y1 - 64
    d.ellipse([k(tx), k(my), k(tx + 40), k(my + 40)], fill=PINK_DEEP)
    heart(d, k(tx + 20), k(my + 20), k(12), WHITE)
    fu = font(["segoeuib.ttf", "arialbd.ttf"], k(24))
    d.text((k(tx + 54), k(my + 20)), "The Love Theory", font=fu, fill=INK, anchor="lm")
    fu2 = font(["segoeui.ttf", "arial.ttf"], k(20))
    d.text((k(x1 - 40), k(my + 20)), url, font=fu2, fill=INK, anchor="rm")
    # painel em ponto-cruz com moldura oval e coração
    px0, py0, px1, py1 = 800, 90, 1144, 540
    rounded(d, [k(px0 + 10), k(py0 + 10), k(px1 + 10), k(py1 + 10)], k(18), INK)
    rounded(d, [k(px0), k(py0), k(px1), k(py1)], k(18), BLUE, INK, k(3))
    step = 14
    for x in range(px0 + 8, px1 - 8, step):
        for y in range(py0 + 8, py1 - 8, step):
            if (x // step + y // step) % 2 == 0:
                d.rectangle([k(x), k(y), k(x + step / 2), k(y + step / 2)], fill=BLUE2)
    ox0, oy0, ox1, oy1 = 862, 140, 1082, 490
    d.ellipse([k(ox0 - 14), k(oy0 - 14), k(ox1 + 14), k(oy1 + 14)], fill=WHITE, outline=INK, width=k(3))
    d.ellipse([k(ox0), k(oy0), k(ox1), k(oy1)], fill=LILAC, outline=INK, width=k(4))
    d.ellipse([k(ox0 + 30), k(oy0 + 40), k(ox1 - 30), k(oy1 - 40)], fill=PINK2)
    heart(d, k((ox0 + ox1) / 2), k((oy0 + oy1) / 2), k(62), PINK_DEEP)
    im.resize((W, H), Image.LANCZOS).save(path, optimize=True)


def make_all(root, langs):
    """langs: [(code, PAGES, HOME)]"""
    sizes = {"apple-touch-icon.png": 180, "icon-192.png": 192, "icon-512.png": 512, "favicon-32.png": 32}
    for name, size in sizes.items():
        icon(size).save(os.path.join(root, name), optimize=True)
    icon(512, maskable=True).save(os.path.join(root, "icon-512-maskable.png"), optimize=True)
    icon(64).save(os.path.join(root, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
    for code, PG, HOME in langs:
        og(os.path.join(root, "og-image.png" if code == "en" else "og-image-pt.png"), HOME["kicker"], HOME["title"], HOME["title2"], PG["studio"])
