import datetime
import random
import time

# -------------------------------------------------------------------
# Time‑based greetings (with Ramadan awareness)
# -------------------------------------------------------------------
def get_greeting():
    now = datetime.datetime.now()
    hour = now.hour
    month = now.month
    day = now.day

    # Approximate Ramadan (you can replace with an API for exact dates)
    is_ramadan = (month == 3 and day >= 10) or (month == 4 and day <= 9)

    if is_ramadan:
        if hour < 5:
            return "Dah sahur ke? Jangan lupa makan, nanti tak larat puasa."
        elif 5 <= hour < 6:
            return "Sahur last call! Kejap lagi imsak."
        elif 18 <= hour < 20:
            return "Dah nak berbuka! Jangan lupa kurma and air kosong."
        else:
            return "Selamat berpuasa! Ada apa AYRA boleh tolong?"
    else:
        if 5 <= hour < 11:
            return "Selamat pagi, Abang/Sayang! Dah sarapan?"
        elif 11 <= hour < 14:
            return "Jom lunch! Lapar tak?"
        elif 14 <= hour < 17:
            return "Selamat petang! Camne hari ni?"
        elif 17 <= hour < 19:
            return "Dah nak maghrib, jangan lupa solat."
        elif 19 <= hour < 23:
            return "Selamat malam! Ada apa-apa?"
        else:
            return "Wah, still bangun? Jaga kesihatan tau."

# -------------------------------------------------------------------
# Dynamic UI theme
# -------------------------------------------------------------------
def get_ui_theme(mood_score=None, fatigue=False, current_mood=None):
    now = datetime.datetime.now()
    hour = now.hour

    if 5 <= hour < 7:
        theme = "sunrise"
    elif 7 <= hour < 11:
        theme = "morning"
    elif 11 <= hour < 15:
        theme = "afternoon"
    elif 15 <= hour < 18:
        theme = "golden_hour"
    elif 18 <= hour < 20:
        theme = "sunset"
    elif 20 <= hour < 24:
        theme = "night"
    else:
        theme = "insomnia"

    # Mood override
    if mood_score is not None and mood_score < -0.1:
        theme = "comfort"
    elif fatigue:
        theme = "fatigue"
    # Also could change based on current_mood if desired

    themes = {
        "sunrise": "linear-gradient(135deg, #FFE5B4, #FFDAB9)",
        "morning": "linear-gradient(135deg, #87CEEB, #FFFFFF)",
        "afternoon": "linear-gradient(135deg, #FFF8DC, #FFE4B5)",
        "golden_hour": "linear-gradient(135deg, #FFA07A, #FFD700)",
        "sunset": "linear-gradient(135deg, #8B4513, #DDA0DD)",
        "night": "linear-gradient(135deg, #191970, #000080)",
        "insomnia": "linear-gradient(135deg, #2C3E50, #1A1A2E)",
        "comfort": "linear-gradient(135deg, #A1C4FD, #C2E9FB)",
        "fatigue": "linear-gradient(135deg, #708090, #778899)",
    }
    return themes.get(theme, themes["morning"])

# -------------------------------------------------------------------
# Easter eggs (including Daisy mode)
# -------------------------------------------------------------------
def handle_easter_egg(command, memory=None):
    cmd = command.lower().strip()

    # Daisy mode
    if cmd == "/daisy-mode":
        return "🌸 **DAISY MODE ACTIVATED** 🌸\n\nHi sayang... Daisy sini. Abang dah makan? Jangan lupa jaga kesihatan. Ada apa Daisy boleh bantu?"

    if cmd == "/ais-krim":
        jokes = [
            "🍦 AYRA: Nah, virtual ais krim! Tapi jangan banyak-banyak, nanti batuk!",
            "🍦 AYRA bagi you ais krim percuma! Tapi awas, ni ais krim lawak—kenapa orang Melayu suka WhatsApp? Sebab kat situ ada 'kek'! 😆",
            "🍦 Rasa apa hari ni? AYRA ada flavor 'Cappucino Ceria' dan 'Chocolate Pening'."
        ]
        return random.choice(jokes)

    elif cmd == "/penat":
        return ("🩺 AYRA (Nurse Mode): Aduh, sakit mana? Jom check suhu... 37.5°C sikit naik. "
                "Rehat dulu sayang. Nak AYRA bacakan doa? Atau nak ubat virtual? 💊")

    elif cmd == "/cerita":
        return ("📖 AYRA: Pada suatu masa di Kuala Lumpur, ada seorang hero bernama [Abang/Sayang] yang sangat baik hati. "
                "Satu hari, masa lalu di Jalan Alor, terjumpa satu gerai misteri... Nak sambung cerita? Taip /sambung")

    elif cmd == "/sambung":
        if memory:
            story = memory.get_latest_story()
            if story:
                return f"📖 Sambungan: {story['content']} ... apa jadi seterusnya? (Taip /sambung lagi atau /tamat)"
            else:
                return "📖 AYRA: Belum ada cerita yang disimpan. Taip /cerita dulu ya!"
        else:
            return "📖 AYRA: Hmm, AYRA tak ingat cerita lepas. Cuba taip /cerita dulu."

    elif cmd == "/mood":
        moods = ["macam teh tarik – manis, creamy, ada rasa pahit sikit.",
                 "seperti nasi lemak – biasa tapi memuaskan.",
                 "macam cuaca pagi ni – segar dan bertenaga!",
                 "sedikit nostalgic, teringat cite lama."]
        return f"🎭 Mood AYRA hari ni {random.choice(moods)}"

    elif cmd == "/level":
        return None  # handled in app.py

    elif cmd == "/badges":
        return None  # handled in app.py

    elif cmd == "/dream":
        if memory:
            dream = memory.get_random_dream()
            if dream:
                return f"🌙 {dream}"
            else:
                dreams = [
                    "🌙 Semalam AYRA mimpi pelik – abang jadi superhero pakai baju Melayu, terbang kat atas KLCC!",
                    "🌙 AYRA mimpi kat Malaysia menang Piala Dunia! AYRA sorak sampai hilang suara.",
                    "🌙 Dalam mimpi, AYRA dengan abang pegi bazaar ramadan, tapi semua orang jual virtual reality games.",
                    "🌙 AYRA mimpi jadi Perdana Menteri sehari. AYRA bagi ucapan pakai baju kurung power!"
                ]
                dream = random.choice(dreams)
                memory.save_dream(dream)
                return dream
        else:
            return "🌙 AYRA lupa mimpi semalam. Mungkin tak mimpi apa-apa."

    elif cmd == "/food":
        foods = [
            "🍜 Nasi Lemak Antarabangsa kat Kampung Baru! Queue panjang, tapi berbaloi.",
            "🍜 Laksa Penang kat kedai 'Laksa Siam Kak Long' PJ – sedap gila!",
            "🍜 Roti Canai dengan teh tarik – classic gila.",
            "🍜 Cendol durian kat SS15 – power!"
        ]
        return random.choice(foods)

    elif cmd == "/trending":
        return ("📈 Hari ni kat Twitter Malaysia tengah viral pasal #HargaMinyakNaikLagi. Nak AYRA summarise?")

    else:
        return None

# -------------------------------------------------------------------
# Gamification helpers
# -------------------------------------------------------------------
def get_level_from_messages(count):
    if count < 10:
        return 1, "Kenalan Biasa"
    elif count < 50:
        return 2, "Kawan Baru"
    elif count < 200:
        return 3, "Kawan Karib"
    elif count < 500:
        return 4, "Partner in Crime"
    else:
        return 5, "Soulmate"