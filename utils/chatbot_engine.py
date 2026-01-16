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
        self.music_engine = music_engine
        super().__init__(music_engine.df, music_engine.model, music_engine.label_encoder)

    def chat(self, user_text: str, thread_id=None):
        # Memaksa LLM menjawab santai agar tidak kaku seperti di gambar Anda
        forced_prompt = f"Jawab sebagai teman chill (aku-kamu). Jangan tulis daftar lagu di teks. Curhat: {user_text}"
        
        response = super().chat(forced_prompt, thread_id)
        llm_text = response.get('text', "")
        detected_mood = response.get('mood', 'Happy')
        
        # Ambil lagu secara acak dari database
        songs_df = self.music_engine.get_recommendations_by_mood(detected_mood, n=5)

        songs_data = []
        if not songs_df.empty:
            for _, row in songs_df.iterrows():
                # WAJIB: Masukkan 'album' dan 'genre' agar TIDAK KeyError lagi
                songs_data.append({
                    "title": row["track_name"],
                    "artist": row["artists"],
                    "album": row.get("album_name", "Unknown Album"), # Ini kuncinya
                    "genre": row.get("track_genre", "Music"),       # Ini kuncinya
                    "popularity": row.get("popularity", 0),
                    "track_id": row["track_id"]
                })

        return {
            "text": llm_text,
            "songs": songs_data,
            "mood": detected_mood
        }
