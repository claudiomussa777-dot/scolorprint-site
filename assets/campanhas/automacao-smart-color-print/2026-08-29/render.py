from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
LOGO = ROOT / "assets" / "logo-scp.png"
BASE = CAMPAIGN / "base-brand-v1.png"
ROLLUP = ROOT / "assets" / "trabalhos" / "rollup-conferencia-direitos-humanos.jpg"
FOLDERS = ROOT / "assets" / "trabalhos" / "folders-e-flyers-impressos.jpg"

WIDTH = 1080
HEIGHT = 1350

NAVY = "#0E1A36"
CYAN = "#18B2E4"
MAGENTA = "#E61A73"
YELLOW = "#F5C517"
LIME = "#D9F238"
OFF_WHITE = "#FFFDF7"
GRAPHITE = "#2E3445"
SOFT_CARD = (255, 253, 247, 232)
CARD_BORDER = (14, 26, 54, 26)

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
    draw.rounded_rectangle((50, 132, 580, 1178), radius=48, fill=(255, 253, 247, 198))
    draw.rounded_rectangle((606, 154, 1024, 1164), radius=48, fill=(255, 253, 247, 86))
    draw.ellipse((-90, 872, 400, 1420), fill=(24, 178, 228, 24))
    draw.ellipse((742, 820, 1150, 1290), fill=(230, 26, 115, 16))
    haze = haze.filter(ImageFilter.GaussianBlur(18))
    return Image.alpha_composite(base, haze)


def place_logo(base: Image.Image) -> None:
    logo = Image.open(LOGO).convert("RGBA")
    logo_width = 252
    logo_height = round(logo.height * logo_width / logo.width)
    logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
    base.alpha_composite(logo, (64, 48))


def add_shadow(base: Image.Image, bounds: tuple[int, int, int, int], radius: int = 30, blur: int = 22) -> Image.Image:
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(bounds, radius=radius, fill=(12, 18, 36, 72))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(base, shadow)


def photo_card(base: Image.Image, source_path: Path, x: int, y: int, width: int, height: int, radius: int = 28) -> Image.Image:
    base = add_shadow(base, (x + 10, y + 12, x + width + 10, y + height + 12), radius=radius, blur=26)
    card = fit_cover(Image.open(source_path), width, height).convert("RGBA")
    mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, width, height), radius=radius, fill=255)
    card.putalpha(mask)
    base.alpha_composite(card, (x, y))
    return base


def fill_card(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], fill, outline=CARD_BORDER) -> None:
    draw.rounded_rectangle(bounds, radius=26, fill=fill, outline=outline, width=2)


def pill(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], fill: str, text: str, text_fill: str = OFF_WHITE) -> None:
    draw.rounded_rectangle(bounds, radius=28, fill=fill)
    draw.text((bounds[0] + 22, bounds[1] + 15), text, font=font(BOLD, 22), fill=text_fill)


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


def footer(draw: ImageDraw.ImageDraw, page: str) -> None:
    draw.rectangle((0, 1250, WIDTH, HEIGHT), fill=NAVY)
    draw.text((64, 1282), "scolorprint.com", font=font(BOLD, 30), fill=OFF_WHITE)
    draw.text((828, 1282), page, font=font(BOLD, 28), fill=OFF_WHITE)


def accent_lines(draw: ImageDraw.ImageDraw, y: int) -> None:
    draw.rectangle((66, y, 146, y + 8), fill=CYAN)
    draw.rectangle((160, y, 240, y + 8), fill=YELLOW)
    draw.rectangle((254, y, 334, y + 8), fill=MAGENTA)


def draw_business_card(base: Image.Image, x: int, y: int, width: int, height: int) -> None:
    card = Image.new("RGBA", (width, height), OFF_WHITE)
    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=30, fill=OFF_WHITE, outline=(14, 26, 54, 28), width=2)
    draw.rectangle((0, 0, width, 24), fill=NAVY)
    draw.rectangle((0, height - 18, width, height), fill=CYAN)
    draw.polygon([(0, height), (0, height - 70), (140, height)], fill=MAGENTA)
    mini_logo = Image.open(LOGO).convert("RGBA")
    mini_width = 168
    mini_height = round(mini_logo.height * mini_width / mini_logo.width)
    mini_logo = mini_logo.resize((mini_width, mini_height), Image.Resampling.LANCZOS)
    card.alpha_composite(mini_logo, (28, 36))
    draw.rounded_rectangle((28, 130, 184, 148), radius=9, fill=(14, 26, 54, 18))
    draw.rounded_rectangle((28, 156, 208, 172), radius=8, fill=(14, 26, 54, 12))
    draw.rounded_rectangle((28, 180, 152, 194), radius=7, fill=(14, 26, 54, 10))
    base.alpha_composite(card, (x, y))


def section_card(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], accent: str, title: str, body: str, width_chars: int = 24) -> None:
    fill_card(draw, bounds, SOFT_CARD)
    draw.rounded_rectangle((bounds[0] + 20, bounds[1] + 20, bounds[0] + 74, bounds[1] + 74), radius=18, fill=accent)
    draw.text((bounds[0] + 96, bounds[1] + 22), title, font=font(BOLD, 24), fill=NAVY)
    wrapped(draw, body, bounds[0] + 96, bounds[1] + 56, width_chars, 18, GRAPHITE, spacing=6)


