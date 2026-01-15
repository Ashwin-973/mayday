def agent_loop(user_input, state):
    intent = classify_intent(user_input)

    if intent == "unknown":
        return "I can help with weather or stock prices."

    handle_new_intent(state, intent)

    slots = extract_slots(intent, user_input, llm)
    state["slots"].update(slots)

    missing = find_missing_slots(intent, state["slots"])

    if missing:
        return ask_clarification(missing[0])

    result = call_api(intent, state["slots"])
    state["intent_complete"] = True

    return format_response(result)
