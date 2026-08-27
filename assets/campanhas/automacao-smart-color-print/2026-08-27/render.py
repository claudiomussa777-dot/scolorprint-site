from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
LOGO = ROOT / "assets" / "logo-scp.png"
BASE = CAMPAIGN / "base-brand-v1.png"
COLETES = ROOT / "assets" / "categorias" / "coletes-uniformes.jpg"

WIDTH = 1080
HEIGHT = 1350

NAVY = "#101935"
CYAN = "#19B3E6"
MAGENTA = "#EA1A72"
YELLOW = "#F3C515"
LIME = "#DFF364"
OFF_WHITE = "#FFFDF8"
GRAPHITE = "#2D3342"
SOFT_CARD = (255, 253, 248, 234)
CARD_BORDER = (16, 25, 53, 32)

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
    draw.rounded_rectangle((54, 146, 594, 1188), radius=52, fill=(255, 253, 248, 224))
    draw.rounded_rectangle((616, 170, 1008, 1158), radius=48, fill=(255, 253, 248, 72))
    draw.ellipse((-120, 944, 386, 1478), fill=(25, 179, 230, 18))
    draw.ellipse((748, 972, 1186, 1420), fill=(16, 25, 53, 18))
    haze = haze.filter(ImageFilter.GaussianBlur(18))
    return Image.alpha_composite(base, haze)


def add_shadow(base: Image.Image, bounds: tuple[int, int, int, int], radius: int = 28, blur: int = 24) -> Image.Image:
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(bounds, radius=radius, fill=(10, 18, 39, 72))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(base, shadow)


def photo_card(base: Image.Image, source_path: Path, x: int, y: int, width: int, height: int, radius: int = 32) -> Image.Image:
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
        color = colors[index % len(colors)]
        draw.rounded_rectangle((x, cursor + 8, x + 28, cursor + 36), radius=9, fill=color)
        cursor = wrapped(draw, item, x + 50, cursor, width_chars, size, GRAPHITE, spacing=7) + 24
    return cursor


def info_card(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], title: str, body: str, accent: str) -> None:
    draw.rounded_rectangle(bounds, radius=28, fill=SOFT_CARD, outline=CARD_BORDER, width=2)
    draw.rounded_rectangle((bounds[0] + 24, bounds[1] + 22, bounds[0] + 214, bounds[1] + 58), radius=18, fill=accent)
    draw.text((bounds[0] + 46, bounds[1] + 31), title, font=font(BOLD, 20), fill=NAVY)
    wrapped(draw, body, bounds[0] + 24, bounds[1] + 76, 33, 18, GRAPHITE, spacing=6)


def footer(draw: ImageDraw.ImageDraw, page: str) -> None:
    draw.rectangle((0, 1250, WIDTH, HEIGHT), fill=NAVY)
    draw.text((64, 1282), "scolorprint.com", font=font(BOLD, 30), fill=OFF_WHITE)
    draw.text((826, 1282), page, font=font(BOLD, 28), fill=OFF_WHITE)


def role_card(draw: ImageDraw.ImageDraw, x: int, y: int, accent: str, title: str, body: str) -> None:
    draw.rounded_rectangle((x, y, x + 480, y + 126), radius=26, fill=SOFT_CARD, outline=CARD_BORDER, width=2)
    draw.rounded_rectangle((x + 20, y + 22, x + 90, y + 90), radius=20, fill=accent)
    draw.text((x + 114, y + 22), title, font=font(BOLD, 24), fill=NAVY)
    wrapped(draw, body, x + 114, y + 54, 27, 17, GRAPHITE, spacing=5)


def checklist_item(draw: ImageDraw.ImageDraw, x: int, y: int, number: str, title: str, body: str, accent: str) -> None:
    draw.rounded_rectangle((x, y, x + 474, y + 134), radius=26, fill=SOFT_CARD, outline=CARD_BORDER, width=2)
    draw.ellipse((x + 22, y + 24, x + 86, y + 88), fill=accent)
    draw.text((x + 47, y + 40), number, font=font(BOLD, 22), fill=NAVY)
    draw.text((x + 112, y + 24), title, font=font(BOLD, 24), fill=NAVY)
    wrapped(draw, body, x + 112, y + 56, 26, 18, GRAPHITE, spacing=5)


