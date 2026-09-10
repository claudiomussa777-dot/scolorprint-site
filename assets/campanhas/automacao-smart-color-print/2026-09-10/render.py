from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
BASE = CAMPAIGN / "base-uniformes-confirmacoes-v1.png"
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
        "tag": "QUINTA | BASTIDORES",
        "title": "ANTES DE\nPERSONALIZAR\nA EQUIPA",
        "body": "4 confirmações que ajudam a preparar camisetas e uniformes com mais clareza.",
        "number": "1/5",
        "accent": MAGENTA,
    },
    {
        "tag": "CONFIRMAÇÃO 1",
        "title": "PEÇA E\nQUANTIDADE",
        "body": "Indique quantas camisetas, bonés, coletes ou uniformes precisa. Separe as quantidades por tipo de peça.",
        "number": "2/5",
        "accent": CYAN,
    },
    {
        "tag": "CONFIRMAÇÃO 2",
        "title": "TAMANHOS E\nCORES",
        "body": "Organize a lista de tamanhos e confirme a cor de cada peça. Isso reduz dúvidas antes da personalização.",
        "number": "3/5",
        "accent": YELLOW,
    },
    {
        "tag": "CONFIRMAÇÃO 3",
        "title": "POSIÇÃO E\nDIMENSÃO",
        "body": "Defina onde a marca será aplicada — frente, costas ou manga — e valide a dimensão adequada para a peça.",
        "number": "4/5",
        "accent": MAGENTA,
    },
    {
        "tag": "CONFIRMAÇÃO 4",
        "title": "ARTE FINAL\nAPROVADA",
        "body": "Revise o logótipo, as cores e o texto na simulação. A produção deve avançar com uma versão final confirmada.",
        "number": "5/5",
        "accent": CYAN,
    },
]


def draw_slide(spec, index):
    image = ImageOps.fit(Image.open(BASE).convert("RGB"), (W, H), method=Image.Resampling.LANCZOS).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle((0, 0, 685, H), fill=(6, 17, 39, 232))
    od.rectangle((0, 0, W, 250), fill=(7, 19, 44, 105))
    overlay = overlay.filter(ImageFilter.GaussianBlur(3))
    image = Image.alpha_composite(image, overlay)
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((58, 48, 340, 171), 28, fill=(255, 255, 255, 242))
    logo = Image.open(LOGO).convert("RGBA")
    lw = 238
    logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.Resampling.LANCZOS)
    image.alpha_composite(logo, (79, 70))

    draw.rounded_rectangle((68, 207, 420, 266), 28, fill=spec["accent"])
    tag_fill = NAVY if spec["accent"] == YELLOW else WHITE
    draw.text((94, 224), spec["tag"], font=font(BOLD, 21), fill=tag_fill)

    title_size = 57 if index == 0 else 55
    draw.multiline_text((70, 324), spec["title"], font=font(BOLD, title_size), fill=WHITE, spacing=8)
    title_box = draw.multiline_textbbox((70, 324), spec["title"], font=font(BOLD, title_size), spacing=8)
    accent_y = min(title_box[3] + 36, 720)
    draw.rectangle((72, accent_y, 165, accent_y + 9), fill=CYAN)
    draw.rectangle((181, accent_y, 274, accent_y + 9), fill=YELLOW)
    draw.rectangle((290, accent_y, 383, accent_y + 9), fill=MAGENTA)

    body = textwrap.fill(spec["body"], 34, break_long_words=False, break_on_hyphens=False)
    draw.multiline_text((72, accent_y + 52), body, font=font(REGULAR, 30), fill=PALE, spacing=11)

    if index == 4:
        draw.rounded_rectangle((70, 1060, 520, 1137), 28, fill=(255, 255, 255, 240))
        draw.text((98, 1084), "GUARDE PARA PREPARAR O PEDIDO", font=font(BOLD, 20), fill=NAVY)
    elif index == 0:
        draw.rounded_rectangle((70, 1048, 526, 1125), 28, fill=(255, 255, 255, 240))
        draw.text((98, 1072), "DESLIZE PARA VER AS 4 CONFIRMAÇÕES", font=font(BOLD, 18), fill=NAVY)

    draw.rectangle((0, 1250, W, H), fill=NAVY)
    draw.text((64, 1281), "scolorprint.com", font=font(BOLD, 29), fill=WHITE)
    draw.text((928, 1282), spec["number"], font=font(BOLD, 26), fill=WHITE)
    image.convert("RGB").save(CAMPAIGN / f"slide-{index + 1:02d}-v1.jpg", quality=94, subsampling=0)


def main():
    for index, spec in enumerate(SLIDES):
        draw_slide(spec, index)


if __name__ == "__main__":
    main()
