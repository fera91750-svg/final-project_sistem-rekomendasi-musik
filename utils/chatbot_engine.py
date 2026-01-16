"""
Music Chatbot Engine for Streamlit
Sinkronisasi total antara teks LLM dan daftar lagu UI
"""

import sys
import os
import random

# Tambahkan folder module ke path
data_music_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'music')
sys.path.insert(0, data_music_folder)

from llm_music_module import MusicLLMChatbot, create_chatbot

class MusicChatbot(MusicLLMChatbot):
    def __init__(self, music_engine):
        self.music_engine = music_engine
        super().__init__(music_engine.df, music_engine.model, music_engine.label_encoder)

    def chat(self, user_text: str, thread_id=None):
        # 1. Paksa LLM HANYA memberikan dukungan kalimat (tanpa nulis list lagu sendiri)
        # Ini supaya tidak ada teks lagu dobel yang kaku di atas
        forced_prompt = f"""
        Kamu adalah teman curhat yang sangat chill dan asik.
        Bahas curhatan user ini dengan santai (pake aku-kamu).
        Kalo user bahas seminar MSIB, kasih semangat yang personal banget.
        
        TUGAS PENTING:
        - HANYA berikan kalimat dukungan/obrolan saja (1-3 kalimat).
        - JANGAN menuliskan judul lagu atau daftar lagu di dalam jawaban teksmu.
        - Tentukan mood: Happy, Sad, Calm, atau Tense.
        
        Curhatan User: {user_text}
        """

        # 2. Ambil respon dari Gemini
        response = super().chat(forced_prompt, thread_id)
        
        llm_text = response.get('text', "")
        detected_mood = response.get('mood', 'Happy')
        
        # 3. Ambil data lagu secara acak dari database
        songs_df = self.music_engine.get_recommendations_by_mood(detected_mood, n=5)

        # 4. Susun data lagu untuk dikirim ke UI
        # UI (1_Music.py) akan otomatis membuatkan player dan caption untuk data ini
        songs_data = []
        
        if not songs_df.empty:
            for _, row in songs_df.iterrows():
                songs_data.append({
                    "title": row["track_name"],
                    "artist": row["artists"],
                    "album": row.get("album_name", "Unknown Album"),
                    "genre": row.get("track_genre", "Music"),
                    "popularity": row.get("popularity", 0),
                    "track_id": row["track_id"]
                })

        # Kirim hasil ke UI
        return {
            "text": llm_text, # Ini berisi kata-kata santai LLM saja
            "songs": songs_data, # Ini berisi data lagu yang akan jadi card & audio player
            "mood": detected_mood
        }

__all__ = ['MusicChatbot', 'create_chatbot']
