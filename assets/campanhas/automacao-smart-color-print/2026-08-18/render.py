from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
LOGO = ROOT / "assets" / "logo-scp.png"
BASE = CAMPAIGN / "base-brand-v1.png"
ROLLUP = ROOT / "assets" / "trabalhos" / "rollup-evento-institucional.jpg"
BACKDROP = ROOT / "assets" / "trabalhos" / "backdrop-evento-institucional.jpg"

WIDTH = 1080
HEIGHT = 1350

NAVY = "#101935"
CYAN = "#19B3E6"
MAGENTA = "#EA1A72"
YELLOW = "#F3C515"
LIME = "#D7F04D"
OFF_WHITE = "#FFFDF8"
GRAPHITE = "#2E3443"
SOFT_CARD = (255, 253, 248, 232)

BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)


def fit_cover(source: Image.Image, width: int, height: int) -> Image.Image:
    return ImageOps.fit(source.convert("RGB"), (width, height), method=Image.Resampling.LANCZOS)


def make_canvas() -> Image.Image:
    base = fit_cover(Image.open(BASE), WIDTH, HEIGHT).convert("RGBA")
    haze = Image.new("RGBA", (WIDTH, HEIGHT), (255, 255, 255, 0))
    draw = ImageDraw.Draw(haze)
    draw.rounded_rectangle((42, 136, 1018, 1206), radius=56, fill=(255, 253, 248, 86))
    draw.rounded_rectangle((58, 156, 596, 1180), radius=48, fill=(255, 253, 248, 232))
    draw.ellipse((-120, 940, 418, 1480), fill=(25, 179, 230, 24))
    draw.ellipse((734, 954, 1178, 1416), fill=(16, 25, 53, 22))
    haze = haze.filter(ImageFilter.GaussianBlur(18))
    return Image.alpha_composite(base, haze)


def add_shadow(base: Image.Image, bounds: tuple[int, int, int, int], radius: int = 30, blur: int = 28) -> Image.Image:
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(bounds, radius=radius, fill=(10, 18, 39, 72))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(base, shadow)


def photo_card(base: Image.Image, source_path: Path, x: int, y: int, width: int, height: int, radius: int = 30) -> Image.Image:
    base = add_shadow(base, (x + 10, y + 12, x + width + 10, y + height + 12), radius=radius, blur=28)
    card = fit_cover(Image.open(source_path), width, height).convert("RGBA")
    mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, width, height), radius=radius, fill=255)
    card.putalpha(mask)
    base.alpha_composite(card, (x, y))
    return base


def place_logo(base: Image.Image) -> None:
    logo = Image.open(LOGO).convert("RGBA")
    logo_width = 248
    logo_height = round(logo.height * logo_width / logo.width)
    logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
    base.alpha_composite(logo, (64, 48))


def pill(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], fill: str, text: str, text_fill: str = OFF_WHITE) -> None:
    draw.rounded_rectangle(bounds, radius=28, fill=fill)
    draw.text((bounds[0] + 24, bounds[1] + 14), text, font=font(BOLD, 22), fill=text_fill)


def wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    x: int,
    y: int,
    width_chars: int,
    size: int,
    fill: str,
    *,
    bold: bool = False,
    spacing: int = 7,
) -> int:
    family = BOLD if bold else REGULAR
    block = textwrap.fill(text, width=width_chars, break_long_words=False, break_on_hyphens=False)
    draw.multiline_text((x, y), block, font=font(family, size), fill=fill, spacing=spacing)
    bbox = draw.multiline_textbbox((x, y), block, font=font(family, size), spacing=spacing)
    return bbox[3]


def bullet_list(draw: ImageDraw.ImageDraw, items: list[str], x: int, y: int, width_chars: int, size: int, colors: list[str]) -> int:
    cursor = y
    for index, item in enumerate(items):
        fill = colors[index % len(colors)]
        draw.rounded_rectangle((x, cursor + 8, x + 28, cursor + 36), radius=9, fill=fill)
        cursor = wrapped(draw, item, x + 50, cursor, width_chars, size, GRAPHITE, spacing=7) + 22
    return cursor


def info_card(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], title: str, body: str, accent: str) -> None:
    draw.rounded_rectangle(bounds, radius=28, fill=SOFT_CARD, outline=(16, 25, 53, 34), width=2)
    draw.rounded_rectangle((bounds[0] + 24, bounds[1] + 24, bounds[0] + 186, bounds[1] + 60), radius=18, fill=accent)
    draw.text((bounds[0] + 46, bounds[1] + 33), title, font=font(BOLD, 20), fill=NAVY)
    wrapped(draw, body, bounds[0] + 24, bounds[1] + 76, 28, 21, GRAPHITE, spacing=6)


def footer(draw: ImageDraw.ImageDraw, page: str) -> None:
    draw.rectangle((0, 1250, WIDTH, HEIGHT), fill=NAVY)
    draw.text((64, 1282), "scolorprint.com", font=font(BOLD, 30), fill=OFF_WHITE)
    draw.text((814, 1282), page, font=font(BOLD, 28), fill=OFF_WHITE)


