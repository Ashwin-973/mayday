"""
Intent detection module.
Uses LLM to classify user intent and generate clarification for unknown intents.
"""

from core.llm import classify_intent as llm_classify_intent


def detect_intent(message: str) -> str:
    """
    Detect user intent from message.
    
    Args:
        message: User's message
    
    Returns:
        One of: "weather", "stock", "unknown"
    """
    return llm_classify_intent(message)


def generate_unknown_intent_response() -> str:
    """
    Generate a guided clarification message for unknown intents.
    
    Returns:
        Clarification message
    """
    return "I can help you with weather forecasts or stock prices. Which would you like?"
