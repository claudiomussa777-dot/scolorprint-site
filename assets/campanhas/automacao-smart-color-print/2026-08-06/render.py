from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
LOGO = ROOT / "assets" / "logo-scp.png"
BASE = CAMPAIGN / "base-brand-v1.png"
PENS = ROOT / "assets" / "trabalhos" / "canetas-personalizadas.jpg"

WIDTH = 1080
HEIGHT = 1350

NAVY = "#101935"
CYAN = "#19B3E6"
MAGENTA = "#EA1A72"
YELLOW = "#F3C515"
OFF_WHITE = "#FFFDF8"
GRAPHITE = "#2D3342"
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
    draw.rounded_rectangle((42, 126, 1018, 1204), radius=54, fill=(255, 253, 248, 86))
    draw.rounded_rectangle((56, 142, 602, 1168), radius=48, fill=(255, 253, 248, 232))
    draw.ellipse((-140, 938, 438, 1524), fill=(16, 25, 53, 34))
    draw.ellipse((760, 1020, 1160, 1470), fill=(25, 179, 230, 26))
    haze = haze.filter(ImageFilter.GaussianBlur(18))
    return Image.alpha_composite(base, haze)


def add_shadow(base: Image.Image, bounds: tuple[int, int, int, int], radius: int = 30, blur: int = 26) -> Image.Image:
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(bounds, radius=radius, fill=(10, 18, 39, 74))
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
    block = textwrap.fill(text, width=width_chars)
    draw.multiline_text((x, y), block, font=font(family, size), fill=fill, spacing=spacing)
    bbox = draw.multiline_textbbox((x, y), block, font=font(family, size), spacing=spacing)
    return bbox[3]


def bullet_list(draw: ImageDraw.ImageDraw, items: list[str], x: int, y: int, width_chars: int, size: int, colors: list[str]) -> int:
    cursor = y
    for index, item in enumerate(items):
        color = colors[index % len(colors)]
        draw.rounded_rectangle((x, cursor + 8, x + 28, cursor + 36), radius=9, fill=color)
        cursor = wrapped(draw, item, x + 50, cursor, width_chars, size, GRAPHITE, spacing=8) + 22
    return cursor


def note_card(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], title: str, body: str) -> None:
    draw.rounded_rectangle(bounds, radius=28, fill=(255, 253, 248, 224), outline=(16, 25, 53, 34), width=2)
    draw.text((bounds[0] + 24, bounds[1] + 22), title, font=font(BOLD, 27), fill=NAVY)
    wrapped(draw, body, bounds[0] + 24, bounds[1] + 72, 30, 22, GRAPHITE, spacing=6)


def checklist_block(draw: ImageDraw.ImageDraw, y: int, accent: str, title: str, body: str) -> None:
    draw.rounded_rectangle((66, y, 600, y + 142), radius=28, fill=(255, 253, 248, 230), outline=(16, 25, 53, 30), width=2)
    draw.rounded_rectangle((88, y + 24, 174, y + 64), radius=18, fill=accent)
    draw.text((108, y + 34), title, font=font(BOLD, 22), fill=NAVY)
    wrapped(draw, body, 88, y + 80, 38, 21, GRAPHITE, spacing=6)


def slide_one() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, PENS, 648, 182, 298, 932)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 430, 228), MAGENTA, "QUINTA | BRINDES UTEIS")
    draw.multiline_text(
        (66, 292),
        "A MARCA\nTERMINA NA\nREUNIAO?",
        font=font(BOLD, 68),
        fill=NAVY,
        spacing=8,
    )
    draw.rectangle((68, 646, 148, 654), fill=CYAN)
    draw.rectangle((162, 646, 242, 654), fill=YELLOW)
    draw.rectangle((256, 646, 336, 654), fill=MAGENTA)
    wrapped(
        draw,
        "Quando o contacto acaba sem uma peca util no dia a dia, a lembranca da marca esfria depressa.",
        68,
        696,
        24,
        29,
        GRAPHITE,
        spacing=8,
    )
    draw.rounded_rectangle((68, 1016, 470, 1092), radius=24, fill=LIME)
    draw.text((98, 1041), "VEJA A SOLUCAO EM 3 PASSOS", font=font(BOLD, 24), fill=NAVY)
    footer(draw, "1/4")
    return canvas


