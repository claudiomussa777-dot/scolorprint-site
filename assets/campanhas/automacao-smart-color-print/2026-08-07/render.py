from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
LOGO = ROOT / "assets" / "logo-scp.png"
BASE = CAMPAIGN / "base-brand-v1.png"
CAP = ROOT / "assets" / "mockup-cap-real-v2.jpg"

WIDTH = 1080
HEIGHT = 1350

NAVY = "#101935"
CYAN = "#19B3E6"
MAGENTA = "#EA1A72"
YELLOW = "#F3C515"
OFF_WHITE = "#FFFDF8"
GRAPHITE = "#2D3342"
SOFT_PANEL = (255, 253, 248, 235)
SOFT_BORDER = (16, 25, 53, 34)

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
    draw.rounded_rectangle((38, 124, 1008, 1218), radius=60, fill=(255, 253, 248, 92))
    draw.rounded_rectangle((54, 148, 566, 1172), radius=48, fill=(255, 253, 248, 222))
    draw.ellipse((744, 972, 1176, 1412), fill=(16, 25, 53, 32))
    draw.ellipse((-120, 910, 390, 1460), fill=(25, 179, 230, 24))
    haze = haze.filter(ImageFilter.GaussianBlur(18))
    return Image.alpha_composite(base, haze)


def add_shadow(base: Image.Image, bounds: tuple[int, int, int, int], radius: int = 30, blur: int = 28) -> Image.Image:
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(bounds, radius=radius, fill=(10, 18, 39, 78))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(base, shadow)


def photo_card(base: Image.Image, source_path: Path, x: int, y: int, width: int, height: int, radius: int = 34) -> Image.Image:
    base = add_shadow(base, (x + 12, y + 14, x + width + 12, y + height + 14), radius=radius, blur=28)
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
    base.alpha_composite(logo, (64, 50))


def pill(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], fill: str, text: str, text_fill: str = OFF_WHITE) -> None:
    draw.rounded_rectangle(bounds, radius=28, fill=fill)
    draw.text((bounds[0] + 24, bounds[1] + 15), text, font=font(BOLD, 22), fill=text_fill)


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
    block = textwrap.fill(text, width=width_chars)
    draw.multiline_text((x, y), block, font=font(family, size), fill=fill, spacing=spacing)
    bbox = draw.multiline_textbbox((x, y), block, font=font(family, size), spacing=spacing)
    return bbox[3]


def feature_card(draw: ImageDraw.ImageDraw, x: int, y: int, accent: str, title: str, body: str) -> None:
    draw.rounded_rectangle((x, y, x + 448, y + 150), radius=28, fill=SOFT_PANEL, outline=SOFT_BORDER, width=2)
    draw.rounded_rectangle((x + 24, y + 26, x + 122, y + 66), radius=18, fill=accent)
    draw.text((x + 44, y + 37), title, font=font(BOLD, 22), fill=NAVY)
    wrapped(draw, body, x + 24, y + 78, 35, 18, GRAPHITE, spacing=5)


def footer(draw: ImageDraw.ImageDraw) -> None:
    draw.rectangle((0, 1250, WIDTH, HEIGHT), fill=NAVY)
    draw.text((64, 1282), "scolorprint.com", font=font(BOLD, 30), fill=OFF_WHITE)
    draw.text((602, 1286), "PECAS COM IDENTIDADE", font=font(BOLD, 20), fill=OFF_WHITE)


def main() -> None:
    canvas = make_canvas()
    canvas = photo_card(canvas, CAP, 612, 188, 348, 858)
    draw = ImageDraw.Draw(canvas)

    place_logo(canvas)
    pill(draw, (64, 172, 490, 228), MAGENTA, "SEXTA | PRODUTO EM FOCO")
    draw.multiline_text(
        (66, 292),
        "BONES\nPERSONALIZADOS\nPARA CIRCULAR",
        font=font(BOLD, 66),
        fill=NAVY,
        spacing=8,
    )

    draw.rectangle((68, 630, 148, 638), fill=CYAN)
    draw.rectangle((162, 630, 242, 638), fill=YELLOW)
    draw.rectangle((256, 630, 336, 638), fill=MAGENTA)

    wrapped(
        draw,
        "Para equipa, promotores e eventos, um bone pode proteger, identificar e manter a marca visivel sem excesso.",
        68,
        676,
        24,
        29,
        GRAPHITE,
        spacing=8,
    )

    feature_card(draw, 64, 890, CYAN, "Equipa", "Ajuda a uniformizar presenca em atendimento, activacoes e terreno.")
    feature_card(draw, 64, 1052, YELLOW, "Logo", "Vale alinhar cor do tecido e posicao do logotipo antes de produzir.")
    draw.rounded_rectangle((620, 1072, 956, 1148), radius=24, fill=NAVY)
    draw.text((666, 1097), "PEDIR ORCAMENTO", font=font(BOLD, 28), fill=OFF_WHITE)

    footer(draw)
    canvas.convert("RGB").save(CAMPAIGN / "poster-v2.jpg", quality=94, subsampling=0)


if __name__ == "__main__":
    main()
