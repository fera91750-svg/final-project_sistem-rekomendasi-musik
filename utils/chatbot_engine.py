import sys
import os

# Menghubungkan ke folder data/music tempat llm_music_module berada
data_music_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'music')
sys.path.insert(0, data_music_folder)

from llm_music_module import MusicLLMChatbot

class MusicChatbot(MusicLLMChatbot):
    def __init__(self, music_engine):
        self.music_engine = music_engine
        # Tetap menggunakan inisialisasi asli dari llm_music_module Anda
        super().__init__(
            self.music_engine.df, 
            self.music_engine.model, 
            self.music_engine.label_encoder
        )

    def chat(self, user_text: str, thread_id=None):
        # 1. Panggil fungsi chat ASLI dari llm_music_module
        response = super().chat(user_text, thread_id)
        
        llm_text = response.get('text', "")
        llm_songs = response.get('songs', [])
        detected_mood = response.get('mood', 'Happy')

        # 2. Logika Anti-Duplikat dan Pengayaan Data
        enriched_songs = []
        seen_titles = set() # Melacak agar tidak ada judul yang sama muncul dua kali

        for s in llm_songs:
            # Ambil judul lagu dari LLM
            search_title = s.get('title') or s.get('track_name', "")
            if not search_title:
                continue
                
            clean_title = search_title.lower().strip()

            # Lewati jika lagu ini sudah pernah dimasukkan (Anti-Duplikat)
            if clean_title in seen_titles:
                continue

            # 3. Cari data lengkap di database asli (df)
            # Menggunakan sorting popularity agar jika ada duplikat di DB, diambil yang terbaik
            match = self.music_engine.df[
                (self.music_engine.df['track_name'].str.lower() == clean_title)
            ].sort_values(by='popularity', ascending=False).head(1)
            
            if not match.empty:
                row = match.iloc[0]
                enriched_songs.append({
                    "title": str(row["track_name"]),
                    "artist": str(row["artists"]),
                    "album": str(row.get("album_name", "Original Album")),
                    "genre": str(row.get("track_genre", "Music")),
                    "popularity": int(row.get("popularity", 0)),
                    "track_id": str(row["track_id"]) # WAJIB untuk Spotify Player
                })
                seen_titles.add(clean_title) # Tandai judul ini sudah diambil
            else:
                # Jika tidak ketemu di DF utama, berikan data fallback agar UI tidak error
                enriched_songs.append({
                    "title": s.get("title", "Unknown"),
                    "artist": s.get("artist", "Various Artists"),
                    "album": "Single",
                    "genre": "Music",
                    "popularity": s.get("popularity", 50),
                    "track_id": s.get("track_id", "")
                })

        # 4. Kirim kembali ke UI 1_Music.py dengan data yang sudah bersih
        return {
            "text": llm_text,
            "songs": enriched_songs,
            "mood": detected_mood
        }
