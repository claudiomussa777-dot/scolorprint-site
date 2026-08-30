from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
LOGO = ROOT / "assets" / "logo-scp.png"
BASE = CAMPAIGN / "base-brand-v1.png"
VINIL = ROOT / "assets" / "trabalhos" / "vinil-montra-institucional.jpg"
FOLDER = ROOT / "assets" / "trabalhos" / "folders-e-flyers-impressos.jpg"
ROLLUP = ROOT / "assets" / "trabalhos" / "rollup-evento-institucional.jpg"

WIDTH = 1080
HEIGHT = 1350

NAVY = "#0E1A36"
CYAN = "#18B2E4"
MAGENTA = "#E61A73"
YELLOW = "#F5C517"
LIME = "#D9F238"
OFF_WHITE = "#FFFDF7"
GRAPHITE = "#2E3445"
CARD_FILL = (255, 253, 247, 238)
CARD_OUTLINE = (14, 26, 54, 34)

BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)


def fit_cover(source: Image.Image, width: int, height: int) -> Image.Image:
    return ImageOps.fit(source.convert("RGB"), (width, height), method=Image.Resampling.LANCZOS)


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


def make_canvas() -> Image.Image:
    base = fit_cover(Image.open(BASE), WIDTH, HEIGHT).convert("RGBA")
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle((42, 144, 592, 1200), radius=44, fill=(255, 253, 247, 176))
    draw.ellipse((-40, 788, 368, 1248), fill=(24, 178, 228, 18))
    draw.ellipse((418, 964, 774, 1312), fill=(230, 26, 115, 14))
    overlay = overlay.filter(ImageFilter.GaussianBlur(16))
    return Image.alpha_composite(base, overlay)


def place_logo(base: Image.Image) -> None:
    logo = Image.open(LOGO).convert("RGBA")
    logo_width = 246
    logo_height = round(logo.height * logo_width / logo.width)
    logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
    base.alpha_composite(logo, (64, 48))


def add_shadow(base: Image.Image, bounds: tuple[int, int, int, int], radius: int = 28, blur: int = 22) -> Image.Image:
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(bounds, radius=radius, fill=(12, 18, 36, 72))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(base, shadow)


def photo_card(base: Image.Image, source_path: Path, x: int, y: int, width: int, height: int, radius: int = 28) -> Image.Image:
    base = add_shadow(base, (x + 10, y + 14, x + width + 10, y + height + 14), radius=radius, blur=26)
    card = fit_cover(Image.open(source_path), width, height).convert("RGBA")
    mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, width, height), radius=radius, fill=255)
    card.putalpha(mask)
    base.alpha_composite(card, (x, y))
    return base


def pill(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], fill: str, text: str, text_fill: str = OFF_WHITE) -> None:
    draw.rounded_rectangle(bounds, radius=28, fill=fill)
    draw.text((bounds[0] + 22, bounds[1] + 15), text, font=font(BOLD, 22), fill=text_fill)


def accent_lines(draw: ImageDraw.ImageDraw, y: int) -> None:
    draw.rectangle((68, y, 150, y + 8), fill=CYAN)
    draw.rectangle((164, y, 246, y + 8), fill=YELLOW)
    draw.rectangle((260, y, 342, y + 8), fill=MAGENTA)


def footer(draw: ImageDraw.ImageDraw) -> None:
    draw.text((62, 1282), "scolorprint.com", font=font(BOLD, 30), fill=OFF_WHITE)
    draw.text((734, 1284), "PECA O SEU ORCAMENTO", font=font(BOLD, 24), fill=OFF_WHITE)


def label_on_photo(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, fill: str, text_fill: str = OFF_WHITE) -> None:
    width = 152 if len(text) < 9 else 176
    draw.rounded_rectangle((x, y, x + width, y + 42), radius=20, fill=fill)
    draw.text((x + 18, y + 10), text, font=font(BOLD, 18), fill=text_fill)


def check_card(draw: ImageDraw.ImageDraw, x: int, y: int, accent: str, number: str, title: str, body: str) -> None:
    draw.rounded_rectangle((x, y, x + 230, y + 124), radius=26, fill=CARD_FILL, outline=CARD_OUTLINE, width=2)
    draw.ellipse((x + 18, y + 18, x + 72, y + 72), fill=accent)
    draw.text((x + 38, y + 31), number, font=font(BOLD, 22), fill=NAVY)
    draw.text((x + 86, y + 20), title, font=font(BOLD, 22), fill=NAVY)
    wrapped(draw, body, x + 86, y + 52, 18, 17, GRAPHITE, spacing=5)


def build_poster() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, VINIL, 650, 194, 286, 242)
    canvas = photo_card(canvas, FOLDER, 650, 470, 286, 242)
    canvas = photo_card(canvas, ROLLUP, 650, 746, 286, 284)

    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (66, 174, 392, 230), MAGENTA, "DOMINGO | REVISAO FINAL")
    draw.multiline_text((66, 286), "ANTES DE\nENVIAR,\nFECHE O\nPEDIDO", font=font(BOLD, 62), fill=NAVY, spacing=8)
    accent_lines(draw, 620)
    wrapped(
        draw,
        "Quando arte, medida, quantidade e uso ja estao fechados, o pedido segue com menos trocas.",
        68,
        662,
        24,
        28,
        GRAPHITE,
        spacing=8,
    )
    draw.rounded_rectangle((68, 842, 454, 920), radius=24, fill=LIME)
    draw.text((100, 868), "GUARDE PARA REVER HOJE", font=font(BOLD, 24), fill=NAVY)

    check_card(draw, 66, 946, CYAN, "1", "Arte final", "Ficheiro certo e versao final.")
    check_card(draw, 316, 946, MAGENTA, "2", "Medida", "Dimensao alinhada com o espaco.")
    check_card(draw, 66, 1084, YELLOW, "3", "Quantidade", "Numero fechado para a entrega.")
    check_card(draw, 316, 1084, LIME, "4", "Uso", "Funcao clara no ponto de uso.")

    label_on_photo(draw, 674, 214, "VINIL", NAVY)
    label_on_photo(draw, 674, 490, "FOLDER", MAGENTA)
    label_on_photo(draw, 674, 766, "ROLL-UP", YELLOW, text_fill=NAVY)
    footer(draw)
    return canvas


def main() -> None:
    build_poster().convert("RGB").save(CAMPAIGN / "poster-v1.jpg", quality=92, subsampling=0)


if __name__ == "__main__":
    main()
