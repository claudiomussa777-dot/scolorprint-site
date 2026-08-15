from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
LOGO = ROOT / "assets" / "logo-scp.png"
BASE = CAMPAIGN / "base-brand-v1.png"
BACKDROP = ROOT / "assets" / "trabalhos" / "backdrop-evento-institucional.jpg"
ROLLUP = ROOT / "assets" / "trabalhos" / "rollup-conferencia-direitos-humanos.jpg"
FOLDER = ROOT / "assets" / "trabalhos" / "folders-e-flyers-impressos.jpg"

WIDTH = 1080
HEIGHT = 1350

NAVY = "#101935"
CYAN = "#19B3E6"
MAGENTA = "#EA1A72"
YELLOW = "#F3C515"
LIME = "#DFF364"
OFF_WHITE = "#FFFDF8"
GRAPHITE = "#2E3443"
CARD_FILL = (255, 253, 248, 232)
CARD_BORDER = (16, 25, 53, 30)

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
    draw.rounded_rectangle((44, 128, 1008, 1214), radius=58, fill=(255, 253, 248, 74))
    draw.rounded_rectangle((58, 146, 596, 1180), radius=48, fill=(255, 253, 248, 232))
    draw.ellipse((-120, 972, 416, 1492), fill=(25, 179, 230, 22))
    draw.ellipse((714, 982, 1168, 1448), fill=(16, 25, 53, 26))
    haze = haze.filter(ImageFilter.GaussianBlur(18))
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
    base.alpha_composite(logo, (64, 48))


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
    block = textwrap.fill(text, width=width_chars, break_long_words=False, break_on_hyphens=False)
    draw.multiline_text((x, y), block, font=font(family, size), fill=fill, spacing=spacing)
    bbox = draw.multiline_textbbox((x, y), block, font=font(family, size), spacing=spacing)
    return bbox[3]


def bullet_list(draw: ImageDraw.ImageDraw, items: list[str], x: int, y: int, width_chars: int, size: int, colors: list[str]) -> int:
    cursor = y
    for index, item in enumerate(items):
        fill = colors[index % len(colors)]
        draw.rounded_rectangle((x, cursor + 8, x + 28, cursor + 36), radius=9, fill=fill)
        cursor = wrapped(draw, item, x + 50, cursor, width_chars, size, GRAPHITE, spacing=7) + 22
    return cursor


def info_card(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], title: str, body: str, accent: str) -> None:
    draw.rounded_rectangle(bounds, radius=28, fill=CARD_FILL, outline=CARD_BORDER, width=2)
    draw.rounded_rectangle((bounds[0] + 22, bounds[1] + 22, bounds[0] + 186, bounds[1] + 58), radius=18, fill=accent)
    draw.text((bounds[0] + 46, bounds[1] + 31), title, font=font(BOLD, 20), fill=NAVY)
    wrapped(draw, body, bounds[0] + 24, bounds[1] + 74, 30, 21, GRAPHITE, spacing=6)


def footer(draw: ImageDraw.ImageDraw, page: str) -> None:
    draw.rectangle((0, 1250, WIDTH, HEIGHT), fill=NAVY)
    draw.text((64, 1282), "scolorprint.com", font=font(BOLD, 30), fill=OFF_WHITE)
    draw.text((814, 1282), page, font=font(BOLD, 28), fill=OFF_WHITE)


def slide_one() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, BACKDROP, 628, 196, 320, 454)
    canvas = photo_card(canvas, ROLLUP, 654, 690, 264, 286)
    canvas = photo_card(canvas, FOLDER, 610, 1010, 348, 178)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 378, 228), MAGENTA, "SABADO | INSPIRACAO")
    draw.multiline_text(
        (66, 286),
        "KIT VISUAL\nPARA EVENTO\nSEM EXCESSO",
        font=font(BOLD, 63),
        fill=NAVY,
        spacing=8,
    )
    draw.rectangle((68, 612, 146, 620), fill=CYAN)
    draw.rectangle((160, 612, 238, 620), fill=MAGENTA)
    draw.rectangle((252, 612, 330, 620), fill=YELLOW)
    wrapped(
        draw,
        "Backdrop, roll-up e folder ajudam a dar recepcao, leitura e continuidade sem encher o espaco com muitas pecas.",
        68,
        654,
        24,
        28,
        GRAPHITE,
        spacing=8,
    )
    draw.rounded_rectangle((68, 998, 498, 1074), radius=24, fill=LIME)
    draw.text((98, 1025), "VEJA COMO ESTE TRIO SE COMPLETA", font=font(BOLD, 22), fill=NAVY)
    footer(draw, "1/4")
    return canvas


