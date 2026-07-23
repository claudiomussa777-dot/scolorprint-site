from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
BASE = CAMPAIGN / "base-abstract-v1.png"
LOGO = ROOT / "assets" / "logo-scp.png"
VINYL_STORE = ROOT / "assets" / "trabalhos" / "vinil-montra-institucional.jpg"
VINYL_CUT = ROOT / "assets" / "trabalhos" / "autocolantes-recorte-vinil.jpg"

WIDTH = 1080
HEIGHT = 1350

NAVY = "#10152D"
CYAN = "#19A6D2"
MAGENTA = "#E91573"
YELLOW = "#F5C400"
LIME = "#DFFF38"
OFF_WHITE = "#FFFDF7"
GRAPHITE = "#31333D"

BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)


def fit_cover(source: Image.Image, width: int, height: int) -> Image.Image:
    source = source.convert("RGB")
    return ImageOps.fit(source, (width, height), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))


def add_shadow(base: Image.Image, bounds: tuple[int, int, int, int], radius: int = 26, blur: int = 24) -> Image.Image:
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    draw.rounded_rectangle(bounds, radius=radius, fill=(8, 17, 42, 60))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(base, shadow)


def rounded_card(image: Image.Image, size: tuple[int, int], radius: int = 32) -> Image.Image:
    card = fit_cover(image, *size).convert("RGBA")
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
    card.putalpha(mask)
    return card


def add_photo_card(base: Image.Image, source_path: Path, x: int, y: int, width: int, height: int, radius: int = 32) -> Image.Image:
    bounds = (x + 12, y + 18, x + width + 12, y + height + 18)
    base = add_shadow(base, bounds, radius=radius, blur=28)
    card = rounded_card(Image.open(source_path), (width, height), radius=radius)
    base.alpha_composite(card, (x, y))
    return base


def place_logo(base: Image.Image) -> None:
    logo = Image.open(LOGO).convert("RGBA")
    logo_width = 250
    logo_height = round(logo.height * logo_width / logo.width)
    logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
    base.alpha_composite(logo, (68, 56))


def pill(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], fill: str, text: str) -> None:
    draw.rounded_rectangle(bounds, radius=28, fill=fill)
    draw.text((bounds[0] + 24, bounds[1] + 15), text, font=font(BOLD, 23), fill=OFF_WHITE)


def footer(draw: ImageDraw.ImageDraw, page: str) -> None:
    draw.rectangle((0, 1250, WIDTH, HEIGHT), fill=NAVY)
    draw.text((66, 1283), "scolorprint.com", font=font(BOLD, 30), fill=OFF_WHITE)
    draw.text((810, 1283), page, font=font(BOLD, 28), fill=OFF_WHITE)


def wrapped(draw: ImageDraw.ImageDraw, text: str, x: int, y: int, width_chars: int, size: int, fill: str, bold: bool = False, spacing: int = 8) -> int:
    family = BOLD if bold else REGULAR
    block = textwrap.fill(text, width=width_chars)
    draw.multiline_text((x, y), block, font=font(family, size), fill=fill, spacing=spacing)
    bbox = draw.multiline_textbbox((x, y), block, font=font(family, size), spacing=spacing)
    return bbox[3]


def make_base() -> Image.Image:
    return fit_cover(Image.open(BASE), WIDTH, HEIGHT).convert("RGBA")


def slide_one() -> Image.Image:
    canvas = make_base()
    canvas = add_photo_card(canvas, VINYL_STORE, 642, 222, 350, 710)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (70, 176, 392, 232), MAGENTA, "QUINTA | VINIL E MONTRAS")
    draw.multiline_text(
        (70, 274),
        "A SUA MONTRA\nESTA A DIZER O\nQUE A MARCA\nPRECISA?",
        font=font(BOLD, 63),
        fill=NAVY,
        spacing=8,
    )
    draw.rectangle((72, 640, 150, 648), fill=CYAN)
    draw.rectangle((162, 640, 228, 648), fill=MAGENTA)
    draw.rectangle((240, 640, 294, 648), fill=YELLOW)
    wrapped(
        draw,
        "Quando o espaço está vazio ou pouco legível, a comunicação perde força antes mesmo do primeiro contacto.",
        72,
        684,
        22,
        29,
        GRAPHITE,
        spacing=9,
    )
    draw.rounded_rectangle((72, 912, 472, 986), radius=24, fill=LIME)
    draw.text((102, 937), "VER O PROBLEMA + SOLUCAO", font=font(BOLD, 24), fill=NAVY)
    footer(draw, "1/4")
    return canvas


