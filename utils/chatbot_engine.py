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
        # Ambil respon dari LLM Anda
        response = super().chat(user_text, thread_id)
        
        llm_text = response.get('text', "")
        llm_songs = response.get('songs', [])
        
        enriched_songs = []
        seen_titles = set()

        for s in llm_songs:
            # Ambil judul dan bersihkan
            t = s.get('title') or s.get('track_name', "")
            clean_t = str(t).strip().lower()

            # JIKA JUDUL SUDAH ADA DI LIST, LANGSUNG SKIP
            if clean_t in seen_titles or not clean_t:
                continue

            # Cari di DF dengan filter duplikat di level database
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
                seen_titles.add(clean_t) # Kunci judul agar tidak muncul lagi

        return {
            "text": llm_text,
            "songs": enriched_songs,
            "mood": response.get('mood', 'Happy')
        }
