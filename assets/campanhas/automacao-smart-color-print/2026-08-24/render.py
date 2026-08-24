from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
LOGO = ROOT / "assets" / "logo-scp.png"
BASE = CAMPAIGN / "base-brand-v1.png"
PHOTO = ROOT / "assets" / "trabalhos" / "canetas-personalizadas.jpg"

WIDTH = 1080
HEIGHT = 1350

NAVY = "#101935"
CYAN = "#19B3E6"
MAGENTA = "#EA1A72"
YELLOW = "#F3C515"
LIME = "#C9F04D"
OFF_WHITE = "#FFFDF8"
GRAPHITE = "#2E3443"
CARD_FILL = (255, 253, 248, 234)
CARD_BORDER = (16, 25, 53, 24)

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
    draw.rounded_rectangle((46, 132, 568, 1188), radius=46, fill=(255, 253, 248, 226))
    draw.rounded_rectangle((72, 170, 500, 1134), radius=38, fill=(255, 255, 255, 44))
    draw.ellipse((-130, 978, 388, 1460), fill=(25, 179, 230, 28))
    draw.ellipse((660, 1004, 1138, 1458), fill=(16, 25, 53, 16))
    haze = haze.filter(ImageFilter.GaussianBlur(18))
    return Image.alpha_composite(base, haze)


def add_shadow(base: Image.Image, bounds: tuple[int, int, int, int], radius: int = 34, blur: int = 28) -> Image.Image:
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(bounds, radius=radius, fill=(10, 18, 39, 74))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(base, shadow)


def photo_card(base: Image.Image, source_path: Path, x: int, y: int, width: int, height: int, radius: int = 34) -> Image.Image:
    base = add_shadow(base, (x + 10, y + 12, x + width + 10, y + height + 12), radius=radius, blur=30)
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
    base.alpha_composite(logo, (62, 46))


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


def label_chip(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], fill: str, text: str, text_fill: str = NAVY) -> None:
    draw.rounded_rectangle(bounds, radius=22, fill=fill)
    draw.text((bounds[0] + 22, bounds[1] + 14), text, font=font(BOLD, 20), fill=text_fill)


def info_card(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], title: str, body: str, accent: str) -> None:
    draw.rounded_rectangle(bounds, radius=28, fill=CARD_FILL, outline=CARD_BORDER, width=2)
    draw.rounded_rectangle((bounds[0] + 22, bounds[1] + 22, bounds[0] + 186, bounds[1] + 58), radius=18, fill=accent)
    draw.text((bounds[0] + 42, bounds[1] + 31), title, font=font(BOLD, 20), fill=NAVY)
    wrapped(draw, body, bounds[0] + 24, bounds[1] + 74, 24, 18, GRAPHITE, spacing=6)


def footer(draw: ImageDraw.ImageDraw) -> None:
    draw.rectangle((0, 1250, WIDTH, HEIGHT), fill=NAVY)
    draw.text((64, 1282), "scolorprint.com", font=font(BOLD, 30), fill=OFF_WHITE)
    draw.text((694, 1286), "GUARDE E PECA ORCAMENTO", font=font(BOLD, 19), fill=OFF_WHITE)


def main() -> None:
    canvas = make_canvas()
    canvas = photo_card(canvas, PHOTO, 612, 174, 350, 944)
    draw = ImageDraw.Draw(canvas)

    place_logo(canvas)
    pill(draw, (64, 168, 354, 224), MAGENTA, "SEGUNDA | REUNIOES")
    draw.multiline_text(
        (64, 280),
        "CANETA UTIL\nPARA A MARCA\nCONTINUAR\nNA MESA",
        font=font(BOLD, 60),
        fill=NAVY,
        spacing=8,
    )

    draw.rectangle((66, 664, 144, 672), fill=CYAN)
    draw.rectangle((158, 664, 236, 672), fill=MAGENTA)
    draw.rectangle((250, 664, 328, 672), fill=YELLOW)

    wrapped(
        draw,
        "Quando a semana abre com visitas, briefing ou kits de apoio, um brinde de uso diario ajuda a marca a seguir presente depois da conversa.",
        66,
        704,
        24,
        28,
        GRAPHITE,
        spacing=8,
    )

    label_chip(draw, (66, 964, 252, 1020), CYAN, "REUNIOES")
    label_chip(draw, (266, 964, 402, 1020), YELLOW, "KITS")
    label_chip(draw, (66, 1036, 308, 1092), MAGENTA, "RECEPCAO", text_fill=OFF_WHITE)
    info_card(
        draw,
        (62, 1102, 488, 1222),
        "Revise antes",
        "Logo, quantidade e cor do corpo da peca.",
        LIME,
    )
    footer(draw)
    canvas.convert("RGB").save(CAMPAIGN / "poster-v1.jpg", quality=94, subsampling=0)


if __name__ == "__main__":
    main()