def slide_two() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, BACKDROP, 620, 194, 348, 876)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 258, 228), NAVY, "BACKDROP")
    draw.multiline_text(
        (66, 286),
        "FUNDO CLARO\nPARA FOTO,\nPALCO OU BOAS\nVINDAS",
        font=font(BOLD, 55),
        fill=NAVY,
        spacing=8,
    )
    bullet_list(
        draw,
        [
            "Cria um ponto visual limpo para registo, recepcao ou comunicacao de apoio.",
            "Ajuda a organizar o espaco quando ha cerimonias, feiras ou momentos de foto.",
            "Tambem reforca a presenca da marca sem depender de estruturas demasiado pesadas.",
        ],
        68,
        612,
        21,
        23,
        [CYAN, MAGENTA, YELLOW],
    )
    info_card(
        draw,
        (64, 1002, 544, 1198),
        "Bom uso",
        "Funciona bem quando precisa de um fundo legivel por tras da equipa, dos convidados ou do ponto de recepcao.",
        LIME,
    )
    footer(draw, "2/4")
    return canvas


def slide_three() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, ROLLUP, 652, 198, 256, 900)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 252, 228), CYAN, "ROLL-UP", text_fill=NAVY)
    draw.multiline_text(
        (66, 286),
        "MENSAGEM\nEM PE,\nSEM TOMAR\nMUITO ESPACO",
        font=font(BOLD, 57),
        fill=NAVY,
        spacing=8,
    )
    bullet_list(
        draw,
        [
            "Entra bem na entrada, num corredor, ao lado da mesa ou perto do palco.",
            "Serve para reforcar tema, programa, direccao ou chamada principal do evento.",
            "Quando a distancia de leitura importa, o roll-up resolve com ocupacao pequena.",
        ],
        68,
        614,
        21,
        23,
        [MAGENTA, YELLOW, CYAN],
    )
    info_card(
        draw,
        (64, 1004, 544, 1188),
        "Dica",
        "Vale pensar no angulo de chegada do publico para o roll-up ficar visivel antes da pessoa parar.",
        YELLOW,
    )
    footer(draw, "3/4")
    return canvas


def slide_four() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, FOLDER, 598, 208, 368, 404)
    canvas = photo_card(canvas, BACKDROP, 674, 666, 244, 246)
    canvas = photo_card(canvas, ROLLUP, 630, 936, 286, 238)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 330, 228), MAGENTA, "FOLDER | FLYER")
    draw.multiline_text(
        (66, 286),
        "A PECA QUE\nVAI COM A\nPESSOA",
        font=font(BOLD, 60),
        fill=NAVY,
        spacing=8,
    )
    bullet_list(
        draw,
        [
            "Entrega informacao de contacto, servicos ou agenda para ser vista depois do evento.",
            "Ajuda a prolongar a conversa quando o visitante ja saiu do espaco.",
            "Fecha bem o conjunto com backdrop e roll-up para quem quer presenca e utilidade.",
        ],
        68,
        592,
        22,
        23,
        [YELLOW, CYAN, MAGENTA],
    )
    draw.rounded_rectangle((66, 1054, 566, 1132), radius=24, fill=NAVY)
    draw.text((100, 1082), "GUARDE E PECA ORCAMENTO", font=font(BOLD, 18), fill=OFF_WHITE)
    wrapped(
        draw,
        "Se vai preparar feira, activacao ou cerimonia, comente evento ou fale connosco em scolorprint.com.",
        66,
        1144,
        40,
        18,
        GRAPHITE,
        spacing=6,
    )
    footer(draw, "4/4")
    return canvas


def main() -> None:
    slides = [slide_one(), slide_two(), slide_three(), slide_four()]
    for index, slide in enumerate(slides, start=1):
        slide.convert("RGB").save(CAMPAIGN / f"slide-{index:02d}-v1.jpg", quality=94, subsampling=0)


if __name__ == "__main__":
    main()
