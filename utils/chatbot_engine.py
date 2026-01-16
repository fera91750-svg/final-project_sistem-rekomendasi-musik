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
        # Inisialisasi class induk dengan komponen dari engine
        super().__init__(
            self.music_engine.df, 
            self.music_engine.model, 
            self.music_engine.label_encoder
        )

    def chat(self, user_text: str, thread_id=None):
        # 1. Deteksi Mood secara internal melalui LLM
        mood_prompt = f"Berdasarkan teks: '{user_text}', pilih 1 mood: Happy, Sad, Calm, atau Tense."
        try:
            detected_mood = self.model.generate_content(mood_prompt).text.strip().capitalize()
            if detected_mood not in ["Happy", "Sad", "Calm", "Tense"]:
                detected_mood = "Happy"
        except:
            detected_mood = "Happy"

        # 2. Ambil data lagu dari music_engine (Database)
        # Kita ambil lagu DULU sebelum LLM menjawab agar sinkron
        songs_df = self.music_engine.get_recommendations_by_mood(detected_mood, n=5)
        
        songs_data = []
        info_lagu_untuk_llm = []
        
        if not songs_df.empty:
            for _, row in songs_df.iterrows():
                # Membuat HTML Spotify Embed menggunakan fungsi di music_engine
                spotify_html = self.music_engine.create_spotify_embed(row['track_id'])
                
                # Menyiapkan data LENGKAP untuk UI agar tidak KeyError
                songs_data.append({
                    "title": row["track_name"],
                    "artist": row["artists"],
                    "album": row.get("album_name", "Single"),
                    "genre": row.get("track_genre", "Music"),
                    "popularity": row.get("popularity", 0), # Ini untuk fix error popularity
                    "track_id": row["track_id"],
                    "embed_html": spotify_html
                })
                # Simpan list judul untuk didikte ke LLM
                info_lagu_untuk_llm.append(f"- {row['track_name']} oleh {row['artists']}")

        # 3. Minta LLM memberikan respon berdasarkan daftar lagu tersebut
        daftar_lagu_str = "\n".join(info_lagu_untuk_llm)
        final_prompt = f"""
        Jawab curhatan user ini sebagai teman yang chill (pake aku-kamu): "{user_text}"
        
        Kamu HARUS merekomendasikan lagu-lagu ini secara spesifik dalam jawabanmu:
        {daftar_lagu_str}
        
        Jangan sebutkan lagu lain selain daftar di atas agar sinkron dengan pemutar musik di bawah.
        """
        
        try:
            llm_response = self.model.generate_content(final_prompt).text.strip()
        except:
            llm_response = "Wah, aku denger kamu! Nih, ada beberapa lagu yang pas banget buat mood kamu saat ini."

        # 4. Return data lengkap ke UI
        return {
            "text": llm_response,
            "songs": songs_data,
            "mood": detected_mood
        }
