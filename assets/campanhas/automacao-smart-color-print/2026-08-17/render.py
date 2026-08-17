from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
LOGO = ROOT / "assets" / "logo-scp.png"
BASE = CAMPAIGN / "base-brand-v1.png"
PLACAS = ROOT / "assets" / "categorias" / "placas-sinaletica.jpg"
VINIL = ROOT / "assets" / "trabalhos" / "vinil-montra-institucional.jpg"
ROLLUP = ROOT / "assets" / "trabalhos" / "rollup-evento-institucional.jpg"
FOLDER = ROOT / "assets" / "trabalhos" / "folders-e-flyers-impressos.jpg"

WIDTH = 1080
HEIGHT = 1350

NAVY = "#101935"
CYAN = "#19B3E6"
MAGENTA = "#EA1A72"
YELLOW = "#F3C515"
LIME = "#D7F04D"
OFF_WHITE = "#FFFDF8"
GRAPHITE = "#2E3443"
SOFT_CARD = (255, 253, 248, 232)

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
    draw.rounded_rectangle((42, 136, 1016, 1206), radius=56, fill=(255, 253, 248, 84))
    draw.rounded_rectangle((58, 156, 586, 1178), radius=46, fill=(255, 253, 248, 232))
    draw.ellipse((-140, 960, 404, 1492), fill=(25, 179, 230, 22))
    draw.ellipse((748, 952, 1170, 1410), fill=(16, 25, 53, 28))
    haze = haze.filter(ImageFilter.GaussianBlur(18))
    return Image.alpha_composite(base, haze)


def add_shadow(base: Image.Image, bounds: tuple[int, int, int, int], radius: int = 30, blur: int = 28) -> Image.Image:
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(bounds, radius=radius, fill=(10, 18, 39, 72))
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
    draw.rounded_rectangle(bounds, radius=28, fill=SOFT_CARD, outline=(16, 25, 53, 34), width=2)
    draw.rounded_rectangle((bounds[0] + 24, bounds[1] + 24, bounds[0] + 190, bounds[1] + 60), radius=18, fill=accent)
    draw.text((bounds[0] + 48, bounds[1] + 33), title, font=font(BOLD, 20), fill=NAVY)
    wrapped(draw, body, bounds[0] + 24, bounds[1] + 76, 29, 21, GRAPHITE, spacing=6)


def footer(draw: ImageDraw.ImageDraw, page: str) -> None:
    draw.rectangle((0, 1250, WIDTH, HEIGHT), fill=NAVY)
    draw.text((64, 1282), "scolorprint.com", font=font(BOLD, 30), fill=OFF_WHITE)
    draw.text((814, 1282), page, font=font(BOLD, 28), fill=OFF_WHITE)


def slide_one() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, PLACAS, 618, 198, 340, 238)
    canvas = photo_card(canvas, VINIL, 618, 474, 340, 422)
    canvas = photo_card(canvas, ROLLUP, 626, 936, 156, 246)
    canvas = photo_card(canvas, FOLDER, 802, 972, 156, 176)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 418, 228), MAGENTA, "SEGUNDA | RECEPCAO")
    draw.multiline_text(
        (66, 286),
        "ATENDIMENTO\nMAIS CLARO\nCOM 4 APOIOS\nVISUAIS",
        font=font(BOLD, 61),
        fill=NAVY,
        spacing=8,
    )
    draw.rectangle((68, 666, 146, 674), fill=CYAN)
    draw.rectangle((160, 666, 238, 674), fill=MAGENTA)
    draw.rectangle((252, 666, 330, 674), fill=YELLOW)
    wrapped(
        draw,
        "Placa, vinil, roll-up e folder ajudam a orientar quem chega antes da primeira explicacao.",
        68,
        710,
        24,
        28,
        GRAPHITE,
        spacing=8,
    )
    draw.rounded_rectangle((68, 1012, 492, 1088), radius=24, fill=LIME)
    draw.text((98, 1038), "VEJA ONDE CADA PECA AJUDA", font=font(BOLD, 22), fill=NAVY)
    footer(draw, "1/5")
    return canvas


