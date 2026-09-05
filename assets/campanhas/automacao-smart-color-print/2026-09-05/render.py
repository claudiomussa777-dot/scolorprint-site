from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parent
LOGO = ROOT / "assets" / "logo-scp.png"
BASE = CAMPAIGN / "base-kit-brindes-v1.png"

WIDTH = 1080
HEIGHT = 1350
NAVY = "#101935"
CYAN = "#19B3E6"
MAGENTA = "#EA1A72"
YELLOW = "#F3C515"
WHITE = "#FFFDF8"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)


def wrap(text: str, width: int) -> str:
    return textwrap.fill(text, width=width, break_long_words=False, break_on_hyphens=False)


def main() -> None:
    base = ImageOps.fit(Image.open(BASE).convert("RGB"), (WIDTH, HEIGHT), method=Image.Resampling.LANCZOS).convert("RGBA")

    shade = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    sd.rounded_rectangle((46, 42, 664, 842), radius=44, fill=(7, 15, 36, 208))
    shade = shade.filter(ImageFilter.GaussianBlur(10))
    base = Image.alpha_composite(base, shade)
    draw = ImageDraw.Draw(base)

    draw.rounded_rectangle((58, 48, 338, 174), radius=28, fill=(255, 253, 248, 238))
    logo = Image.open(LOGO).convert("RGBA")
    logo_width = 238
    logo_height = round(logo.height * logo_width / logo.width)
    logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
    base.alpha_composite(logo, (78, 72))

    draw.rounded_rectangle((72, 190, 418, 248), radius=28, fill=MAGENTA)
    draw.text((98, 207), "SÁBADO | INSPIRAÇÃO", font=font(BOLD, 22), fill=WHITE)

    title = "UM KIT QUE\nCONTINUA\nA MARCA"
    draw.multiline_text((74, 310), title, font=font(BOLD, 62), fill=WHITE, spacing=8)
    draw.rectangle((76, 590, 160, 598), fill=CYAN)
    draw.rectangle((174, 590, 258, 598), fill=MAGENTA)
    draw.rectangle((272, 590, 356, 598), fill=YELLOW)

    body = wrap("Caneca, garrafa, caderno e caneta podem formar uma recepção mais coerente para eventos e equipas.", 29)
    draw.multiline_text((76, 640), body, font=font(REGULAR, 28), fill=WHITE, spacing=9)

    draw.rounded_rectangle((70, 782, 514, 844), radius=28, fill=(255, 253, 248, 235))
    draw.text((98, 800), "PENSE NO USO, DEPOIS PERSONALIZE", font=font(BOLD, 19), fill=NAVY)

    draw.rectangle((0, 1250, WIDTH, HEIGHT), fill=NAVY)
    draw.text((64, 1282), "scolorprint.com", font=font(BOLD, 30), fill=WHITE)
    draw.text((676, 1286), "PEÇA O SEU ORÇAMENTO", font=font(BOLD, 20), fill=WHITE)

    base.convert("RGB").save(CAMPAIGN / "poster-v1.jpg", quality=94, subsampling=0)


if __name__ == "__main__":
    main()
