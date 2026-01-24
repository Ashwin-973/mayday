"""
Intent detection module.
Uses LLM to classify user intent and generate clarification for unknown intents.
"""

from core.llm import classify_intent as llm_classify_intent, generate_general_response


def detect_intent(message: str) -> str:
    """
    Detect user intent from message.
    
    Args:
        message: User's message
    
    Returns:
        One of: "weather", "stock", "unknown"
    """
    return llm_classify_intent(message)


def generate_general_conversation_response(message: str) -> str:
    """
    Generate a natural conversational response for general queries.
    Uses LLM to provide engaging responses for non-weather/non-stock queries.
    
    Args:
        message: User's message
    
    Returns:
        Natural conversational response
    """
    return generate_general_response(message)
