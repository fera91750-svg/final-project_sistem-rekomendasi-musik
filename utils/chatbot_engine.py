"""
Music Chatbot Engine for Streamlit
Hybrid: LLM for understanding + Engine for recommendation
"""

import os
import google.generativeai as genai


# =========================
# API KEY CONFIG
# =========================
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise RuntimeError(
        "GOOGLE_API_KEY tidak ditemukan. "
        "Set di Streamlit Cloud → Settings → Secrets"
    )

genai.configure(api_key=GOOGLE_API_KEY)


class MusicChatbot:
    def __init__(self, music_engine):
        self.engine = music_engine
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    # =========================
    # SIMPLE MOOD DETECTION
    # =========================
    def detect_mood(self, text: str) -> str:
        text = text.lower()

        if any(k in text for k in ["sedih", "galau", "kecewa", "nangis"]):
            return "Sad"
        if any(k in text for k in ["senang", "bahagia", "happy"]):
            return "Happy"
        if any(k in text for k in ["tenang", "santai", "relax", "calm"]):
            return "Calm"
        if any(k in text for k in ["marah", "emosi", "stress", "tegang"]):
            return "Tense"

        return "Happy"

    # =========================
    # CHAT MAIN FUNCTION
    # =========================
    def chat(self, user_text: str, thread_id=None):
        # 1. Detect mood
        mood = self.detect_mood(user_text)

        # 2. Get songs from engine
        songs_df = self.engine.get_recommendations_by_mood(mood, n=5)

        songs = []
        for _, row in songs_df.iterrows():
            songs.append({
                "title": row["track_name"],
                "artist": row["artists"],
                "album": row["album_name"],
                "genre": row["track_genre"],
                "popularity": row["popularity"],
                "track_id": row["track_id"]
            })

        # 3. Generate natural language response (LLM)
        prompt = f"""
        User merasa {mood}.
        Buat respon singkat, ramah, dan empatik dalam Bahasa Indonesia.
        Jangan rekomendasikan lagu di teks.
        """

        response = self.model.generate_content(prompt)

        return {
            "text": response.text.strip(),
            "songs": songs
        }
