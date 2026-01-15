"""
Music Chatbot Engine for Streamlit
Wrapper that imports from data/music/llm_music_module.py
"""

import sys
import os
import random

# Tambahkan folder module ke path
data_music_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'music')
sys.path.insert(0, data_music_folder)

# Import dari music module asli
from llm_music_module import MusicLLMChatbot, create_chatbot

class MusicChatbot(MusicLLMChatbot):
    def __init__(self, music_engine):
        # Ambil komponen dari engine utama
        self.music_engine = music_engine
        music_df = music_engine.df
        model = music_engine.model
        label_encoder = music_engine.label_encoder

        # Inisialisasi class induk (LLM)
        super().__init__(music_df, model, label_encoder)

    def chat(self, user_text: str, thread_id=None):
        # 1. Langsung pakai fungsi chat bawaan model LLM
        # Model ini sudah punya kemampuan deteksi mood sendiri
        response = super().chat(user_text, thread_id)
        
        # Ambil mood yang dideteksi oleh LLM (biasanya ada di response['mood'])
        # Jika tidak ada, default ke Happy
        detected_mood = response.get('mood', 'Happy')
        
        # 2. Ambil lagu dari music_engine dengan fitur random (.sample)
        # Ini agar lagu yang muncul tidak kaku dan tidak berulang
        songs_df = self.music_engine.get_recommendations_by_mood(detected_mood, n=5)

        # 3. Susun data lagu dengan lengkap (Wajib ada Album & Genre agar UI tidak error)
        songs_data = []
        if not songs_df.empty:
            for _, row in songs_df.iterrows():
                songs_data.append({
                    "title": row["track_name"],
                    "artist": row["artists"],
                    "album": row.get("album_name", "Unknown Album"), # Solusi KeyError
                    "genre": row.get("track_genre", "Music"),       # Solusi KeyError
                    "popularity": row.get("popularity", 0),
                    "track_id": row["track_id"]
                })

        # 4. Return hasil yang sudah digabung
        return {
            "text": response.get('text', "Nih, dengerin lagu ini biar makin asik!"),
            "songs": songs_data,
            "mood": detected_mood
        }

# Export agar bisa dipanggil di app utama
__all__ = ['MusicChatbot', 'create_chatbot']
