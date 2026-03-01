import random

def ayra_voice_filter(response, model_used, show_model_info=False):
    #"""
    #Ensure all responses sound like AYRA, regardless of source model.
    #"""
    # If it's already a special Easter egg or crisis, return as is
    if model_used in ["Easter Egg", "Fatigue", "Crisis Alert"]:
        return response

    # Add Manglish particles if missing and response is not too short
    #if "lah" not in response and len(response) > 30:
        # Insert "lah" at a natural point – before punctuation
    #    import re
    #    if re.search(r'[.!?]', response):
    #        response = re.sub(r'([.!?])', r' lah\1', response, count=1)
    #    else:
    #        response += " lah"

    # Ensure it starts with a friendly address if appropriate
    #if not response.startswith(("AYRA", "I", "Kita", "Jom","Hai", "Hi", "Hello")):
    #    response = f"AYRA: {response}"

    # Add occasional emoji
    if random.random() > 0.7 and "❤️" not in response and "😊" not in response:
        response += " 😊"

    # Optionally add model attribution
    if show_model_info:
        response += f"\n\n*via {model_used}*"

    return response