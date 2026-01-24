"""
Quick test script to verify the general conversation feature.
"""

from agents.intent import detect_intent, generate_general_conversation_response

def test_intent_detection():
    print("Testing Intent Detection:")
    print("=" * 50)
    
    # Test weather intent
    weather_msg = "What is the weather in Chennai?"
    weather_intent = detect_intent(weather_msg)
    print(f"Message: '{weather_msg}'")
    print(f"Intent: {weather_intent}\n")
    
    # Test stock intent
    stock_msg = "Tesla stock price"
    stock_intent = detect_intent(stock_msg)
    print(f"Message: '{stock_msg}'")
    print(f"Intent: {stock_intent}\n")
    
    # Test general conversation
    general_msg = "Hello, how are you?"
    general_intent = detect_intent(general_msg)
    print(f"Message: '{general_msg}'")
    print(f"Intent: {general_intent}\n")
    
    print("=" * 50)
    print("\nTesting General Conversation Response:")
    print("=" * 50)
    
    # Test general response generation
    test_messages = [
        "Hello!",
        "Tell me a joke",
        "What can you do?"
    ]
    
    for msg in test_messages:
        response = generate_general_conversation_response(msg)
        print(f"\nUser: {msg}")
        print(f"Bot: {response}")

if __name__ == "__main__":
    test_intent_detection()
