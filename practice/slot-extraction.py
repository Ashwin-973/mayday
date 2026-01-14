from ollama import chat


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



tests = [
    # "tesla stock prices",
    # "microsoft at NASDAQ",
    # "random bs",
    "reliance at NSE"

]

for t in tests:
    print(t, ":", extract_stock_slots(t))
