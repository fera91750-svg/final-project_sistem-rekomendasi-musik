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
        # 1. Panggil fungsi chat asli dari LLM (Biarkan LLM yang berpikir & merangkai kata)
        # LLM akan memberikan jawaban yang berbeda sesuai input (misal: seminar MSIB)
        response = super().chat(user_text, thread_id)
        
        # Ambil teks jawaban asli dari LLM
        llm_text = response.get('text', "")
        
        # Ambil mood yang dideteksi oleh LLM
        detected_mood = response.get('mood', 'Happy')
        
        # 2. Ambil lagu dari music_engine dengan fitur random (.sample)
        # n=5 lagu acak agar rekomendasi tidak itu-itu saja
        songs_df = self.music_engine.get_recommendations_by_mood(detected_mood, n=5)

        # 3. Susun data lagu untuk dikirim ke UI
        # Kita sertakan semua informasi (album, genre, popularity) agar UI tidak error
        songs_data = []
        
        # Buat teks daftar lagu tambahan yang simpel untuk digabung ke teks LLM
        song_list_text = f"\n\n**Nih, playlist {detected_mood} yang pas buat kamu:**\n"
        
        if not songs_df.empty:
            for i, row in songs_df.iterrows():
                song_list_text += f"{i+1}. **{row['track_name']}** – {row['artists']}\n"
                
                songs_data.append({
                    "title": row["track_name"],
                    "artist": row["artists"],
                    "album": row.get("album_name", "Unknown Album"),
                    "genre": row.get("track_genre", "Music"),
                    "popularity": row.get("popularity", 0),
                    "track_id": row["track_id"]
                })
            
            # Gabungkan jawaban asli LLM dengan daftar lagu
            # JADI: [Jawaban Kreatif LLM] + [Daftar Lagu]
            final_display_text = f"{llm_text}\n{song_list_text}"
        else:
            final_display_text = llm_text

        return {
            "text": final_display_text,
            "songs": songs_data,
            "mood": detected_mood
        }

# Export agar bisa dipanggil di app utama
__all__ = ['MusicChatbot', 'create_chatbot']
