from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
LOGO = ROOT / "assets" / "logo-scp.png"
BASE = CAMPAIGN / "base-brand-v1.png"
KIT = ROOT / "assets" / "mockup-giftkit-real-v2.jpg"

WIDTH = 1080
HEIGHT = 1350

NAVY = "#101935"
CYAN = "#19B3E6"
MAGENTA = "#EA1A72"
YELLOW = "#F3C515"
LIME = "#DFF364"
OFF_WHITE = "#FFFDF8"
GRAPHITE = "#2E3443"
SOFT_CARD = (255, 253, 248, 234)

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
    draw.rounded_rectangle((42, 136, 1018, 1206), radius=56, fill=(255, 253, 248, 84))
    draw.rounded_rectangle((58, 156, 592, 1182), radius=48, fill=(255, 253, 248, 232))
    draw.ellipse((-140, 948, 404, 1488), fill=(25, 179, 230, 22))
    draw.ellipse((730, 958, 1178, 1422), fill=(16, 25, 53, 22))
    haze = haze.filter(ImageFilter.GaussianBlur(18))
    return Image.alpha_composite(base, haze)


def add_shadow(base: Image.Image, bounds: tuple[int, int, int, int], radius: int = 30, blur: int = 28) -> Image.Image:
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(bounds, radius=radius, fill=(10, 18, 39, 72))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(base, shadow)


def photo_card(base: Image.Image, source_path: Path, x: int, y: int, width: int, height: int, radius: int = 32) -> Image.Image:
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
    draw.rounded_rectangle((bounds[0] + 24, bounds[1] + 24, bounds[0] + 212, bounds[1] + 60), radius=18, fill=accent)
    draw.text((bounds[0] + 46, bounds[1] + 33), title, font=font(BOLD, 20), fill=NAVY)
    wrapped(draw, body, bounds[0] + 24, bounds[1] + 76, 32, 19, GRAPHITE, spacing=6)


def footer(draw: ImageDraw.ImageDraw, page: str) -> None:
    draw.rectangle((0, 1250, WIDTH, HEIGHT), fill=NAVY)
    draw.text((64, 1282), "scolorprint.com", font=font(BOLD, 30), fill=OFF_WHITE)
    draw.text((826, 1282), page, font=font(BOLD, 28), fill=OFF_WHITE)


def recipients_diagram(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    draw.rounded_rectangle((x, y, x + 316, y + 250), radius=30, fill=(255, 255, 255, 178), outline=(16, 25, 53, 36), width=2)
    draw.rounded_rectangle((x + 30, y + 28, x + 286, y + 64), radius=18, fill=NAVY)
    draw.text((x + 52, y + 37), "ONDE O KIT AJUDA", font=font(BOLD, 18), fill=OFF_WHITE)
    rows = [
        (CYAN, "Equipa", "onboarding e rotina"),
        (MAGENTA, "Oferta", "clientes e parceiros"),
        (YELLOW, "Evento", "evento e recepcao"),
    ]
    cursor = y + 92
    for color, title, body in rows:
        draw.rounded_rectangle((x + 30, cursor, x + 96, cursor + 44), radius=14, fill=color)
        draw.text((x + 46, cursor + 11), title, font=font(BOLD, 18), fill=NAVY)
        draw.text((x + 120, cursor + 13), body, font=font(REGULAR, 18), fill=GRAPHITE)
        cursor += 58


def decisions_diagram(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    draw.rounded_rectangle((x, y, x + 320, y + 276), radius=30, fill=(255, 255, 255, 176), outline=(16, 25, 53, 36), width=2)
    steps = [
        ("1", CYAN, "Quem vai receber"),
        ("2", YELLOW, "Que pecas entram"),
        ("3", MAGENTA, "Que identidade aparece"),
    ]
    cursor = y + 28
    for number, color, label in steps:
        draw.ellipse((x + 28, cursor, x + 90, cursor + 62), fill=color)
        draw.text((x + 50, cursor + 16), number, font=font(BOLD, 22), fill=NAVY)
        draw.rounded_rectangle((x + 108, cursor + 6, x + 292, cursor + 56), radius=18, fill=(255, 253, 248, 226))
        wrapped(draw, label, x + 126, cursor + 16, 18, 20, GRAPHITE, bold=True, spacing=5)
        cursor += 78


def pieces_diagram(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    draw.rounded_rectangle((x, y, x + 324, y + 266), radius=30, fill=(255, 255, 255, 176), outline=(16, 25, 53, 36), width=2)
    draw.rounded_rectangle((x + 34, y + 28, x + 288, y + 64), radius=18, fill=LIME)
    draw.text((x + 56, y + 38), "COMECAR SIMPLES", font=font(BOLD, 18), fill=NAVY)
    cards = [
        (CYAN, "Camiseta"),
        (MAGENTA, "Caneca"),
        (YELLOW, "Bloco"),
        (NAVY, "Bone"),
    ]
    positions = [(x + 34, y + 92), (x + 182, y + 92), (x + 34, y + 170), (x + 182, y + 170)]
    for (color, label), (left, top) in zip(cards, positions):
        right = left + 110
        bottom = top + 54
        draw.rounded_rectangle((left, top, right, bottom), radius=18, fill=color)
        fill = OFF_WHITE if color == NAVY else NAVY
        draw.text((left + 18, top + 17), label, font=font(BOLD, 16), fill=fill)


def slide_one() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, KIT, 620, 220, 336, 800)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 488, 228), MAGENTA, "SEXTA | PRODUTO EM FOCO")
    draw.multiline_text(
        (66, 286),
        "KITS\nCORPORATIVOS\nQUE CONTINUAM\nA CIRCULAR",
        font=font(BOLD, 58),
        fill=NAVY,
        spacing=8,
    )
    draw.rectangle((68, 682, 146, 690), fill=CYAN)
    draw.rectangle((160, 682, 238, 690), fill=YELLOW)
    draw.rectangle((252, 682, 330, 690), fill=MAGENTA)
    wrapped(
        draw,
        "Quando as pecas fazem sentido juntas, a marca fica presente no onboarding, na oferta e no evento sem depender de exagero.",
        68,
        724,
        24,
        28,
        GRAPHITE,
        spacing=8,
    )
    draw.rounded_rectangle((68, 1044, 472, 1118), radius=24, fill=LIME)
    draw.text((106, 1070), "GUARDE PARA A PROXIMA ENCOMENDA", font=font(BOLD, 20), fill=NAVY)
    footer(draw, "1/4")
    return canvas


