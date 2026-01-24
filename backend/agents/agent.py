"""
Main agent orchestrator.
Implements the conversation loop with intent detection, slot filling, and API calling.
"""

from typing import AsyncGenerator
from agents.intent import detect_intent, generate_general_conversation_response
from agents.slots import extract_slots, validate_slots, generate_clarification
from services.weather import (
    get_weather_for_city,
    CityNotFoundError,
    WeatherAPIError
)
from services.stocks import (
    get_stock_quote,
    FreeTierLimitError,
    StockNotFoundError,
    StockServiceError
)
from utils.formatters import (
    format_weather_response,
    format_stock_response,
    format_error_message
)
from core.memory import get_memory
from core.llm import format_response


async def process_message(session_id: str, message: str) -> AsyncGenerator[str, None]:
    """
    Main agent loop - processes user message and streams response.
    
    Flow:
    1. Load conversation state
    2. Detect intent
    3. Check for intent switch (reset slots if needed)
    4. Extract slots from message
    5. Validate slots
    6. If incomplete: ask clarifying question
    7. If complete: call API and format response
    8. Stream response chunks
    
    Args:
        session_id: Unique session identifier
        message: User's message
    
    Yields:
        Response chunks (for streaming)
    """
    memory = get_memory()
    state = memory.get_state(session_id)
    
    # Step 1: Detect intent
    intent = detect_intent(message)
    
    # Handle general conversation (unknown intent)
    if intent == "unknown":
        # Use LLM to generate natural conversational response
        response = generate_general_conversation_response(message)
        # Stream response word by word for smooth effect
        words = response.split()
        for i, word in enumerate(words):
            if i < len(words) - 1:
                yield word + " "
            else:
                yield word
        return
    
    # Step 2: Check for intent switch and update state
    if state.active_intent != intent:
        state.update_intent(intent)
    
    # Step 3: Extract slots from message (progressive filling)
    new_slots = extract_slots(message, intent, state.slots)
    state.update_slots(new_slots)
    
    # Step 4: Validate slots
    validation = validate_slots(state.slots, intent)
    
    if not validation["valid"]:
        # Slots incomplete - ask clarifying question
        clarification = generate_clarification(validation["missing"], intent)
        
        # Stream clarification
        words = clarification.split()
        for i, word in enumerate(words):
            if i < len(words) - 1:
                yield word + " "
            else:
                yield word
        return
    
    # Step 5: All slots filled - call appropriate API
    try:
        if intent == "weather":
            # Call weather API
            location = state.get_slot("location")
            weather_data = get_weather_for_city(location)
            
            # Format response using simple formatter
            response = format_weather_response(weather_data)
            
        elif intent == "stock":
            # Call stock API
            symbol = state.get_slot("symbol")
            exchange = state.get_slot("exchange", "NASDAQ")
            stock_data = get_stock_quote(symbol, exchange)
            
            # Format response using simple formatter
            response = format_stock_response(stock_data)
        
        else:
            response = "I'm not sure how to help with that."
        
        # Reset state after successful response
        state.reset_slots()
        
        # Stream response
        words = response.split()
        for i, word in enumerate(words):
            if i < len(words) - 1:
                yield word + " "
            else:
                yield word
    
    except CityNotFoundError as e:
        # City not found error
        response = format_error_message(e, "city_not_found")
        state.reset_slots()  # Reset so user can try again
        
        words = response.split()
        for i, word in enumerate(words):
            if i < len(words) - 1:
                yield word + " "
            else:
                yield word
    
    except FreeTierLimitError as e:
        # Free tier limitation (NSE/BSE)
        response = format_error_message(e, "free_tier_limit")
        state.reset_slots()
        
        words = response.split()
        for i, word in enumerate(words):
            if i < len(words) - 1:
                yield word + " "
            else:
                yield word
    
    except StockNotFoundError as e:
        # Stock not found
        response = format_error_message(e, "stock_not_found")
        state.reset_slots()
        
        words = response.split()
        for i, word in enumerate(words):
            if i < len(words) - 1:
                yield word + " "
            else:
                yield word
    
    except (WeatherAPIError, StockServiceError) as e:
        # General API errors
        response = format_error_message(e, "general")
        state.reset_slots()
        
        words = response.split()
        for i, word in enumerate(words):
            if i < len(words) - 1:
                yield word + " "
            else:
                yield word
    
    except Exception as e:
        # Unexpected errors
        print(f"Unexpected error: {e}")
        response = "I encountered an unexpected error. Please try again."
        state.reset_slots()
        
        words = response.split()
        for i, word in enumerate(words):
            if i < len(words) - 1:
                yield word + " "
            else:
                yield word
