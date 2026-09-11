from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
BASE = CAMPAIGN / "base-bones-v1.png"
LOGO = ROOT / "assets" / "logo-scp.png"
W, H = 1080, 1350
NAVY, CYAN, MAGENTA, YELLOW = "#0A1428", "#13B9E9", "#EC1977", "#F4C542"
WHITE, PALE = "#FFFFFF", "#E8F5FA"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def main():
    image = ImageOps.fit(
        Image.open(BASE).convert("RGB"), (W, H), method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5)
    ).convert("RGBA")

    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    sd.rounded_rectangle((34, 28, 640, 1125), 48, fill=(4, 12, 28, 226))
    shade = shade.filter(ImageFilter.GaussianBlur(7))
    image = Image.alpha_composite(image, shade)
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((56, 48, 350, 172), 28, fill=(255, 255, 255, 245))
    logo = Image.open(LOGO).convert("RGBA")
    lw = 250
    logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.Resampling.LANCZOS)
    image.alpha_composite(logo, (77, 70))

    draw.rounded_rectangle((66, 208, 335, 268), 28, fill=YELLOW)
    draw.text((93, 225), "SEXTA | EM FOCO", font=font(BOLD, 22), fill=NAVY)

    draw.multiline_text((66, 324), "BONÉS QUE\nIDENTIFICAM\nA SUA EQUIPA", font=font(BOLD, 57), fill=WHITE, spacing=5)
    draw.rectangle((68, 548, 152, 558), fill=CYAN)
    draw.rectangle((168, 548, 252, 558), fill=YELLOW)
    draw.rectangle((268, 548, 352, 558), fill=MAGENTA)

    body = textwrap.fill(
        "Para atendimento, eventos ou trabalho no terreno, personalize cores, aplicação e quantidade conforme o uso.",
        29,
        break_long_words=False,
        break_on_hyphens=False,
    )
    draw.multiline_text((68, 609), body, font=font(REGULAR, 29), fill=PALE, spacing=11)

    draw.rounded_rectangle((66, 862, 500, 944), 30, fill=(255, 255, 255, 242))
    draw.text((97, 888), "PEÇA O SEU ORÇAMENTO", font=font(BOLD, 24), fill=NAVY)

    draw.rectangle((0, 1250, W, H), fill=NAVY)
    draw.text((62, 1281), "scolorprint.com", font=font(BOLD, 29), fill=WHITE)
    draw.text((750, 1286), "BONÉS PERSONALIZADOS", font=font(BOLD, 20), fill=WHITE)

    image.convert("RGB").save(CAMPAIGN / "poster-v1.jpg", quality=94, subsampling=0)


if __name__ == "__main__":
    main()
