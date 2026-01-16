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
        
        llm_text = response.get('text', "")
        llm_songs = response.get('songs', [])
        mood = response.get('mood', 'Normal')

        # Jika tidak ada lagu yang direkomendasikan (ngobrol biasa), 
        # langsung kembalikan teks asli LLM agar tidak terjadi pengulangan.
        if not llm_songs:
            return response

        # 2. Jika ada lagu, lakukan filter anti-duplikat
        enriched_songs = []
        seen_titles = set()
        
        for s in llm_songs:
            title = s.get('title') or s.get('track_name', "")
            clean_t = str(title).strip().lower()

            if clean_t in seen_titles or not clean_t:
                continue

            # Cari di Database, ambil yang paling populer
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

        # 3. Susun teks baru HANYA jika ada lagu yang ditemukan
        if enriched_songs:
            final_text = f"**Rekomendasi Lagu untuk Mood {mood}:**\n\n"
            for i, song in enumerate(enriched_songs, 1):
                final_text += f"{i}. **{song['title']}** - {song['artist']} (Popularity: {song['popularity']})\n"
            final_text += "\nSemoga lagu-lagu ini bisa menemani harimu! ✨"
        else:
            # Jika proses filter menghasilkan list kosong, gunakan teks asli
            final_text = llm_text

        return {
            "text": final_text,
            "songs": enriched_songs,
            "mood": mood
        }
