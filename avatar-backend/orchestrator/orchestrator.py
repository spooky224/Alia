# orchestrator/orchestrator.py

import re
from presentation_agent.builder import build_presentation


# =================================================
# INTENT HANDLERS
# =================================================
def detect_presentation_intent(text: str) -> str | None:
    """
    Detect if the user is asking for a product presentation.
    Returns normalized product id or None.
    """
    text = text.lower().strip()

    keywords = [
        "presentation",
        "present",
        "show me",
        "introduce",
        "explain",
    ]

    if not any(k in text for k in keywords):
        return None

    match = re.search(r"for\s+(.+)", text)
    if not match:
        return None

    product = match.group(1).strip()
    product_id = product.replace(" ", "_").replace("-", "_")

    return product_id


# =================================================
# MAIN ENTRYPOINT
# =================================================
def handle_message(message: str) -> dict:
    """
    Central decision-making unit.
    """
    if not message or not message.strip():
        return {
            "mode": "speech",
            "speech_text": "I didn't catch that. Could you please repeat?"
        }

    # -------------------------
    # Presentation intent
    # -------------------------
    product_id = detect_presentation_intent(message)
    if product_id:
        presentation = build_presentation(product_id)

        return {
            "mode": "presentation",
            "speech_text": presentation["speech_text"],
            "timeline": presentation["timeline"],
        }

    # -------------------------
    # Default: plain speech
    # -------------------------
    return {
        "mode": "speech",
        "speech_text": message
    }