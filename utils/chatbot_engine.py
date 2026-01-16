import sys
import os
import streamlit as st
import pandas as pd

# Add data/music folder to path
data_music_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'music')
sys.path.insert(0, data_music_folder)

from llm_music_module import MusicLLMChatbot

class MusicChatbot(MusicLLMChatbot):
    def __init__(self, music_engine):
        # Simpan engine untuk akses data dan visualisasi
        self.engine = music_engine
        
        music_df = music_engine.df
        model = music_engine.model
        label_encoder = music_engine.label_encoder

        # Initialize parent class (MusicLLMChatbot)
        super().__init__(music_df, model, label_encoder)

    def chat(self, user_input, thread_id="default"):
        """
        Overriding fungsi chat untuk menambahkan filter duplikat 
        pada data songs yang dikirim ke UI.
        """
        # 1. Panggil fungsi chat asli dari parent (LLM)
        # Parent mengembalikan dict: {"text": "...", "songs": [...]}
        response = super().chat(user_input, thread_id=thread_id)
        
        # 2. Ambil list lagu dari response jika ada
        if "songs" in response and response["songs"]:
            raw_songs = response["songs"]
            
            # --- LOGIKA ANTI DUPLIKAT ---
            # Kita gunakan DataFrame sementara untuk membuang duplikat
            df_temp = pd.DataFrame(raw_songs)
            
            # Hapus lagu dengan judul (title) dan artis (artist) yang sama
            # Kita biarkan satu saja (yang pertama muncul)
            df_clean = df_temp.drop_duplicates(subset=['title', 'artist'], keep='first')
            
            # Kembalikan ke format list of dictionary
            response["songs"] = df_clean.to_dict('records')

        return response
