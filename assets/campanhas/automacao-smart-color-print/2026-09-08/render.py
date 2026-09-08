from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
BASE = CAMPAIGN / "base-marca-legivel-v1.png"
LOGO = ROOT / "assets" / "logo-scp.png"
W, H = 1080, 1350
NAVY, CYAN, MAGENTA, YELLOW = "#0C1933", "#19B7E8", "#E71D73", "#F2C94C"
WHITE, PALE = "#FFFFFF", "#EAF6FB"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


SLIDES = [
    {
        "tag": "TERÇA | GUIA RÁPIDO",
        "title": "UM LOGÓTIPO,\nVÁRIOS\nMATERIAIS",
        "body": "4 cuidados para manter a sua marca clara em camisetas, bonés, flyers e roll-ups.",
        "number": "1/5",
        "accent": MAGENTA,
    },
    {
        "tag": "CUIDADO 1",
        "title": "COMECE PELO\nFICHEIRO CERTO",
        "body": "Prefira o logótipo em vector ou PDF de boa qualidade. Uma imagem retirada do WhatsApp pode perder definição ao ampliar.",
        "number": "2/5",
        "accent": CYAN,
    },
    {
        "tag": "CUIDADO 2",
        "title": "AJUSTE O\nDETALHE À\nESCALA",
        "body": "Linhas finas e letras pequenas podem funcionar num roll-up, mas desaparecer num boné. Simplifique quando o espaço é menor.",
        "number": "3/5",
        "accent": YELLOW,
    },
    {
        "tag": "CUIDADO 3",
        "title": "CONFIRME O\nCONTRASTE",
        "body": "O mesmo logótipo pode precisar de versão clara ou escura. Verifique sempre a cor do material antes de aprovar.",
        "number": "4/5",
        "accent": MAGENTA,
    },
    {
        "tag": "CUIDADO 4",
        "title": "RESPEITE A\nÁREA DE\nAPLICAÇÃO",
        "body": "Costuras, dobras e margens alteram o resultado. Peça uma simulação e confirme posição, tamanho e acabamento.",
        "number": "5/5",
        "accent": CYAN,
    },
]


def draw_slide(spec, index):
    image = ImageOps.fit(Image.open(BASE).convert("RGB"), (W, H), method=Image.Resampling.LANCZOS).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle((0, 0, 680, H), fill=(6, 17, 39, 228))
    od.rectangle((0, 0, W, 250), fill=(7, 19, 44, 110))
    overlay = overlay.filter(ImageFilter.GaussianBlur(3))
    image = Image.alpha_composite(image, overlay)
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((58, 48, 340, 171), 28, fill=(255, 255, 255, 242))
    logo = Image.open(LOGO).convert("RGBA")
    lw = 238
    logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.Resampling.LANCZOS)
    image.alpha_composite(logo, (79, 70))

    draw.rounded_rectangle((68, 207, 392, 266), 28, fill=spec["accent"])
    tag_fill = NAVY if spec["accent"] == YELLOW else WHITE
    draw.text((94, 224), spec["tag"], font=font(BOLD, 21), fill=tag_fill)

    title_size = 59 if index == 0 else 55
    draw.multiline_text((70, 324), spec["title"], font=font(BOLD, title_size), fill=WHITE, spacing=8)
    title_box = draw.multiline_textbbox((70, 324), spec["title"], font=font(BOLD, title_size), spacing=8)
    accent_y = min(title_box[3] + 36, 720)
    draw.rectangle((72, accent_y, 165, accent_y + 9), fill=CYAN)
    draw.rectangle((181, accent_y, 274, accent_y + 9), fill=YELLOW)
    draw.rectangle((290, accent_y, 383, accent_y + 9), fill=MAGENTA)

    body = textwrap.fill(spec["body"], 34, break_long_words=False, break_on_hyphens=False)
    draw.multiline_text((72, accent_y + 52), body, font=font(REGULAR, 30), fill=PALE, spacing=11)

    if index == 4:
        draw.rounded_rectangle((70, 1060, 568, 1137), 28, fill=(255, 255, 255, 240))
        draw.text((98, 1084), "GUARDE PARA O PRÓXIMO PEDIDO", font=font(BOLD, 20), fill=NAVY)
    elif index == 0:
        draw.rounded_rectangle((70, 1048, 510, 1125), 28, fill=(255, 255, 255, 240))
        draw.text((98, 1072), "DESLIZE PARA VER OS 4 CUIDADOS", font=font(BOLD, 19), fill=NAVY)

    draw.rectangle((0, 1250, W, H), fill=NAVY)
    draw.text((64, 1281), "scolorprint.com", font=font(BOLD, 29), fill=WHITE)
    draw.text((928, 1282), spec["number"], font=font(BOLD, 26), fill=WHITE)
    image.convert("RGB").save(CAMPAIGN / f"slide-{index + 1:02d}-v1.jpg", quality=94, subsampling=0)


def main():
    for index, spec in enumerate(SLIDES):
        draw_slide(spec, index)


if __name__ == "__main__":
    main()
