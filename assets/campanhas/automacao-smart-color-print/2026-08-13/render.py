from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
LOGO = ROOT / "assets" / "logo-scp.png"
BASE = CAMPAIGN / "base-brand-v1.png"
FOLDERS = ROOT / "assets" / "trabalhos" / "folders-e-flyers-impressos.jpg"
FOLDER_DETAIL = ROOT / "assets" / "trabalhos" / "folder-criativo-corte-vinco.jpg"

WIDTH = 1080
HEIGHT = 1350

NAVY = "#101935"
CYAN = "#19B3E6"
MAGENTA = "#EA1A72"
YELLOW = "#F3C515"
OFF_WHITE = "#FFFDF8"
GRAPHITE = "#2D3342"
LIME = "#DFF364"
CARD_FILL = (255, 253, 248, 236)
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
    draw.rounded_rectangle((40, 126, 604, 1202), radius=56, fill=(255, 253, 248, 232))
    draw.rounded_rectangle((56, 144, 1024, 1216), radius=62, outline=(16, 25, 53, 18), width=4)
    draw.ellipse((-142, 936, 392, 1446), fill=(25, 179, 230, 20))
    draw.ellipse((730, 980, 1168, 1412), fill=(16, 25, 53, 24))
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
    block = textwrap.fill(text, width=width_chars)
    draw.multiline_text((x, y), block, font=font(family, size), fill=fill, spacing=spacing)
    bbox = draw.multiline_textbbox((x, y), block, font=font(family, size), spacing=spacing)
    return bbox[3]


def bullets(draw: ImageDraw.ImageDraw, items: list[str], x: int, y: int, width_chars: int, size: int, colors: list[str]) -> int:
    cursor = y
    for index, item in enumerate(items):
        color = colors[index % len(colors)]
        draw.rounded_rectangle((x, cursor + 8, x + 28, cursor + 36), radius=9, fill=color)
        cursor = wrapped(draw, item, x + 48, cursor, width_chars, size, GRAPHITE, spacing=7) + 24
    return cursor


def info_card(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], title: str, body: str) -> None:
    draw.rounded_rectangle(bounds, radius=28, fill=CARD_FILL, outline=CARD_BORDER, width=2)
    draw.text((bounds[0] + 24, bounds[1] + 18), title, font=font(BOLD, 28), fill=NAVY)
    wrapped(draw, body, bounds[0] + 24, bounds[1] + 66, 30, 21, GRAPHITE, spacing=6)


def checklist_card(draw: ImageDraw.ImageDraw, y: int, title: str, body: str, accent: str, *, dark_text: bool = False) -> None:
    draw.rounded_rectangle((66, y, 590, y + 148), radius=28, fill=CARD_FILL, outline=CARD_BORDER, width=2)
    draw.rounded_rectangle((88, y + 24, 242, y + 62), radius=18, fill=accent)
    fill = NAVY if dark_text else OFF_WHITE
    draw.text((108, y + 33), title, font=font(BOLD, 19), fill=fill)
    wrapped(draw, body, 90, y + 76, 39, 19, GRAPHITE, spacing=5)


def footer(draw: ImageDraw.ImageDraw, page: str) -> None:
    draw.rectangle((0, 1250, WIDTH, HEIGHT), fill=NAVY)
    draw.text((64, 1282), "scolorprint.com", font=font(BOLD, 30), fill=OFF_WHITE)
    draw.text((814, 1282), page, font=font(BOLD, 28), fill=OFF_WHITE)


def slide_one() -> Image.Image:
    canvas = make_canvas()
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 560, 228), MAGENTA, "QUINTA | SOLUCAO")
    draw.multiline_text((66, 292), "FOLDER OU\nFOLHAS\nSOLTAS?", font=font(BOLD, 70), fill=NAVY, spacing=8)
    draw.rectangle((68, 592, 148, 600), fill=CYAN)
    draw.rectangle((162, 592, 242, 600), fill=YELLOW)
    draw.rectangle((256, 592, 336, 600), fill=MAGENTA)
    wrapped(
        draw,
        "Quando a informacao cresce, um folder ajuda a organizar servicos, imagens e contactos sem cansar quem recebe.",
        68,
        636,
        24,
        29,
        GRAPHITE,
        spacing=8,
    )
    draw.rounded_rectangle((68, 944, 550, 1018), radius=24, fill=LIME)
    draw.text((98, 970), "GUARDE PARA O PROXIMO MATERIAL", font=font(BOLD, 22), fill=NAVY)
    wrapped(
        draw,
        "Nem tudo cabe bem num flyer unico. Em alguns casos, a dobra certa melhora a leitura e a entrega.",
        68,
        1052,
        28,
        24,
        GRAPHITE,
        spacing=7,
    )
    footer(draw, "1/4")
    return canvas


