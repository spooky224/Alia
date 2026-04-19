import os
from PIL import Image, ImageDraw, ImageFont
from rembg import remove

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

BASE_SLIDE = os.path.join(BASE_DIR, "slide_01_base.png")
FONT_PATH = os.path.join(BASE_DIR, "Poppins-SemiBold.ttf")

MAIN_NAME_COLOR = (38, 66, 53)
DETAIL_COLOR = (38, 66, 53)

NAME_BOX = {"x": 200, "y": 350, "w": 720, "h": 320}
DETAIL_BOX = {"x": 200, "y": 690, "w": 720, "h": 120}

NAME_MAX_FONT_SIZE = 100
NAME_MIN_FONT_SIZE = 64
DETAIL_MAX_FONT_SIZE = 42
DETAIL_MIN_FONT_SIZE = 28

PRODUCT_RENDER_SIZE = 700


def slugify(text: str) -> str:
    return text.lower().replace(" ", "_").replace("é", "e").replace("è", "e").replace("à", "a")


def normalize_product_image(img, size):
    img = img.convert("RGBA")
    img.thumbnail((size, size), Image.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.paste(img, ((size - img.width)//2, (size - img.height)//2), img)
    return canvas


def draw_text_box(draw, text, box, max_size, min_size, color):
    x, y, w, h = box.values()
    for size in range(max_size, min_size, -2):
        font = ImageFont.truetype(FONT_PATH, size)
        lines, current = [], ""
        for word in text.split():
            trial = (current + " " + word).strip()
            if draw.textlength(trial, font=font) <= w:
                current = trial
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
        draw.text((x + (w - lw)//2, y_cursor), line, fill=color, font=font)
        y_cursor += lh


# ✅ NEW callable API
def generate_slide_01(gamme, product_name, image_path, product_detail=None, no_bg=False):
    out_dir = os.path.join(
        PROJECT_ROOT, "presentations", slugify(gamme), slugify(product_name)
    )
    os.makedirs(out_dir, exist_ok=True)

    slide = Image.open(BASE_SLIDE).convert("RGBA")
    draw = ImageDraw.Draw(slide)

    draw_text_box(draw, product_name, NAME_BOX, NAME_MAX_FONT_SIZE, NAME_MIN_FONT_SIZE, MAIN_NAME_COLOR)

    if product_detail:
        draw_text_box(draw, product_detail, DETAIL_BOX, DETAIL_MAX_FONT_SIZE, DETAIL_MIN_FONT_SIZE, DETAIL_COLOR)

    product = Image.open(image_path).convert("RGBA")
    if not no_bg:
        product = remove(product)

    product = normalize_product_image(product, PRODUCT_RENDER_SIZE)

    mask = Image.new("L", product.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, *product.size), fill=255)
    product = Image.composite(product, Image.new("RGBA", product.size), mask)

    slide.paste(product, (1500 - product.size[0]//2, 610 - product.size[1]//2), product)

    out_path = os.path.join(out_dir, "slide_01.png")
    slide.save(out_path)
    return out_path


# ✅ CLI preserved
def main():
    generate_slide_01(
        input("Product gamme: "),
        input("Product name: "),
        input("Image path: "),
        input("Small detail: ") or None,
        input("Image already transparent? (y/N): ").lower() == "y",
    )


if __name__ == "__main__":
    main()