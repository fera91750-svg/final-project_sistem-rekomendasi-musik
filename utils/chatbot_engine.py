"""
Music Chatbot Engine for Streamlit
Versi: Anti-Duplikat & Reset Konteks Jawaban
"""

import sys
import os
import pandas as pd

# 1. Pastikan folder data/music terdaftar di sistem path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
data_music_folder = os.path.join(project_root, 'data', 'music')

if data_music_folder not in sys.path:
    sys.path.insert(0, data_music_folder)

# 2. Import modul LLM asli
try:
    from llm_music_module import MusicLLMChatbot, create_chatbot
except ImportError as e:
    # Fallback jika struktur folder berbeda di server
    from data.music.llm_music_module import MusicLLMChatbot, create_chatbot

class MusicChatbot(MusicLLMChatbot):
    """
    Wrapper khusus Streamlit yang mewarisi fungsi LLM
    dengan tambahan filter track_id dan pembersihan teks history.
    """

    def __init__(self, music_engine):
        # Menyimpan engine untuk akses database utama
        self.engine = music_engine
        
        # Inisialisasi parent class (MusicLLMChatbot)
        super().__init__(
            music_engine.df, 
            music_engine.model, 
            music_engine.label_encoder
        )

    def chat(self, user_text, thread_id=None):
        """
        Overriding fungsi chat untuk memfilter output agar tidak terjadi duplikasi
        dan mencegah jawaban lagu sebelumnya muncul kembali.
        """
        # A. Dapatkan respon dasar dari model LLM
        response = super().chat(user_text, thread_id)
        
        # Ambil list lagu mentah dan mood yang dideteksi
        raw_songs = response.get('songs', [])
        mood = response.get('mood', 'Normal')

        # B. Logika Anti-Duplikat & Sinkronisasi Teks
        # Jika model memberikan rekomendasi lagu (bukan sekadar ngobrol)
        if raw_songs:
            unique_songs = []
            seen_track_ids = set()

            # 1. Filter menggunakan track_id unik
            for song in raw_songs:
                # Ambil track_id dari baris data
                tid = song.get('track_id')
                
                # Hanya masukkan jika ID belum pernah muncul di respon ini
                if tid and tid not in seen_track_ids:
                    unique_songs.append(song)
                    seen_track_ids.add(tid)

            # 2. PAKSA RE-WRITE TEKS (Pembersihan History)
            # Ini menghapus teks lagu 'Happy' sebelumnya agar tidak muncul saat user minta lagu 'Sad'
            new_text = f"**Rekomendasi Lagu untuk Mood {mood}:**\n\n"
            
            for i, s in enumerate(unique_songs, 1):
                # Ambil judul dan artis dengan fallback 'Unknown'
                title = s.get('title') or s.get('track_name', 'Unknown')
                artist = s.get('artist') or s.get('artists', 'Unknown Artist')
                new_text += f"{i}. **{title}** - {artist}\n"
            
            new_text += "\nSemoga lagu-lagu ini bisa menemani harimu! ✨"
            
            # Ganti teks asli yang berantakan/duplikat dengan teks yang bersih
            response['text'] = new_text
            response['songs'] = unique_songs
        
        # Jika user hanya menyapa/ngobrol (tidak ada list lagu), 
        # biarkan response['text'] apa adanya dari LLM.
        return response

# Export agar bisa dipanggil di main.py atau 1_Music.py
__all__ = ['MusicChatbot', 'create_chatbot']
