# presentation_agent/product_resolver.py

import json
import os
import unicodedata
import re


PRODUCTS_PATH = os.path.join(
    os.path.dirname(__file__),
    "products.json"
)

with open(PRODUCTS_PATH, "r", encoding="utf-8") as f:
    PRODUCTS = json.load(f)


# ----------------------------
# Normalization utilities
# ----------------------------

STOPWORDS = {
    "can", "you", "please", "generate", "presentation", "present",
    "for", "a", "an", "the", "of", "do", "does", "want", "would",
    "like", "me", "i", "need", "show", "make",
    # French
    "peux", "peut", "vous", "svp", "sil", "te", "plait",
    "faire", "generer", "presentation", "presenter", "sur",
}


def normalize(text: str) -> str:
    """
    Strong normalization:
    - lowercase
    - remove accents
    - remove punctuation
    - collapse whitespace
    """
    text = text.lower().strip()

    # Remove accents
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")

    # Remove punctuation
    text = re.sub(r"[^\w\s]", " ", text)

    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def tokenize(text: str) -> set[str]:
    """
    Tokenize normalized text and drop stopwords.
    """
    return {
        token
        for token in text.split()
        if token and token not in STOPWORDS
    }


# ----------------------------
# Product resolution
# ----------------------------

def resolve_product(text: str) -> str | None:
    """
    Identify product from free-form user input.

    Strategy (safe escalation):
    1. Exact substring match on display name
    2. Exact substring match on aliases
    3. Token overlap scoring (>= 2 shared tokens)
    """
    text_norm = normalize(text)
    text_tokens = tokenize(text_norm)

    # ------------------------
    # 1️⃣ Exact display name match (UNCHANGED behavior)
    # ------------------------
    for product_id, meta in PRODUCTS.items():
        display_norm = normalize(meta["display_name"])
        if display_norm in text_norm:
            return product_id

    # ------------------------
    # 2️⃣ Exact alias match (UNCHANGED behavior)
    # ------------------------
    for product_id, meta in PRODUCTS.items():
        for alias in meta.get("aliases", []):
            alias_norm = normalize(alias)
            if alias_norm in text_norm:
                return product_id

    # ------------------------
    # 3️⃣ Token overlap matching (NEW, conservative)
    # ------------------------
    best_match = None
    best_score = 0

    for product_id, meta in PRODUCTS.items():
        # Collect tokens from display name + aliases
        name_tokens = tokenize(normalize(meta["display_name"]))
        alias_tokens = set()

        for alias in meta.get("aliases", []):
            alias_tokens |= tokenize(normalize(alias))

        product_tokens = name_tokens | alias_tokens

        if not product_tokens:
            continue

        overlap = text_tokens & product_tokens
        score = len(overlap)

        # Require at least 2 shared tokens to avoid false positives
        if score >= 2 and score > best_score:
            best_match = product_id
            best_score = score

    return best_match