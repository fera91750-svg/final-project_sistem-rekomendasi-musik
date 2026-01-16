import sys
import os
import streamlit as st
import pandas as pd

# Path ke folder data/music
data_music_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'music')
sys.path.insert(0, data_music_folder)

from llm_music_module import MusicLLMChatbot

class MusicChatbot(MusicLLMChatbot):
    def __init__(self, music_engine):
        self.engine = music_engine
        # Inisialisasi parent class (MusicLLMChatbot)
        super().__init__(music_engine.df, music_engine.model, music_engine.label_encoder)

    def chat(self, user_input, thread_id="default"):
        """
        Fungsi ini mengambil respon dari AI, membersihkan teks dari daftar lagu manual,
        dan menghapus duplikat lagu untuk tampilan Card.
        """
        # 1. Ambil respon asli dari LLM (berisi teks dan list songs)
        response = super().chat(user_input, thread_id=thread_id)
        
        bot_text = response.get("text", "")
        songs_data = response.get("songs", [])

        # 2. PROSES PEMBERSIHAN DUPLIKAT (Untuk Card)
        if songs_data:
            df_temp = pd.DataFrame(songs_data)
            # Hapus lagu dengan Judul dan Artis yang sama (abaikan perbedaan genre)
            df_clean = df_temp.drop_duplicates(subset=['title', 'artist'], keep='first')
            # Ambil 3-5 lagu saja agar tidak kepanjangan
            clean_list = df_clean.head(3).to_dict('records')
            response["songs"] = clean_list

            # 3. PROSES PEMBERSIHAN TEKS (Agar tidak double dengan Card)
            # Kita potong teks AI jika ia mulai menulis daftar lagu secara manual
            # Biasanya ditandai dengan kata "Rekomendasi Lagu" atau pola angka 1. 2.
            if "Rekomendasi Lagu" in bot_text:
                # Ambil hanya kalimat pembuka sebelum daftar lagu dimulai
                bot_text = bot_text.split("Rekomendasi Lagu")[0].strip()
                bot_text += "\n\nBerikut adalah beberapa lagu yang pas untuk mood kamu:"
            
            response["text"] = bot_text

        return response
