"""
Music Chatbot Engine - Sinkronisasi Teks & Player
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
        # Ambil komponen dari engine utama
        super().__init__(music_engine.df, music_engine.model, music_engine.label_encoder)

    def chat(self, user_text: str, thread_id=None):
        # 1. Gunakan Prompt agar LLM hanya fokus memberi respon kata-kata yang santai
        # Kita minta LLM JANGAN menuliskan daftar lagu sendiri agar tidak dobel/beda
        forced_prompt = f"""
        Jawab curhatan user sebagai teman yang sangat chill (pake aku-kamu).
        HANYA berikan kalimat dukungan atau obrolan santai saja.
        JANGAN menuliskan judul lagu atau daftar lagu apapun di dalam teks jawabanmu.
        Biarkan sistem yang akan menampilkan lagunya secara otomatis.
        
        Curhatan: {user_text}
        """

        # 2. Ambil respon dari Gemini (LLM)
        response = super().chat(forced_prompt, thread_id)
        llm_text = response.get('text', "")
        detected_mood = response.get('mood', 'Happy')
        
        # 3. Ambil lagu dari database berdasarkan Mood yang dideteksi LLM
        # Menggunakan .sample(n=5) agar lagu yang muncul selalu acak/random
        songs_df = self.music_engine.get_recommendations_by_mood(detected_mood, n=5)

        # 4. Susun data lagu dengan field LENGKAP agar UI tidak error merah (KeyError)
        songs_data = []
        if not songs_df.empty:
            for _, row in songs_df.iterrows():
                songs_data.append({
                    "title": row["track_name"],
                    "artist": row["artists"],
                    "album": row.get("album_name", "Original Album"), # Field ini wajib ada
                    "genre": row.get("track_genre", "Music"),        # Field ini wajib ada
                    "popularity": row.get("popularity", 0),          # Field ini wajib ada
                    "track_id": row["track_id"]
                })

        # 5. Return ke UI
        return {
            "text": llm_text,    # Teks santai dari LLM
            "songs": songs_data, # Data lagu untuk Player & Detail
            "mood": detected_mood
        }

__all__ = ['MusicChatbot', 'create_chatbot']
