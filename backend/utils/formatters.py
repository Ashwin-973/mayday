"""
Utility functions for formatting API responses into user-friendly messages.
"""

from typing import Dict


def format_weather_response(data: Dict) -> str:
    """
    Format weather data into a user-friendly message.
    
    Args:
        data: Weather data dictionary from weather service
    
    Returns:
        Formatted string
    """
    return f"""Weather in {data['city']}, {data['country']}:
• Condition: {data['condition']}
• Temperature: {data['temperature']}°C (feels like {data['feels_like']}°C)
• Humidity: {data['humidity']}%
• Wind speed: {data['wind_speed']} m/s"""


def format_stock_response(data: Dict) -> str:
    """
    Format stock data into a user-friendly message.
    
    Args:
        data: Stock data dictionary from stock service
    
    Returns:
        Formatted string
    """
    sign = "+" if data['change'] >= 0 else ""
    market_status = "Open" if data['market_open'] else "Closed"
    
    return f"""{data['name']} ({data['symbol']}) is trading at ${data['price']:.2f} {data['currency']} on {data['exchange']}.
Today's change: {sign}{data['percent_change']:.2f}%.
Market status: {market_status}."""


def format_error_message(error: Exception, error_type: str = "general") -> str:
    """
    Format error messages to be user-friendly.
    Never expose raw API errors or internal details.
    
    Args:
        error: Exception object
        error_type: Type of error for specific handling
    
    Returns:
        User-friendly error message
    """
    if error_type == "city_not_found":
        return """I couldn't find weather data for that location.
Could you check the spelling or specify a nearby city?"""
    
    elif error_type == "free_tier_limit":
        return """I can't fetch live prices for NSE/BSE stocks with the free data plan.

I can provide:
• US markets like NASDAQ or NYSE
• Or general company information

Would you like to try a US exchange instead?"""
    
    elif error_type == "stock_not_found":
        return """I couldn't find that stock symbol.
Please check the symbol or try specifying the exchange (e.g., "TSLA on NASDAQ")."""
    
    elif error_type == "api_timeout":
        return "The service is taking too long to respond. Please try again in a moment."
    
    else:
        return "I encountered an error processing your request. Please try again."
