from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
BASE = CAMPAIGN / "base-planeamento-v1.png"
LOGO = ROOT / "assets" / "logo-scp.png"
W, H = 1080, 1350
NAVY, CYAN, MAGENTA = "#0C1933", "#19B7E8", "#E71D73"
WHITE, PALE, GREY, YELLOW = "#FFFFFF", "#F4F7FA", "#354158", "#F2C94C"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, xy, chars, size, fill, bold=False, spacing=8):
    block = textwrap.fill(text, chars, break_long_words=False, break_on_hyphens=False)
    draw.multiline_text(xy, block, font=font(BOLD if bold else REGULAR, size), fill=fill, spacing=spacing)


def canvas(photo=False):
    if photo:
        base = ImageOps.fit(Image.open(BASE).convert("RGB"), (W, H), method=Image.Resampling.LANCZOS).convert("RGBA")
        veil = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(veil).rounded_rectangle((40, 120, 650, 1160), 44, fill=(9, 22, 48, 218))
        base = Image.alpha_composite(base, veil)
    else:
        base = Image.new("RGBA", (W, H), PALE)
        d = ImageDraw.Draw(base)
        d.ellipse((690, -170, 1190, 330), fill="#DDF5FC")
        d.ellipse((-180, 980, 280, 1440), fill="#FBE0EC")
    logo = Image.open(LOGO).convert("RGBA")
    lw = 236
    logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.Resampling.LANCZOS)
    base.alpha_composite(logo, (62, 42))
    return base


def header(draw, kicker, title, light=False):
    fg = WHITE if light else NAVY
    draw.rounded_rectangle((62, 166, 430, 222), 28, fill=MAGENTA)
    draw.text((86, 181), kicker, font=font(BOLD, 22), fill=WHITE)
    wrap(draw, title, (64, 278), 17, 58, fg, True, 9)
    draw.rectangle((64, 492, 150, 500), fill=CYAN)
    draw.rectangle((164, 492, 250, 500), fill=YELLOW)
    draw.rectangle((264, 492, 350, 500), fill=MAGENTA)


def footer(draw, page):
    draw.rectangle((0, 1250, W, H), fill=NAVY)
    draw.text((64, 1281), "scolorprint.com", font=font(BOLD, 29), fill=WHITE)
    draw.text((920, 1281), page, font=font(BOLD, 27), fill=WHITE)


def card(draw, y, number, title, body, accent):
    draw.rounded_rectangle((64, y, 1016, y + 178), 30, fill=WHITE, outline="#DDE3EA", width=2)
    draw.ellipse((92, y + 46, 178, y + 132), fill=accent)
    draw.text((122, y + 70), number, font=font(BOLD, 28), fill=NAVY)
    draw.text((210, y + 35), title, font=font(BOLD, 29), fill=NAVY)
    wrap(draw, body, (210, y + 78), 50, 23, GREY, False, 6)


def slide1():
    im = canvas(True); d = ImageDraw.Draw(im)
    header(d, "DOMINGO | PLANEAMENTO", "ALINHE A SEMANA ANTES DE IMPRIMIR", True)
    wrap(d, "Quatro decisões simples ajudam cada peça a comunicar com clareza — da equipa ao ponto de atendimento.", (66, 560), 31, 29, WHITE, False, 9)
    d.rounded_rectangle((64, 820, 570, 1050), 30, fill=(255, 255, 255, 235))
    d.text((96, 858), "OBJECTIVO • PÚBLICO", font=font(BOLD, 26), fill=NAVY)
    d.text((96, 906), "PEÇAS • REVISÃO", font=font(BOLD, 26), fill=MAGENTA)
    wrap(d, "Deslize e guarde para preparar o próximo pedido.", (96, 964), 30, 21, GREY)
    footer(d, "1/4"); return im


def info_slide(kicker, title, items, page):
    im = canvas(); d = ImageDraw.Draw(im); header(d, kicker, title)
    colors = [CYAN, MAGENTA, YELLOW]
    for i, (head, body) in enumerate(items): card(d, 570 + i * 205, str(i + 1), head, body, colors[i])
    footer(d, page); return im


def slide4():
    im = canvas(); d = ImageDraw.Draw(im)
    header(d, "4 | REVISÃO FINAL", "ANTES DE ENVIAR PARA PRODUÇÃO")
    checks = [
        "Nomes, datas e contactos estão certos?",
        "Cores e tamanhos servem ao local de uso?",
        "As quantidades correspondem à equipa ou evento?",
        "Os ficheiros e referências estão organizados?",
    ]
    for i, line in enumerate(checks):
        y = 566 + i * 128
        d.rounded_rectangle((64, y, 1016, y + 98), 25, fill=WHITE, outline="#DDE3EA", width=2)
        d.ellipse((92, y + 22, 146, y + 76), fill=[CYAN, MAGENTA, YELLOW, "#B6D947"][i])
        d.text((110, y + 35), "✓", font=font(BOLD, 23), fill=NAVY)
        d.text((176, y + 31), line, font=font(BOLD, 24), fill=NAVY)
    d.rounded_rectangle((64, 1090, 1016, 1194), 28, fill=NAVY)
    d.text((98, 1126), "Peça o seu orçamento quando estes dados estiverem prontos.", font=font(BOLD, 24), fill=WHITE)
    footer(d, "4/4"); return im


def main():
    slides = [
        slide1(),
        info_slide("1 | OBJECTIVO", "COMECE PELA FUNÇÃO DA PEÇA", [
            ("Orientar", "Sinalética, placas ou vinil ajudam quem chega a encontrar o caminho."),
            ("Apresentar", "Flyers, folders e cartões organizam a mensagem e os contactos."),
            ("Identificar", "Camisetas, bonés, coletes ou uniformes tornam a equipa reconhecível."),
        ], "2/4"),
        info_slide("2–3 | PÚBLICO E PEÇAS", "ESCOLHA O QUE FAZ SENTIDO", [
            ("Quem vai receber?", "Equipa, cliente, visitante ou participante precisam de informação diferente."),
            ("Onde será usado?", "Recepção, evento, rua ou escritório mudam o formato e o acabamento."),
            ("O que deve continuar?", "Defina a mensagem ou contacto que a pessoa deve levar consigo."),
        ], "3/4"),
        slide4(),
    ]
    for i, im in enumerate(slides, 1):
        im.convert("RGB").save(CAMPAIGN / f"slide-{i:02d}-v1.jpg", quality=94, subsampling=0)


if __name__ == "__main__":
    main()
