from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
BASE = CAMPAIGN / "base-educativo-v1.png"
LOGO = ROOT / "assets" / "logo-scp.png"
COLETES = ROOT / "assets" / "categorias" / "coletes-uniformes.jpg"
PLACAS = ROOT / "assets" / "categorias" / "placas-sinaletica.jpg"
VINIL = ROOT / "assets" / "trabalhos" / "vinil-montra-institucional.jpg"

WIDTH = 1080
HEIGHT = 1350

NAVY = "#11172C"
CYAN = "#18A8D8"
MAGENTA = "#E91573"
YELLOW = "#F4C318"
LIME = "#D8F24B"
OFF_WHITE = "#FFFDF7"
GRAPHITE = "#343946"
SOFT_CARD = (255, 253, 247, 228)

BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)


def fit_cover(source: Image.Image, width: int, height: int) -> Image.Image:
    source = source.convert("RGB")
    return ImageOps.fit(source, (width, height), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))


def make_base() -> Image.Image:
    return fit_cover(Image.open(BASE), WIDTH, HEIGHT).convert("RGBA")


def add_shadow(base: Image.Image, bounds: tuple[int, int, int, int], radius: int = 28, blur: int = 24) -> Image.Image:
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    draw.rounded_rectangle(bounds, radius=radius, fill=(7, 14, 30, 68))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(base, shadow)


def rounded_card(image: Image.Image, size: tuple[int, int], radius: int = 28) -> Image.Image:
    card = fit_cover(image, *size).convert("RGBA")
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
    card.putalpha(mask)
    return card


def add_photo_card(base: Image.Image, source_path: Path, x: int, y: int, width: int, height: int, radius: int = 28) -> Image.Image:
    bounds = (x + 12, y + 16, x + width + 12, y + height + 16)
    base = add_shadow(base, bounds, radius=radius, blur=28)
    card = rounded_card(Image.open(source_path), (width, height), radius=radius)
    base.alpha_composite(card, (x, y))
    return base


def place_logo(base: Image.Image) -> None:
    logo = Image.open(LOGO).convert("RGBA")
    logo_width = 248
    logo_height = round(logo.height * logo_width / logo.width)
    logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
    base.alpha_composite(logo, (64, 54))


def pill(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], fill: str, text: str, text_fill: str = OFF_WHITE) -> None:
    draw.rounded_rectangle(bounds, radius=28, fill=fill)
    draw.text((bounds[0] + 24, bounds[1] + 15), text, font=font(BOLD, 23), fill=text_fill)


def footer(draw: ImageDraw.ImageDraw, page: str) -> None:
    draw.rectangle((0, 1250, WIDTH, HEIGHT), fill=NAVY)
    draw.text((64, 1282), "scolorprint.com", font=font(BOLD, 30), fill=OFF_WHITE)
    draw.text((810, 1282), page, font=font(BOLD, 28), fill=OFF_WHITE)


def wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    x: int,
    y: int,
    width_chars: int,
    size: int,
    fill: str,
    bold: bool = False,
    spacing: int = 7,
) -> int:
    family = BOLD if bold else REGULAR
    block = textwrap.fill(text, width=width_chars)
    draw.multiline_text((x, y), block, font=font(family, size), fill=fill, spacing=spacing)
    bbox = draw.multiline_textbbox((x, y), block, font=font(family, size), spacing=spacing)
    return bbox[3]


def bullet_list(draw: ImageDraw.ImageDraw, items: list[str], x: int, y: int, width_chars: int, size: int, fill_cycle: list[str]) -> int:
    cursor = y
    for index, item in enumerate(items):
        fill = fill_cycle[index % len(fill_cycle)]
        draw.rounded_rectangle((x, cursor + 10, x + 30, cursor + 40), radius=10, fill=fill)
        cursor = wrapped(draw, item, x + 52, cursor, width_chars, size, GRAPHITE, spacing=8) + 24
    return cursor


def info_card(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], title: str, body: str) -> None:
    draw.rounded_rectangle(bounds, radius=28, fill=SOFT_CARD, outline=(17, 23, 44, 35), width=2)
    draw.text((bounds[0] + 28, bounds[1] + 24), title, font=font(BOLD, 28), fill=NAVY)
    wrapped(draw, body, bounds[0] + 28, bounds[1] + 78, 23, 24, GRAPHITE, spacing=7)


