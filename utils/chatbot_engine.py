import sys
import os
import random

# Menghubungkan ke modul LLM asli
data_music_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'music')
sys.path.insert(0, data_music_folder)

from llm_music_module import MusicLLMChatbot

class MusicChatbot(MusicLLMChatbot):
    def __init__(self, music_engine):
        self.music_engine = music_engine
        super().__init__(
            self.music_engine.df, 
            self.music_engine.model, 
            self.music_engine.label_encoder
        )

    def chat(self, user_text: str, thread_id=None):
        # 1. Deteksi Mood secara cepat
        mood_prompt = f"Tentukan mood musik (1 kata: Happy/Sad/Calm/Tense) untuk: {user_text}"
        try:
            detected_mood = self.model.generate_content(mood_prompt).text.strip().capitalize()
            if detected_mood not in ["Happy", "Sad", "Calm", "Tense"]:
                detected_mood = "Happy"
        except:
            detected_mood = "Happy"

        # 2. Ambil lagu dari database (Satu-satunya sumber lagu)
        songs_df = self.music_engine.get_recommendations_by_mood(detected_mood, n=5)
        
        songs_data = []
        text_list_lagu = "" # Untuk ditempel ke chat
        
        if not songs_df.empty:
            for i, row in songs_df.iterrows():
                # Simpan untuk player di UI
                spotify_html = self.music_engine.create_spotify_embed(row['track_id'])
                songs_data.append({
                    "title": row["track_name"],
                    "artist": row["artists"],
                    "album": row.get("album_name", "Original Album"),
                    "genre": row.get("track_genre", "Music"),
                    "track_id": row["track_id"],
                    "embed_html": spotify_html
                })
                # Simpan untuk teks di chat
                text_list_lagu += f"{i+1}. **{row['track_name']}** - {row['artists']}\n"

        # 3. Minta LLM buat kalimat pendukung SAJA (Tanpa List Lagu)
        chat_prompt = f"""
        Kamu teman curhat yang chill (aku-kamu). 
        Beri respon singkat & asik untuk curhatan ini: "{user_text}"
        Jangan tulis daftar lagu apapun dalam jawabanmu.
        """
        
        try:
            llm_response = self.model.generate_content(chat_prompt).text.strip()
        except:
            llm_response = "Wah, aku ngerti perasaanmu. Nih, aku pilihin lagu yang pas buat kamu!"

        # 4. GABUNGKAN SECARA PAKSA: Pesan LLM + List Lagu Database
        final_text = f"{llm_response}\n\n**Rekomendasi lagu untuk mood {detected_mood}:**\n{text_list_lagu}"

        return {
            "text": final_text,
            "songs": songs_data,
            "mood": detected_mood
        }
