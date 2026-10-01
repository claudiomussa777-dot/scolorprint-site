from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
BASE = CAMPAIGN / "base-corte-preciso-v1.png"
LOGO = ROOT / "assets" / "logo-scp.png"
W, H = 1080, 1350
NAVY, CYAN, MAGENTA, YELLOW = "#0A1428", "#13B9E9", "#EC1977", "#F4C542"
WHITE, PALE = "#FFFFFF", "#E8F5FA"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def main():
    image = ImageOps.fit(Image.open(BASE).convert("RGB"), (W, H), Image.Resampling.LANCZOS).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)
    draw_overlay.rounded_rectangle((38, 34, 652, 1115), 48, fill=(4, 12, 28, 232))
    image = Image.alpha_composite(image, overlay.filter(ImageFilter.GaussianBlur(7)))
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((60, 56, 352, 178), 28, fill=(255, 255, 255, 248))
    logo = Image.open(LOGO).convert("RGBA")
    logo = logo.resize((246, round(logo.height * 246 / logo.width)), Image.Resampling.LANCZOS)
    image.alpha_composite(logo, (83, 78))

    draw.rounded_rectangle((68, 220, 382, 280), 28, fill=YELLOW)
    draw.text((94, 238), "DICA DE ACABAMENTO", font=font(BOLD, 19), fill=NAVY)
    draw.multiline_text((68, 334), "CORTE CERTO\nCOMEÇA COM MARGEM.", font=font(BOLD, 46), fill=WHITE, spacing=4)
    draw.text((70, 476), "PROTEJA O QUE IMPORTA", font=font(BOLD, 25), fill=CYAN)

    items = [
        ("1", "MARGEM SEGURA", "afaste texto e logótipo do corte", CYAN),
        ("2", "SANGRIA", "prolongue a cor até além da linha final", MAGENTA),
        ("3", "MARCAS", "guie o corte sem entrar na arte", YELLOW),
        ("4", "REVISÃO", "confirme o ficheiro antes de produzir", CYAN),
    ]
    y = 545
    for number, title, detail, color in items:
        draw.ellipse((70, y, 118, y + 48), fill=color)
        draw.text((86, y + 11), number, font=font(BOLD, 20), fill=NAVY)
        draw.text((140, y - 2), title, font=font(BOLD, 25), fill=PALE)
        draw.text((140, y + 32), detail, font=font(REGULAR, 20), fill=WHITE)
        y += 88

    draw.rounded_rectangle((68, 974, 568, 1066), 30, fill=(255, 255, 255, 246))
    draw.text((104, 1006), "PEÇA O SEU ORÇAMENTO", font=font(BOLD, 23), fill=NAVY)

    draw.rectangle((0, 1250, W, H), fill=NAVY)
    draw.text((62, 1281), "scolorprint.com", font=font(BOLD, 29), fill=WHITE)
    draw.text((726, 1286), "IMPRESSÃO & PERSONALIZAÇÃO", font=font(BOLD, 17), fill=WHITE)
    image.convert("RGB").save(CAMPAIGN / "poster-v1.jpg", quality=94, subsampling=0)


if __name__ == "__main__":
    main()