def slide_two() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, PLACAS, 620, 188, 350, 892)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 250, 228), NAVY, "PLACA")
    draw.multiline_text(
        (66, 286),
        "IDENTIFIQUE\nO ESPACO\nLOGO A\nDISTANCIA",
        font=font(BOLD, 57),
        fill=NAVY,
        spacing=8,
    )
    bullet_list(
        draw,
        [
            "Ajuda a localizar recepcao, bloco, piso ou entrada sem depender logo de pergunta.",
            "Funciona bem quando ha mais de um acesso ou mais de um servico no mesmo espaco.",
            "Quando a leitura esta clara ainda fora, a chegada de segunda fica mais fluida.",
        ],
        68,
        632,
        21,
        24,
        [CYAN, MAGENTA, YELLOW],
    )
    info_card(
        draw,
        (64, 1006, 550, 1186),
        "Bom uso",
        "Fachada, condominio, instituicao, loja ou ponto de atendimento com mais de uma referencia visual.",
        LIME,
    )
    footer(draw, "2/5")
    return canvas


def slide_three() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, VINIL, 624, 188, 348, 892)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 250, 228), CYAN, "VINIL", text_fill=NAVY)
    draw.multiline_text(
        (66, 286),
        "DE LEITURA\nA PORTA\nE A\nMONTRA",
        font=font(BOLD, 58),
        fill=NAVY,
        spacing=8,
    )
    bullet_list(
        draw,
        [
            "Transforma vidro ou porta num ponto claro de identificacao sem ocupar area util.",
            "Ajuda a mostrar nome, servico ou mensagem principal logo na entrada.",
            "Fecha bem a presenca da marca quando a montra e a primeira referencia do espaco.",
        ],
        68,
        632,
        21,
        24,
        [MAGENTA, YELLOW, CYAN],
    )
    info_card(
        draw,
        (64, 1008, 550, 1188),
        "Dica",
        "Menos elementos costuma dar melhor leitura a media distancia do que uma porta sobrecarregada.",
        YELLOW,
    )
    footer(draw, "3/5")
    return canvas


def slide_four() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, ROLLUP, 652, 196, 256, 900)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 284, 228), YELLOW, "ROLL-UP", text_fill=NAVY)
    draw.multiline_text(
        (66, 286),
        "UMA\nMENSAGEM\nFORTE NUM\nPONTO SO",
        font=font(BOLD, 57),
        fill=NAVY,
        spacing=8,
    )
    bullet_list(
        draw,
        [
            "Serve para orientar, receber ou resumir uma chamada principal onde a pessoa abranda.",
            "Entra bem em corredores, recepcoes, salas, eventos e cantos com pouco espaco.",
        ],
        68,
        632,
        21,
        22,
        [YELLOW, CYAN, MAGENTA],
    )
    info_card(
        draw,
        (64, 1008, 550, 1190),
        "Regra simples",
        "Escolha uma so ideia principal para o roll-up e deixe o restante apoio para outras pecas.",
        CYAN,
    )
    footer(draw, "4/5")
    return canvas


def slide_five() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, FOLDER, 602, 214, 358, 430)
    canvas = photo_card(canvas, PLACAS, 634, 714, 146, 174)
    canvas = photo_card(canvas, VINIL, 800, 714, 146, 174)
    canvas = photo_card(canvas, ROLLUP, 718, 908, 146, 220)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 346, 228), MAGENTA, "FOLDER | FLYER")
    draw.multiline_text(
        (66, 286),
        "A REFERENCIA\nQUE SEGUE\nCOM A\nPESSOA",
        font=font(BOLD, 58),
        fill=NAVY,
        spacing=8,
    )
    bullet_list(
        draw,
        [
            "Folder ou flyer prolonga a conversa depois da visita, reuniao ou atendimento.",
            "Funciona melhor quando placa, vinil ou roll-up ja prepararam a chegada.",
            "Guarde este carrossel para rever antes da semana.",
        ],
        68,
        642,
        21,
        22,
        [CYAN, MAGENTA, YELLOW],
    )
    draw.rounded_rectangle((66, 1110, 550, 1190), radius=24, fill=NAVY)
    draw.text((98, 1138), 'COMENTE "ATENDIMENTO" OU PECA ORCAMENTO', font=font(BOLD, 18), fill=OFF_WHITE)
    footer(draw, "5/5")
    return canvas


def main() -> None:
    slides = [slide_one(), slide_two(), slide_three(), slide_four(), slide_five()]
    for index, slide in enumerate(slides, start=1):
        output = CAMPAIGN / f"slide-{index:02d}-v1.jpg"
        slide.convert("RGB").save(output, quality=95, subsampling=0)


if __name__ == "__main__":
    main()
