from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
LOGO = ROOT / "assets" / "logo-scp.png"
BASE = CAMPAIGN / "base-brand-v1.png"
CARDS = ROOT / "assets" / "mockup-cartao-real-v1.jpg"
FLYERS = ROOT / "assets" / "trabalhos" / "folders-e-flyers-impressos.jpg"
FOLDER = ROOT / "assets" / "trabalhos" / "folder-criativo-corte-vinco.jpg"

WIDTH = 1080
HEIGHT = 1350

NAVY = "#101935"
CYAN = "#19B3E6"
MAGENTA = "#EA1A72"
YELLOW = "#F3C515"
OFF_WHITE = "#FFFDF8"
GRAPHITE = "#2D3342"
MIST = "#EFF4F8"
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
    draw.rounded_rectangle((42, 124, 1018, 1204), radius=54, fill=(255, 253, 248, 84))
    draw.rounded_rectangle((54, 140, 618, 1168), radius=48, fill=(255, 253, 248, 232))
    draw.ellipse((-120, 980, 420, 1490), fill=(16, 25, 53, 42))
    haze = haze.filter(ImageFilter.GaussianBlur(18))
    return Image.alpha_composite(base, haze)


def add_shadow(base: Image.Image, bounds: tuple[int, int, int, int], radius: int = 30, blur: int = 26) -> Image.Image:
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(bounds, radius=radius, fill=(10, 18, 39, 72))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(base, shadow)


def photo_card(base: Image.Image, source_path: Path, x: int, y: int, width: int, height: int, radius: int = 28) -> Image.Image:
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
    base.alpha_composite(logo, (66, 52))


def pill(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], fill: str, text: str, text_fill: str = OFF_WHITE) -> None:
    draw.rounded_rectangle(bounds, radius=28, fill=fill)
    draw.text((bounds[0] + 24, bounds[1] + 14), text, font=font(BOLD, 23), fill=text_fill)


def footer(draw: ImageDraw.ImageDraw, page: str) -> None:
    draw.rectangle((0, 1250, WIDTH, HEIGHT), fill=NAVY)
    draw.text((64, 1282), "scolorprint.com", font=font(BOLD, 30), fill=OFF_WHITE)
    draw.text((812, 1282), page, font=font(BOLD, 28), fill=OFF_WHITE)


def wrapped(draw: ImageDraw.ImageDraw, text: str, x: int, y: int, width_chars: int, size: int, fill: str, *, bold: bool = False, spacing: int = 7) -> int:
    family = BOLD if bold else REGULAR
    block = textwrap.fill(text, width=width_chars)
    draw.multiline_text((x, y), block, font=font(family, size), fill=fill, spacing=spacing)
    bbox = draw.multiline_textbbox((x, y), block, font=font(family, size), spacing=spacing)
    return bbox[3]


def bullets(draw: ImageDraw.ImageDraw, items: list[str], x: int, y: int, width_chars: int, size: int, colors: list[str]) -> int:
    cursor = y
    for index, item in enumerate(items):
        color = colors[index % len(colors)]
        draw.rounded_rectangle((x, cursor + 8, x + 28, cursor + 36), radius=9, fill=color)
        cursor = wrapped(draw, item, x + 50, cursor, width_chars, size, GRAPHITE, spacing=8) + 20
    return cursor


def info_card(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], title: str, body: str) -> None:
    draw.rounded_rectangle(bounds, radius=28, fill=(255, 253, 248, 224), outline=(16, 25, 53, 34), width=2)
    draw.text((bounds[0] + 24, bounds[1] + 22), title, font=font(BOLD, 29), fill=NAVY)
    wrapped(draw, body, bounds[0] + 24, bounds[1] + 74, 28, 22, GRAPHITE, spacing=6)


def combo_block(draw: ImageDraw.ImageDraw, y: int, title: str, body: str, accent: str) -> None:
    draw.rounded_rectangle((66, y, 592, y + 162), radius=28, fill=(255, 253, 248, 230), outline=(16, 25, 53, 32), width=2)
    draw.rounded_rectangle((86, y + 24, 184, y + 66), radius=20, fill=accent)
    draw.text((104, y + 34), title, font=font(BOLD, 22), fill=NAVY)
    wrapped(draw, body, 88, y + 82, 38, 22, GRAPHITE, spacing=6)