def slide_one() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, COLETES, 642, 190, 314, 920)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 458, 228), MAGENTA, "QUINTA | PROBLEMA + SOLUCAO")
    draw.multiline_text(
        (66, 286),
        "EQUIPA SEM\nIDENTIFICACAO\nNO LOCAL?",
        font=font(BOLD, 60),
        fill=NAVY,
        spacing=8,
    )
    draw.rectangle((68, 610, 146, 618), fill=CYAN)
    draw.rectangle((160, 610, 238, 618), fill=YELLOW)
    draw.rectangle((252, 610, 330, 618), fill=MAGENTA)
    wrapped(
        draw,
        "Coletes personalizados ajudam a distinguir visitante, apoio e equipa logo na chegada, com leitura simples e mais ordem no espaco.",
        68,
        652,
        24,
        28,
        GRAPHITE,
        spacing=8,
    )
    draw.rounded_rectangle((68, 1032, 458, 1108), radius=24, fill=LIME)
    draw.text((104, 1058), "GUARDE PARA O PROXIMO SERVICO", font=font(BOLD, 20), fill=NAVY)
    footer(draw, "1/4")
    return canvas


def slide_two() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, COLETES, 656, 222, 270, 324)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 280, 228), NAVY, "1 | PROBLEMA")
    draw.multiline_text((66, 286), "QUANDO TODA\nA GENTE\nPARECE IGUAL", font=font(BOLD, 58), fill=NAVY, spacing=8)
    bullet_list(
        draw,
        [
            "Visitantes e clientes demoram mais a perceber quem pode orientar.",
            "Apoio, recepcao e trabalho no terreno ficam menos claros em momentos de pressa.",
            "A marca aparece, mas a funcao de cada pessoa continua escondida.",
        ],
        68,
        604,
        22,
        22,
        [CYAN, MAGENTA, YELLOW],
    )
    info_card(
        draw,
        (64, 978, 966, 1168),
        "Leitura rapida",
        "Em obra, evento ou atendimento, a funcao precisa de ser percebida logo no primeiro olhar.",
        LIME,
    )
    footer(draw, "2/4")
    return canvas


def slide_three() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, COLETES, 652, 210, 288, 410)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 286, 228), CYAN, "2 | SOLUCAO", text_fill=NAVY)
    draw.multiline_text((66, 286), "COLETE CERTO,\nFUNCAO CLARA", font=font(BOLD, 58), fill=NAVY, spacing=8)
    wrapped(
        draw,
        "Quando a peca traz cor, marca e funcao visiveis, a equipa passa a ser reconhecida antes mesmo da conversa.",
        68,
        498,
        25,
        26,
        GRAPHITE,
        spacing=7,
    )
    role_card(draw, 64, 686, CYAN, "Visitante", "Separa quem visita de quem esta a operar no local.")
    role_card(draw, 64, 834, MAGENTA, "Apoio", "Ajuda a apontar quem recebe, orienta ou responde.")
    role_card(draw, 64, 982, YELLOW, "Equipa", "Mantem a marca visivel com funcao pratica de identificacao.")
    footer(draw, "3/4")
    return canvas


def slide_four() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, COLETES, 690, 204, 236, 316)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 358, 228), YELLOW, "3 | ANTES DE PEDIR", text_fill=NAVY)
    draw.multiline_text((66, 286), "4 DADOS PARA\nPEDIR MELHOR", font=font(BOLD, 60), fill=NAVY, spacing=8)
    checklist_item(draw, 64, 576, "1", "Quantidade", "Quantas pessoas vao usar e se ha funcoes diferentes.", CYAN)
    checklist_item(draw, 64, 724, "2", "Tamanho", "Que tamanhos precisam de entrar no mesmo pedido.", MAGENTA)
    checklist_item(draw, 64, 872, "3", "Funcao", "Se vai levar so a marca ou tambem visitante, apoio ou outra indicacao.", YELLOW)
    checklist_item(draw, 64, 1020, "4", "Uso", "Se o colete vai para obra, evento, logistica ou atendimento.", LIME)
    footer(draw, "4/4")
    return canvas


def main() -> None:
    slides = [slide_one(), slide_two(), slide_three(), slide_four()]
    for index, slide in enumerate(slides, start=1):
        target = CAMPAIGN / f"slide-0{index}-v1.jpg"
        slide.convert("RGB").save(target, format="JPEG", quality=92, optimize=True)


if __name__ == "__main__":
    main()
