from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
LOGO = ROOT / "assets" / "logo-scp.png"
VINIL = ROOT / "assets" / "trabalhos" / "vinil-montra-institucional.jpg"
ROLLUP = ROOT / "assets" / "trabalhos" / "rollup-evento-institucional.jpg"
BACKDROP = ROOT / "assets" / "trabalhos" / "backdrop-evento-institucional.jpg"
FOLDER = ROOT / "assets" / "trabalhos" / "folder-criativo-corte-vinco.jpg"

WIDTH = 1080
HEIGHT = 1350

NAVY = "#0F1630"
CYAN = "#16A9D7"
MAGENTA = "#E91A72"
YELLOW = "#F4C21C"
LIME = "#D7F04D"
OFF_WHITE = "#FFFDF7"
GRAPHITE = "#303744"
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
        r = round(255 - (255 - 242) * blend)
        g = round(253 - (253 - 247) * blend)
        b = round(247 - (247 - 252) * blend)
        for x in range(WIDTH):
            px[x, y] = (r, g, b, 255)

    haze = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(haze)
    draw.ellipse((-140, -30, 620, 520), fill=(22, 169, 215, 34))
    draw.ellipse((580, 700, 1240, 1330), fill=(233, 26, 114, 24))
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
    canvas = add_photo_card(canvas, VINIL, 622, 204, 326, 424)
    canvas = add_photo_card(canvas, ROLLUP, 650, 670, 164, 392)
    canvas = add_photo_card(canvas, FOLDER, 844, 760, 126, 178)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 176, 430, 232), MAGENTA, "DOMINGO | PLANEAMENTO")
    draw.multiline_text(
        (64, 286),
        "ANTES DE\nSEGUNDA,\nALINHE ESTAS\n4 PECAS",
        font=font(BOLD, 64),
        fill=NAVY,
        spacing=8,
    )
    draw.rectangle((68, 662, 146, 670), fill=CYAN)
    draw.rectangle((160, 662, 236, 670), fill=MAGENTA)
    draw.rectangle((250, 662, 310, 670), fill=YELLOW)
    wrapped(
        draw,
        "Entrada, mensagem, fundo e material de apoio podem ser fechados hoje com mais calma.",
        68,
        706,
        24,
        28,
        GRAPHITE,
        spacing=8,
    )
    draw.rounded_rectangle((68, 1012, 444, 1090), radius=24, fill=LIME)
    draw.text((98, 1038), "GUARDE PARA A SEMANA", font=font(BOLD, 24), fill=NAVY)
    footer(draw, "1/5")
    return canvas


def slide_two() -> Image.Image:
    canvas = make_canvas()
    canvas = add_photo_card(canvas, VINIL, 622, 190, 356, 894)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 176, 246, 232), NAVY, "PASSO 1")
    draw.multiline_text(
        (64, 284),
        "PREPARE A\nCHEGADA DA\nMARCA",
        font=font(BOLD, 58),
        fill=NAVY,
        spacing=8,
    )
    bullet_list(
        draw,
        [
            "Vinil ou peca de entrada ajuda a acolher melhor quem chega ao espaco.",
            "Tambem melhora a leitura da montra, porta ou recepcao antes do primeiro contacto.",
            "Se esta definicao fica pronta no domingo, segunda comeca com menos improviso.",
        ],
        68,
        628,
        22,
        25,
        [MAGENTA, CYAN, YELLOW],
    )
    info_card(draw, (64, 1014, 548, 1178), "Pergunta util", "Onde a pessoa vai perceber a marca logo nos primeiros segundos?")
    footer(draw, "2/5")
    return canvas


def slide_three() -> Image.Image:
    canvas = make_canvas()
    canvas = add_photo_card(canvas, ROLLUP, 626, 198, 350, 860)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 176, 246, 232), CYAN, "PASSO 2", text_fill=NAVY)
    draw.multiline_text(
        (64, 284),
        "FECHE A\nMENSAGEM\nPRINCIPAL",
        font=font(BOLD, 58),
        fill=NAVY,
        spacing=8,
    )
    bullet_list(
        draw,
        [
            "Roll-up funciona bem quando a marca precisa orientar, receber ou reforcar uma mensagem curta.",
            "Vale escolher uma frase principal antes de enviar o ficheiro para evitar excesso de texto.",
            "Em corredores, entradas e pontos fixos, costuma resolver bem a leitura imediata.",
        ],
        68,
        632,
        22,
        25,
        [YELLOW, MAGENTA, CYAN],
    )
    info_card(draw, (64, 1016, 548, 1204), "Planeie antes", "Uma mensagem forte costuma funcionar melhor do que varias ao mesmo tempo.")
    footer(draw, "3/5")
    return canvas


def slide_four() -> Image.Image:
    canvas = make_canvas()
    canvas = add_photo_card(canvas, BACKDROP, 610, 198, 366, 430)
    canvas = add_photo_card(canvas, FOLDER, 652, 696, 286, 292)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 176, 246, 232), YELLOW, "PASSO 3", text_fill=NAVY)
    draw.multiline_text(
        (64, 284),
        "DEIXE O\nFUNDO E O\nMATERIAL\nPRONTOS",
        font=font(BOLD, 58),
        fill=NAVY,
        spacing=8,
    )
    bullet_list(
        draw,
        [
            "Backdrop entra quando vai existir recepcao, palco, fotografia ou zona institucional.",
            "Folder ou flyer ajuda a prolongar a conversa depois da reuniao, visita ou evento.",
            "Quando estas duas pecas ja estao previstas, a semana avanca com mais ordem.",
        ],
        68,
        682,
        21,
        27,
        [LIME, MAGENTA, CYAN],
    )
    footer(draw, "4/5")
    return canvas


def slide_five() -> Image.Image:
    canvas = make_canvas()
    canvas = add_photo_card(canvas, FOLDER, 608, 188, 360, 330)
    canvas = add_photo_card(canvas, VINIL, 608, 556, 170, 344)
    canvas = add_photo_card(canvas, ROLLUP, 798, 556, 170, 344)
    canvas = add_photo_card(canvas, BACKDROP, 608, 930, 360, 182)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 176, 420, 232), MAGENTA, "CHECKLIST DE DOMINGO")
    draw.multiline_text(
        (64, 284),
        "ANTES DE\nAMANHA,\nREVEJA ISTO",
        font=font(BOLD, 58),
        fill=NAVY,
        spacing=8,
    )
    info_card(draw, (64, 612, 476, 786), "Entrada", "Vinil, porta ou recepcao alinhados com a primeira impressao.")
    info_card(draw, (64, 804, 476, 978), "Mensagem", "Roll-up e fundo institucional prontos para orientar o espaco.")
    info_card(draw, (64, 996, 476, 1170), "Fecho", "Folder, flyer ou pedido de orcamento preparado para a conversa continuar.")
    draw.rounded_rectangle((606, 1114, 972, 1210), radius=26, fill=(255, 253, 247, 236), outline=(17, 23, 44, 35), width=2)
    wrapped(draw, "Comente 'semana' e planeamos consigo.", 632, 1140, 24, 20, NAVY, bold=True, spacing=6)
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
