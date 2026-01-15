"""
Slot extraction and validation module.
Handles progressive slot filling with deterministic validation logic.
"""

from typing import Dict, List, Optional
from core.llm import extract_slots as llm_extract_slots
from utils.validators import normalize_exchange, normalize_stock_symbol


# Define required slots for each intent
REQUIRED_SLOTS = {
    "weather": ["location"],
    "stock": ["symbol", "exchange"],
}


def extract_slots(message: str, intent: str, existing_slots: Optional[Dict] = None) -> Dict:
    """
    Extract slots from user message using LLM.
    
    Args:
        message: User's message
        intent: Classified intent ("weather" or "stock")
        existing_slots: Previously extracted slots for progressive filling
    
    Returns:
        Dictionary of extracted slots
    """
    slots = llm_extract_slots(message, intent, existing_slots)
    
    # Normalize stock-related slots
    if intent == "stock":
        if "symbol" in slots and slots["symbol"]:
            slots["symbol"] = normalize_stock_symbol(slots["symbol"])
        if "exchange" in slots and slots["exchange"]:
            slots["exchange"] = normalize_exchange(slots["exchange"])
    
    return slots


def validate_slots(slots: Dict, intent: str) -> Dict:
    """
    Validate that all required slots are present and non-empty.
    This is DETERMINISTIC Python logic, not LLM-based.
    
    Args:
        slots: Extracted slots dictionary
        intent: Intent type ("weather" or "stock")
    
    Returns:
        Dictionary with:
        - valid: bool indicating if all required slots are present
        - missing: list of missing slot names
    """
    if intent not in REQUIRED_SLOTS:
        return {"valid": True, "missing": []}
    
    required = REQUIRED_SLOTS[intent]
    missing = []
    
    for slot_name in required:
        value = slots.get(slot_name)
        if not value or (isinstance(value, str) and not value.strip()):
            missing.append(slot_name)
    
    return {
        "valid": len(missing) == 0,
        "missing": missing
    }


def generate_clarification(missing_slots: List[str], intent: str) -> str:
    """
    Generate a targeted clarifying question for missing slots.
    Ask for ONE slot at a time to avoid overwhelming the user.
    
    Args:
        missing_slots: List of missing slot names
        intent: Intent type
    
    Returns:
        Clarification question
    """
    if not missing_slots:
        return ""
    
    # Ask for the first missing slot
    slot = missing_slots[0]
    
    if intent == "weather":
        if slot == "location":
            return "Which city would you like the weather for?"
    
    elif intent == "stock":
        if slot == "symbol":
            return "Which stock would you like to check? Please provide the symbol (e.g., TSLA for Tesla)."
        elif slot == "exchange":
            return "Which exchange? (e.g., NASDAQ, NYSE)"
    
    return "Could you provide more information?"


def get_missing_slot_count(missing_slots: List[str]) -> int:
    """
    Get the count of missing slots.
    
    Args:
        missing_slots: List of missing slot names
    
    Returns:
        Number of missing slots
    """
    return len(missing_slots)
