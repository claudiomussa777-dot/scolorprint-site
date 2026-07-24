from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
BASE = CAMPAIGN / "base-brand-v1.png"
LOGO = ROOT / "assets" / "logo-scp.png"
ROLLUP_EVENT = ROOT / "assets" / "trabalhos" / "rollup-evento-institucional.jpg"
ROLLUP_CONF = ROOT / "assets" / "trabalhos" / "rollup-conferencia-direitos-humanos.jpg"
BACKDROP = ROOT / "assets" / "trabalhos" / "backdrop-evento-institucional.jpg"
EVENT_KIT = ROOT / "assets" / "categorias" / "kits-eventos.jpg"

WIDTH = 1080
HEIGHT = 1350

NAVY = "#11172C"
CYAN = "#18A8D8"
MAGENTA = "#E91573"
YELLOW = "#F4C318"
LIME = "#D8F24B"
OFF_WHITE = "#FFFDF7"
GRAPHITE = "#343946"
SOFT_CARD = (255, 253, 247, 226)

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
    draw.rounded_rectangle(bounds, radius=radius, fill=(9, 16, 36, 70))
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


def wrapped(draw: ImageDraw.ImageDraw, text: str, x: int, y: int, width_chars: int, size: int, fill: str, bold: bool = False, spacing: int = 7) -> int:
    family = BOLD if bold else REGULAR
    block = textwrap.fill(text, width=width_chars)
    draw.multiline_text((x, y), block, font=font(family, size), fill=fill, spacing=spacing)
    bbox = draw.multiline_textbbox((x, y), block, font=font(family, size), spacing=spacing)
    return bbox[3]


def info_card(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], title: str, body: str) -> None:
    draw.rounded_rectangle(bounds, radius=28, fill=SOFT_CARD, outline=(17, 23, 44, 35), width=2)
    draw.text((bounds[0] + 28, bounds[1] + 24), title, font=font(BOLD, 30), fill=NAVY)
    wrapped(draw, body, bounds[0] + 28, bounds[1] + 82, 24, 24, GRAPHITE, spacing=7)


def slide_one() -> Image.Image:
    canvas = make_base()
    canvas = add_photo_card(canvas, ROLLUP_CONF, 660, 208, 284, 512)
    canvas = add_photo_card(canvas, BACKDROP, 738, 760, 238, 316)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 176, 332, 232), MAGENTA, "SEXTA | EVENTOS")
    draw.multiline_text(
        (64, 282),
        "ROLL-UPS E\nBACKDROPS\nPARA EVENTOS",
        font=font(BOLD, 66),
        fill=NAVY,
        spacing=8,
    )
    draw.rectangle((68, 614, 146, 622), fill=CYAN)
    draw.rectangle((160, 614, 236, 622), fill=MAGENTA)
    draw.rectangle((250, 614, 310, 622), fill=YELLOW)
    wrapped(
        draw,
        "Duas peças simples que ajudam a sua marca a aparecer melhor em recepções, palestras, feiras e zonas de foto.",
        68,
        652,
        24,
        28,
        GRAPHITE,
        spacing=8,
    )
    draw.rounded_rectangle((68, 956, 484, 1032), radius=24, fill=LIME)
    draw.text((98, 981), "GUARDE PARA O PRÓXIMO EVENTO", font=font(BOLD, 25), fill=NAVY)
    footer(draw, "1/4")
    return canvas


def slide_two() -> Image.Image:
    canvas = make_base()
    canvas = add_photo_card(canvas, ROLLUP_EVENT, 620, 190, 372, 920)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 176, 246, 232), NAVY, "ROLL-UP")
    draw.multiline_text(
        (64, 284),
        "QUANDO\nFAZ MAIS\nSENTIDO?",
        font=font(BOLD, 61),
        fill=NAVY,
        spacing=8,
    )
    items = [
        "Na entrada, recepção ou junto ao balcão.",
        "Quando precisa de uma peça fácil de montar e mover.",
        "Para destacar serviços, agenda ou patrocinadores.",
    ]
    y = 546
    for label, fill in zip(items, [MAGENTA, CYAN, YELLOW]):
        draw.rounded_rectangle((68, y + 10, 100, y + 42), radius=10, fill=fill)
        y = wrapped(draw, label, 122, y, 22, 27, GRAPHITE, spacing=8) + 34
    info_card(draw, (64, 1028, 560, 1188), "Peça em foco", "Bom para entrada, recepção e presença imediata.")
    footer(draw, "2/4")
    return canvas


def slide_three() -> Image.Image:
    canvas = make_base()
    canvas = add_photo_card(canvas, BACKDROP, 70, 764, 940, 402)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 176, 258, 232), CYAN, "BACKDROP")
    draw.multiline_text(
        (64, 284),
        "ONDE ELE\nGANHA MAIS\nFORÇA?",
        font=font(BOLD, 61),
        fill=NAVY,
        spacing=8,
    )
    items = [
        "No palco, em fotos oficiais ou na área de imprensa.",
        "Quando a marca precisa de um fundo limpo e reconhecível.",
        "Para reforçar identidade visual em eventos institucionais.",
    ]
    y = 546
    for item in items:
        draw.rounded_rectangle((68, y + 10, 100, y + 42), radius=10, fill=LIME)
        y = wrapped(draw, item, 122, y, 31, 27, GRAPHITE, spacing=8) + 24
    draw.rounded_rectangle((720, 698, 1002, 742), radius=18, fill=NAVY)
    draw.text((744, 710), "EXEMPLO REAL", font=font(BOLD, 21), fill=OFF_WHITE)
    footer(draw, "3/4")
    return canvas


def slide_four() -> Image.Image:
    canvas = make_base()
    canvas = add_photo_card(canvas, EVENT_KIT, 604, 200, 404, 548)
    canvas = add_photo_card(canvas, ROLLUP_CONF, 668, 792, 276, 338)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 176, 292, 232), MAGENTA, "ORÇAMENTO")
    draw.multiline_text(
        (64, 284),
        "SE O SEU\nEVENTO ESTÁ A\nCHEGAR,",
        font=font(BOLD, 61),
        fill=NAVY,
        spacing=8,
    )
    wrapped(
        draw,
        "Podemos apoiar com roll-ups, backdrops, camisetas e outras peças para a marca aparecer com mais clareza no local.",
        64,
        560,
        23,
        28,
        GRAPHITE,
        spacing=8,
    )
    draw.rounded_rectangle((64, 820, 486, 898), radius=24, fill=LIME)
    draw.text((98, 846), "PEDIR ORÇAMENTO", font=font(BOLD, 30), fill=NAVY)
    wrapped(
        draw,
        "Comente 'evento' ou envie mensagem. Também pode guardar este carrossel para a próxima produção.",
        64,
        944,
        24,
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
