from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
LOGO = ROOT / "assets" / "logo-scp.png"
BASE = CAMPAIGN / "base-brand-v1.png"
VINIL = ROOT / "assets" / "trabalhos" / "vinil-montra-institucional.jpg"
FOLDER = ROOT / "assets" / "trabalhos" / "folders-e-flyers-impressos.jpg"
CARTAO = ROOT / "assets" / "mockup-cartao-real-v1.jpg"
ROLLUP = ROOT / "assets" / "trabalhos" / "rollup-evento-institucional.jpg"
BACKDROP = ROOT / "assets" / "trabalhos" / "backdrop-evento-institucional.jpg"

WIDTH = 1080
HEIGHT = 1350

NAVY = "#101935"
CYAN = "#19B3E6"
MAGENTA = "#EA1A72"
YELLOW = "#F3C515"
LIME = "#DFF364"
OFF_WHITE = "#FFFDF8"
GRAPHITE = "#2D3342"
SOFT_CARD = (255, 253, 248, 236)
CARD_BORDER = (16, 25, 53, 34)

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
    draw.rounded_rectangle((40, 126, 602, 1202), radius=54, fill=(255, 253, 248, 232))
    draw.rounded_rectangle((54, 144, 1024, 1216), radius=60, outline=(16, 25, 53, 18), width=4)
    draw.ellipse((-150, 980, 420, 1500), fill=(25, 179, 230, 20))
    draw.ellipse((748, 1010, 1160, 1410), fill=(16, 25, 53, 28))
    haze = haze.filter(ImageFilter.GaussianBlur(18))
    return Image.alpha_composite(base, haze)


def add_shadow(base: Image.Image, bounds: tuple[int, int, int, int], radius: int = 28, blur: int = 24) -> Image.Image:
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(bounds, radius=radius, fill=(10, 18, 39, 76))
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


def place_logo(base: Image.Image) -> None:
    logo = Image.open(LOGO).convert("RGBA")
    logo_width = 248
    logo_height = round(logo.height * logo_width / logo.width)
    logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
    base.alpha_composite(logo, (64, 48))


def pill(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], fill: str, text: str, text_fill: str = OFF_WHITE) -> None:
    draw.rounded_rectangle(bounds, radius=28, fill=fill)
    draw.text((bounds[0] + 24, bounds[1] + 14), text, font=font(BOLD, 22), fill=text_fill)


def footer(draw: ImageDraw.ImageDraw, page: str) -> None:
    draw.rectangle((0, 1250, WIDTH, HEIGHT), fill=NAVY)
    draw.text((64, 1282), "scolorprint.com", font=font(BOLD, 30), fill=OFF_WHITE)
    draw.text((814, 1282), page, font=font(BOLD, 28), fill=OFF_WHITE)


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


def bullets(draw: ImageDraw.ImageDraw, items: list[str], x: int, y: int, width_chars: int, size: int, colors: list[str]) -> int:
    cursor = y
    for index, item in enumerate(items):
        color = colors[index % len(colors)]
        draw.rounded_rectangle((x, cursor + 8, x + 28, cursor + 36), radius=9, fill=color)
        cursor = wrapped(draw, item, x + 50, cursor, width_chars, size, GRAPHITE, spacing=7) + 22
    return cursor


def info_card(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], title: str, body: str) -> None:
    draw.rounded_rectangle(bounds, radius=28, fill=SOFT_CARD, outline=CARD_BORDER, width=2)
    draw.text((bounds[0] + 24, bounds[1] + 20), title, font=font(BOLD, 28), fill=NAVY)
    wrapped(draw, body, bounds[0] + 24, bounds[1] + 70, 29, 21, GRAPHITE, spacing=6)


def checklist_card(draw: ImageDraw.ImageDraw, y: int, title: str, body: str, accent: str) -> None:
    draw.rounded_rectangle((66, y, 592, y + 148), radius=28, fill=SOFT_CARD, outline=CARD_BORDER, width=2)
    draw.rounded_rectangle((88, y + 24, 238, y + 62), radius=18, fill=accent)
    draw.text((108, y + 33), title, font=font(BOLD, 19), fill=NAVY)
    wrapped(draw, body, 90, y + 76, 40, 19, GRAPHITE, spacing=5)


def slide_one() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, VINIL, 652, 200, 286, 384)
    canvas = photo_card(canvas, FOLDER, 632, 628, 336, 232)
    canvas = photo_card(canvas, CARTAO, 682, 904, 236, 170)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 356, 228), MAGENTA, "DOMINGO | CHECKLIST")
    draw.multiline_text(
        (66, 286),
        "ANTES DE\nPEDIR O\nMATERIAL\nDA SEMANA",
        font=font(BOLD, 64),
        fill=NAVY,
        spacing=8,
    )
    draw.rectangle((68, 652, 146, 660), fill=CYAN)
    draw.rectangle((160, 652, 238, 660), fill=YELLOW)
    draw.rectangle((252, 652, 330, 660), fill=MAGENTA)
    wrapped(
        draw,
        "Fechar o briefing no domingo ajuda a pedir vinil, folders, cartoes, roll-ups ou fundo de evento com menos correria na segunda.",
        68,
        698,
        24,
        28,
        GRAPHITE,
        spacing=8,
    )
    draw.rounded_rectangle((68, 1046, 500, 1122), radius=24, fill=LIME)
    draw.text((98, 1072), "GUARDE PARA REVER HOJE", font=font(BOLD, 22), fill=NAVY)
    footer(draw, "1/5")
    return canvas