def check_item(draw: ImageDraw.ImageDraw, x: int, y: int, number: str, title: str, body: str, accent: str) -> None:
    fill_card(draw, (x, y, x + 462, y + 128), SOFT_CARD)
    draw.ellipse((x + 22, y + 22, x + 86, y + 86), fill=accent)
    draw.text((x + 46, y + 40), number, font=font(BOLD, 22), fill=NAVY)
    draw.text((x + 108, y + 24), title, font=font(BOLD, 22), fill=NAVY)
    wrapped(draw, body, x + 108, y + 56, 25, 17, GRAPHITE, spacing=5)


def slide_one() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, ROLLUP, 650, 174, 264, 506)
    canvas = photo_card(canvas, FOLDERS, 622, 712, 338, 254)
    draw_business_card(canvas, 694, 996, 248, 150)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 370, 228), MAGENTA, "SABADO | INSPIRACAO")
    draw.multiline_text((66, 286), "PONTO DE\nATENDIMENTO\nLEVE", font=font(BOLD, 62), fill=NAVY, spacing=8)
    accent_lines(draw, 602)
    wrapped(
        draw,
        "Para balcao, recepcao ou feira pequena, um conjunto simples ja ajuda a explicar, orientar e continuar o contacto.",
        68,
        644,
        24,
        28,
        GRAPHITE,
        spacing=8,
    )
    fill_card(draw, (66, 980, 500, 1110), (217, 242, 56, 214))
    draw.text((98, 1008), "ROLL-UP + FOLDERS + CARTOES", font=font(BOLD, 22), fill=NAVY)
    wrapped(draw, "Tres pecas, funcoes diferentes e leitura mais clara.", 98, 1044, 30, 17, NAVY, spacing=5)
    footer(draw, "1/4")
    return canvas


def slide_two() -> Image.Image:
    canvas = make_canvas()
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 324, 228), NAVY, "1 | O CONJUNTO")
    draw.multiline_text((66, 286), "3 PECAS,\n3 FUNCOES", font=font(BOLD, 60), fill=NAVY, spacing=8)
    section_card(draw, (64, 514, 510, 690), CYAN, "Roll-up", "Ajuda a chamar atencao de longe e resume a mensagem principal.")
    section_card(draw, (64, 724, 510, 900), MAGENTA, "Folders", "Levam servicos, detalhes ou contactos para a pessoa consultar depois.")
    section_card(draw, (64, 934, 510, 1110), YELLOW, "Cartoes", "Mantem o contacto activo quando a conversa termina e a visita segue.")
    canvas = photo_card(canvas, ROLLUP, 628, 248, 292, 366)
    canvas = photo_card(canvas, FOLDERS, 602, 650, 340, 220)
    draw_business_card(canvas, 646, 942, 244, 148)
    draw = ImageDraw.Draw(canvas)
    footer(draw, "2/4")
    return canvas


def slide_three() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, FOLDERS, 620, 230, 316, 236)
    canvas = photo_card(canvas, ROLLUP, 716, 500, 188, 404)
    draw_business_card(canvas, 638, 950, 256, 154)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 394, 228), CYAN, "2 | QUANDO AJUDA", text_fill=NAVY)
    draw.multiline_text((66, 286), "ONDE ESTE\nCONJUNTO\nFAZ SENTIDO", font=font(BOLD, 58), fill=NAVY, spacing=8)
    section_card(draw, (64, 612, 510, 760), CYAN, "Recepcao pequena", "Quando ha pouco espaco, mas a marca precisa de se apresentar logo na chegada.", width_chars=25)
    section_card(draw, (64, 790, 510, 938), MAGENTA, "Feira compacta", "Funciona bem para apoio rapido, conversa curta e entrega de material util.", width_chars=25)
    section_card(draw, (64, 968, 510, 1116), YELLOW, "Ponto de apoio", "Ajuda a orientar quem passa sem depender de muita estrutura montada.", width_chars=25)
    footer(draw, "3/4")
    return canvas


def slide_four() -> Image.Image:
    canvas = make_canvas()
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 386, 228), YELLOW, "3 | ANTES DE PEDIR", text_fill=NAVY)
    draw.multiline_text((66, 286), "4 DADOS PARA\nPEDIR MELHOR", font=font(BOLD, 60), fill=NAVY, spacing=8)
    check_item(draw, 64, 570, "1", "Mensagem", "Qual e a ideia principal que precisa de ser lida primeiro.", CYAN)
    check_item(draw, 552, 570, "2", "Espaco", "Quanto espaco existe no balcao, recepcao ou ponto de apoio.", MAGENTA)
    check_item(draw, 64, 724, "3", "Entrega", "Que material a pessoa deve levar consigo depois do contacto.", YELLOW)
    check_item(draw, 552, 724, "4", "Uso", "Se a montagem vai servir evento, reuniao, activacao ou atendimento.", LIME)
    fill_card(draw, (64, 916, 1016, 1112), (16, 26, 54, 222), outline=(16, 26, 54, 0))
    draw.text((96, 954), "Guarde esta ideia para o proximo balcao ou activacao.", font=font(BOLD, 28), fill=OFF_WHITE)
    wrapped(
        draw,
        "Se precisar de roll-up, folders, cartoes ou outras pecas de apoio, peca o seu orcamento por mensagem ou em scolorprint.com.",
        96,
        998,
        49,
        21,
        OFF_WHITE,
        spacing=6,
    )
    footer(draw, "4/4")
    return canvas


def main() -> None:
    slides = [slide_one(), slide_two(), slide_three(), slide_four()]
    for index, slide in enumerate(slides, start=1):
        output = CAMPAIGN / f"slide-{index:02d}-v1.jpg"
        slide.convert("RGB").save(output, quality=92, subsampling=0)


if __name__ == "__main__":
    main()
