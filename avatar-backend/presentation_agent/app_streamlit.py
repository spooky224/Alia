import streamlit as st
import sys
import os

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


def save_product_image(uploaded_file, gamme, product_name):
    """
    Save uploaded image to:
    product_images/<gamme>/<product_name>.png
    """
    gamme_slug = slugify(gamme)
    product_slug = slugify(product_name)

    target_dir = os.path.join(PRODUCT_IMAGES_DIR, gamme_slug)
    os.makedirs(target_dir, exist_ok=True)

    image_path = os.path.join(target_dir, f"{product_slug}.png")

    with open(image_path, "wb") as f:
        f.write(uploaded_file.read())

    return image_path


# -------------------------------------------------
# STREAMLIT CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Product Presentation Generator",
    layout="wide",
)

st.title("🖼️ Product Presentation Generator")


# =================================================
# 1️⃣ PRODUCT INFORMATION (SHARED)
# =================================================
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


st.divider()


# =================================================
# 2️⃣ SLIDE 02 – MEDICAL INFO
# =================================================
st.header("2️⃣ Slide 02 – Medical Information")

indications = st.text_area(
    "Indications (one per line)",
    help="Each line will be rendered as a bullet point",
).splitlines()

composition = st.text_area(
    "Composition (one per line)",
    help="Each line will be rendered as a bullet point",
).splitlines()

col3, col4 = st.columns(2)

with col3:
    ages = st.text_area(
        "Dosage – Age (one per line)"
    ).splitlines()

with col4:
    utilisation = st.text_input(
        "Dosage – Utilisation (single sentence)"
    )


st.divider()


# =================================================
# 🚀 GENERATE BOTH SLIDES
# =================================================
if st.button("🚀 Generate Presentation (Slide 01 + Slide 02)", use_container_width=True):

    if not gamme or not product_name or not uploaded_image:
        st.error("Please provide product gamme, product name, and an image.")
    else:
        # ✅ Save image permanently in product_images
        image_path = save_product_image(
            uploaded_image, gamme, product_name
        )

        # -----------------------------
        # Generate Slide 01
        # -----------------------------
        slide_01_path = generate_slide_01(
            gamme=gamme,
            product_name=product_name,
            image_path=image_path,
            product_detail=product_detail or None,
            no_bg=no_bg,
        )

        # -----------------------------
        # Generate Slide 02
        # -----------------------------
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

        # -----------------------------
        # Results
        # -----------------------------
        st.success("✅ Presentation generated successfully")

        colA, colB = st.columns(2)

        with colA:
            st.subheader("Slide 01 – Product Overview")
            st.image(slide_01_path)

        with colB:
            st.subheader("Slide 02 – Product Details")
            st.image(slide_02_path)
