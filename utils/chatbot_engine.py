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
        # Menggunakan model Gemini 1.5 Flash untuk pemrosesan cepat
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    # =========================
    # CHAT MAIN FUNCTION
    # =========================
    def chat(self, user_text: str, thread_id=None):
        # 1. Prompt untuk Gemini agar memberikan respon empati & deteksi mood
        prompt = f"""
        User curhat: "{user_text}"
        
        Tugas Anda:
        1. Berikan respon empati, ramah, dan sangat personal dalam Bahasa Indonesia. 
           Jika user menyebut kegiatan khusus (seperti seminar MSIB, ujian, atau kerja), 
           berikan semangat dan dukungan spesifik untuk kegiatan tersebut.
        2. Tentukan satu kategori mood musik yang paling cocok (pilih salah satu: Happy, Sad, Calm, atau Tense).
        
        Format jawaban wajib:
        Kategori: [Nama Mood]
        Respon: [Isi kalimat dukungan Anda]
        """

        try:
            # Meminta Gemini menganalisis perasaan user
            raw_response = self.model.generate_content(prompt).text
            lines = raw_response.split('\n')
            detected_mood = "Happy" # Default
            support_msg = ""
            
            # Parsing hasil dari Gemini
            for line in lines:
                if "Kategori:" in line:
                    for m in ["Happy", "Sad", "Calm", "Tense"]:
                        if m.lower() in line.lower(): 
                            detected_mood = m
                if "Respon:" in line:
                    support_msg = line.replace("Respon:", "").strip()
            
            # Jika parsing gagal, ambil seluruh teks sebagai respon
            if not support_msg: 
                support_msg = raw_response.strip()
                
        except Exception as e:
            detected_mood = "Happy"
            support_msg = "Wah, semangat ya untuk hari ini! Apapun yang kamu lalui, kamu pasti bisa menghadapinya dengan baik."

        # 2. Ambil lagu dari music_engine berdasarkan mood yang dideteksi Gemini
        # Fungsi ini sekarang menggunakan random sampling (dari perbaikan sebelumnya)
        songs_df = self.engine.get_recommendations_by_mood(detected_mood, n=5)

        # 3. Susun Pesan Teks dan List Data Lagu Lengkap untuk UI
        full_text = f"{support_msg}\n\n**Rekomendasi lagu untuk mood {detected_mood}:**\n"
        songs_data = []
        
        if not songs_df.empty:
            for i, row in songs_df.iterrows():
                # Menambahkan daftar lagu ke teks chat
                full_text += f"{i+1}. **{row['track_name']}** – {row['artists']}\n"
                
                # Menyiapkan data lengkap untuk dikirim ke UI (Mencegah KeyError: 'album')
                songs_data.append({
                    "title": row["track_name"],
                    "artist": row["artists"],
                    "album": row.get("album_name", "Unknown Album"), # Mencegah error jika kolom kosong
                    "genre": row.get("track_genre", "General"),      # Mencegah error jika kolom kosong
                    "popularity": row.get("popularity", 0),
                    "track_id": row["track_id"]
                })
        else:
            full_text += "Maaf, saya tidak menemukan lagu yang cocok saat ini. Tapi tetap semangat ya!"

        return {
            "text": full_text, 
            "songs": songs_data
        }