def measurement_diagram(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    draw.rounded_rectangle((x, y, x + 300, y + 212), radius=30, fill=(255, 255, 255, 170), outline=(16, 25, 53, 36), width=2)
    draw.rounded_rectangle((x + 80, y + 46, x + 220, y + 172), radius=18, outline=NAVY, width=5)
    draw.line((x + 58, y + 38, x + 58, y + 180), fill=MAGENTA, width=5)
    draw.polygon([(x + 58, y + 32), (x + 50, y + 46), (x + 66, y + 46)], fill=MAGENTA)
    draw.polygon([(x + 58, y + 186), (x + 50, y + 172), (x + 66, y + 172)], fill=MAGENTA)
    draw.line((x + 68, y + 188, x + 232, y + 188), fill=CYAN, width=5)
    draw.polygon([(x + 60, y + 188), (x + 74, y + 180), (x + 74, y + 196)], fill=CYAN)
    draw.polygon([(x + 240, y + 188), (x + 226, y + 180), (x + 226, y + 196)], fill=CYAN)
    draw.text((x + 94, y + 18), "LARGURA", font=font(BOLD, 19), fill=CYAN)
    draw.text((x + 14, y + 98), "ALT.", font=font(BOLD, 19), fill=MAGENTA)
    draw.text((x + 102, y + 92), "PECA", font=font(BOLD, 24), fill=NAVY)


def brief_diagram(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    draw.rounded_rectangle((x, y, x + 308, y + 248), radius=30, fill=(255, 255, 255, 174), outline=(16, 25, 53, 36), width=2)
    draw.rounded_rectangle((x + 24, y + 28, x + 284, y + 64), radius=16, fill=NAVY)
    draw.text((x + 42, y + 37), "FICHEIROS DO PEDIDO", font=font(BOLD, 18), fill=OFF_WHITE)
    draw.ellipse((x + 34, y + 92, x + 92, y + 150), fill=CYAN)
    draw.text((x + 116, y + 92), "Logo", font=font(BOLD, 22), fill=NAVY)
    draw.rounded_rectangle((x + 116, y + 124, x + 262, y + 142), radius=8, fill=(16, 25, 53, 36))
    draw.rounded_rectangle((x + 34, y + 176, x + 126, y + 216), radius=14, fill=YELLOW)
    draw.text((x + 56, y + 186), "Texto", font=font(BOLD, 20), fill=NAVY)
    draw.rounded_rectangle((x + 152, y + 168, x + 274, y + 224), radius=16, fill=(25, 179, 230, 44), outline=(25, 179, 230, 90), width=2)
    draw.line((x + 166, y + 214, x + 194, y + 188, x + 218, y + 202, x + 260, y + 176), fill=NAVY, width=4)


def support_diagram(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    draw.rounded_rectangle((x, y, x + 300, y + 228), radius=30, fill=(255, 255, 255, 170), outline=(16, 25, 53, 36), width=2)
    draw.rounded_rectangle((x + 118, y + 28, x + 182, y + 182), radius=16, outline=NAVY, width=5)
    draw.line((x + 150, y + 184, x + 96, y + 214), fill=NAVY, width=5)
    draw.line((x + 150, y + 184, x + 204, y + 214), fill=NAVY, width=5)
    draw.line((x + 114, y + 182, x + 86, y + 214), fill=NAVY, width=4)
    draw.line((x + 186, y + 182, x + 214, y + 214), fill=NAVY, width=4)
    draw.rounded_rectangle((x + 28, y + 44, x + 92, y + 82), radius=14, fill=LIME)
    draw.text((x + 44, y + 54), "SO", font=font(BOLD, 18), fill=NAVY)
    draw.rounded_rectangle((x + 208, y + 44, x + 274, y + 82), radius=14, fill=YELLOW)
    draw.text((x + 218, y + 54), "KIT", font=font(BOLD, 18), fill=NAVY)
    draw.text((x + 34, y + 112), "impressao", font=font(BOLD, 18), fill=GRAPHITE)
    draw.text((x + 202, y + 112), "estrutura", font=font(BOLD, 18), fill=GRAPHITE)


def slide_one() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, BACKDROP, 620, 206, 334, 314)
    canvas = photo_card(canvas, ROLLUP, 620, 560, 162, 544)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 414, 228), MAGENTA, "TERCA | ORCAMENTO")
    draw.multiline_text(
        (66, 286),
        "ROLL-UP,\nBANNER OU\nBACKDROP?\nENVIE 4 DADOS",
        font=font(BOLD, 58),
        fill=NAVY,
        spacing=8,
    )
    draw.rectangle((68, 664, 146, 672), fill=CYAN)
    draw.rectangle((160, 664, 238, 672), fill=MAGENTA)
    draw.rectangle((252, 664, 330, 672), fill=YELLOW)
    wrapped(
        draw,
        "Quando o pedido ja chega com contexto, a orientacao fica mais clara e a proposta segue alinhada ao uso real da peca.",
        68,
        706,
        24,
        28,
        GRAPHITE,
        spacing=8,
    )
    measurement_diagram(draw, 650, 944)
    draw.rounded_rectangle((68, 1038, 472, 1114), radius=24, fill=LIME)
    draw.text((98, 1064), "GUARDE PARA O PROXIMO PEDIDO", font=font(BOLD, 22), fill=NAVY)
    footer(draw, "1/5")
    return canvas


