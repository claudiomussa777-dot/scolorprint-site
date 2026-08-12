from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
LOGO = ROOT / "assets" / "logo-scp.png"
BASE = CAMPAIGN / "base-brand-v1.png"
CARD = ROOT / "assets" / "mockup-cartao-real-v1.jpg"

WIDTH = 1080
HEIGHT = 1350

NAVY = "#101935"
CYAN = "#19B3E6"
MAGENTA = "#EA1A72"
YELLOW = "#F3C515"
OFF_WHITE = "#FFFDF8"
GRAPHITE = "#2D3342"
CARD_FILL = (255, 253, 248, 238)
CARD_BORDER = (16, 25, 53, 32)
LIME = "#DFF364"

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
    draw.rounded_rectangle((42, 126, 610, 1202), radius=56, fill=(255, 253, 248, 228))
    draw.rounded_rectangle((56, 144, 1024, 1216), radius=62, outline=(16, 25, 53, 18), width=4)
    draw.ellipse((-140, 940, 394, 1450), fill=(25, 179, 230, 22))
    draw.ellipse((716, 986, 1168, 1438), fill=(16, 25, 53, 26))
    haze = haze.filter(ImageFilter.GaussianBlur(16))
    return Image.alpha_composite(base, haze)


def add_shadow(base: Image.Image, bounds: tuple[int, int, int, int], radius: int = 30, blur: int = 28) -> Image.Image:
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(bounds, radius=radius, fill=(10, 18, 39, 70))
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
    base.alpha_composite(logo, (64, 46))


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
    block = textwrap.fill(text, width=width_chars)
    draw.multiline_text((x, y), block, font=font(family, size), fill=fill, spacing=spacing)
    bbox = draw.multiline_textbbox((x, y), block, font=font(family, size), spacing=spacing)
    return bbox[3]


def tip_card(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    width: int,
    accent: str,
    title: str,
    body: str,
    *,
    title_fill: str = NAVY,
) -> None:
    draw.rounded_rectangle((x, y, x + width, y + 136), radius=28, fill=CARD_FILL, outline=CARD_BORDER, width=2)
    draw.rounded_rectangle((x + 24, y + 22, x + 154, y + 58), radius=18, fill=accent)
    draw.text((x + 44, y + 31), title, font=font(BOLD, 21), fill=title_fill)
    wrapped(draw, body, x + 24, y + 70, max(28, width // 15), 18, GRAPHITE, spacing=5)


def footer(draw: ImageDraw.ImageDraw) -> None:
    draw.rectangle((0, 1250, WIDTH, HEIGHT), fill=NAVY)
    draw.text((64, 1282), "scolorprint.com", font=font(BOLD, 30), fill=OFF_WHITE)
    draw.text((700, 1286), "PECA O SEU ORCAMENTO", font=font(BOLD, 19), fill=OFF_WHITE)


def main() -> None:
    canvas = make_canvas()
    canvas = photo_card(canvas, CARD, 650, 204, 296, 828)
    draw = ImageDraw.Draw(canvas)

    place_logo(canvas)
    pill(draw, (64, 172, 548, 228), MAGENTA, "QUARTA | DICA DE ACABAMENTO")
    draw.multiline_text(
        (66, 290),
        "CARTAO QUE\nRESPIRA\nMELHOR",
        font=font(BOLD, 66),
        fill=NAVY,
        spacing=8,
    )

    draw.rectangle((68, 570, 148, 578), fill=CYAN)
    draw.rectangle((162, 570, 242, 578), fill=YELLOW)
    draw.rectangle((256, 570, 336, 578), fill=MAGENTA)

    wrapped(
        draw,
        "Antes de imprimir, vale rever tres detalhes simples que ajudam a leitura e a presenca da peca.",
        68,
        616,
        24,
        29,
        GRAPHITE,
        spacing=8,
    )

    draw.rounded_rectangle((68, 860, 522, 934), radius=24, fill=LIME)
    draw.text((98, 886), "GUARDE PARA A PROXIMA TIRAGEM", font=font(BOLD, 22), fill=NAVY)

    tip_card(draw, 64, 972, 472, CYAN, "Margem", "Nao aperte nome, logo ou contacto junto a borda. Respiro melhora a leitura.")
    tip_card(draw, 544, 972, 472, MAGENTA, "Papel", "Uma gramagem firme ajuda o cartao a passar melhor na mao e durar mais.")
    tip_card(
        draw,
        64,
        1118,
        952,
        NAVY,
        "Contraste",
        "Texto claro sobre fundo claro ou escuro sobre escuro perde forca no uso real. A leitura precisa funcionar no primeiro olhar.",
        title_fill=OFF_WHITE,
    )

    footer(draw)
    canvas.convert("RGB").save(CAMPAIGN / "poster-v1.jpg", quality=94, subsampling=0)


if __name__ == "__main__":
    main()
