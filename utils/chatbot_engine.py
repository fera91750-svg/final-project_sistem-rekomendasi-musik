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
        # 1. Langkah Pertama: Deteksi Mood
        mood_prompt = f"Tentukan mood musik (1 kata: Happy/Sad/Calm/Tense) untuk kalimat ini: '{user_text}'"
        try:
            detected_mood = self.model.generate_content(mood_prompt).text.strip().capitalize()
            if detected_mood not in ["Happy", "Sad", "Calm", "Tense"]:
                detected_mood = "Happy"
        except:
            detected_mood = "Happy"

        # 2. Langkah Kedua: Ambil Data Lagu dari Database (Satu-satunya Sumber)
        # Kita ambil lagu sebelum LLM membuat kalimat
        songs_df = self.music_engine.get_recommendations_by_mood(detected_mood, n=5)
        
        songs_data = []
        list_nama_lagu = []
        
        if not songs_df.empty:
            for _, row in songs_df.iterrows():
                # Simpan untuk data embed spotify
                spotify_html = self.music_engine.create_spotify_embed(row['track_id'])
                songs_data.append({
                    "title": row["track_name"],
                    "artist": row["artists"],
                    "album": row.get("album_name", "Original Album"),
                    "genre": row.get("track_genre", "Music"),
                    "track_id": row["track_id"],
                    "embed_html": spotify_html
                })
                # Simpan nama lagu untuk "didikte" ke LLM
                list_nama_lagu.append(f"{row['track_name']} oleh {row['artists']}")

        # 3. Langkah Ketiga: Suruh LLM membuat jawaban berdasarkan Lagu tadi
        # Kita masukkan daftar lagu ke dalam prompt agar LLM membacanya
        string_lagu = "\n".join(list_nama_lagu)
        final_prompt = f"""
        Kamu adalah teman curhat yang chill (aku-kamu).
        User curhat: "{user_text}"
        Mood: {detected_mood}
        
        TUGAS:
        1. Berikan respon santai terhadap curhatan user.
        2. Sebutkan bahwa kamu merekomendasikan lagu-lagu berikut:
        {string_lagu}
        
        JANGAN menyebutkan lagu lain selain daftar di atas agar sinkron dengan pemutar musik!
        """
        
        try:
            llm_response = self.model.generate_content(final_prompt).text.strip()
        except:
            llm_response = f"Wah, aku ngerti. Nih, aku pilihin beberapa lagu {detected_mood} buat nemenin kamu!"

        return {
            "text": llm_response,
            "songs": songs_data,
            "mood": detected_mood
        }