def slide_two() -> Image.Image:
    canvas = make_base()
    canvas = add_photo_card(canvas, VINYL_CUT, 646, 186, 330, 916)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (70, 176, 250, 232), NAVY, "PROBLEMA")
    draw.multiline_text(
        (70, 282),
        "SEM VINIL\nBEM PENSADO,",
        font=font(BOLD, 58),
        fill=NAVY,
        spacing=8,
    )
    points = [
        "A marca demora mais a ser identificada.",
        "Promocoes e orientações passam despercebidas.",
        "Portas e vitrines ficam sem função comercial clara.",
    ]
    y = 504
    for point, fill in zip(points, [MAGENTA, CYAN, YELLOW]):
        draw.rounded_rectangle((72, y + 10, 104, y + 42), radius=10, fill=fill)
        y = wrapped(draw, point, 126, y, 23, 28, GRAPHITE, spacing=8) + 42
    draw.rounded_rectangle((70, 1056, 566, 1194), radius=28, fill=(255, 253, 247, 220), outline=NAVY, width=3)
    wrapped(
        draw,
        "Aqui o foco está na produção: corte limpo para facilitar a aplicação final.",
        96,
        1084,
        25,
        22,
        NAVY,
        spacing=7,
    )
    footer(draw, "2/4")
    return canvas


def slide_three() -> Image.Image:
    canvas = make_base()
    canvas = add_photo_card(canvas, VINYL_STORE, 70, 736, 940, 398)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (70, 176, 236, 232), CYAN, "SOLUCAO")
    draw.multiline_text(
        (70, 282),
        "COM VINIL,\nA MONTRA PODE:",
        font=font(BOLD, 58),
        fill=NAVY,
        spacing=8,
    )
    items = [
        "Dar presença imediata à entrada.",
        "Reforçar campanhas, horários ou identidade visual.",
        "Aproveitar vidro e paredes sem obras pesadas.",
    ]
    y = 474
    for item in items:
        draw.rounded_rectangle((74, y + 12, 98, y + 36), radius=8, fill=LIME)
        y = wrapped(draw, item, 122, y, 32, 27, GRAPHITE, spacing=7) + 22
    draw.rounded_rectangle((630, 672, 1000, 720), radius=18, fill=NAVY)
    draw.text((658, 685), "EXEMPLO REAL DE APLICACAO", font=font(BOLD, 22), fill=OFF_WHITE)
    footer(draw, "3/4")
    return canvas


def slide_four() -> Image.Image:
    canvas = make_base()
    canvas = add_photo_card(canvas, VINYL_STORE, 634, 232, 330, 284)
    canvas = add_photo_card(canvas, VINYL_CUT, 634, 548, 330, 360)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (70, 176, 262, 232), MAGENTA, "PROXIMO PASSO")
    draw.multiline_text(
        (70, 282),
        "SE O SEU ESPACO\nPRECISA DE MAIS\nPRESENCA,",
        font=font(BOLD, 59),
        fill=NAVY,
        spacing=8,
    )
    wrapped(
        draw,
        "Podemos estudar vinil para montras, portas, sinalética e comunicação de campanha conforme o local.",
        70,
        560,
        24,
        28,
        GRAPHITE,
        spacing=8,
    )
    draw.rounded_rectangle((70, 792, 516, 870), radius=24, fill=LIME)
    draw.text((102, 818), "PEDIR ORCAMENTO  ->", font=font(BOLD, 28), fill=NAVY)
    wrapped(
        draw,
        "Comente 'vinil' ou fale connosco em scolorprint.com.",
        70,
        930,
        26,
        27,
        NAVY,
        bold=True,
        spacing=8,
    )
    footer(draw, "4/4")
    return canvas


def main() -> None:
    slides = [slide_one(), slide_two(), slide_three(), slide_four()]
    for index, slide in enumerate(slides, start=1):
        output = CAMPAIGN / f"slide-{index:02d}-v1.jpg"
        slide.convert("RGB").save(output, "JPEG", quality=93, optimize=True, progressive=True)
        print(output)


if __name__ == "__main__":
    main()
