"""
Music Chatbot Engine - Integrasi Langsung Spotify Embed
"""

import sys
import os
import random

# Menghubungkan ke modul LLM asli
data_music_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'music')
sys.path.insert(0, data_music_folder)

from llm_music_module import MusicLLMChatbot

class MusicChatbot(MusicLLMChatbot):
    def __init__(self, music_engine):
        self.music_engine = music_engine
        super().__init__(
            self.music_engine.df, 
            self.music_engine.model, 
            self.music_engine.label_encoder
        )

    def chat(self, user_text: str, thread_id=None):
        # 1. Deteksi Mood terlebih dahulu menggunakan LLM
        # Kita buat prompt singkat hanya untuk tahu mood-nya apa
        mood_prompt = f"Berdasarkan teks ini: '{user_text}', apa mood musik yang cocok? (Happy/Sad/Calm/Tense). Jawab 1 kata saja."
        try:
            detected_mood = self.model.generate_content(mood_prompt).text.strip().capitalize()
            if detected_mood not in ["Happy", "Sad", "Calm", "Tense"]:
                detected_mood = "Happy"
        except:
            detected_mood = "Happy"

        # 2. Ambil lagu SECARA MANUAL di sini (Satu sumber data)
        songs_df = self.music_engine.get_recommendations_by_mood(detected_mood, n=5)
        
        # 3. Buat daftar teks lagu untuk dimasukkan ke jawaban LLM
        song_names = []
        songs_data = []
        
        for _, row in songs_df.iterrows():
            song_info = f"{row['track_name']} - {row['artists']}"
            song_names.append(song_info)
            
            # Siapkan data untuk player Spotify di UI
            spotify_html = self.music_engine.create_spotify_embed(row['track_id'])
            songs_data.append({
                "title": row["track_name"],
                "artist": row["artists"],
                "album": row.get("album_name", "Original Album"),
                "genre": row.get("track_genre", "Music"),
                "track_id": row["track_id"],
                "embed_html": spotify_html
            })

        # 4. Berikan data lagu tadi ke LLM agar dia membuat kalimat berdasarkan lagu TERSEBUT
        final_prompt = f"""
        User curhat: "{user_text}"
        Mood terdeteksi: {detected_mood}
        Daftar lagu yang WAJIB kamu sebutkan:
        {", ".join(song_names)}
        
        Tugas: Berikan respon santai (aku-kamu) dan sebutkan ulang daftar lagu di atas sebagai rekomendasi.
        Jangan ambil lagu lain selain daftar di atas.
        """
        
        try:
            llm_response = self.model.generate_content(final_prompt).text
        except:
            llm_response = f"Oke! Ini beberapa lagu {detected_mood} pilihan buat kamu."

        return {
            "text": llm_response,
            "songs": songs_data,
            "mood": detected_mood
        }
