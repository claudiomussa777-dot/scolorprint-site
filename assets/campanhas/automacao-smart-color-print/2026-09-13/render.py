from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
BASE = CAMPAIGN / "base-evento-semana-v1.png"
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
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    sd.rounded_rectangle((34, 28, 668, 1170), 48, fill=(4, 12, 28, 232))
    image = Image.alpha_composite(image, shade.filter(ImageFilter.GaussianBlur(7)))
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((56, 48, 350, 172), 28, fill=(255, 255, 255, 245))
    logo = Image.open(LOGO).convert("RGBA")
    logo = logo.resize((250, round(logo.height * 250 / logo.width)), Image.Resampling.LANCZOS)
    image.alpha_composite(logo, (77, 70))

    draw.rounded_rectangle((66, 208, 404, 268), 28, fill=YELLOW)
    draw.text((92, 225), "DOMINGO | PLANEAMENTO", font=font(BOLD, 21), fill=NAVY)
    draw.multiline_text((66, 320), "EVENTO ESTA\nSEMANA?", font=font(BOLD, 65), fill=WHITE, spacing=4)
    draw.text((69, 485), "CONFIRME 4 PONTOS", font=font(BOLD, 29), fill=CYAN)

    items = ["DATA E LOCAL", "PEÇAS NECESSÁRIAS", "QUANTIDADES", "FICHEIROS FINAIS"]
    colors = [CYAN, MAGENTA, YELLOW, CYAN]
    y = 557
    for i, (item, color) in enumerate(zip(items, colors), 1):
        draw.ellipse((70, y + 4, 112, y + 46), fill=color)
        draw.text((84, y + 12), str(i), font=font(BOLD, 19), fill=NAVY)
        draw.text((133, y + 9), item, font=font(BOLD, 27), fill=PALE)
        y += 82

    draw.rounded_rectangle((66, 920, 485, 1002), 30, fill=(255, 255, 255, 244))
    draw.text((98, 946), "GUARDE ESTA CHECKLIST", font=font(BOLD, 23), fill=NAVY)
    draw.text((68, 1052), "Planeie hoje. Produza com clareza.", font=font(REGULAR, 27), fill=PALE)

    draw.rectangle((0, 1250, W, H), fill=NAVY)
    draw.text((62, 1281), "scolorprint.com", font=font(BOLD, 29), fill=WHITE)
    draw.text((744, 1286), "COMUNICAÇÃO PARA EVENTOS", font=font(BOLD, 18), fill=WHITE)
    image.convert("RGB").save(CAMPAIGN / "poster-v1.jpg", quality=94, subsampling=0)


if __name__ == "__main__":
    main()
