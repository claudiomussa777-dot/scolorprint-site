from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
LOGO = ROOT / "assets" / "logo-scp.png"
BACKDROP = ROOT / "assets" / "trabalhos" / "backdrop-evento-institucional.jpg"
ROLLUP = ROOT / "assets" / "trabalhos" / "rollup-conferencia-direitos-humanos.jpg"
VINIL = ROOT / "assets" / "trabalhos" / "vinil-montra-institucional.jpg"
PENS = ROOT / "assets" / "trabalhos" / "canetas-personalizadas.jpg"

WIDTH = 1080
HEIGHT = 1350

NAVY = "#0F1630"
CYAN = "#16A9D7"
MAGENTA = "#E91A72"
YELLOW = "#F4C21C"
LIME = "#D7F04D"
OFF_WHITE = "#FFFDF7"
GRAPHITE = "#303744"
MIST = "#EEF3F8"
SOFT_CARD = (255, 253, 247, 228)

BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)


def fit_cover(source: Image.Image, width: int, height: int) -> Image.Image:
    source = source.convert("RGB")
    return ImageOps.fit(source, (width, height), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))


def gradient_background() -> Image.Image:
    canvas = Image.new("RGBA", (WIDTH, HEIGHT), OFF_WHITE)
    px = canvas.load()
    for y in range(HEIGHT):
        blend = y / (HEIGHT - 1)
        r = round(255 - (255 - 240) * blend)
        g = round(253 - (253 - 246) * blend)
        b = round(247 - (247 - 252) * blend)
        for x in range(WIDTH):
            px[x, y] = (r, g, b, 255)

    haze = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(haze)
    draw.ellipse((-120, -40, 640, 520), fill=(22, 169, 215, 34))
    draw.ellipse((580, 700, 1220, 1320), fill=(233, 26, 114, 24))
    draw.rounded_rectangle((58, 156, 1018, 1210), radius=48, outline=(15, 22, 48, 28), width=2)
    haze = haze.filter(ImageFilter.GaussianBlur(22))
    return Image.alpha_composite(canvas, haze)


def add_shadow(base: Image.Image, bounds: tuple[int, int, int, int], radius: int = 28, blur: int = 24) -> Image.Image:
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    draw.rounded_rectangle(bounds, radius=radius, fill=(7, 13, 28, 66))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(base, shadow)


def rounded_card(image: Image.Image, size: tuple[int, int], radius: int = 28) -> Image.Image:
    card = fit_cover(image, *size).convert("RGBA")
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
    card.putalpha(mask)
    return card


def add_photo_card(base: Image.Image, source_path: Path, x: int, y: int, width: int, height: int, radius: int = 28) -> Image.Image:
    bounds = (x + 10, y + 14, x + width + 10, y + height + 14)
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
        draw.rounded_rectangle((x, cursor + 8, x + 28, cursor + 36), radius=9, fill=fill)
        cursor = wrapped(draw, item, x + 52, cursor, width_chars, size, GRAPHITE, spacing=7) + 22
    return cursor


def info_card(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], title: str, body: str) -> None:
    draw.rounded_rectangle(bounds, radius=28, fill=SOFT_CARD, outline=(17, 23, 44, 35), width=2)
    draw.text((bounds[0] + 28, bounds[1] + 24), title, font=font(BOLD, 29), fill=NAVY)
    wrapped(draw, body, bounds[0] + 28, bounds[1] + 78, 23, 24, GRAPHITE, spacing=7)


def make_canvas() -> Image.Image:
    return gradient_background()


def slide_one() -> Image.Image:
    canvas = make_canvas()
    canvas = add_photo_card(canvas, BACKDROP, 636, 208, 314, 430)
    canvas = add_photo_card(canvas, ROLLUP, 668, 678, 160, 392)
    canvas = add_photo_card(canvas, PENS, 848, 754, 122, 186)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 176, 408, 232), MAGENTA, "SABADO | INSPIRACAO")
    draw.multiline_text(
        (64, 286),
        "PECAS QUE\nCOMBINAM\nBEM NUM\nEVENTO",
        font=font(BOLD, 66),
        fill=NAVY,
        spacing=8,
    )
    draw.rectangle((68, 662, 146, 670), fill=CYAN)
    draw.rectangle((160, 662, 236, 670), fill=MAGENTA)
    draw.rectangle((250, 662, 310, 670), fill=YELLOW)
    wrapped(
        draw,
        "Backdrop, roll-up, vinil e brindes ajudam a criar uma presenca mais completa sem complicar a mensagem.",
        68,
        706,
        24,
        28,
        GRAPHITE,
        spacing=8,
    )
    draw.rounded_rectangle((68, 1012, 482, 1090), radius=24, fill=LIME)
    draw.text((100, 1038), "GUARDE PARA O PROXIMO EVENTO", font=font(BOLD, 24), fill=NAVY)
    footer(draw, "1/5")
    return canvas


