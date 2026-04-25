import streamlit as st
import sys
import os
import json
import re
import unicodedata

import pytesseract
import cv2
import numpy as np
from PIL import Image

# -------------------------------------------------
# PATH SETUP
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SLIDE_01_DIR = os.path.join(BASE_DIR, "slide_01_Generator")
SLIDE_02_DIR = os.path.join(BASE_DIR, "slide_02_Generator")
PRODUCT_IMAGES_DIR = os.path.join(BASE_DIR, "product_images")

sys.path.append(SLIDE_01_DIR)
sys.path.append(SLIDE_02_DIR)

from generate_slide_01 import generate_slide_01
from generate_slide_02 import generate_slide_02

PRODUCTS_JSON_PATH = os.path.join(BASE_DIR, "products.json")

# -------------------------------------------------
# SESSION STATE INIT (CRITICAL)
# -------------------------------------------------
for key, default in {
    "indications": [],
    "composition": [],
    "ages": [],
    "utilisation": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# -------------------------------------------------
# UTILS
# -------------------------------------------------
def slugify(text: str) -> str:
    return (
        text.lower()
        .replace(" ", "_")
        .replace("é", "e")
        .replace("è", "e")
        .replace("à", "a")
    )


def normalize_text(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


def extract_text_from_image(image_file) -> str:
    img = Image.open(image_file).convert("RGB")
    open_cv_image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

    return pytesseract.image_to_string(gray, lang="fra")


def parse_product_semantics(ocr_text: str) -> dict:
    text = normalize_text(ocr_text).upper()

    def extract_block(start, end=None):
        if end:
            pattern = rf"{start}(.*?){end}"
        else:
            pattern = rf"{start}(.*)"
        match = re.search(pattern, text, re.S)
        return match.group(1).strip() if match else ""

    indications_block = extract_block("INDICATIONS", "COMPOSITION")
    composition_block = extract_block("COMPOSITION", "CONSEILS")
    utilisation_block = extract_block("UTILISATION", None)

    def bullets(block):
        return [
            line.strip("•- ").capitalize()
            for line in block.splitlines()
            if len(line.strip()) > 5
        ]

    return {
        "indications": bullets(indications_block),
        "composition": bullets(composition_block),
        "age_and_population": ["Adulte"] if "ADULTE" in text else [],
        "utilisation": " ".join(bullets(utilisation_block)),
    }


def save_product_image(uploaded_file, gamme, product_name):
    target_dir = os.path.join(PRODUCT_IMAGES_DIR, slugify(gamme))
    os.makedirs(target_dir, exist_ok=True)

    path = os.path.join(target_dir, f"{slugify(product_name)}.png")
    with open(path, "wb") as f:
        f.write(uploaded_file.read())

    return path


def save_slide_02_semantics(
    out_dir,
    gamme,
    product,
    indications,
    composition,
    ages,
    usage,
):
    payload = {
        "name": product,
        "category": gamme,
        "indications": [i for i in indications if i.strip()],
        "composition": [c for c in composition if c.strip()],
        "age_and_population": [a for a in ages if a.strip()],
        "utilisation": [usage] if usage else [],
    }

    with open(os.path.join(out_dir, "slide_02.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def register_product_if_missing(product_name: str, category: str):
    product_id = slugify(product_name)

    products = {}
    if os.path.isfile(PRODUCTS_JSON_PATH):
        with open(PRODUCTS_JSON_PATH, "r", encoding="utf-8") as f:
            products = json.load(f)

    if product_id in products:
        return

    products[product_id] = {
        "display_name": product_name,
        "category": slugify(category),
        "aliases": [
            product_name.lower(),
            product_name.replace("_", " ").lower(),
            product_id.replace("_", " "),
        ],
    }

    with open(PRODUCTS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)


# -------------------------------------------------
# STREAMLIT UI
# -------------------------------------------------
st.set_page_config(page_title="Product Presentation Generator", layout="wide")

st.title("🖼️ Product Presentation Generator")

# -------------------------------------------------
# OCR MIGRATION
# -------------------------------------------------
st.header("📥 Optional: Migrate from existing product slide")

screenshot = st.file_uploader(
    "Upload existing product slide (PNG/JPG)",
    type=["png", "jpg", "jpeg"],
)

if screenshot:
    with st.spinner("Extracting product information from slide..."):
        extracted = parse_product_semantics(extract_text_from_image(screenshot))

    st.session_state.indications = extracted["indications"]
    st.session_state.composition = extracted["composition"]
    st.session_state.ages = extracted["age_and_population"]
    st.session_state.utilisation = extracted["utilisation"]

    st.success("✅ Information extracted — please review and adjust below")


# -------------------------------------------------
# PRODUCT INFO
# -------------------------------------------------
st.header("1️⃣ Product Information")

col1, col2 = st.columns(2)

with col1:
    gamme = st.text_input("Product gamme / category")
    product_name = st.text_input("Product name")
    product_detail = st.text_input("Small detail (optional)")

with col2:
    uploaded_image = st.file_uploader(
        "Upload product image (photo or screenshot)",
        type=["png", "jpg", "jpeg"],
    )
    no_bg = st.checkbox("Image already has a transparent background")

if screenshot and not uploaded_image:
    uploaded_image = screenshot

st.divider()

# -------------------------------------------------
# MEDICAL INFO
# -------------------------------------------------
st.header("2️⃣ Slide 02 – Medical Information")

indications = st.text_area(
    "Indications (one per line)",
    value="\n".join(st.session_state.indications),
).splitlines()

composition = st.text_area(
    "Composition (one per line)",
    value="\n".join(st.session_state.composition),
).splitlines()

col3, col4 = st.columns(2)

with col3:
    ages = st.text_area(
        "Dosage – Age (one per line)",
        value="\n".join(st.session_state.ages),
    ).splitlines()

with col4:
    utilisation = st.text_input(
        "Dosage – Utilisation (single sentence)",
        value=st.session_state.utilisation,
    )

st.divider()

# -------------------------------------------------
# GENERATE
# -------------------------------------------------
if st.button("🚀 Generate Presentation (Slide 01 + Slide 02)", use_container_width=True):

    if not gamme or not product_name or not uploaded_image:
        st.error("Please provide product gamme, product name, and an image.")
        st.stop()

    image_path = save_product_image(uploaded_image, gamme, product_name)

    slide_01_path = generate_slide_01(
        gamme=gamme,
        product_name=product_name,
        image_path=image_path,
        product_detail=product_detail or None,
        no_bg=no_bg,
    )

    slide_02_path = generate_slide_02(
        gamme=gamme,
        product=product_name,
        image_path=image_path,
        indications=indications,
        composition=composition,
        ages=ages,
        usage=utilisation,
        no_bg=no_bg,
    )

    out_dir = os.path.dirname(slide_02_path)

    save_slide_02_semantics(
        out_dir,
        gamme,
        product_name,
        indications,
        composition,
        ages,
        utilisation,
    )

    register_product_if_missing(product_name, gamme)

    st.success("✅ Presentation generated successfully")

    colA, colB = st.columns(2)
    with colA:
        st.subheader("Slide 01 – Product Overview")
        st.image(slide_01_path)

    with colB:
        st.subheader("Slide 02 – Product Details")
        st.image(slide_02_path)