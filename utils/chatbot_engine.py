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
        # Jalankan logika asli LLM Anda
        response = super().chat(user_text, thread_id)
        
        llm_text = response.get('text', "")
        llm_songs = response.get('songs', [])
        detected_mood = response.get('mood', 'Happy')

        enriched_songs = []
        for s in llm_songs:
            # Ambil judul lagu dari LLM
            search_name = s.get('title') or s.get('track_name', "")
            
            # Cari di DF asli (Gunakan contains agar lebih fleksibel)
            match = self.music_engine.df[
                self.music_engine.df['track_name'].str.contains(search_name, case=False, na=False)
            ].head(1)
            
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
        
        return {
            "text": llm_text,
            "songs": enriched_songs,
            "mood": detected_mood
        }
