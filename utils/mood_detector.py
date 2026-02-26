import re
import threading
import time
import json
import os
from collections import deque

# Sentiment lexicon (optional, we can use TextBlob)
from textblob import TextBlob

class MoodDetector:
    def __init__(self, window_size=5):
        self.window_size = window_size
        self.scores = deque(maxlen=window_size)
        self.current_mood = "Lembut"  # default
        self.mood_history = []
        self.locked = False
        self.suggestion_file = "temp_mood_suggestion.json"

    def analyze_sentiment(self, text):
        """Return sentiment polarity between -1 and 1."""
        blob = TextBlob(text)
        return blob.sentiment.polarity

    def map_sentiment_to_mood(self, sentiment):
        """Map sentiment score to one of 4 moods."""
        if sentiment < -0.5:
            return "Memujuk"   # very negative -> need comfort
        elif sentiment < -0.1:
            return "Lembut"     # slightly negative
        elif sentiment < 0.3:
            return "Bijak"      # neutral/positive -> analytical
        else:
            return "Tegas"      # very positive -> energetic/direct

    def update_from_text(self, text):
        """Update mood based on user text (runs in background)."""
        sentiment = self.analyze_sentiment(text)
        self.scores.append(sentiment)
        avg_sentiment = sum(self.scores) / len(self.scores)
        suggested_mood = self.map_sentiment_to_mood(avg_sentiment)

        # Write suggestion to temp file (for main thread to read)
        suggestion = {
            "mood": suggested_mood,
            "confidence": abs(avg_sentiment),
            "timestamp": time.time()
        }
        with open(self.suggestion_file, 'w') as f:
            json.dump(suggestion, f)

    def check_suggestion(self):
        """Read suggestion file and return if exists (main thread)."""
        try:
            if os.path.exists(self.suggestion_file):
                with open(self.suggestion_file, 'r') as f:
                    data = json.load(f)
                # Only consider if less than 2 seconds old
                if time.time() - data['timestamp'] < 2:
                    os.remove(self.suggestion_file)
                    return data
                else:
                    os.remove(self.suggestion_file)
        except:
            pass
        return None

    def apply_suggestion(self, suggestion):
        """Change current mood if not locked."""
        if not self.locked and suggestion:
            self.mood_history.append({
                "from": self.current_mood,
                "to": suggestion['mood'],
                "time": time.strftime("%H:%M"),
                "confidence": suggestion['confidence']
            })
            self.current_mood = suggestion['mood']
            return True
        return False

    def get_mood_prompt(self):
        """Return system prompt fragment for current mood."""
        prompts = {
            "Tegas": "Kau dalam mode TEGAS. Bercakap dengan tegas, tepat, terus terang. Fokus pada solusi cepat.",
            "Bijak": "Kau dalam mode BIJAK. Guna logik, data, analisis mendalam. Struktur jawapan dengan teratur.",
            "Lembut": "Kau dalam mode LEMBUT. Bercakap lembut, penuh empati. Tanya khabar, tawarkan sokongan.",
            "Memujuk": "Kau dalam mode MEMUJUK. Beri motivasi, ingatkan kejayaan lepas, semangatkan user."
        }
        return prompts.get(self.current_mood, prompts["Lembut"])