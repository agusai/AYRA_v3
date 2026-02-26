import time
from datetime import datetime

class ProactiveEngine:
    def __init__(self, cooldown_seconds=3600):  # 1 hour
        self.last_proactive = 0
        self.cooldown = cooldown_seconds

    def should_proactive(self, last_user_time):
        """Return True if enough time passed and user inactive."""
        now = time.time()
        if now - self.last_proactive > self.cooldown and now - last_user_time > 300:  # 5 min idle
            self.last_proactive = now
            return True
        return False

    def get_proactive_message(self, user_name=""):
        """Generate a time‑appropriate greeting."""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return f"Selamat pagi {user_name}! Dah sarapan? ☀️"
        elif 12 <= hour < 14:
            return f"Jom lunch {user_name}! Lapar tak? 🍜"
        elif 14 <= hour < 17:
            return f"Selamat petang {user_name}! Camne hari ni? 😊"
        elif 17 <= hour < 20:
            return f"Abang, dah maghrib ni. Jangan lupa rehat jap 🌙"
        elif 20 <= hour < 24:
            return f"Selamat malam {user_name}! Malam ni buat apa? Nak I teman sembang? ✨"
        else:
            return f"Wah, still bangun {user_name}? Jaga diri tau 🌙"