def slide_two() -> Image.Image:
    canvas = make_canvas()
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 246, 228), NAVY, "1 | MEDIDA")
    draw.multiline_text(
        (66, 286),
        "COMECE PELA\nMEDIDA E\nORIENTACAO",
        font=font(BOLD, 58),
        fill=NAVY,
        spacing=8,
    )
    bullet_list(
        draw,
        [
            "Diga se a peca sera vertical ou horizontal.",
            "Mesmo que seja aproximado, envie largura x altura.",
            "Se houver estrutura existente, indique a area util de impressao.",
        ],
        68,
        566,
        22,
        24,
        [CYAN, MAGENTA, YELLOW],
    )
    measurement_diagram(draw, 628, 340)
    info_card(
        draw,
        (64, 980, 966, 1186),
        "Exemplo util",
        "Em vez de dizer so banner grande, ajuda mais enviar algo como 0,85 x 2,00 m ou 3 x 2,3 m.",
        LIME,
    )
    footer(draw, "2/5")
    return canvas


def slide_three() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, BACKDROP, 626, 222, 330, 654)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 222, 228), CYAN, "2 | USO", text_fill=NAVY)
    draw.multiline_text(
        (66, 286),
        "EXPLIQUE ONDE\nA PECA VAI\nFICAR",
        font=font(BOLD, 58),
        fill=NAVY,
        spacing=8,
    )
    bullet_list(
        draw,
        [
            "Interior, exterior, evento ou recepcao mudam a forma de pensar a peca.",
            "Diga se a leitura sera de perto, a media distancia ou em fotografia.",
            "Se vai atras de palco, numa parede ou junto de mesa, escreva isso no pedido.",
        ],
        68,
        574,
        22,
        24,
        [MAGENTA, YELLOW, CYAN],
    )
    info_card(
        draw,
        (64, 998, 966, 1188),
        "Porque importa",
        "Esse contexto ajuda a perceber formato, ocupacao e presenca visual.",
        YELLOW,
    )
    footer(draw, "3/5")
    return canvas


def slide_four() -> Image.Image:
    canvas = make_canvas()
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 228, 228), MAGENTA, "3 | ARTE")
    draw.multiline_text(
        (66, 286),
        "ENVIE LOGO,\nTEXTO FINAL\nE IMAGENS\nBOAS",
        font=font(BOLD, 56),
        fill=NAVY,
        spacing=8,
    )
    bullet_list(
        draw,
        [
            "Mande o logotipo legivel, de preferencia num ficheiro limpo.",
            "Junte o texto exactamente como deve aparecer na peca.",
            "Se houver foto, evite capturas desfocadas ou muito comprimidas.",
        ],
        68,
        620,
        22,
        24,
        [YELLOW, CYAN, MAGENTA],
    )
    brief_diagram(draw, 628, 350)
    info_card(
        draw,
        (64, 998, 966, 1188),
        "Se ainda falta arte",
        "Mesmo sem tudo fechado, diga o que ja existe e o que ainda esta em falta para orientar melhor a conversa.",
        CYAN,
    )
    footer(draw, "4/5")
    return canvas


def slide_five() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, ROLLUP, 650, 214, 242, 734)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 242, 228), YELLOW, "4 | FECHO", text_fill=NAVY)
    draw.multiline_text(
        (66, 286),
        "DIGA SE\nPRECISA SO\nDA IMPRESSAO\nOU TAMBEM\nDA ESTRUTURA",
        font=font(BOLD, 50),
        fill=NAVY,
        spacing=8,
    )
    bullet_list(
        draw,
        [
            "No mesmo pedido, indique se precisa apenas da peca impressa ou tambem do suporte.",
            "Se houver montagem, local de uso ou reposicao, vale a pena escrever logo.",
            "Com estas 4 informacoes, a conversa comeca mais alinhada.",
        ],
        68,
        694,
        22,
        23,
        [CYAN, MAGENTA, YELLOW],
    )
    support_diagram(draw, 626, 970)
    draw.rounded_rectangle((68, 1088, 482, 1162), radius=24, fill=LIME)
    draw.text((112, 1113), "COMENTE 'EVENTO' OU PECA ORCAMENTO", font=font(BOLD, 20), fill=NAVY)
    footer(draw, "5/5")
    return canvas


SLIDES = [
    ("slide-01-v1.jpg", slide_one),
    ("slide-02-v1.jpg", slide_two),
    ("slide-03-v1.jpg", slide_three),
    ("slide-04-v1.jpg", slide_four),
    ("slide-05-v1.jpg", slide_five),
]


for filename, build in SLIDES:
    image = build().convert("RGB")
    image.save(CAMPAIGN / filename, quality=95, subsampling=0)
