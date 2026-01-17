"""
Music Chatbot Engine for Streamlit
Wrapper that imports from data/music/llm_music_module.py
"""

import sys
import os
import pandas as pd

# Add data/music folder to path
data_music_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'music')
if data_music_folder not in sys.path:
    sys.path.insert(0, data_music_folder)

# Import from music module
from llm_music_module import MusicLLMChatbot, create_chatbot

class MusicChatbot(MusicLLMChatbot):
    """
    Streamlit-specific wrapper for MusicLLMChatbot dengan fitur Anti-Duplikat
    menggunakan track_id sebagai identifier unik.
    """

    def __init__(self, music_engine):
        # Simpan engine untuk akses dataframe dan fungsi rekomendasi
        self.engine = music_engine
        
        # Inisialisasi parent class
        super().__init__(
            music_engine.df, 
            music_engine.model, 
            music_engine.label_encoder
        )

    def chat(self, user_text, thread_id=None):
        """
        Override fungsi chat untuk membersihkan duplikat berdasarkan track_id
        sebelum data dikirim ke UI.
        """
        # 1. Ambil respon asli dari LLM module
        response = super().chat(user_text, thread_id)
        
        raw_songs = response.get('songs', [])
        mood = response.get('mood', 'Normal')
        
        if not raw_songs:
            return response

        # 2. Filter Duplikat menggunakan track_id
        unique_songs = []
        seen_track_ids = set()

        for song in raw_songs:
            # Ambil track_id (pastikan key sesuai dengan yang ada di dataset Anda)
            tid = song.get('track_id')
            
            # Jika track_id belum pernah terlihat, masukkan ke list
            if tid and tid not in seen_track_ids:
                unique_songs.append(song)
                seen_track_ids.add(tid)
        
        # 3. Sinkronisasi Teks Chatbot agar tidak menampilkan daftar duplikat
        if unique_songs:
            new_text = f"**Rekomendasi Lagu untuk Mood {mood}:**\n\n"
            for i, s in enumerate(unique_songs, 1):
                title = s.get('title') or s.get('track_name', 'Unknown')
                artist = s.get('artist') or s.get('artists', 'Unknown Artist')
                new_text += f"{i}. **{title}** - {artist}\n"
            
            new_text += "\nSemoga lagu-lagu ini bisa menemani harimu! ✨"
            response['text'] = new_text
            response['songs'] = unique_songs

        return response

# Export for easy import in Streamlit
__all__ = ['MusicChatbot', 'create_chatbot']
