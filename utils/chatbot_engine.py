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
        # Simpan engine agar bisa memanggil fungsi create_spotify_embed nanti
        self.engine = music_engine
        
        music_df = music_engine.df
        model = music_engine.model
        label_encoder = music_engine.label_encoder

        # Initialize parent class
        super().__init__(music_df, model, label_encoder)

    def get_chat_response(self, user_input):
        """
        Method untuk mendapatkan teks jawaban DAN data lagu tanpa duplikat
        """
        # 1. Dapatkan respon teks dari LLM
        response_text = self.generate_response(user_input)
        
        # 2. Deteksi mood dari input user
        mood_detected = None
        user_input_low = user_input.lower()
        
        if any(word in user_input_low for word in ['sedih', 'galau', 'sad', 'merana', 'nangis']):
            mood_detected = 'Sad'
        elif any(word in user_input_low for word in ['senang', 'happy', 'bahagia', 'ceria', 'gembira']):
            mood_detected = 'Happy'
        elif any(word in user_input_low for word in ['tenang', 'calm', 'santai', 'rileks', 'adem']):
            mood_detected = 'Calm'
        elif any(word in user_input_low for word in ['tense', 'tegang', 'stres', 'marah', 'semangat']):
            mood_detected = 'Tense'

        recommendations = pd.DataFrame()
        
        if mood_detected:
            # Mengambil lebih banyak data dari engine untuk difilter duplikatnya
            raw_recs = self.engine.get_recommendations_by_mood(mood_detected, n=20)
            
            # --- PROSES PENGHILANGAN DUPLIKAT ---
            # Kita hapus duplikat berdasarkan judul lagu (track_name) dan artis
            if not raw_recs.empty:
                recommendations = raw_recs.drop_duplicates(subset=['track_name', 'artists'], keep='first')
                
                # Setelah duplikat hilang, baru kita ambil 3 atau 5 teratas
                recommendations = recommendations.head(3)
            
        return response_text, recommendations
