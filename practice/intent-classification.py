from ollama import chat

def classify_intent(user_input):
    prompt = f"""
    Classify the user's query into ONE of the following intents:
    - weather
    - stock
    - unknown

    User query: "{user_input}"

    Respond ONLY with the intent name.
    """

    response = chat(
        model="llama3.2",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"].strip().lower()


# Try it
tests = [
    "Weather in Chennai",
    "Is it raining today?",
    "Tesla stock price",
    "TSLA price on NASDAQ",
    "tell me something random",
    "Edward Norton is the goat",
    "Is it sunny at the place where edward norton lives?"
]

for t in tests:
    print(t, ":", classify_intent(t))
