# presentation_agent/product_resolver.py

import json
import os
import unicodedata


PRODUCTS_PATH = os.path.join(
    os.path.dirname(__file__),
    "products.json"
)

with open(PRODUCTS_PATH, "r", encoding="utf-8") as f:
    PRODUCTS = json.load(f)


def normalize(text: str) -> str:
    """
    Lowercase + remove accents + strip.
    """
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text


def resolve_product(text: str) -> str | None:
    """
    Identify product from free-form user input.
    """
    text_norm = normalize(text)

    for product_id, meta in PRODUCTS.items():
        # Match display name
        if normalize(meta["display_name"]) in text_norm:
            return product_id

        # Match aliases
        for alias in meta.get("aliases", []):
            if normalize(alias) in text_norm:
                return product_id

    return None