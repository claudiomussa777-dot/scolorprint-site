from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
LOGO = ROOT / "assets" / "logo-scp.png"
BASE = CAMPAIGN / "base-brand-v1.png"
VINIL_PORTAS = ROOT / "assets" / "categorias" / "vinil-portas.jpg"
VINIL_MONTRA = ROOT / "assets" / "trabalhos" / "vinil-montra-institucional.jpg"
PLACAS = ROOT / "assets" / "categorias" / "placas-sinaletica.jpg"
ROLLUP = ROOT / "assets" / "trabalhos" / "rollup-evento-institucional.jpg"

WIDTH = 1080
HEIGHT = 1350

NAVY = "#0F1833"
CYAN = "#1AB3E5"
MAGENTA = "#E81A72"
YELLOW = "#F3C515"
LIME = "#DFF15D"
OFF_WHITE = "#FFFDF8"
GRAPHITE = "#2F3543"
SOFT_CARD = (255, 253, 248, 230)
CARD_BORDER = (15, 24, 51, 34)

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
    draw.rounded_rectangle((44, 132, 1008, 1214), radius=56, fill=(255, 253, 248, 82))
    draw.rounded_rectangle((58, 150, 594, 1170), radius=46, fill=(255, 253, 248, 232))
    draw.ellipse((740, 968, 1160, 1422), fill=(15, 24, 51, 26))
    draw.ellipse((-130, 978, 420, 1506), fill=(26, 179, 229, 22))
    haze = haze.filter(ImageFilter.GaussianBlur(18))
    return Image.alpha_composite(base, haze)


def add_shadow(base: Image.Image, bounds: tuple[int, int, int, int], radius: int = 28, blur: int = 24) -> Image.Image:
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(bounds, radius=radius, fill=(9, 15, 31, 68))
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
    base.alpha_composite(logo, (64, 50))


def pill(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], fill: str, text: str, text_fill: str = OFF_WHITE) -> None:
    draw.rounded_rectangle(bounds, radius=28, fill=fill)
    draw.text((bounds[0] + 24, bounds[1] + 15), text, font=font(BOLD, 22), fill=text_fill)


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
    block = textwrap.fill(text, width=width_chars)
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


def info_card(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], title: str, body: str) -> None:
    draw.rounded_rectangle(bounds, radius=28, fill=SOFT_CARD, outline=CARD_BORDER, width=2)
    draw.text((bounds[0] + 24, bounds[1] + 22), title, font=font(BOLD, 26), fill=NAVY)
    wrapped(draw, body, bounds[0] + 24, bounds[1] + 72, 30, 21, GRAPHITE, spacing=6)


def slide_one() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, VINIL_PORTAS, 670, 194, 244, 390)
    canvas = photo_card(canvas, PLACAS, 620, 632, 332, 236)
    canvas = photo_card(canvas, ROLLUP, 726, 904, 164, 250)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 378, 228), MAGENTA, "SABADO | INSPIRACAO")
    draw.multiline_text(
        (66, 290),
        "ENTRADA QUE\nJA FALA\nPELA MARCA",
        font=font(BOLD, 66),
        fill=NAVY,
        spacing=8,
    )
    draw.rectangle((68, 638, 146, 646), fill=CYAN)
    draw.rectangle((160, 638, 238, 646), fill=MAGENTA)
    draw.rectangle((252, 638, 330, 646), fill=YELLOW)
    wrapped(
        draw,
        "Quando vinil, placas e um apoio de recepcao combinam, a chegada fica mais clara logo no primeiro olhar.",
        68,
        684,
        24,
        29,
        GRAPHITE,
        spacing=8,
    )
    draw.rounded_rectangle((68, 1008, 514, 1086), radius=24, fill=LIME)
    draw.text((98, 1034), "VEJA 3 PECAS QUE FUNCIONAM JUNTAS", font=font(BOLD, 22), fill=NAVY)
    footer(draw, "1/4")
    return canvas


def slide_two() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, VINIL_MONTRA, 620, 190, 352, 878)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 218, 228), NAVY, "VINIL")
    draw.multiline_text(
        (66, 286),
        "VIDRO OU\nMONTRA COM\nPRESENCA",
        font=font(BOLD, 60),
        fill=NAVY,
        spacing=8,
    )
    bullet_list(
        draw,
        [
            "Ajuda a identificar o local logo a chegada, mesmo antes de entrar.",
            "Funciona bem em vidro, montra, porta ou divisoria de acesso.",
            "Tambem orienta melhor sem depender de uma peca demasiado pesada.",
        ],
        68,
        574,
        21,
        24,
        [CYAN, MAGENTA, YELLOW],
    )
    info_card(
        draw,
        (64, 980, 548, 1192),
        "Bom uso",
        "Quando a entrada esta neutra, o vinil reforca marca, leitura e acolhimento de forma simples.",
    )
    footer(draw, "2/4")
    return canvas


def slide_three() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, PLACAS, 610, 226, 372, 324)
    canvas = photo_card(canvas, VINIL_PORTAS, 664, 628, 264, 426)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 236, 228), CYAN, "PLACAS", text_fill=NAVY)
    draw.multiline_text(
        (66, 286),
        "ORIENTAR\nSEM CRIAR\nRUIDO",
        font=font(BOLD, 60),
        fill=NAVY,
        spacing=8,
    )
    bullet_list(
        draw,
        [
            "Placas ajudam a nomear lojas, servicos, pisos ou areas de atendimento.",
            "Quando a leitura e clara, o espaco parece mais organizado e profissional.",
            "Podem trabalhar bem com vinil na entrada para reforcar o mesmo percurso.",
        ],
        68,
        554,
        21,
        24,
        [YELLOW, MAGENTA, CYAN],
    )
    info_card(
        draw,
        (64, 982, 548, 1198),
        "Dica pratica",
        "Vale pensar primeiro no percurso de quem chega: o que a pessoa precisa de ler logo?",
    )
    footer(draw, "3/4")
    return canvas


def slide_four() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, ROLLUP, 650, 194, 270, 896)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 278, 228), MAGENTA, "ROLL-UP")
    draw.multiline_text(
        (66, 286),
        "RECEPCAO,\nAPOIO OU\nMINI-EVENTO",
        font=font(BOLD, 58),
        fill=NAVY,
        spacing=8,
    )
    bullet_list(
        draw,
        [
            "O roll-up entra bem quando a mensagem principal precisa de ficar visivel a distancia.",
            "Ajuda em recepcao, activacao, visita institucional ou canto de apoio.",
            "Tambem fecha bem a combinacao com vinil e placas quando o espaco precisa de contexto.",
        ],
        68,
        558,
        21,
        23,
        [MAGENTA, CYAN, YELLOW],
    )
    draw.rounded_rectangle((66, 1022, 472, 1100), radius=24, fill=NAVY)
    draw.text((102, 1048), "GUARDE E PECA ORCAMENTO", font=font(BOLD, 24), fill=OFF_WHITE)
    wrapped(draw, "Comente entrada ou fale connosco em scolorprint.com.", 66, 1112, 38, 19, GRAPHITE, spacing=6)
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
