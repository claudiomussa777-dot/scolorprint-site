from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
BASE = CAMPAIGN / "base-evento-identidade-v1.png"
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
    draw_overlay.rounded_rectangle((38, 34, 666, 1140), 48, fill=(4, 12, 28, 235))
    image = Image.alpha_composite(image, overlay.filter(ImageFilter.GaussianBlur(7)))
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((60, 56, 352, 178), 28, fill=(255, 255, 255, 248))
    logo = Image.open(LOGO).convert("RGBA")
    logo = logo.resize((246, round(logo.height * 246 / logo.width)), Image.Resampling.LANCZOS)
    image.alpha_composite(logo, (83, 78))

    draw.rounded_rectangle((68, 220, 342, 280), 28, fill=YELLOW)
    draw.text((94, 238), "INSPIRAÇÃO DE SÁBADO", font=font(BOLD, 18), fill=NAVY)
    draw.multiline_text((68, 332), "UM EVENTO,\nUMA IDENTIDADE.", font=font(BOLD, 47), fill=WHITE, spacing=4)
    draw.multiline_text((70, 480), "Quando as peças falam a mesma\nlinguagem, a marca aparece melhor.", font=font(REGULAR, 23), fill=PALE, spacing=7)

    items = [
        ("BACKDROP", "uma presença de fundo clara", CYAN),
        ("ROLL-UP", "informação visível no ponto certo", MAGENTA),
        ("CREDENCIAIS", "equipa e convidados bem identificados", YELLOW),
    ]
    y = 635
    for title, detail, color in items:
        draw.rounded_rectangle((70, y, 548, y + 76), 22, fill=(10, 20, 40, 245), outline=color, width=3)
        draw.text((96, y + 12), title, font=font(BOLD, 23), fill=color)
        draw.text((96, y + 42), detail, font=font(REGULAR, 18), fill=WHITE)
        y += 100

    draw.rounded_rectangle((68, 1026, 600, 1118), 30, fill=(255, 255, 255, 246))
    draw.text((100, 1058), "PLANEIE O SEU KIT DE EVENTO", font=font(BOLD, 20), fill=NAVY)

    draw.rectangle((0, 1250, W, H), fill=NAVY)
    draw.text((62, 1281), "scolorprint.com", font=font(BOLD, 29), fill=WHITE)
    draw.text((726, 1286), "IMPRESSÃO & PERSONALIZAÇÃO", font=font(BOLD, 17), fill=WHITE)
    image.convert("RGB").save(CAMPAIGN / "poster-v1.jpg", quality=94, subsampling=0)


if __name__ == "__main__":
    main()
