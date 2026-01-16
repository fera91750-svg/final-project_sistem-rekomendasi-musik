"""
Music Chatbot Engine for Streamlit
Wrapper that imports from data/music/llm_music_module.py

This file acts as a bridge between the LLM module and Streamlit UI
"""

import sys
import os
import streamlit as st

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
        Custom method untuk mendapatkan teks jawaban DAN data lagu
        """
        # 1. Dapatkan respon teks dari logika LLM/Module asli
        response_text = self.generate_response(user_input)
        
        # 2. Deteksi mood dari input user (menggunakan logika engine)
        # Anda bisa menyesuaikan ini dengan fungsi deteksi mood yang sudah kita buat
        from engine.music_engine import MusicRecommendationEngine # Pastikan path benar
        
        # Sederhananya, kita cari rekomendasi lagu jika user minta
        recommendations = pd.DataFrame()
        mood_detected = None
        
        # Logika deteksi sederhana (bisa dikembangkan)
        if any(word in user_input.lower() for word in ['sedih', 'galau', 'sad']):
            mood_detected = 'Sad'
        elif any(word in user_input.lower() for word in ['senang', 'happy', 'bahagia']):
            mood_detected = 'Happy'
        elif any(word in user_input.lower() for word in ['tenang', 'calm', 'santai']):
            mood_detected = 'Calm'
        elif any(word in user_input.lower() for word in ['tense', 'tegang', 'stres']):
            mood_detected = 'Tense'

        if mood_detected:
            recommendations = self.engine.get_recommendations_by_mood(mood_detected, n=3)
            
        return response_text, recommendations
