from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
BASE = CAMPAIGN / "base-domingo-checklist-v1.png"
LOGO = ROOT / "assets" / "logo-scp.png"
FOLDERS = ROOT / "assets" / "trabalhos" / "folders-e-flyers-impressos.jpg"
FOLDER_DIECUT = ROOT / "assets" / "trabalhos" / "folder-criativo-corte-vinco.jpg"
ROLLUP = ROOT / "assets" / "trabalhos" / "rollup-evento-institucional.jpg"
BACKDROP = ROOT / "assets" / "trabalhos" / "backdrop-evento-institucional.jpg"
VINYL = ROOT / "assets" / "trabalhos" / "vinil-montra-institucional.jpg"

WIDTH = 1080
HEIGHT = 1350

NAVY = "#10152D"
CYAN = "#19A6D2"
MAGENTA = "#E91573"
YELLOW = "#F5C400"
LIME = "#DFFF38"
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
    draw.rounded_rectangle(bounds, radius=radius, fill=(8, 16, 36, 64))
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
    draw.text((808, 1282), page, font=font(BOLD, 28), fill=OFF_WHITE)


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
        cursor = wrapped(draw, item, x + 52, cursor, width_chars, size, GRAPHITE, spacing=7) + 26
    return cursor


def info_card(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], title: str, body: str) -> None:
    draw.rounded_rectangle(bounds, radius=28, fill=SOFT_CARD, outline=(17, 23, 44, 35), width=2)
    draw.text((bounds[0] + 28, bounds[1] + 24), title, font=font(BOLD, 30), fill=NAVY)
    wrapped(draw, body, bounds[0] + 28, bounds[1] + 82, 24, 24, GRAPHITE, spacing=7)


def slide_one() -> Image.Image:
    canvas = make_base()
    canvas = add_photo_card(canvas, FOLDER_DIECUT, 650, 212, 304, 484)
    canvas = add_photo_card(canvas, BACKDROP, 726, 742, 248, 308)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 176, 350, 232), MAGENTA, "DOMINGO | CHECKLIST")
    draw.multiline_text(
        (64, 286),
        "A SUA MARCA\nESTÁ PRONTA\nPARA A\nSEMANA?",
        font=font(BOLD, 64),
        fill=NAVY,
        spacing=8,
    )
    draw.rectangle((68, 664, 146, 672), fill=CYAN)
    draw.rectangle((160, 664, 236, 672), fill=MAGENTA)
    draw.rectangle((250, 664, 310, 672), fill=YELLOW)
    wrapped(
        draw,
        "Use este checklist para alinhar prioridade, materiais, ficheiros e orçamento antes de segunda-feira.",
        68,
        704,
        24,
        28,
        GRAPHITE,
        spacing=8,
    )
    draw.rounded_rectangle((68, 998, 486, 1076), radius=24, fill=LIME)
    draw.text((100, 1024), "GUARDE PARA REVER HOJE", font=font(BOLD, 25), fill=NAVY)
    footer(draw, "1/5")
    return canvas


def slide_two() -> Image.Image:
    canvas = make_base()
    canvas = add_photo_card(canvas, FOLDERS, 620, 196, 356, 936)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 176, 246, 232), NAVY, "PASSO 1")
    draw.multiline_text(
        (64, 284),
        "COMECE PELO\nOBJETIVO DA\nSEMANA",
        font=font(BOLD, 60),
        fill=NAVY,
        spacing=8,
    )
    bullet_list(
        draw,
        [
            "Vai divulgar um serviço, preparar um evento ou reforçar a presença da equipa?",
            "Quando o foco está claro, o material certo aparece mais depressa.",
            "Anote primeiro a prioridade e só depois escolha as peças.",
        ],
        68,
        580,
        22,
        28,
        [MAGENTA, CYAN, YELLOW],
    )
    info_card(draw, (64, 1038, 548, 1208), "Exemplo real", "Bom para apresentar serviços com clareza.")
    footer(draw, "2/5")
    return canvas


def slide_three() -> Image.Image:
    canvas = make_base()
    canvas = add_photo_card(canvas, ROLLUP, 634, 196, 322, 404)
    canvas = add_photo_card(canvas, VINYL, 634, 634, 322, 420)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 176, 248, 232), CYAN, "PASSO 2", text_fill=NAVY)
    draw.multiline_text(
        (64, 284),
        "ESCOLHA AS\nPEÇAS QUE\nAPOIAM O\nPLANO",
        font=font(BOLD, 60),
        fill=NAVY,
        spacing=8,
    )
    bullet_list(
        draw,
        [
            "Flyers e folders para explicar serviços e campanhas.",
            "Roll-up ou backdrop para recepção, evento e zona de foto.",
            "Vinil e sinalética para orientar melhor o espaço.",
        ],
        68,
        676,
        22,
        27,
        [YELLOW, MAGENTA, CYAN],
    )
    footer(draw, "3/5")
    return canvas


def slide_four() -> Image.Image:
    canvas = make_base()
    canvas = add_photo_card(canvas, FOLDER_DIECUT, 70, 898, 446, 310)
    canvas = add_photo_card(canvas, VINYL, 550, 898, 460, 310)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 176, 248, 232), YELLOW, "PASSO 3", text_fill=NAVY)
    draw.multiline_text(
        (64, 284),
        "REVEJA O\nFICHEIRO ANTES\nDE ENVIAR",
        font=font(BOLD, 60),
        fill=NAVY,
        spacing=8,
    )
    bullet_list(
        draw,
        [
            "Confirme texto, contactos e nomes.",
            "Use logótipos nítidos e imagens em boa qualidade.",
            "Valide medidas, quantidades e acabamento.",
        ],
        68,
        564,
        24,
        28,
        [LIME, MAGENTA, CYAN],
    )
    footer(draw, "4/5")
    return canvas


def slide_five() -> Image.Image:
    canvas = make_base()
    canvas = add_photo_card(canvas, BACKDROP, 616, 200, 348, 260)
    canvas = add_photo_card(canvas, ROLLUP, 616, 494, 164, 382)
    canvas = add_photo_card(canvas, FOLDERS, 798, 494, 166, 382)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 176, 248, 232), MAGENTA, "PASSO 4")
    draw.multiline_text(
        (64, 284),
        "PEÇA O\nORÇAMENTO\nCOM TEMPO",
        font=font(BOLD, 60),
        fill=NAVY,
        spacing=8,
    )
    wrapped(
        draw,
        "Preparar hoje ajuda a começar a semana com menos correria e com a produção mais alinhada ao objectivo.",
        64,
        560,
        23,
        28,
        GRAPHITE,
        spacing=8,
    )
    draw.rounded_rectangle((64, 840, 492, 918), radius=24, fill=LIME)
    draw.text((96, 866), "PEDIR ORÇAMENTO", font=font(BOLD, 29), fill=NAVY)
    wrapped(
        draw,
        "Comente 'semana', guarde este carrossel ou fale connosco em scolorprint.com.",
        64,
        970,
        24,
        27,
        NAVY,
        bold=True,
        spacing=8,
    )
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
