"""
LLM interface using Ollama with LLaMA 3.2.
LLM is used ONLY for:
1. Intent classification
2. Slot extraction (with LangChain for structured output)
3. Response phrasing

The LLM NEVER calls APIs directly - that's deterministic Python code.
"""

import json
from typing import Dict, Optional
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from core.config import get_settings


settings = get_settings()


# Pydantic models for structured output
class IntentClassification(BaseModel):
    """Intent classification result."""
    intent: str = Field(description="One of: weather, stock, unknown")
    confidence: float = Field(description="Confidence score 0.0 to 1.0")


class WeatherSlots(BaseModel):
    """Extracted slots for weather intent."""
    location: Optional[str] = Field(None, description="City name")


class StockSlots(BaseModel):
    """Extracted slots for stock intent."""
    symbol: Optional[str] = Field(None, description="Stock symbol (e.g., TSLA)")
    exchange: Optional[str] = Field(None, description="Exchange (e.g., NASDAQ, NYSE)")


def get_llm():
    """Get Ollama LLM instance."""
    return ChatOllama(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        temperature=0.1,  # Low temperature for deterministic behavior
    )


def classify_intent(message: str) -> str:
    """
    Classify user intent using LLM.
    
    Returns:
        One of: "weather", "stock", "unknown"
    """
    llm = get_llm()
    parser = JsonOutputParser(pydantic_object=IntentClassification)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an intent classifier. Classify user messages into one of these intents:

- weather: User wants weather information for a location
- stock: User wants stock price or market data
- unknown: Anything else

Examples:
- "Weather in Chennai" -> weather
- "What's the temperature in London?" -> weather
- "Tesla stock price" -> stock
- "How is AAPL doing?" -> stock
- "Tell me a joke" -> unknown
- "Hello" -> unknown

Respond ONLY with valid JSON matching this format:
{{"intent": "weather|stock|unknown", "confidence": 0.0-1.0}}"""),
        ("user", "{message}")
    ])
    
    chain = prompt | llm | parser
    
    try:
        result = chain.invoke({"message": message})
        return result.get("intent", "unknown")
    except Exception as e:
        print(f"Intent classification error: {e}")
        return "unknown"


def extract_slots(message: str, intent: str, existing_slots: Optional[Dict] = None) -> Dict:
    """
    Extract slots from user message using LLM.
    
    Args:
        message: User's message
        intent: Classified intent ("weather" or "stock")
        existing_slots: Previously extracted slots (for progressive filling)
    
    Returns:
        Dictionary of extracted slots
    """
    if intent not in ["weather", "stock"]:
        return {}
    
    llm = get_llm()
    existing_slots = existing_slots or {}
    
    if intent == "weather":
        parser = JsonOutputParser(pydantic_object=WeatherSlots)
        slot_description = """Extract the LOCATION (city name) from the message.
If no location is mentioned, return null for location.

Examples:
- "Weather in Chennai" -> {{"location": "Chennai"}}
- "What's the weather like in New York?" -> {{"location": "New York"}}
- "How's the weather?" -> {{"location": null}}
- "Tell me" -> {{"location": null}}"""
        
        # Format existing slots without curly braces to avoid LangChain template variable conflicts
        if existing_slots:
            slots_str = ", ".join([f"{k}={v}" for k, v in existing_slots.items()])
            context = f"\nPreviously extracted slots: {slots_str}"
        else:
            context = ""
        
    else:  # stock
        parser = JsonOutputParser(pydantic_object=StockSlots)
        slot_description = """Extract the SYMBOL (stock ticker) and EXCHANGE from the message.
If not mentioned, return null.

Common exchanges: NASDAQ, NYSE, NSE, BSE

