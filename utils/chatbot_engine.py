"""
Music Chatbot Engine for Streamlit
Hybrid: LLM for understanding + Engine for recommendation
"""

import os
import google.generativeai as genai
import pandas as pd

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
        # Gunakan model yang tersedia (flash 1.5 atau 2.0)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

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

        # 2. Get songs from engine (Menggunakan fungsi random yang baru)
        songs_df = self.engine.get_recommendations_by_mood(mood, n=5)

        # 3. Generate natural language response (LLM)
        prompt = f"""
        User sedang merasa {mood}.
        Buat respon singkat, ramah, dan empatik dalam Bahasa Indonesia yang cocok dengan perasaan tersebut.
        HANYA berikan 1-2 kalimat pengantar saja. 
        Jika user menyebutkan kegiatan spesifik (seperti seminar, ujian, kerja), berikan semangat khusus untuk kegiatan itu.
        Jangan menyebutkan judul lagu atau list lagu di sini.
        """        
      
        try:
            llm_response = self.model.generate_content(prompt)
            intro_text = llm_response.text.strip()
        except:
            intro_text = "Berikut adalah beberapa lagu yang mungkin cocok dengan suasana hati Anda:"

        # 4. GABUNGKAN TEKS DAN DAFTAR LAGU UNTUK TAMPILAN CHAT
        full_message = f"{intro_text}\n\n**Rekomendasi Lagu untuk Mood {mood}:**\n\n"
        
        songs_data = []
        if not songs_df.empty:
            for i, row in songs_df.iterrows():
                # Format Teks (Judul - Artis | Genre | Popularity)
                song_info = f"{i+1}. **{row['track_name']}** – {row['artists']} | Genre: {row['track_genre']} | Popularity: {row['popularity']}\n"
                full_message += song_info
                
                # Simpan data lagu untuk audio player
                songs_data.append({
                    "title": row["track_name"],
                    "artist": row["artists"],
                    "track_id": row["track_id"]
                })
        else:
            full_message += "Maaf, saya tidak menemukan lagu yang cocok saat ini."

        return {
            "text": full_message,  # Ini berisi teks ramah + daftar lagu
            "songs": songs_data    # Ini dikirim untuk kebutuhan Audio Player di UI
        }
