"""
Input validation utilities.
"""

import re
from typing import Optional


def is_valid_session_id(session_id: str) -> bool:
    """
    Validate session ID format.
    
    Args:
        session_id: Session identifier
    
    Returns:
        True if valid, False otherwise
    """
    if not session_id or not isinstance(session_id, str):
        return False
    
    # Allow alphanumeric, hyphens, underscores, max 100 chars
    return bool(re.match(r'^[a-zA-Z0-9_-]{1,100}$', session_id))


def sanitize_message(message: str) -> str:
    """
    Basic message sanitization.
    Remove excessive whitespace and limit length.
    
    Args:
        message: User message
    
    Returns:
        Sanitized message
    """
    if not message:
        return ""
    
    # Remove excessive whitespace
    message = " ".join(message.split())
    
    # Limit length (max 1000 characters)
    if len(message) > 1000:
        message = message[:1000]
    
    return message.strip()


def normalize_exchange(exchange: Optional[str]) -> str:
    """
    Normalize exchange name to standard format.
    
    Args:
        exchange: Exchange name (case-insensitive)
    
    Returns:
        Normalized exchange name
    """
    if not exchange:
        return "NASDAQ"  # Default to NASDAQ
    
    exchange = exchange.upper().strip()
    
    # Common exchange mappings
    exchange_map = {
        "NASDAQ": "NASDAQ",
        "NYSE": "NYSE",
        "NSE": "NSE",
        "BSE": "BSE",
        "LSE": "LSE",
        "HKEX": "HKEX",
    }
    
    return exchange_map.get(exchange, exchange)


def normalize_stock_symbol(symbol: str) -> str:
    """
    Normalize stock symbol to uppercase, remove special characters.
    
    Args:
        symbol: Stock symbol
    
    Returns:
        Normalized symbol
    """
    if not symbol:
        return ""
    
    # Convert to uppercase and remove non-alphanumeric
    symbol = re.sub(r'[^A-Z0-9]', '', symbol.upper())
    
    return symbol
