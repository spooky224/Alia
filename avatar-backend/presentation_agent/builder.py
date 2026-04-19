import os
import json
from typing import Dict, List


# =================================================
# CONFIG
# =================================================
BASE_DIR = os.path.dirname(__file__)
PRESENTATIONS_DIR = os.path.join(BASE_DIR, "presentations")


# =================================================
# HELPERS
# =================================================
def _get_product_dir(product_id: str) -> str:
    """
    Category-aware product resolver.

    Supports:
    presentations/<category>/<product_id>/
    """

    if not os.path.isdir(PRESENTATIONS_DIR):
        raise FileNotFoundError("Presentations directory not found")

    for category in os.listdir(PRESENTATIONS_DIR):
        category_path = os.path.join(PRESENTATIONS_DIR, category)

        if not os.path.isdir(category_path):
            continue

        product_path = os.path.join(category_path, product_id)

        if os.path.isdir(product_path):
            return product_path

    raise FileNotFoundError(
        f"No presentation folder found for product '{product_id}'"
    )


def _load_slide_02_semantics(product_dir: str) -> Dict:
    """
    Loads semantic medical data for slide 02.
    """
    json_path = os.path.join(product_dir, "slide_02.json")

    if not os.path.isfile(json_path):
        raise FileNotFoundError("slide_02.json not found")

    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _build_llm_prompt(product_id: str, semantics: Dict) -> str:
    """
    Converts structured medical JSON into a natural LLM prompt.
    """

    def fmt(title: str, values: List[str]) -> str:
        if not values:
            return ""
        lines = "\n".join(f"- {v}" for v in values)
        return f"{title}:\n{lines}\n"

    prompt = f"""
You are a medical representative speaking to a doctor.

Product name:
{semantics.get("name", product_id)}

Medical information:

{fmt("Indications", semantics.get("indications", []))}
{fmt("Composition", semantics.get("composition", []))}
{fmt("Target population", semantics.get("age_and_population", []))}
{fmt("Utilisation", semantics.get("utilisation", []))}

Instructions:
- Produce ONE continuous spoken presentation
- Use a clear, professional medical tone
- Do NOT mention slides
- Do NOT mention bullet points or sections
- Do NOT describe layouts or visuals
- Speak naturally, as if orally presenting the product
"""

    return prompt.strip()


def _call_llm(prompt: str) -> str:
    """
    LLM call stub.
    Replace with OpenAI / local LLM later.
    """
    return (
        "Bactol Savon Professionnel is a disinfectant soap designed for daily use "
        "in professional and medical environments. Its formulation, based on "
        "benzalkonium chloride at a concentration of 0.18 grams, ensures effective "
        "cleansing while supporting hygienic practices. The product is intended "
        "for adult use and integrates easily into routine hand hygiene protocols "
        "where regular disinfection is required."
    )


# =================================================
# PUBLIC API
# =================================================
def build_presentation(product_id: str) -> dict:
    """
    Returns presentation speech + static slide timeline.
    """

    product_dir = _get_product_dir(product_id)
    semantics = _load_slide_02_semantics(product_dir)

    prompt = _build_llm_prompt(product_id, semantics)
    speech_text = _call_llm(prompt)

    if not speech_text or len(speech_text.strip()) < 40:
        raise RuntimeError("Generated speech is too short or empty")

    # ✅ STATIC TIMELINE (V1)
    timeline = [
        {"slide": "slide_01.png", "start": 0.0},
        {"slide": "slide_02.png", "start": 5.0}
    ]

    return {
        "speech_text": speech_text.strip(),
        "timeline": timeline
    }