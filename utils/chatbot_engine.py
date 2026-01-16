import sys
import os

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
        # 1. Ambil respon asli dari LLM
        response = super().chat(user_text, thread_id)
        
        llm_songs = response.get('songs', [])
        detected_mood = response.get('mood', 'Happy')
        
        enriched_songs = []
        seen_titles = set()
        
        # 2. Filter lagu agar benar-benar unik
        for s in llm_songs:
            t = s.get('title') or s.get('track_name', "")
            clean_t = str(t).strip().lower()

            if clean_t in seen_titles or not clean_t:
                continue

            match = self.music_engine.df[
                self.music_engine.df['track_name'].str.lower() == clean_t
            ].drop_duplicates('track_name').sort_values('popularity', ascending=False).head(1)
            
            if not match.empty:
                row = match.iloc[0]
                enriched_songs.append({
                    "title": str(row["track_name"]),
                    "artist": str(row["artists"]),
                    "album": str(row.get("album_name", "Album")),
                    "genre": str(row.get("track_genre", "Music")),
                    "popularity": int(row.get("popularity", 0)),
                    "track_id": str(row["track_id"])
                })
                seen_titles.add(clean_t)

        # 3. SUSUN ULANG TEKS JAWABAN (Agar teks tidak duplikat)
        # Kita buat teks baru berdasarkan list yang sudah difilter
        new_text = f"**Rekomendasi Lagu untuk Mood {detected_mood}:**\n"
        for i, song in enumerate(enriched_songs, 1):
            new_text += f"{i}. {song['title']} - {song['artist']} | Popularity: {song['popularity']}\n"
        
        new_text += "\nSemoga lagu-lagu ini bisa nemenin kamu ya ✨"

        return {
            "text": new_text, # Menggunakan teks yang sudah dibersihkan
            "songs": enriched_songs,
            "mood": detected_mood
        }
