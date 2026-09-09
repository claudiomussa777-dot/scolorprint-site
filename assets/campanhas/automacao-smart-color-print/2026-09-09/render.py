from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
BASE = CAMPAIGN / "base-margem-seguranca-v1.png"
LOGO = ROOT / "assets" / "logo-scp.png"
W, H = 1080, 1350
NAVY, CYAN, MAGENTA, YELLOW = "#0C1933", "#19B7E8", "#E71D73", "#F2C94C"
WHITE, PALE = "#FFFFFF", "#EAF6FB"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def main():
    image = ImageOps.fit(Image.open(BASE).convert("RGB"), (W, H), method=Image.Resampling.LANCZOS).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle((38, 30, 660, 1055), 44, fill=(5, 15, 35, 220))
    overlay = overlay.filter(ImageFilter.GaussianBlur(8))
    image = Image.alpha_composite(image, overlay)
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((58, 46, 340, 170), 28, fill=(255, 255, 255, 242))
    logo = Image.open(LOGO).convert("RGBA")
    lw = 238
    logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.Resampling.LANCZOS)
    image.alpha_composite(logo, (79, 69))

    draw.rounded_rectangle((70, 205, 380, 264), 28, fill=CYAN)
    draw.text((96, 222), "QUARTA | ACABAMENTO", font=font(BOLD, 21), fill=NAVY)

    draw.multiline_text((70, 324), "EVITE CORTES\nNO TEXTO", font=font(BOLD, 64), fill=WHITE, spacing=8)
    draw.rectangle((72, 520, 165, 529), fill=CYAN)
    draw.rectangle((181, 520, 274, 529), fill=YELLOW)
    draw.rectangle((290, 520, 383, 529), fill=MAGENTA)

    body = textwrap.fill(
        "Deixe texto, logótipo e contactos afastados da linha de corte. A margem de segurança ajuda a preservar a informação depois do acabamento.",
        32,
        break_long_words=False,
        break_on_hyphens=False,
    )
    draw.multiline_text((72, 581), body, font=font(REGULAR, 30), fill=PALE, spacing=11)

    draw.rounded_rectangle((70, 883, 571, 961), 30, fill=(255, 255, 255, 240))
    draw.text((98, 907), "CONFIRME A MARGEM ANTES DE APROVAR", font=font(BOLD, 18), fill=NAVY)

    draw.rectangle((0, 1250, W, H), fill=NAVY)
    draw.text((64, 1281), "scolorprint.com", font=font(BOLD, 29), fill=WHITE)
    draw.text((818, 1284), "GUARDE ESTA DICA", font=font(BOLD, 20), fill=WHITE)

    image.convert("RGB").save(CAMPAIGN / "poster-v1.jpg", quality=94, subsampling=0)


if __name__ == "__main__":
    main()
