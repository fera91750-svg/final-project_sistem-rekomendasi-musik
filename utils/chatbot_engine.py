import sys
import os

# Menghubungkan ke folder data/music
data_music_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'music')
sys.path.insert(0, data_music_folder)

from llm_music_module import MusicLLMChatbot

class MusicChatbot(MusicLLMChatbot):
    def __init__(self, music_engine):
        self.music_engine = music_engine
        # Gunakan inisialisasi asli
        super().__init__(
            self.music_engine.df, 
            self.music_engine.model, 
            self.music_engine.label_encoder
        )

    def chat(self, user_text: str, thread_id=None):
        # 1. Panggil fungsi chat asli LLM Anda
        response = super().chat(user_text, thread_id)
        
        llm_text = response.get('text', "")
        llm_songs = response.get('songs', [])
        detected_mood = response.get('mood', 'Happy')

        # 2. Mapping data agar SESUAI dengan kebutuhan 1_Music.py
        enriched_songs = []
        for s in llm_songs:
            # Ambil judul lagu (bisa dari key 'title' atau 'track_name')
            title_to_search = s.get('title') or s.get('track_name')
            
            # Cari data lengkap di database asli (df) untuk mendapatkan track_id
            match = self.music_engine.df[
                (self.music_engine.df['track_name'].str.lower() == title_to_search.lower())
            ].head(1)
            
            if not match.empty:
                row = match.iloc[0]
                # Format ini WAJIB sama dengan yang dibaca di 1_Music.py baris 632-646
                enriched_songs.append({
                    "title": str(row["track_name"]),
                    "artist": str(row["artists"]),
                    "album": str(row.get("album_name", "Original Album")),
                    "genre": str(row.get("track_genre", "Music")),
                    "popularity": int(row.get("popularity", 0)),
                    "track_id": str(row["track_id"]) # Ini kunci agar embed muncul
                })

        # 3. Kirim balik hasil yang sudah diperkaya
        return {
            "text": llm_text,
            "songs": enriched_songs, # List ini yang akan memicu card muncul di UI
            "mood": detected_mood
        }