def slide_two() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, VINIL, 642, 196, 300, 904)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 254, 228), NAVY, "PASSO 1")
    draw.multiline_text((66, 286), "ONDE A\nMARCA VAI\nAPARECER\nPRIMEIRO?", font=font(BOLD, 56), fill=NAVY, spacing=8)
    bullets(
        draw,
        [
            "Entrada, porta, montra ou recepcao costumam abrir a leitura da semana.",
            "Quando esse ponto esta claro, vinil, placa ou orientacao ficam mais faceis de pedir.",
            "Se a chegada precisa acolher melhor, comece por aqui.",
        ],
        68,
        658,
        22,
        20,
        [CYAN, MAGENTA, YELLOW],
    )
    info_card(draw, (64, 1016, 548, 1198), "Entrada", "A primeira leitura da marca precisa funcionar antes da pessoa pedir ajuda.")
    footer(draw, "2/5")
    return canvas


def slide_three() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, FOLDER, 632, 194, 324, 418)
    canvas = photo_card(canvas, CARTAO, 668, 676, 252, 344)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 254, 228), CYAN, "PASSO 2", text_fill=NAVY)
    draw.multiline_text((66, 286), "O QUE A\nPESSOA VAI\nLEVAR?", font=font(BOLD, 58), fill=NAVY, spacing=8)
    bullets(
        draw,
        [
            "Folder, flyer ou cartao ajudam a conversa continuar depois da visita ou atendimento.",
            "Decida se a informacao precisa ser breve, dobrada ou pronta para circular.",
            "Com a peca de apoio definida, o pedido fica mais objectivo.",
        ],
        68,
        566,
        22,
        20,
        [YELLOW, MAGENTA, CYAN],
    )
    info_card(draw, (64, 998, 548, 1198), "Peca de apoio", "Escolha o formato pela utilidade real: entregar contacto, resumir servicos ou apoiar a proposta.")
    footer(draw, "3/5")
    return canvas


def slide_four() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, BACKDROP, 634, 198, 322, 358)
    canvas = photo_card(canvas, ROLLUP, 666, 612, 258, 466)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 254, 228), YELLOW, "PASSO 3", text_fill=NAVY)
    draw.multiline_text((66, 286), "O ESPACO\nPRECISA DE\nORIENTACAO\nOU FUNDO?", font=font(BOLD, 54), fill=NAVY, spacing=8)
    bullets(
        draw,
        [
            "Roll-up orienta a mensagem principal sem ocupar muito espaco.",
            "Backdrop entra quando a semana inclui recepcao, palco ou fotografia.",
            "As duas pecas resolvem funcoes diferentes no espaco.",
        ],
        68,
        690,
        21,
        20,
        [MAGENTA, CYAN, YELLOW],
    )
    info_card(draw, (64, 1020, 548, 1198), "Espaco", "Definir a funcao do local antes da producao evita pedir uma estrutura pouco util.")
    footer(draw, "4/5")
    return canvas


def slide_five() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, VINIL, 646, 196, 132, 280)
    canvas = photo_card(canvas, FOLDER, 798, 196, 146, 280)
    canvas = photo_card(canvas, ROLLUP, 646, 514, 132, 324)
    canvas = photo_card(canvas, BACKDROP, 798, 514, 146, 324)
    canvas = photo_card(canvas, CARTAO, 646, 878, 298, 220)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 360, 228), MAGENTA, "ANTES DO ORCAMENTO")
    draw.multiline_text((66, 286), "FECHE ESTAS\n4 DECISOES", font=font(BOLD, 62), fill=NAVY, spacing=8)
    checklist_card(draw, 520, "Entrada", "Onde a marca vai ser vista primeiro: porta, montra, recepcao ou corredor?", CYAN)
    checklist_card(draw, 690, "Apoio", "A pessoa precisa sair com folder, flyer, cartao ou apenas memorizar a mensagem?", YELLOW)
    checklist_card(draw, 860, "Espaco", "Vai existir ponto fixo que pede roll-up, backdrop ou outra peca de orientacao?", MAGENTA)
    checklist_card(draw, 1030, "Ficheiro", "Medida, texto final, contactos e quantidade ja estao fechados para pedir sem troca extra?", LIME)
    footer(draw, "5/5")
    return canvas


def export(image: Image.Image, name: str) -> None:
    image.convert("RGB").save(CAMPAIGN / name, quality=94, subsampling=0)


def main() -> None:
    slides = [
        ("slide-01-v1.jpg", slide_one()),
        ("slide-02-v1.jpg", slide_two()),
        ("slide-03-v1.jpg", slide_three()),
        ("slide-04-v1.jpg", slide_four()),
        ("slide-05-v1.jpg", slide_five()),
    ]
    for filename, image in slides:
        export(image, filename)


if __name__ == "__main__":
    main()
