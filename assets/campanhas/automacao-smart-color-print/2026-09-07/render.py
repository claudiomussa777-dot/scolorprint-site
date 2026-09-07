from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
BASE = CAMPAIGN / "base-uniformes-v1.png"
LOGO = ROOT / "assets" / "logo-scp.png"
W, H = 1080, 1350
NAVY, CYAN, MAGENTA, YELLOW = "#0C1933", "#19B7E8", "#E71D73", "#F2C94C"
WHITE = "#FFFFFF"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def main():
    image = ImageOps.fit(Image.open(BASE).convert("RGB"), (W, H), method=Image.Resampling.LANCZOS).convert("RGBA")
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    sd.rounded_rectangle((42, 34, 625, 1035), 42, fill=(5, 15, 35, 220))
    shade = shade.filter(ImageFilter.GaussianBlur(9))
    image = Image.alpha_composite(image, shade)
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((58, 46, 340, 170), 28, fill=(255, 255, 255, 240))
    logo = Image.open(LOGO).convert("RGBA")
    lw = 238
    logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.Resampling.LANCZOS)
    image.alpha_composite(logo, (79, 69))

    draw.rounded_rectangle((70, 200, 388, 258), 28, fill=MAGENTA)
    draw.text((96, 217), "SEGUNDA | PREPARAÇÃO", font=font(BOLD, 21), fill=WHITE)

    draw.multiline_text((70, 322), "EQUIPA\nALINHADA\nDESDE O\nPRIMEIRO DIA", font=font(BOLD, 57), fill=WHITE, spacing=7)
    draw.rectangle((72, 652, 158, 660), fill=CYAN)
    draw.rectangle((172, 652, 258, 660), fill=YELLOW)
    draw.rectangle((272, 652, 358, 660), fill=MAGENTA)

    body = textwrap.fill("Uniformes personalizados ajudam a identificar funções e a apresentar a marca com coerência.", 30, break_long_words=False, break_on_hyphens=False)
    draw.multiline_text((72, 706), body, font=font(REGULAR, 28), fill=WHITE, spacing=9)

    draw.rounded_rectangle((70, 895, 515, 972), 30, fill=(255, 255, 255, 238))
    draw.text((96, 920), "CAMISETAS • COLETES • BONÉS", font=font(BOLD, 20), fill=NAVY)

    draw.rectangle((0, 1250, W, H), fill=NAVY)
    draw.text((64, 1281), "scolorprint.com", font=font(BOLD, 29), fill=WHITE)
    draw.text((714, 1285), "PEÇA O SEU ORÇAMENTO", font=font(BOLD, 20), fill=WHITE)

    image.convert("RGB").save(CAMPAIGN / "poster-v1.jpg", quality=94, subsampling=0)


if __name__ == "__main__":
    main()