def slide_one() -> Image.Image:
    canvas = make_base()
    canvas = add_photo_card(canvas, COLETES, 646, 208, 318, 536)
    canvas = add_photo_card(canvas, PLACAS, 716, 792, 252, 292)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 176, 354, 232), MAGENTA, "TERCA | GUIA RAPIDO")
    draw.multiline_text(
        (64, 284),
        "COLETES,\nVINIL OU\nPLACAS?",
        font=font(BOLD, 68),
        fill=NAVY,
        spacing=8,
    )
    draw.rectangle((68, 598, 146, 606), fill=CYAN)
    draw.rectangle((160, 598, 236, 606), fill=MAGENTA)
    draw.rectangle((250, 598, 310, 606), fill=YELLOW)
    wrapped(
        draw,
        "Cada peca resolve uma necessidade diferente da marca. Veja por onde faz mais sentido comecar.",
        68,
        638,
        24,
        28,
        GRAPHITE,
        spacing=8,
    )
    draw.rounded_rectangle((68, 970, 470, 1048), radius=24, fill=LIME)
    draw.text((98, 996), "GUARDE ESTE GUIA", font=font(BOLD, 29), fill=NAVY)
    footer(draw, "1/4")
    return canvas


def slide_two() -> Image.Image:
    canvas = make_base()
    canvas = add_photo_card(canvas, COLETES, 622, 190, 360, 924)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 176, 244, 232), NAVY, "COLETES")
    draw.multiline_text(
        (64, 284),
        "QUANDO A\nEQUIPA\nPRECISA DE\nSER VISTA",
        font=font(BOLD, 58),
        fill=NAVY,
        spacing=8,
    )
    bullet_list(
        draw,
        [
            "Boa escolha para equipas, visitas, eventos e apoio no local.",
            "Ajuda a identificar funcao e reforcar a presenca da marca.",
            "Ideal quando a prioridade e visibilidade imediata.",
        ],
        68,
        646,
        21,
        27,
        [MAGENTA, CYAN, YELLOW],
    )
    info_card(draw, (64, 1018, 548, 1162), "Funciona bem para", "equipas, recepcao e apoio no local.")
    footer(draw, "2/4")
    return canvas


def slide_three() -> Image.Image:
    canvas = make_base()
    canvas = add_photo_card(canvas, VINIL, 618, 188, 356, 410)
    canvas = add_photo_card(canvas, PLACAS, 618, 632, 356, 412)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 176, 292, 232), CYAN, "VINIL + PLACAS", text_fill=NAVY)
    draw.multiline_text(
        (64, 284),
        "QUANDO O\nESPACO PRECISA\nDE ORIENTAR",
        font=font(BOLD, 58),
        fill=NAVY,
        spacing=8,
    )
    bullet_list(
        draw,
        [
            "Vinil ajuda montras, portas e entradas a comunicar melhor.",
            "Placas e sinaletica organizam informacao e identificam melhor o local.",
            "As duas pecas funcionam bem quando o espaco precisa de mais clareza.",
        ],
        68,
        618,
        21,
        27,
        [YELLOW, MAGENTA, CYAN],
    )
    footer(draw, "3/4")
    return canvas


def slide_four() -> Image.Image:
    canvas = make_base()
    canvas = add_photo_card(canvas, COLETES, 72, 924, 248, 244)
    canvas = add_photo_card(canvas, VINIL, 352, 924, 248, 244)
    canvas = add_photo_card(canvas, PLACAS, 632, 924, 248, 244)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 176, 312, 232), MAGENTA, "COMO ESCOLHER")
    draw.multiline_text(
        (64, 284),
        "SE O FOCO E...",
        font=font(BOLD, 58),
        fill=NAVY,
        spacing=8,
    )
    info_card(draw, (64, 418, 456, 570), "Equipa visivel", "Comece por coletes ou uniformes.")
    info_card(draw, (64, 598, 456, 750), "Entrada com identidade", "Vinil ajuda a marca a aparecer melhor.")
    info_card(draw, (64, 778, 456, 930), "Orientacao do espaco", "Placas e sinaletica organizam a informacao.")
    wrapped(
        draw,
        "Se quiser, podemos ajudar a combinar as pecas certas para o seu caso. Comente 'equipa' ou 'espaco'.",
        542,
        428,
        18,
        30,
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
