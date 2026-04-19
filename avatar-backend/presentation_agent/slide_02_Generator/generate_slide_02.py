import os
from PIL import Image, ImageDraw, ImageFont
from rembg import remove

# -----------------------------
# PATH RESOLUTION
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

BASE_SLIDE = os.path.join(BASE_DIR, "slide_02_base.png")
FONT_PATH = os.path.join(BASE_DIR, "Poppins-SemiBold.ttf")
PRODUCT_IMAGES_ROOT = os.path.join(PROJECT_ROOT, "product_images")

# -----------------------------
# COLORS
# -----------------------------
TEXT_COLOR = (255, 255, 255)
SUBTEXT_COLOR = (50, 50, 50)

# -----------------------------
# IMAGE CONSTRAINTS
# -----------------------------
PRODUCT_MAX_BOX = (540, 540)
IMAGE_CENTER = {"x": 330, "y": 550}

# -----------------------------
# TEXT BOXES
# -----------------------------
INDICATIONS_BOX = {"x": 680, "y": 100, "w": 820, "h": 360}
COMPOSITION_BOX = {"x": 680, "y": 490, "w": 820, "h": 360}
POSO_AGE_BOX = {"x": 680, "y": 940, "w": 200, "h": 110}
POSO_UTIL_BOX = {"x": 920, "y": 945, "w": 550, "h": 110}

# -----------------------------
# FONT LIMITS
# -----------------------------
TEXT_MAX = 32
TEXT_MIN = 18

# -----------------------------
# HELPERS
# -----------------------------
def slugify(text: str) -> str:
    return (
        text.lower()
        .replace(" ", "_")
        .replace("é", "e")
        .replace("è", "e")
        .replace("à", "a")
    )


def normalize_product_image(img, max_size):
    img = img.convert("RGBA")
    img.thumbnail(max_size, Image.LANCZOS)
    return img


# ✅ BULLETED + WRAPPED + LEFT‑ALIGNED (INDICATIONS & COMPOSITION)
def draw_bulleted_wrapped_text(draw, lines, box, color):
    x, y, w, h = box["x"], box["y"], box["w"], box["h"]
    BULLET = "• "
    LINE_GAP = 6

    for size in range(TEXT_MAX, TEXT_MIN, -2):
        font = ImageFont.truetype(FONT_PATH, size)
        layout = []

        for line in lines:
            words = line.split()
            current = ""
            first = True
            limit = w - draw.textlength(BULLET, font=font)

            for word in words:
                test = f"{current} {word}".strip()
                if draw.textlength(test, font=font) <= limit:
                    current = test
                else:
                    layout.append((first, current))
                    current = word
                    first = False

            if current:
                layout.append((first, current))

        heights = [
            draw.textbbox((0, 0), text, font=font)[3]
            for _, text in layout
        ]

        if sum(heights) + LINE_GAP * len(heights) <= h:
            break

    y_cursor = y
    bullet_width = draw.textlength(BULLET, font=font)

    for is_first, text in layout:
        if is_first:
            draw.text((x, y_cursor), BULLET, fill=color, font=font)
        draw.text((x + bullet_width, y_cursor), text, fill=color, font=font)
        y_cursor += font.size + LINE_GAP


# ✅ MULTI‑LINE CENTERED (AGE ONLY)
def draw_multiline_centered_text(draw, lines, box, color):
    x, y, w, h = box["x"], box["y"], box["w"], box["h"]

    for size in range(TEXT_MAX, TEXT_MIN, -2):
        font = ImageFont.truetype(FONT_PATH, size)
        heights = [draw.textbbox((0, 0), l, font=font)[3] for l in lines]
        if sum(heights) <= h:
            break

    y_cursor = y + (h - sum(heights)) // 2
    for line, lh in zip(lines, heights):
        lw = draw.textlength(line, font=font)
        x_cursor = x + (w - lw) // 2
        draw.text((x_cursor, y_cursor), line, fill=color, font=font)
        y_cursor += lh


