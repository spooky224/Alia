# orchestrator/orchestrator.py

from presentation_agent.builder import build_presentation
from presentation_agent.product_resolver import resolve_product


# =================================================
# INTENT DETECTION
# =================================================
def detect_intent(text: str) -> str:
    """
    Detect high-level user intent.
    """
    text = text.lower()

    presentation_triggers = [
        "presentation",
        "present",
        "show",
        "introduce",
        "explain",
        "overview",
        "talk about",
    ]

    if any(trigger in text for trigger in presentation_triggers):
        return "presentation"

    return "speech"


# =================================================
# MAIN ENTRYPOINT
# =================================================
def handle_message(message: str) -> dict:
    """
    Central decision-making unit.
    Responsible for:
    - intent detection
    - product resolution
    - orchestration choice
    """

    if not message or not message.strip():
        return {
            "mode": "speech",
            "speech_text": "I didn't catch that. Could you please repeat?"
        }

    # Normalize once
    message_clean = message.strip()

    # -------------------------
    # Detect intent + product
    # -------------------------
    intent = detect_intent(message_clean)
    product_id = resolve_product(message_clean)

    # -------------------------
    # Presentation intent
    # -------------------------
    if intent == "presentation" and product_id:
        presentation = build_presentation(product_id)

        return {
            "mode": "presentation",
            "product": product_id,
            "category": presentation["category"],
            "speech_text": presentation["speech_text"],
            "timeline": presentation["timeline"],
        }

    # -------------------------
    # Presentation requested but product unknown
    # -------------------------
    if intent == "presentation" and not product_id:
        return {
            "mode": "speech",
            "speech_text": (
                "I understand you want a presentation, "
                "but I couldn't identify the product."
            )
        }

    # -------------------------
    # Default: plain speech
    # -------------------------
    return {
        "mode": "speech",
        "speech_text": message_clean
    }