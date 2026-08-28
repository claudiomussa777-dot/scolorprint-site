from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
LOGO = ROOT / "assets" / "logo-scp.png"
BASE = CAMPAIGN / "base-brand-v1.png"
PHOTO = ROOT / "assets" / "mockup-cartao-real-v1.jpg"

WIDTH = 1080
HEIGHT = 1350

NAVY = "#101935"
CYAN = "#19B3E6"
MAGENTA = "#EA1A72"
YELLOW = "#F3C515"
LIME = "#D8EF5D"
OFF_WHITE = "#FFFDF8"
GRAPHITE = "#2E3443"
CARD_FILL = (255, 253, 248, 236)
CARD_BORDER = (16, 25, 53, 26)

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
    draw.rounded_rectangle((40, 132, 560, 1182), radius=48, fill=(255, 253, 248, 226))
    draw.rounded_rectangle((70, 172, 506, 1128), radius=40, fill=(255, 255, 255, 38))
    draw.ellipse((-140, 982, 410, 1466), fill=(25, 179, 230, 24))
    draw.ellipse((662, 1010, 1140, 1452), fill=(16, 25, 53, 18))
    haze = haze.filter(ImageFilter.GaussianBlur(18))
    return Image.alpha_composite(base, haze)


def add_shadow(base: Image.Image, bounds: tuple[int, int, int, int], radius: int = 34, blur: int = 28) -> Image.Image:
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(bounds, radius=radius, fill=(10, 18, 39, 76))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(base, shadow)


def photo_card(base: Image.Image, source_path: Path, x: int, y: int, width: int, height: int, radius: int = 34) -> Image.Image:
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


def pill(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], fill: str, text: str, text_fill: str = OFF_WHITE) -> None:
    draw.rounded_rectangle(bounds, radius=28, fill=fill)
    draw.text((bounds[0] + 24, bounds[1] + 14), text, font=font(BOLD, 22), fill=text_fill)


def chip(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], fill: str, text: str, text_fill: str = NAVY) -> None:
    draw.rounded_rectangle(bounds, radius=22, fill=fill)
    draw.text((bounds[0] + 22, bounds[1] + 14), text, font=font(BOLD, 20), fill=text_fill)


def info_card(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], title: str, body: str, accent: str) -> None:
    draw.rounded_rectangle(bounds, radius=28, fill=CARD_FILL, outline=CARD_BORDER, width=2)
    draw.rounded_rectangle((bounds[0] + 22, bounds[1] + 22, bounds[0] + 188, bounds[1] + 58), radius=18, fill=accent)
    draw.text((bounds[0] + 42, bounds[1] + 31), title, font=font(BOLD, 20), fill=NAVY)
    wrapped(draw, body, bounds[0] + 24, bounds[1] + 74, 24, 18, GRAPHITE, spacing=6)


def footer(draw: ImageDraw.ImageDraw) -> None:
    draw.rectangle((0, 1250, WIDTH, HEIGHT), fill=NAVY)
    draw.text((64, 1282), "scolorprint.com", font=font(BOLD, 30), fill=OFF_WHITE)
    draw.text((676, 1286), "PECA O SEU ORCAMENTO", font=font(BOLD, 19), fill=OFF_WHITE)


def main() -> None:
    canvas = make_canvas()
    canvas = photo_card(canvas, PHOTO, 606, 184, 356, 936)
    draw = ImageDraw.Draw(canvas)

    place_logo(canvas)
    pill(draw, (64, 168, 490, 224), MAGENTA, "SEXTA | PRODUTO EM FOCO")
    draw.multiline_text(
        (64, 280),
        "CARTOES\nDE VISITA\nPARA FICAR\nNA MAO",
        font=font(BOLD, 60),
        fill=NAVY,
        spacing=8,
    )

    draw.rectangle((66, 664, 144, 672), fill=CYAN)
    draw.rectangle((158, 664, 236, 672), fill=MAGENTA)
    draw.rectangle((250, 664, 328, 672), fill=YELLOW)

    wrapped(
        draw,
        "Em reunioes, visitas e entregas, um cartao bem preparado ajuda a apresentar a marca com clareza e facilita o proximo contacto.",
        66,
        704,
        24,
        28,
        GRAPHITE,
        spacing=8,
    )

    chip(draw, (66, 964, 244, 1020), CYAN, "REUNIOES")
    chip(draw, (258, 964, 428, 1020), YELLOW, "VISITAS")
    chip(draw, (66, 1036, 272, 1092), MAGENTA, "EVENTOS", text_fill=OFF_WHITE)
    info_card(
        draw,
        (62, 1102, 492, 1222),
        "Revise antes",
        "Nome, contacto, quantidade e acabamento.",
        LIME,
    )

    footer(draw)
    canvas.convert("RGB").save(CAMPAIGN / "poster-v1.jpg", quality=94, subsampling=0)


if __name__ == "__main__":
    main()
