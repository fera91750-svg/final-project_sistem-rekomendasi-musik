import sys
import os

# Menghubungkan ke folder data/music
data_music_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'music')
sys.path.insert(0, data_music_folder)

from llm_music_module import MusicLLMChatbot

class MusicChatbot(MusicLLMChatbot):
    def __init__(self, music_engine):
        self.music_engine = music_engine
        # Tetap gunakan inisialisasi asli dari llm_music_module
        super().__init__(
            self.music_engine.df, 
            self.music_engine.model, 
            self.music_engine.label_encoder
        )

    def chat(self, user_text: str, thread_id=None):
        # 1. Panggil fungsi chat ASLI dari llm_music_module (Tanpa buat prompt baru)
        # Biarkan LLM menjalankan tugasnya seperti biasa
        response = super().chat(user_text, thread_id)
        
        # 2. Ambil hasil asli dari LLM
        llm_text = response.get('text', "")
        llm_songs = response.get('songs', []) # Lagu yang dipilih oleh LLM Anda
        detected_mood = response.get('mood', 'Happy')

        # 3. PERBAIKAN DATA: Agar UI tidak KeyError dan Embed Spotify Muncul
        enriched_songs = []
        for s in llm_songs:
            # Cari data lengkap lagu di database berdasarkan judul/artist
            # agar kita dapat 'track_id' untuk Spotify Embed
            match = self.music_engine.df[
                (self.music_engine.df['track_name'] == s['title'])
            ].head(1)
            
            if not match.empty:
                row = match.iloc[0]
                enriched_songs.append({
                    "title": row["track_name"],
                    "artist": row["artists"],
                    "album": row.get("album_name", "Album"), # Fix KeyError Album
                    "genre": row.get("track_genre", "Music"), # Fix KeyError Genre
                    "popularity": row.get("popularity", 0),   # Fix KeyError Popularity
                    "track_id": row["track_id"]               # UNTUK EMBED SPOTIFY
                })
            else:
                # Jika tidak ketemu di DF, kirim data apa adanya agar tidak crash
                s["album"] = s.get("album", "Original Mix")
                s["genre"] = s.get("genre", "Music")
                s["popularity"] = s.get("popularity", 0)
                enriched_songs.append(s)

        # 4. Kirim kembali ke UI 1_Music.py
        return {
            "text": llm_text,
            "songs": enriched_songs,
            "mood": detected_mood
        }
