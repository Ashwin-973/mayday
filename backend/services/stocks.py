"""
Stock service using TwelveData API.
Fetches real-time stock quotes with proper error handling for free tier limitations.
"""

import requests
from typing import Dict
from core.config import get_settings


settings = get_settings()


class StockServiceError(Exception):
    """Base exception for stock service errors."""
    pass


class StockNotFoundError(StockServiceError):
    """Raised when stock symbol is not found."""
    pass


class FreeTierLimitError(StockServiceError):
    """Raised when free tier doesn't support the requested exchange."""
    pass


def get_stock_quote(symbol: str, exchange: str = "NASDAQ") -> Dict:
    """
    Get stock quote from TwelveData API.
    
    Args:
        symbol: Stock symbol (e.g., "TSLA", "AAPL")
        exchange: Exchange name (e.g., "NASDAQ", "NYSE", "NSE", "BSE")
    
    Returns:
        Dictionary with stock data:
        - symbol: Stock symbol
        - name: Company name
        - exchange: Exchange name
        - price: Current price
        - currency: Currency
        - change: Price change
        - percent_change: Percentage change
        - market_open: Boolean indicating if market is open
    
    Raises:
        StockNotFoundError: If stock symbol is invalid
        FreeTierLimitError: If free tier doesn't support the exchange
        StockServiceError: For other API errors
    """
    try:
        params = {
            "symbol": symbol.upper(),
            "exchange": exchange.upper(),
            "apikey": settings.twelvedata_api_key
        }
        
        response = requests.get(
            settings.twelvedata_quote_url,
            params=params,
            timeout=settings.api_timeout
        )
        response.raise_for_status()
        
        data = response.json()
        
        # Check for API error response
        if data.get("status") == "error":
            error_msg = data.get("message", "Unknown error")
            error_code = data.get("code", 500)
            
            # Check for free tier limitation
            if "Grow" in error_msg or "plan" in error_msg.lower():
                raise FreeTierLimitError(
                    f"Free tier doesn't support {exchange}. "
                    f"Try US exchanges like NASDAQ or NYSE."
                )
            
            # Check for invalid symbol
            if error_code == 404 or "not found" in error_msg.lower():
                raise StockNotFoundError(f"Stock '{symbol}' not found on {exchange}")
            
            raise StockServiceError(f"API error: {error_msg}")
        
        # Extract relevant stock data
        stock_data = {
            "symbol": data.get("symbol", symbol),
            "name": data.get("name", "Unknown"),
            "exchange": data.get("exchange", exchange),
            "price": float(data.get("close", 0)),
            "currency": data.get("currency", "USD"),
            "change": float(data.get("change", 0)),
            "percent_change": float(data.get("percent_change", 0)),
            "market_open": data.get("is_market_open", False),
        }
        
        return stock_data
        
    except (FreeTierLimitError, StockNotFoundError):
        raise
    except requests.exceptions.Timeout:
        raise StockServiceError("Stock service timeout")
    except requests.exceptions.RequestException as e:
        raise StockServiceError(f"Stock API request failed: {str(e)}")
    except (KeyError, ValueError) as e:
        raise StockServiceError(f"Invalid API response: {str(e)}")


def format_stock_symbol(company_name: str) -> str:
    """
    Try to convert common company names to stock symbols.
    This is a simple helper for common cases.
    
    Args:
        company_name: Company name (e.g., "Tesla", "Apple")
    
    Returns:
        Stock symbol (e.g., "TSLA", "AAPL")
    """
    # Common mappings
    mappings = {
        "tesla": "TSLA",
        "apple": "AAPL",
        "microsoft": "MSFT",
        "google": "GOOGL",
        "amazon": "AMZN",
        "meta": "META",
        "facebook": "META",
        "nvidia": "NVDA",
        "netflix": "NFLX",
    }
    
    return mappings.get(company_name.lower(), company_name.upper())
