import sys
import os

# Menghubungkan ke folder data/music
data_music_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'music')
sys.path.insert(0, data_music_folder)

from llm_music_module import MusicLLMChatbot

class MusicChatbot(MusicLLMChatbot):
    def __init__(self, music_engine):
        self.music_engine = music_engine
        # Inisialisasi class induk
        super().__init__(
            self.music_engine.df, 
            self.music_engine.model, 
            self.music_engine.label_encoder
        )

    def chat(self, user_text: str, thread_id=None):
        # 1. Langkah Pertama: Deteksi Mood
        # Kita minta AI menentukan mood saja dari chat user
        mood_prompt = f"Berdasarkan teks ini: '{user_text}', pilih satu mood musik: Happy, Sad, Calm, atau Tense. Jawab HANYA 1 kata mood saja."
        try:
            detected_mood = self.model.generate_content(mood_prompt).text.strip().capitalize()
            if detected_mood not in ["Happy", "Sad", "Calm", "Tense"]:
                detected_mood = "Happy"
        except:
            detected_mood = "Happy"

        # 2. Langkah Kedua: Ambil lagu dari DATABASE (Sama dengan yang dipakai UI)
        # Kita ambil 3-5 lagu berdasarkan mood yang dideteksi
        songs_df = self.music_engine.get_recommendations_by_mood(detected_mood, n=3)
        
        songs_data = []
        list_judul_untuk_ai = []
        
        if not songs_df.empty:
            for _, row in songs_df.iterrows():
                # Masukkan ke list untuk UI (Agar Player Muncul)
                songs_data.append({
                    "title": row["track_name"],
                    "artist": row["artists"],
                    "album": row.get("album_name", "Original Album"),
                    "genre": row.get("track_genre", "Music"),
                    "popularity": row.get("popularity", 0),
                    "track_id": row["track_id"]
                })
                # Masukkan ke list untuk didiktekan ke AI
                list_judul_untuk_ai.append(f"- {row['track_name']} oleh {row['artists']}")

        # 3. Langkah Ketiga: Suruh AI merespon menggunakan lagu TERSEBUT
        daftar_lagu_str = "\n".join(list_judul_untuk_ai)
        final_prompt = f"""
        Kamu adalah teman curhat yang chill (pake aku-kamu).
        User curhat: "{user_text}"
        Mood yang cocok: {detected_mood}
        
        TUGAS KAMU:
        1. Berikan kalimat penyemangat/respon yang sesuai dengan curhatan user.
        2. Sebutkan bahwa kamu merekomendasikan lagu-lagu ini:
        {daftar_lagu_str}
        
        PENTING: JANGAN menyebutkan lagu lain selain daftar di atas agar sinkron dengan pemutar musik!
        """
        
        try:
            llm_response = self.model.generate_content(final_prompt).text.strip()
        except:
            llm_response = f"Wah, aku dengerin curhatan kamu. Kayaknya lagu {detected_mood} pas banget nih buat nemenin kamu sekarang!"

        # 4. Return data ke 1_Music.py
        return {
            "text": llm_response,
            "songs": songs_data, # Data ini yang akan dibaca UI untuk bikin Embed Spotify
            "mood": detected_mood
        }
