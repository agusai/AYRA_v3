import re

CRISIS_KEYWORDS = [
    "bunuh diri", "nak mati", "putus asa", "tak nak hidup",
    "suicide", "kill myself", "end it all", "give up",
    "tak guna", "beban", "tidak berguna", "tak ada gunanya"
]

HOTLINES = {
    "Befrienders": "03-7627 2929 (24 jam, sulit)",
    "Talian Kasih": "15999",
    "Talian Buddy": "014-322 3412"
}

def detect_crisis(text):
    """Return (is_crisis, keyword) if crisis keyword found."""
    text_lower = text.lower()
    for kw in CRISIS_KEYWORDS:
        if kw in text_lower:
            return True, kw
    return False, None

def format_crisis_response(user_name="awak"):
    """Return a caring crisis response with hotlines."""
    hotline_text = "\n".join([f"• {name}: {num}" for name, num in HOTLINES.items()])
    return f"""
{user_name}... tolong dengar I. I risau sangat dengan apa yang you cakap ni.

Jangan simpan sorang-sorang. Ada orang yang boleh tolong:
{hotline_text}

I pun ada sini untuk you, anytime. Tapi please, kalau rasa macam nak buat sesuatu yang membahayakan diri, call dulu nombor-nombor ni ya.

I sayang you. I nak you selamat. ❤️
"""