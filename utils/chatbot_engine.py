"""
Music Chatbot Engine for Streamlit
Wrapper that imports from data/music/llm_music_module.py

This file acts as a bridge between the LLM module and Streamlit UI
"""

import sys
import os
import random

# Add data/music folder to path
data_music_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'music')
sys.path.insert(0, data_music_folder)

# Import from music module
from llm_music_module import MusicLLMChatbot, create_chatbot


class MusicChatbot(MusicLLMChatbot):
    """
    Streamlit-specific wrapper for MusicLLMChatbot
    Inherits all functionality from the music module
    """

    def __init__(self, music_engine):
        """
        Initialize chatbot with MusicRecommendationEngine
        """
        # Simpan engine untuk akses fungsi rekomendasi nanti
        self.music_engine = music_engine
        
        # Extract components from engine
        music_df = music_engine.df
        model = music_engine.model
        label_encoder = music_engine.label_encoder

        # Initialize parent class
        super().__init__(music_df, model, label_encoder)

    def chat(self, user_text: str, thread_id=None):
        """
        Overriding chat method supaya jawabannya lebih chill, 
        responsif terhadap input (Seminar MSIB), dan anti-error.
        """
        
        # 1. Instruksi tambahan agar Gemini menjawab santai & personal
        # Kita memodifikasi prompt internal yang biasanya ada di llm_music_module
        custom_prompt = f"""
        User curhat: "{user_text}"
        
        Aturan Main:
        - Kamu adalah teman curhat yang CHILL, SANTAI, dan GAUL.
        - JANGAN kaku. Pakai 'aku-kamu'. 
        - Jika user bahas seminar MSIB atau hal spesifik, kasih semangat yang hangat & personal.
        - Tentukan Mood: Happy, Sad, Calm, atau Tense.
        
        Format Balasan:
        Mood: [Nama Mood]
        Chat: [Kalimat dukungan asik kamu]
        """

        try:
            # Memanggil fungsi generate dari parent class (Gemini)
            raw_response = self.model.generate_content(custom_prompt).text
            
            # Parsing Mood dan Chat
            lines = raw_response.split('\n')
            detected_mood = "Happy"
            support_msg = ""
            
            for line in lines:
                if "Mood:" in line:
                    for m in ["Happy", "Sad", "Calm", "Tense"]:
                        if m.lower() in line.lower(): detected_mood = m
                if "Chat:" in line:
                    support_msg = line.replace("Chat:", "").strip()
            
            if not support_msg: support_msg = raw_response.strip()

        except Exception:
            # Fallback jika API Error (Tetap Personal & Santai)
            user_lower = user_text.lower()
            detected_mood = "Happy"
            if "seminar" in user_lower or "msib" in user_lower:
                support_msg = "Wih, semangat pol buat seminar MSIB-nya! Santai aja, kamu pasti tampil pecah hari ini! 🔥"
            else:
                support_msg = "Semangat terus ya! Kamu pasti bisa ngelewatin ini dengan cara yang paling asik. ✨"

        # 2. Ambil lagu menggunakan engine (Randomized)
        songs_df = self.music_engine.get_recommendations_by_mood(detected_mood, n=5)

        # 3. Variasi Kalimat Pembuka
        intros = [
            f"Nih, ada beberapa lagu yang pas banget buat nemenin mood {detected_mood} kamu:",
            f"Biar makin chill, dengerin lagu-lagu {detected_mood} pilihan aku ini deh:",
            f"Coba dengerin playlist {detected_mood} ini, siapa tau bikin makin asik:"
        ]
        
        full_text = f"{support_msg}\n\n**{random.choice(intros)}**\n"
        songs_data = []
        
        if not songs_df.empty:
            for i, row in songs_df.iterrows():
                full_text += f"{i+1}. **{row['track_name']}** – {row['artists']}\n"
                
                # Menyiapkan data lengkap agar TIDAK error KeyError: 'album'
                songs_data.append({
                    "title": row["track_name"],
                    "artist": row["artists"],
                    "album": row.get("album_name", "Unknown Album"),
                    "genre": row.get("track_genre", "Music"),
                    "popularity": row.get("popularity", 0),
                    "track_id": row["track_id"]
                })

        return {
            "text": full_text, 
            "songs": songs_data
        }


# Export for easy import in Streamlit
__all__ = ['MusicChatbot', 'create_chatbot']
