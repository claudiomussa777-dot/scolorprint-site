from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
LOGO = ROOT / "assets" / "logo-scp.png"
BASE = CAMPAIGN / "base-brand-v1.png"
VEST = ROOT / "assets" / "categorias" / "coletes-uniformes.jpg"
TSHIRT = ROOT / "assets" / "mockup-tshirt-real-v2.jpg"
CAP = ROOT / "assets" / "mockup-cap-real-v2.jpg"

WIDTH = 1080
HEIGHT = 1350

NAVY = "#101935"
CYAN = "#19B3E6"
MAGENTA = "#EA1A72"
YELLOW = "#F3C515"
OFF_WHITE = "#FFFDF8"
GRAPHITE = "#2D3342"
LIME = "#DFF364"
SOFT_CARD = (255, 253, 248, 232)
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
    draw.rounded_rectangle((42, 124, 612, 1200), radius=56, fill=(255, 253, 248, 236))
    draw.rounded_rectangle((54, 140, 1026, 1216), radius=62, outline=(16, 25, 53, 18), width=4)
    draw.ellipse((-160, 992, 442, 1510), fill=(25, 179, 230, 20))
    draw.ellipse((744, 1014, 1154, 1410), fill=(16, 25, 53, 28))
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
    block = textwrap.fill(text, width=width_chars)
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
    wrapped(draw, body, bounds[0] + 24, bounds[1] + 70, 30, 21, GRAPHITE, spacing=6)


def checklist_card(draw: ImageDraw.ImageDraw, y: int, title: str, body: str, accent: str) -> None:
    draw.rounded_rectangle((66, y, 592, y + 148), radius=28, fill=SOFT_CARD, outline=CARD_BORDER, width=2)
    draw.rounded_rectangle((88, y + 24, 242, y + 62), radius=18, fill=accent)
    draw.text((108, y + 33), title, font=font(BOLD, 19), fill=OFF_WHITE if accent == NAVY else NAVY)
    wrapped(draw, body, 90, y + 76, 40, 19, GRAPHITE, spacing=5)


def slide_one() -> Image.Image:
    canvas = make_canvas()
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 344, 228), MAGENTA, "TERCA | EDUCATIVO")
    draw.multiline_text(
        (66, 290),
        "VESTUARIO\nPERSONALIZADO",
        font=font(BOLD, 64),
        fill=NAVY,
        spacing=8,
    )
    draw.rectangle((68, 512, 148, 520), fill=CYAN)
    draw.rectangle((162, 512, 242, 520), fill=YELLOW)
    draw.rectangle((256, 512, 336, 520), fill=MAGENTA)
    wrapped(
        draw,
        "4 perguntas para escolher a peca certa para cada funcao da sua equipa sem produzir no impulso.",
        68,
        560,
        24,
        29,
        GRAPHITE,
        spacing=8,
    )
    draw.rounded_rectangle((68, 930, 530, 1008), radius=24, fill=LIME)
    draw.text((96, 956), "GUARDE PARA A PROXIMA PRODUCAO", font=font(BOLD, 22), fill=NAVY)
    wrapped(
        draw,
        "Coletes, camisetas, uniformes e bones nao fazem exactamente o mesmo trabalho no dia a dia.",
        68,
        1040,
        28,
        24,
        GRAPHITE,
        spacing=7,
    )
    footer(draw, "1/5")
    return canvas


def slide_two() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, VEST, 646, 204, 286, 868)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 254, 228), NAVY, "PERGUNTA 1")
    draw.multiline_text((66, 286), "QUEM PRECISA\nDE SER VISTO\nMAIS RAPIDO?", font=font(BOLD, 54), fill=NAVY, spacing=8)
    bullets(
        draw,
        [
            "Coletes entram bem quando a prioridade e visibilidade imediata em terreno, obra, logistica ou controlo de acesso.",
            "Tambem ajudam a distinguir visitantes, equipas tecnicas e apoio operacional sem muita leitura.",
            "Mais movimento e distancia costumam pedir esta peca.",
        ],
        68,
        540,
        22,
        22,
        [CYAN, MAGENTA, YELLOW],
    )
    info_card(draw, (64, 978, 548, 1198), "Peca indicada", "Coletes personalizados fazem sentido quando a identificacao precisa aparecer antes da conversa.")
    footer(draw, "2/5")
    return canvas


def slide_three() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, TSHIRT, 642, 210, 292, 860)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 254, 228), CYAN, "PERGUNTA 2", text_fill=NAVY)
    draw.multiline_text((66, 286), "QUEM VAI\nUSAR A PECA\nPOR MAIS HORAS?", font=font(BOLD, 54), fill=NAVY, spacing=8)
    bullets(
        draw,
        [
            "Camisetas e uniformes rendem melhor quando a equipa passa muitas horas em atendimento, loja, entrega ou promocao.",
            "Aqui conforto, corte e leitura do logotipo contam tanto quanto a cor da marca.",
            "Se a peca vai circular todos os dias, pense no tecido e na combinacao real de uso.",
        ],
        68,
        540,
        22,
        22,
        [YELLOW, MAGENTA, CYAN],
    )
    info_card(draw, (64, 978, 548, 1198), "Peca indicada", "A peca principal deve aguentar uso repetido sem perder presenca nem legibilidade.")
    footer(draw, "3/5")
    return canvas


def slide_four() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, CAP, 646, 222, 284, 842)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 254, 228), YELLOW, "PERGUNTA 3", text_fill=NAVY)
    draw.multiline_text((66, 286), "A MARCA VAI\nCIRCULAR MAIS\nAO AR LIVRE?", font=font(BOLD, 54), fill=NAVY, spacing=8)
    bullets(
        draw,
        [
            "Bone personalizado entra bem em activacoes, promotores, entregas e equipas externas.",
            "Ajuda a reforcar a marca quando a equipa esta em movimento ou exposta ao sol.",
            "Na maioria dos casos funciona melhor como complemento da peca principal.",
        ],
        68,
        540,
        22,
        22,
        [MAGENTA, CYAN, YELLOW],
    )
    info_card(draw, (64, 978, 548, 1198), "Peca indicada", "O bone soma presenca e repeticao visual quando a equipa precisa de circular mais.")
    footer(draw, "4/5")
    return canvas


def slide_five() -> Image.Image:
    canvas = make_canvas()
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 404, 228), MAGENTA, "ANTES DE PRODUZIR")
    draw.multiline_text((66, 286), "FECHE ESTAS\n4 DECISOES", font=font(BOLD, 62), fill=NAVY, spacing=8)
    checklist_card(draw, 520, "Funcao", "Quem precisa de ser identificado primeiro: atendimento, terreno, logistica ou activacao?", CYAN)
    checklist_card(draw, 690, "Rotina", "A peca vai trabalhar o dia todo ou apenas reforcar uma accao especifica?", YELLOW)
    checklist_card(draw, 860, "Leitura", "Cor, tecido e area de impressao deixam o logotipo legivel a distancia normal?", MAGENTA)
    checklist_card(draw, 1030, "Conjunto", "A equipa precisa de uma peca principal sozinha ou de um conjunto com bone ou colete?", NAVY)
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