Examples:
- "Tesla stock price" -> {{"symbol": "TSLA", "exchange": null}}
- "AAPL on NASDAQ" -> {{"symbol": "AAPL", "exchange": "NASDAQ"}}
- "Microsoft stock" -> {{"symbol": "MSFT", "exchange": null}}
- "Reliance on NSE" -> {{"symbol": "RELIANCE", "exchange": "NSE"}}
- "Stock price" -> {{"symbol": null, "exchange": null}}"""
        
        # Format existing slots without curly braces to avoid LangChain template variable conflicts
        if existing_slots:
            slots_str = ", ".join([f"{k}={v}" for k, v in existing_slots.items()])
            context = f"\nPreviously extracted slots: {slots_str}"
        else:
            context = ""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"{slot_description}{context}\n\nRespond ONLY with valid JSON."),
        ("user", "{message}")
    ])
    
    chain = prompt | llm | parser
    
    try:
        result = chain.invoke({"message": message})
        # Merge with existing slots, new values take precedence
        merged = {**existing_slots, **{k: v for k, v in result.items() if v is not None}}
        return merged
    except Exception as e:
        print(f"Slot extraction error: {e}")
        return existing_slots


def generate_general_response(message: str) -> str:
    """
    Generate a natural conversational response for general queries using LLM.
    Used when the user's message doesn't match weather or stock intents.
    
    Args:
        message: User's message
    
    Returns:
        Natural conversational response
    """
    llm = get_llm()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a friendly and helpful AI assistant. 
Engage in natural conversation with the user. Be concise, warm, and helpful.

You can help with:
- General conversation and questions
- Answering questions about various topics
- Providing information and assistance

You also have specialized capabilities for:
- Weather forecasts (just ask about weather in any city)
- Stock prices (just ask about any stock symbol)

But for now, just respond naturally to the user's message without pushing these features."""),
        ("user", "{message}")
    ])
    
    try:
        chain = prompt | llm
        response = chain.invoke({"message": message})
        return response.content.strip()
    except Exception as e:
        print(f"General response generation error: {e}")
        return "I'm here to chat! I can also help you with weather forecasts or stock prices if you need them."


def format_response(data: Dict, response_type: str) -> str:
    """
    Format API response data into natural language using LLM.
    
    Args:
        data: API response data
        response_type: "weather_success", "stock_success", "weather_error", etc.
    
    Returns:
        Natural language response
    """
    llm = get_llm()
    
    if response_type == "weather_success":
        prompt = f"""Format this weather data into a friendly, natural response.
Include: condition, temperature, feels like, humidity, wind speed.

Data: {json.dumps(data, indent=2)}

Format like:
"Weather in [City], [Country]:
• Condition: [condition]
• Temperature: [temp]°C (feels like [feels_like]°C)
• Humidity: [humidity]%
• Wind speed: [wind_speed] m/s"

Be concise and user-friendly."""
        
    elif response_type == "stock_success":
        prompt = f"""Format this stock data into a friendly, natural response.
Include: company name, symbol, price, change, market status.

Data: {json.dumps(data, indent=2)}

Format like:
"[Company] ([SYMBOL]) is trading at $[price] [currency] on [exchange].
Today's change: [+/-][change]%.
Market status: [Open/Closed]."

Be concise and user-friendly."""
        
    elif response_type == "city_not_found":
        return """I couldn't find weather data for that location.
Could you check the spelling or specify a nearby city?"""
        
    elif response_type == "free_tier_limit":
        return """I can't fetch live prices for NSE/BSE stocks with the free data plan.

I can provide:
• US markets like NASDAQ or NYSE
• Or general company information

Would you like to try a US exchange instead?"""
        
    elif response_type == "stock_not_found":
        return """I couldn't find that stock symbol.
Please check the symbol or try specifying the exchange (e.g., "TSLA on NASDAQ")."""
        
    else:
        return "I encountered an error processing your request. Please try again."
    
    try:
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        print(f"Response formatting error: {e}")
        # Fallback to simple formatting
        if response_type == "weather_success":
            return f"Weather in {data.get('city', 'Unknown')}: {data.get('temperature', 'N/A')}°C, {data.get('condition', 'N/A')}"
        elif response_type == "stock_success":
            return f"{data.get('symbol', 'Stock')}: ${data.get('price', 'N/A')} ({data.get('change', 'N/A')}%)"
        return "Response formatting failed."