def slide_two() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, FOLDERS, 644, 204, 292, 864)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 254, 228), NAVY, "O PROBLEMA")
    draw.multiline_text((66, 288), "MUITA COISA\nSOLTA\nNA MESMA PECA", font=font(BOLD, 56), fill=NAVY, spacing=8)
    bullets(
        draw,
        [
            "Quando servicos, fotos, contactos e chamada principal entram sem hierarquia, a peca pede explicacao a mais.",
            "Folhas avulsas tambem perdem contexto com facilidade em reunioes, balcoes ou visitas.",
            "Mesmo com boa imagem, a leitura pode ficar cansativa no uso real.",
        ],
        68,
        536,
        22,
        20,
        [CYAN, MAGENTA, YELLOW],
    )
    info_card(draw, (64, 972, 548, 1196), "Sinal de alerta", "Se a explicacao oral faz quase todo o trabalho, a peca impressa ainda pode estar a pedir mais organizacao.")
    footer(draw, "2/4")
    return canvas


def slide_three() -> Image.Image:
    canvas = make_canvas()
    canvas = photo_card(canvas, FOLDER_DETAIL, 642, 210, 296, 852)
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 256, 228), CYAN, "A SOLUCAO", text_fill=NAVY)
    draw.multiline_text((66, 286), "DOBRA E\nVINCO A\nTRABALHAR", font=font(BOLD, 56), fill=NAVY, spacing=8)
    bullets(
        draw,
        [
            "O folder separa melhor capa, interior e chamada final sem apertar tudo no mesmo plano.",
            "Com a dobra certa, cada bloco apresenta, explica e depois fecha o contacto.",
            "Vinco limpo e alinhamento bom ajudam a peca a abrir e fechar melhor.",
        ],
        68,
        538,
        22,
        20,
        [YELLOW, MAGENTA, CYAN],
    )
    info_card(draw, (64, 972, 548, 1196), "Quando faz sentido", "Pastas, menus, servicos, programas, propostas e materiais de apresentacao costumam ganhar mais ordem com este formato.")
    footer(draw, "3/4")
    return canvas


def slide_four() -> Image.Image:
    canvas = make_canvas()
    draw = ImageDraw.Draw(canvas)
    place_logo(canvas)
    pill(draw, (64, 172, 338, 228), MAGENTA, "ANTES DE IMPRIMIR")
    draw.multiline_text((66, 286), "FECHE ESTAS\n4 ESCOLHAS", font=font(BOLD, 62), fill=NAVY, spacing=8)
    checklist_card(draw, 520, "Conteudo", "Quais informacoes sao essenciais e quais podem passar para o interior?", CYAN, dark_text=True)
    checklist_card(draw, 690, "Fluxo", "A leitura comeca na capa e termina com um contacto claro ou pedido de acao?", YELLOW, dark_text=True)
    checklist_card(draw, 860, "Formato", "Bi-fold, tri-fold ou pasta simples: qual dobra combina melhor com a quantidade real de conteudo?", MAGENTA)
    checklist_card(draw, 1030, "Acabamento", "O papel, o vinco e a area util deixam a peca abrir bem e continuar legivel?", NAVY)
    footer(draw, "4/4")
    return canvas


def export(image: Image.Image, name: str) -> None:
    image.convert("RGB").save(CAMPAIGN / name, quality=94, subsampling=0)


def main() -> None:
    export(slide_one(), "slide-01-v1.jpg")
    export(slide_two(), "slide-02-v1.jpg")
    export(slide_three(), "slide-03-v1.jpg")
    export(slide_four(), "slide-04-v1.jpg")


if __name__ == "__main__":
    main()
