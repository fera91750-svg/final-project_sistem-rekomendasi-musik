import sys
import os
import streamlit as st
import pandas as pd

# Add data/music folder to path
data_music_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'music')
sys.path.insert(0, data_music_folder)

from llm_music_module import MusicLLMChatbot, create_chatbot

class MusicChatbot(MusicLLMChatbot):
    def __init__(self, music_engine):
        # Simpan engine untuk akses data dan fungsi embed
        self.engine = music_engine
        
        music_df = music_engine.df
        model = music_engine.model
        label_encoder = music_engine.label_encoder

        # Initialize parent class
        super().__init__(music_df, model, label_encoder)

    def chat(self, user_input, thread_id=None):
        """
        Fungsi utama yang dipanggil oleh music.py
        Mengembalikan DICTIONARY berisi teks dan list lagu tanpa duplikat
        """
        # 1. Dapatkan respon teks dari LLM asli
        response_text = self.generate_response(user_input)
        
        # 2. Deteksi Mood secara internal
        mood_detected = None
        ui = user_input.lower()
        if any(w in ui for w in ['sedih', 'galau', 'sad', 'kecewa']): mood_detected = 'Sad'
        elif any(w in ui for w in ['senang', 'happy', 'bahagia', 'ceria']): mood_detected = 'Happy'
        elif any(w in ui for w in ['santai', 'tenang', 'calm', 'rileks']): mood_detected = 'Calm'
        elif any(w in ui for w in ['tense', 'tegang', 'stres', 'marah', 'semangat']): mood_detected = 'Tense'

        list_lagu = []
        if mood_detected:
            # Ambil 15 lagu untuk difilter duplikatnya
            raw_recs = self.engine.get_recommendations_by_mood(mood_detected, n=15)
            
            if not raw_recs.empty:
                # HAPUS DUPLIKAT berdasarkan judul dan artis
                clean_recs = raw_recs.drop_duplicates(subset=['track_name', 'artists'], keep='first').head(3)
                
                # Format ke list dictionary agar bisa dibaca loop di music.py
                for _, r in clean_recs.iterrows():
                    list_lagu.append({
                        'track_id': r['track_id'],
                        'title': r['track_name'],   # Key ini harus pas dengan music.py
                        'artist': r['artists'],
                        'album': r['album_name'],
                        'genre': r['track_genre'],
                        'popularity': r['popularity']
                    })

        # 3. KEMBALIKAN DALAM FORMAT DICTIONARY (Penting!)
        return {
            "text": response_text,
            "songs": list_lagu
        }
