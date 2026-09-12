from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
BASE = CAMPAIGN / "base-sinaletica-evento-v1.png"
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
        "tag": "SÁBADO | INSPIRAÇÃO",
        "title": "UM EVENTO\nQUE SE ORIENTA\nCOM CLAREZA",
        "body": "Combine peças visuais para receber, identificar e conduzir participantes pelo espaço.",
        "number": "1/4",
        "accent": MAGENTA,
    },
    {
        "tag": "1 | RECEBER",
        "title": "BACKDROP OU\nROLL-UP",
        "body": "Use uma peça de destaque na entrada, recepção ou área de fotografia para apresentar a identidade do evento.",
        "number": "2/4",
        "accent": CYAN,
    },
    {
        "tag": "2 | ORIENTAR",
        "title": "PLACAS E\nVINIL",
        "body": "Indique credenciação, salas, circulação e áreas de apoio com mensagens curtas e leitura fácil.",
        "number": "3/4",
        "accent": YELLOW,
    },
    {
        "tag": "3 | IDENTIFICAR",
        "title": "CRACHÁS E\nSINALÉTICA",
        "body": "Diferencie equipa, convidados e pontos de atendimento. Planeie cada peça conforme o espaço e a função.",
        "number": "4/4",
        "accent": MAGENTA,
    },
]


def draw_slide(spec, index):
    image = ImageOps.fit(Image.open(BASE).convert("RGB"), (W, H), method=Image.Resampling.LANCZOS).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle((0, 0, 690, H), fill=(6, 17, 39, 228))
    od.rectangle((0, 0, W, 255), fill=(7, 19, 44, 100))
    overlay = overlay.filter(ImageFilter.GaussianBlur(3))
    image = Image.alpha_composite(image, overlay)
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((58, 48, 340, 171), 28, fill=(255, 255, 255, 242))
    logo = Image.open(LOGO).convert("RGBA")
    lw = 238
    logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.Resampling.LANCZOS)
    image.alpha_composite(logo, (79, 70))

    draw.rounded_rectangle((68, 207, 430, 266), 28, fill=spec["accent"])
    tag_fill = NAVY if spec["accent"] == YELLOW else WHITE
    draw.text((94, 224), spec["tag"], font=font(BOLD, 21), fill=tag_fill)

    title_size = 57 if index == 0 else 58
    draw.multiline_text((70, 324), spec["title"], font=font(BOLD, title_size), fill=WHITE, spacing=8)
    title_box = draw.multiline_textbbox((70, 324), spec["title"], font=font(BOLD, title_size), spacing=8)
    accent_y = min(title_box[3] + 36, 700)
    draw.rectangle((72, accent_y, 165, accent_y + 9), fill=CYAN)
    draw.rectangle((181, accent_y, 274, accent_y + 9), fill=YELLOW)
    draw.rectangle((290, accent_y, 383, accent_y + 9), fill=MAGENTA)

    body = textwrap.fill(spec["body"], 33, break_long_words=False, break_on_hyphens=False)
    draw.multiline_text((72, accent_y + 52), body, font=font(REGULAR, 30), fill=PALE, spacing=11)

    if index == 0:
        draw.rounded_rectangle((70, 1048, 473, 1125), 28, fill=(255, 255, 255, 240))
        draw.text((98, 1072), "DESLIZE PARA VER A COMBINAÇÃO", font=font(BOLD, 19), fill=NAVY)
    elif index == 3:
        draw.rounded_rectangle((70, 1048, 478, 1125), 28, fill=(255, 255, 255, 240))
        draw.text((98, 1072), "GUARDE PARA PLANEAR O EVENTO", font=font(BOLD, 19), fill=NAVY)

    draw.rectangle((0, 1250, W, H), fill=NAVY)
    draw.text((64, 1281), "scolorprint.com", font=font(BOLD, 29), fill=WHITE)
    draw.text((928, 1282), spec["number"], font=font(BOLD, 26), fill=WHITE)
    image.convert("RGB").save(CAMPAIGN / f"slide-{index + 1:02d}-v1.jpg", quality=94, subsampling=0)


def main():
    for index, spec in enumerate(SLIDES):
        draw_slide(spec, index)


if __name__ == "__main__":
    main()
