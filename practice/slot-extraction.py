from ollama import chat
import json


def extract_stock_slots(user_input):
    prompt = f"""
    Extract the following fields from the user query.
    If missing, return null.

    Fields:
    - symbol
    - exchange

    User query: "{user_input}"

    Respond in JSON only.
    """

    response = chat(
        model="llama3.2",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]



# while required_slots_missing:
#     ask for ONE missing slot
#     wait for user response
#     validate slot


def extract_slots(intent, user_input):
    if intent == "stock":
        prompt = f"""
        Extract stock-related fields from the user query.
        Fields:
        - symbol
        - exchange

        If missing or unknown, return null.
        Respond ONLY in JSON.

        Query: "{user_input}"
        """

    elif intent == "weather":
        prompt = f"""
        Extract weather-related fields.
        Fields:
        - location

        Respond ONLY in JSON.

        Query: "{user_input}"
        """

    else : 
        return "Sorry, I can help with weather or stock prices. Please clarify."


    response = chat(
        model="llama3.2",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]


tests = [
    # "tesla stock prices",
    # "microsoft at NASDAQ",
    # "random bs",
    "reliance at NSE"

]

# for t in tests:
#     print(t, ":", extract_stock_slots(t))


print(extract_slots("weather","is it raining in texas?"))