# ✅ WRAPPED + CENTERED (UTILISATION ONLY)
def draw_wrapped_centered_text(draw, text, box, color):
    x, y, w, h = box["x"], box["y"], box["w"], box["h"]

    for size in range(TEXT_MAX, TEXT_MIN, -2):
        font = ImageFont.truetype(FONT_PATH, size)
        words = text.split()
        lines = []
        current = ""

        for word in words:
            test = f"{current} {word}".strip()
            if draw.textlength(test, font=font) <= w:
                current = test
            else:
                lines.append(current)
                current = word

        if current:
            lines.append(current)

        heights = [draw.textbbox((0, 0), l, font=font)[3] for l in lines]
        if sum(heights) <= h:
            break

    y_cursor = y + (h - sum(heights)) // 2
    for line, lh in zip(lines, heights):
        lw = draw.textlength(line, font=font)
        x_cursor = x + (w - lw) // 2
        draw.text((x_cursor, y_cursor), line, fill=color, font=font)
        y_cursor += lh + 4


def collect_multiline(prompt):
    print(prompt)
    print("Enter one line per item. Press ENTER on empty line.\n")
    lines = []
    while True:
        l = input("> ").strip()
        if not l:
            break
        lines.append(l)
    return lines




def generate_slide_02(
    gamme, product, image_path,
    indications, composition, ages, usage, no_bg=False
):
    out_dir = os.path.join(PROJECT_ROOT, "presentations", slugify(gamme), slugify(product))
    os.makedirs(out_dir, exist_ok=True)

    slide = Image.open(BASE_SLIDE).convert("RGBA")
    draw = ImageDraw.Draw(slide)

    if indications:
        draw_bulleted_wrapped_text(draw, indications, INDICATIONS_BOX, TEXT_COLOR)

    if composition:
        draw_bulleted_wrapped_text(draw, composition, COMPOSITION_BOX, TEXT_COLOR)

    if ages:
        draw_multiline_centered_text(draw, ages, POSO_AGE_BOX, SUBTEXT_COLOR)

    if usage:
        draw_wrapped_centered_text(draw, usage, POSO_UTIL_BOX, SUBTEXT_COLOR)

    img = Image.open(image_path)
    if not no_bg:
        img = remove(img)

    img = normalize_product_image(img, PRODUCT_MAX_BOX)
    slide.paste(img,
        (IMAGE_CENTER["x"] - img.width//2, IMAGE_CENTER["y"] - img.height//2),
        img
    )

    out_path = os.path.join(out_dir, "slide_02.png")
    slide.save(out_path)
    return out_path


# -----------------------------
# MAIN
# -----------------------------
def main():
    gamme = input("Product gamme / category: ").strip()
    product = input("Product name: ").strip()
    image_name = input("Product image filename: ").strip()

    indications = collect_multiline("INDICATIONS:")
    composition = collect_multiline("COMPOSITION:")
    ages = collect_multiline("POSOLOGIE — AGE:")
    utilisations = collect_multiline("POSOLOGIE — UTILISATION:")

    no_bg = input("Image already transparent? (y/N): ").lower() == "y"

    img_path = os.path.join(PRODUCT_IMAGES_ROOT, slugify(gamme), image_name)
    if not os.path.exists(img_path):
        raise FileNotFoundError(img_path)

    out_dir = os.path.join(PROJECT_ROOT, "presentations", slugify(gamme), slugify(product))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "slide_02.png")

    slide = Image.open(BASE_SLIDE).convert("RGBA")
    draw = ImageDraw.Draw(slide)

    if indications:
        draw_bulleted_wrapped_text(draw, indications, INDICATIONS_BOX, TEXT_COLOR)

    if composition:
        draw_bulleted_wrapped_text(draw, composition, COMPOSITION_BOX, TEXT_COLOR)

    if ages:
        draw_multiline_centered_text(draw, ages, POSO_AGE_BOX, SUBTEXT_COLOR)

    # ✅ ONLY CHANGE APPLIED HERE
    if utilisations:
        draw_wrapped_centered_text(draw, utilisations[0], POSO_UTIL_BOX, SUBTEXT_COLOR)

    img = Image.open(img_path)
    if not no_bg:
        img = remove(img)

    img = normalize_product_image(img, PRODUCT_MAX_BOX)

    slide.paste(
        img,
        (IMAGE_CENTER["x"] - img.width // 2, IMAGE_CENTER["y"] - img.height // 2),
        img,
    )

    slide.save(out_path)
    print("✅ Slide created:", out_path)


if __name__ == "__main__":
    main()