from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
CAMPAIGN = Path(__file__).resolve().parent
BASE = CAMPAIGN / "base-studio.png"
LOGO = ROOT / "assets" / "logo-scp.png"
OUTPUT = CAMPAIGN / "poster.jpg"

WIDTH, HEIGHT = 1080, 1350
NAVY = "#10152D"
MAGENTA = "#ED0B73"
CYAN = "#16A8D1"
LIME = "#DFFF38"
OFF_WHITE = "#FFFDF8"

BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)


def fit_cover(source: Image.Image) -> Image.Image:
    source = source.convert("RGB")
    source_ratio = source.width / source.height
    target_ratio = WIDTH / HEIGHT
    if source_ratio < target_ratio:
        crop_height = round(source.width / target_ratio)
        top = 0
        source = source.crop((0, top, source.width, top + crop_height))
    else:
        crop_width = round(source.height * target_ratio)
        left = (source.width - crop_width) // 2
        source = source.crop((left, 0, left + crop_width, source.height))
    return source.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)


canvas = fit_cover(Image.open(BASE)).convert("RGBA")

# Painel de leitura com sombra suave: mantém a fotografia visível e garante
# legibilidade no telemóvel.
shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
shadow_draw = ImageDraw.Draw(shadow)
shadow_draw.rounded_rectangle((42, 34, 700, 875), radius=36, fill=(8, 17, 42, 72))
shadow = shadow.filter(ImageFilter.GaussianBlur(18))
canvas = Image.alpha_composite(canvas, shadow)

panel = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
panel_draw = ImageDraw.Draw(panel)
panel_draw.rounded_rectangle((34, 26, 692, 865), radius=36, fill=(255, 253, 248, 236))
canvas = Image.alpha_composite(canvas, panel)

draw = ImageDraw.Draw(canvas)

logo = Image.open(LOGO).convert("RGBA")
logo_width = 260
logo_height = round(logo.height * logo_width / logo.width)
logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
canvas.alpha_composite(logo, (72, 62))

pill_box = (72, 178, 382, 234)
draw.rounded_rectangle(pill_box, radius=28, fill=MAGENTA)
draw.text((96, 191), "BOM DOMINGO, MAPUTO", font=font(BOLD, 24), fill=OFF_WHITE)

headline = "HOJE PLANEIA.\nESTA SEMANA,\nA SUA MARCA\nGANHA FORMA."
draw.multiline_text(
    (72, 270),
    headline,
    font=font(BOLD, 61),
    fill=NAVY,
    spacing=7,
)

draw.rectangle((72, 598, 160, 607), fill=CYAN)
draw.rectangle((168, 598, 232, 607), fill=MAGENTA)
draw.rectangle((240, 598, 296, 607), fill="#F6BF26")

draw.multiline_text(
    (72, 637),
    "Impressão • personalização •\nmateriais para eventos",
    font=font(REGULAR, 31),
    fill=NAVY,
    spacing=8,
)

cta_box = (72, 750, 544, 824)
draw.rounded_rectangle(cta_box, radius=20, fill=LIME)
draw.text((102, 771), "PEÇA O SEU ORÇAMENTO  →", font=font(BOLD, 25), fill=NAVY)

footer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
footer_draw = ImageDraw.Draw(footer)
footer_draw.rectangle((0, 1248, WIDTH, HEIGHT), fill=(16, 21, 45, 246))
footer_draw.text((62, 1276), "scolorprint.com", font=font(BOLD, 30), fill=OFF_WHITE)
footer_draw.text((620, 1278), "+258 84 990 0402", font=font(BOLD, 27), fill=OFF_WHITE)
canvas = Image.alpha_composite(canvas, footer)

canvas.convert("RGB").save(OUTPUT, "JPEG", quality=93, optimize=True, progressive=True)
print(OUTPUT)