def slide_one() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, CARDS, 672, 174, 274, 238)
    canvas = photo_card(canvas, FLYERS, 620, 454, 324, 332)
    canvas = photo_card(canvas, FOLDER, 652, 832, 284, 300)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 318, 228), MAGENTA, "TERÇA | EDUCATIVO")
    draw.multiline_text(
        (66, 286),
        "CARTÃO,\nFLYER OU\nFOLDER?",
        font=font(BOLD, 68),
        fill=NAVY,
        spacing=8,
    )
    draw.rectangle((68, 626, 148, 634), fill=CYAN)
    draw.rectangle((162, 626, 242, 634), fill=YELLOW)
    draw.rectangle((256, 626, 336, 634), fill=MAGENTA)
    wrapped(
        draw,
        "Cada peça resolve uma parte diferente da conversa com o cliente. Escolher bem evita material bonito, mas pouco útil.",
        68,
        676,
        24,
        29,
        GRAPHITE,
        spacing=8,
    )
    draw.rounded_rectangle((68, 1016, 504, 1094), radius=24, fill=LIME)
    draw.text((96, 1040), "GUARDE PARA ESCOLHER MELHOR", font=font(BOLD, 24), fill=NAVY)
    footer(draw, "1/5")
    return canvas


def slide_two() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, CARDS, 632, 196, 328, 902)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 218, 228), NAVY, "PEÇA 1")
    draw.multiline_text((66, 286), "CARTÃO DE\nVISITA", font=font(BOLD, 62), fill=NAVY, spacing=8)
    bullets(
        draw,
        [
            "Serve bem quando o objectivo é deixar contacto rápido depois de uma reunião, visita ou entrega.",
            "Nome, função, telefone e WhatsApp precisam de ficar legíveis logo no primeiro olhar.",
            "Se os dados mudam com frequência, vale rever a informação antes de imprimir.",
        ],
        68,
        520,
        22,
        25,
        [CYAN, MAGENTA, YELLOW],
    )
    info_card(draw, (64, 970, 548, 1200), "Use quando", "Precisa que a pessoa guarde o seu contacto sem depender do telemóvel na hora.")
    footer(draw, "2/5")
    return canvas


def slide_three() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, FLYERS, 626, 196, 334, 906)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 206, 228), CYAN, "PEÇA 2", text_fill=NAVY)
    draw.multiline_text((66, 286), "FLYER", font=font(BOLD, 68), fill=NAVY, spacing=8)
    bullets(
        draw,
        [
            "Ajuda quando quer divulgar uma campanha, serviço, evento ou menu com mensagem curta e directa.",
            "Funciona melhor com uma ideia principal e um CTA claro, em vez de tentar dizer tudo de uma vez.",
            "Se o texto já está grande demais, talvez precise de outra peça para não perder leitura rápida.",
        ],
        68,
        474,
        22,
        25,
        [YELLOW, MAGENTA, CYAN],
    )
    info_card(draw, (64, 996, 548, 1188), "Use quando", "Quer distribuir a mesma mensagem a muitas pessoas e precisa de leitura imediata.")
    footer(draw, "3/5")
    return canvas


def slide_four() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, FOLDER, 630, 198, 330, 902)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 210, 228), YELLOW, "PEÇA 3", text_fill=NAVY)
    draw.multiline_text((66, 286), "FOLDER", font=font(BOLD, 68), fill=NAVY, spacing=8)
    bullets(
        draw,
        [
            "É útil quando precisa apresentar serviços, categorias ou passos com mais detalhe e melhor ordem.",
            "Costuma funcionar bem em reuniões, balcão, propostas presenciais e apresentações da marca.",
            "Antes de imprimir, confirme só o essencial para não sobrecarregar o conteúdo.",
        ],
        68,
        474,
        22,
        25,
        [MAGENTA, CYAN, YELLOW],
    )
    info_card(draw, (64, 974, 548, 1200), "Use quando", "Precisa explicar mais do que uma oferta e quer deixar a informação organizada.")
    footer(draw, "4/5")
    return canvas


def slide_five() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, CARDS, 644, 198, 264, 214)
    canvas = photo_card(canvas, FLYERS, 610, 454, 318, 268)
    canvas = photo_card(canvas, FOLDER, 642, 764, 276, 292)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 312, 228), MAGENTA, "GUIA RÁPIDO")
    draw.multiline_text((66, 286), "ESCOLHA PELA\nCONVERSA QUE\nQUER ABRIR", font=font(BOLD, 58), fill=NAVY, spacing=8)
    combo_block(draw, 610, "Cartão", "Quando o foco é contacto rápido e continuidade depois da conversa.", CYAN)
    combo_block(draw, 778, "Flyer", "Quando a prioridade é circular a mesma mensagem em mais mãos.", YELLOW)
    combo_block(draw, 946, "Folder", "Quando precisa mostrar melhor a oferta antes do próximo passo.", MAGENTA)
    draw.rounded_rectangle((66, 1126, 590, 1194), radius=24, fill=NAVY)
    draw.text((92, 1146), "Comente a peça que mais usa.", font=font(BOLD, 24), fill=OFF_WHITE)
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
