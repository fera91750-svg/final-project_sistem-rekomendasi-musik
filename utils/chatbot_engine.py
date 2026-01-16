"""
Music Chatbot Engine - Integrasi Langsung Spotify Embed
"""

import sys
import os
import random

# Menghubungkan ke modul LLM asli Anda
data_music_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'music')
sys.path.insert(0, data_music_folder)

from llm_music_module import MusicLLMChatbot, create_chatbot

class MusicChatbot(MusicLLMChatbot):
    def __init__(self, music_engine):
        # Simpan instance engine agar bisa panggil fungsi embed
        self.music_engine = music_engine
        
        # Inisialisasi parent class dengan komponen dari engine
        super().__init__(
            self.music_engine.df, 
            self.music_engine.model, 
            self.music_engine.label_encoder
        )

    def chat(self, user_text: str, thread_id=None):
        # 1. Instruksi agar LLM santai dan tidak kaku
        forced_prompt = f"""
        Jawab curhatan user sebagai teman chill (pake aku-kamu). 
        Jika user bahas seminar MSIB atau hal spesifik, kasih semangat personal.
        JANGAN tulis daftar lagu di dalam teks ini.
        
        Curhatan: {user_text}
        """

        # 2. Ambil respon dari LLM (Gemini)
        response = super().chat(forced_prompt, thread_id)
        llm_text = response.get('text', "")
        detected_mood = response.get('mood', 'Happy')
        
        # 3. Ambil lagu dari music_engine berdasarkan Mood
        # n=5 lagu acak menggunakan fungsi rekomendasi engine
        songs_df = self.music_engine.get_recommendations_by_mood(detected_mood, n=5)

        # 4. Susun data lagu + Panggil fungsi Embed dari music_engine
        songs_data = []
        if not songs_df.empty:
            for _, row in songs_df.iterrows():
                # Memanggil fungsi embed dari music_engine Anda agar bisa didengar langsung
                spotify_html = self.music_engine.create_spotify_embed(row['track_id'])
                
                songs_data.append({
                    "title": row["track_name"],
                    "artist": row["artists"],
                    "album": row.get("album_name", "Unknown Album"),
                    "genre": row.get("track_genre", "Music"),
                    "popularity": row.get("popularity", 0),
                    "track_id": row["track_id"],
                    "embed_html": spotify_html  # Link embed spotify untuk UI
                })

        # 5. Return ke UI (1_Music.py)
        return {
            "text": llm_text,
            "songs": songs_data,
            "mood": detected_mood
        }

__all__ = ['MusicChatbot', 'create_chatbot']