def slide_two() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, PENS, 642, 208, 316, 520)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 248, 228), NAVY, "PROBLEMA")
    draw.multiline_text((66, 286), "FICA SO\nNAQUELA\nCONVERSA", font=font(BOLD, 62), fill=NAVY, spacing=8)
    bullet_list(
        draw,
        [
            "Depois da reuniao, o contacto perde-se entre muitas tarefas, mensagens e papeis.",
            "Quando o material nao tem uso real, a pessoa olha uma vez e guarda sem voltar.",
            "A marca deixa de circular logo depois do primeiro encontro.",
        ],
        68,
        516,
        22,
        25,
        [CYAN, MAGENTA, YELLOW],
    )
    note_card(
        draw,
        (64, 982, 560, 1198),
        "Resultado",
        "A reuniao pode correr bem, mas a lembranca da marca nao acompanha o resto do dia.",
    )
    footer(draw, "2/4")
    return canvas


def slide_three() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, PENS, 632, 194, 330, 892)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 232, 228), CYAN, "SOLUCAO", text_fill=NAVY)
    draw.multiline_text((66, 286), "UMA PECA\nUTIL PODE\nCONTINUAR", font=font(BOLD, 60), fill=NAVY, spacing=8)
    bullet_list(
        draw,
        [
            "Canetas personalizadas entram bem em reunioes, recepcao, kits, formacoes e eventos.",
            "Se forem uteis e simples, continuam na mesa, na bolsa ou no balcao por mais tempo.",
            "O melhor resultado costuma vir com logotipo legivel, contraste limpo e impressao bem aplicada.",
        ],
        68,
        520,
        22,
        24,
        [YELLOW, MAGENTA, CYAN],
    )
    draw.rounded_rectangle((674, 1034, 982, 1084), radius=18, fill=NAVY)
    draw.text((706, 1049), "EXEMPLO REAL", font=font(BOLD, 22), fill=OFF_WHITE)
    footer(draw, "3/4")
    return canvas


def slide_four() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, PENS, 690, 194, 248, 250)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 350, 228), MAGENTA, "ANTES DE FECHAR")
    draw.multiline_text((66, 286), "3 PONTOS QUE\nVALE CONFIRMAR", font=font(BOLD, 60), fill=NAVY, spacing=8)
    checklist_block(draw, 560, CYAN, "Leitura", "O logotipo precisa de continuar claro mesmo numa area pequena.")
    checklist_block(draw, 720, YELLOW, "Contraste", "A cor da impressao deve aparecer bem no corpo da caneta escolhida.")
    checklist_block(draw, 880, MAGENTA, "Quantidade", "Vale alinhar a quantidade com reunioes, kits ou accoes reais da marca.")
    draw.rounded_rectangle((66, 1068, 540, 1146), radius=24, fill=NAVY)
    draw.text((92, 1094), "PEDIR ORCAMENTO", font=font(BOLD, 28), fill=OFF_WHITE)
    wrapped(draw, "Comente brinde ou fale connosco em scolorprint.com.", 66, 1152, 40, 19, GRAPHITE, spacing=6)
    footer(draw, "4/4")
    return canvas


def export(image: Image.Image, name: str) -> None:
    image.convert("RGB").save(CAMPAIGN / name, quality=94, subsampling=0)


def main() -> None:
    slides = [
        ("slide-01-v1.jpg", slide_one()),
        ("slide-02-v1.jpg", slide_two()),
        ("slide-03-v1.jpg", slide_three()),
        ("slide-04-v1.jpg", slide_four()),
    ]
    for filename, image in slides:
        export(image, filename)


if __name__ == "__main__":
    main()