def slide_two() -> Image.Image:
    canvas = make_canvas()
    canvas = add_photo_card(canvas, BACKDROP, 622, 190, 356, 894)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 176, 264, 232), NAVY, "BACKDROP")
    draw.multiline_text(
        (64, 284),
        "FUNDO QUE\nORGANIZA A\nPRESENCA\nVISUAL",
        font=font(BOLD, 58),
        fill=NAVY,
        spacing=8,
    )
    bullet_list(
        draw,
        [
            "Ajuda a criar zona de foto, palco ou ponto institucional.",
            "Funciona bem quando a marca precisa de aparecer de forma consistente nas imagens.",
            "Tambem ajuda o espaco a parecer mais organizado.",
        ],
        68,
        640,
        22,
        25,
        [MAGENTA, CYAN, YELLOW],
    )
    info_card(draw, (64, 1014, 548, 1178), "Boa combinacao", "Use com roll-up ou mesa de recepcao para dar mais contexto.")
    footer(draw, "2/5")
    return canvas


def slide_three() -> Image.Image:
    canvas = make_canvas()
    canvas = add_photo_card(canvas, ROLLUP, 626, 198, 350, 860)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 176, 244, 232), CYAN, "ROLL-UP", text_fill=NAVY)
    draw.multiline_text(
        (64, 284),
        "MENSAGEM\nVISIVEL NA\nENTRADA OU\nRECEPCAO",
        font=font(BOLD, 58),
        fill=NAVY,
        spacing=8,
    )
    bullet_list(
        draw,
        [
            "Serve para orientar, apresentar o tema ou reforcar a identidade do evento.",
            "E facil de posicionar em recepcao, corredor ou ponto de atendimento.",
            "Quando o espaco precisa de mensagem clara, resolve bem.",
        ],
        68,
        642,
        22,
        25,
        [YELLOW, MAGENTA, CYAN],
    )
    info_card(draw, (64, 1016, 548, 1204), "Dica pratica", "Escolha uma mensagem principal para manter a leitura imediata.")
    footer(draw, "3/5")
    return canvas


def slide_four() -> Image.Image:
    canvas = make_canvas()
    canvas = add_photo_card(canvas, PENS, 610, 200, 366, 430)
    canvas = add_photo_card(canvas, VINIL, 642, 674, 302, 352)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 176, 338, 232), YELLOW, "BRINDES + ENTRADA", text_fill=NAVY)
    draw.multiline_text(
        (64, 284),
        "DETALHES QUE\nFAZEM A MARCA\nCONTINUAR",
        font=font(BOLD, 58),
        fill=NAVY,
        spacing=8,
    )
    bullet_list(
        draw,
        [
            "Brindes uteis, como canetas, ajudam a marca a continuar presente depois do encontro.",
            "Vinil na entrada ou na montra reforca a chegada e melhora a leitura do local.",
            "Juntos, estes detalhes deixam o evento mais coerente do inicio ao fim.",
        ],
        68,
        614,
        21,
        27,
        [LIME, MAGENTA, CYAN],
    )
    footer(draw, "4/5")
    return canvas


def slide_five() -> Image.Image:
    canvas = make_canvas()
    canvas = add_photo_card(canvas, VINIL, 612, 188, 356, 330)
    canvas = add_photo_card(canvas, BACKDROP, 612, 552, 170, 350)
    canvas = add_photo_card(canvas, ROLLUP, 798, 552, 170, 350)
    canvas = add_photo_card(canvas, PENS, 612, 934, 356, 184)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 176, 430, 232), MAGENTA, "COMBINACAO SIMPLES")
    draw.multiline_text(
        (64, 284),
        "SE O OBJECTIVO\nE RECEBER BEM,\nPODE COMEÇAR\nASSIM",
        font=font(BOLD, 56),
        fill=NAVY,
        spacing=8,
    )
    info_card(draw, (64, 612, 476, 786), "Entrada", "Vinil para dar presenca ao local.")
    info_card(draw, (64, 804, 476, 978), "No espaco", "Backdrop ou roll-up para orientar melhor.")
    info_card(draw, (64, 996, 476, 1170), "No fecho", "Brinde util para prolongar o contacto.")
    draw.rounded_rectangle((612, 1112, 970, 1210), radius=26, fill=(255, 253, 247, 236), outline=(17, 23, 44, 35), width=2)
    wrapped(draw, "Comente 'evento' e montamos consigo.", 638, 1138, 24, 20, NAVY, bold=True, spacing=6)
    footer(draw, "5/5")
    return canvas


def main() -> None:
    slides = [slide_one(), slide_two(), slide_three(), slide_four(), slide_five()]
    for index, slide in enumerate(slides, start=1):
        output = CAMPAIGN / f"slide-{index:02d}-v1.jpg"
        slide.convert("RGB").save(output, "JPEG", quality=93, optimize=True, progressive=True)
        print(output)


if __name__ == "__main__":
    main()
