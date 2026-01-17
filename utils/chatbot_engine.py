"""
Music Chatbot Engine for Streamlit
Hybrid: LLM for understanding + Engine for recommendation (Chill Version)
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
        # Menggunakan model Gemini 1.5 Flash yang responsif
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    # =========================
    # CHAT MAIN FUNCTION
    # =========================
    def chat(self, user_text: str, thread_id=None):
        # 1. Prompt dengan gaya bahasa santai/chill
        prompt = f"""
        User curhat: "{user_text}"
        
        Tugas Anda:
        1. Jadilah teman curhat yang asik, chill, dan friendly. Gunakan Bahasa Indonesia yang santai (nggak kaku).
        2. Berikan respon empati yang tulus. Kalau user bilang mau seminar MSIB, ujian, atau lagi capek, kasih semangat yang hangat kayak temen deket.
        3. Gunakan sedikit emoji biar suasananya makin seru.
        4. Tentukan satu kategori mood musik yang paling pas (Happy, Sad, Calm, atau Tense).
        
        Format jawaban wajib:
        Kategori: [Nama Mood]
        Respon: [Isi kalimat dukungan santai kamu]
        """

        try:
            # Meminta Gemini menganalisis perasaan user
            raw_response = self.model.generate_content(prompt).text
            lines = raw_response.split('\n')
            detected_mood = "Happy" # Default jika gagal
            support_msg = ""
            
            # Parsing hasil dari Gemini
            for line in lines:
                if "Kategori:" in line:
                    for m in ["Happy", "Sad", "Calm", "Tense"]:
                        if m.lower() in line.lower(): 
                            detected_mood = m
                if "Respon:" in line:
                    support_msg = line.replace("Respon:", "").strip()
            
            # Jika format parsing gagal, gunakan teks mentah
            if not support_msg: 
                support_msg = raw_response.strip()
                
        except Exception:
            detected_mood = "Happy"
            support_msg = "Semangat terus ya! Aku yakin kamu pasti bisa ngelewatin hari ini dengan keren banget. ✨"

        # 2. Ambil lagu dari music_engine berdasarkan mood
        songs_df = self.engine.get_recommendations_by_mood(detected_mood, n=5)

        # 3. Susun Pesan Teks dan List Data Lagu Lengkap untuk UI
        full_text = f"{support_msg}\n\n**Nih, ada beberapa lagu yang cocok buat nemenin mood {detected_mood} kamu:**\n"
        songs_data = []
        
        if not songs_df.empty:
            for i, row in songs_df.iterrows():
                # List teks simpel di balon chat
                full_text += f"{i+1}. **{row['track_name']}** – {row['artists']}\n"
                
                # Data lengkap agar tidak terjadi KeyError di pages/1_Music.py
                songs_data.append({
                    "title": row["track_name"],
                    "artist": row["artists"],
                    "album": row.get("album_name", "No Album"),
                    "genre": row.get("track_genre", "Music"),
                    "popularity": row.get("popularity", 0),
                    "track_id": row["track_id"]
                })
        else:
            full_text += "Duh, aku belum nemu lagu yang pas nih buat sekarang. Tapi tetep semangat ya! 🙌"

        return {
            "text": full_text, 
            "songs": songs_data
        }