def slide_two() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, KIT, 646, 308, 286, 360)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 300, 228), NAVY, "1 | USO")
    draw.multiline_text(
        (66, 286),
        "EM QUE CASOS\nFAZ SENTIDO?",
        font=font(BOLD, 58),
        fill=NAVY,
        spacing=8,
    )
    bullet_list(
        draw,
        [
            "Onboarding simples para receber a equipa com mais identidade.",
            "Oferta util para parceiros, clientes ou convidados.",
            "Activacoes e eventos em que a marca precisa de seguir com a pessoa.",
        ],
        68,
        524,
        22,
        24,
        [CYAN, MAGENTA, YELLOW],
    )
    recipients_diagram(draw, 620, 736)
    info_card(
        draw,
        (64, 1008, 966, 1168),
        "Boa regra",
        "Nao precisa de ser grande. Um kit curto e util ja funciona bem.",
        LIME,
    )
    footer(draw, "2/4")
    return canvas


def slide_three() -> Image.Image:
    canvas = make_canvas()
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 366, 228), CYAN, "2 | BRIEFING", text_fill=NAVY)
    draw.multiline_text(
        (66, 286),
        "COMECE POR\n3 DECISOES\nSIMPLES",
        font=font(BOLD, 58),
        fill=NAVY,
        spacing=8,
    )
    bullet_list(
        draw,
        [
            "Defina quem vai receber o kit e em que contexto.",
            "Escolha pecas com uso real para esse momento.",
            "Alinhe logo, cor principal e a mensagem que precisa de aparecer.",
        ],
        68,
        584,
        22,
        24,
        [MAGENTA, YELLOW, CYAN],
    )
    decisions_diagram(draw, 620, 344)
    info_card(
        draw,
        (64, 1002, 966, 1188),
        "O que ajuda no pedido",
        "Mesmo sem tudo fechado, estas tres decisoes ja deixam o orcamento e a conversa mais alinhados.",
        YELLOW,
    )
    footer(draw, "3/4")
    return canvas


def slide_four() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, KIT, 648, 230, 286, 522)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 264, 228), MAGENTA, "3 | CTA")
    draw.multiline_text(
        (66, 286),
        "PODE COMECAR\nSIMPLES E\nAJUSTAR\nDEPOIS",
        font=font(BOLD, 58),
        fill=NAVY,
        spacing=8,
    )
    bullet_list(
        draw,
        [
            "Camiseta, caneca, bloco ou bone entram conforme o objectivo.",
            "Nem tudo precisa de seguir junto no primeiro pedido.",
            "Com um briefing curto, o conjunto ja pode sair mais coerente.",
        ],
        68,
        666,
        22,
        23,
        [CYAN, MAGENTA, YELLOW],
    )
    pieces_diagram(draw, 620, 826)
    draw.rounded_rectangle((68, 1088, 450, 1162), radius=24, fill=LIME)
    draw.text((116, 1114), "COMENTE 'KIT' OU PECA ORCAMENTO", font=font(BOLD, 18), fill=NAVY)
    footer(draw, "4/4")
    return canvas


SLIDES = [
    ("slide-01-v1.jpg", slide_one),
    ("slide-02-v1.jpg", slide_two),
    ("slide-03-v1.jpg", slide_three),
    ("slide-04-v1.jpg", slide_four),
]


for filename, build in SLIDES:
    image = build().convert("RGB")
    image.save(CAMPAIGN / filename, quality=95, subsampling=0)
