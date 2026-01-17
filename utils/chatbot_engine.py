"""
Music Chatbot Engine for Streamlit
Versi: Anti-Duplikat & Reset Konteks Jawaban
"""

import sys
import os
import pandas as pd

# 1. Pastikan folder data/music terdaftar di sistem path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
data_music_folder = os.path.join(project_root, 'data', 'music')

if data_music_folder not in sys.path:
    sys.path.insert(0, data_music_folder)

# 2. Import modul LLM asli
try:
    from llm_music_module import MusicLLMChatbot, create_chatbot
except ImportError as e:
    # Fallback jika struktur folder berbeda di server
    from data.music.llm_music_module import MusicLLMChatbot, create_chatbot

class MusicChatbot(MusicLLMChatbot):
    """
    Wrapper khusus Streamlit yang mewarisi fungsi LLM
    dengan tambahan filter track_id dan pembersihan teks history.
    """

    def __init__(self, music_engine):
        # Menyimpan engine untuk akses database utama
        self.engine = music_engine
        
        # Inisialisasi parent class (MusicLLMChatbot)
        super().__init__(
            music_engine.df, 
            music_engine.model, 
            music_engine.label_encoder
        )

  def chat(self, user_message: str, thread_id: str = "default") -> Dict[str, Any]:
        """
        Fungsi chat di chatbot_engine.py yang menggunakan track_id 
        untuk memastikan tidak ada duplikasi lagu.
        """
        if not self.llm or not self.agent:
            return {"text": "Error: Chatbot belum diinisialisasi."}

        if not self.is_music_related(user_message):
            return {"text": "Maaf, saya hanya dapat membantu rekomendasi musik berdasarkan mood."}

        try:
            config = {"configurable": {"thread_id": thread_id}}
            result = self.agent.invoke(
                {"messages": [HumanMessage(content=user_message)]},
                config=config
            )

            last_message = result["messages"][-1]
            response_text = last_message.content

            # --- FILTER DUPLIKAT MENGGUNAKAN TRACK_ID ---
            songs = []
            seen_track_ids = set() # Menggunakan ID unik sebagai filter

            for message in result["messages"]:
                if isinstance(message, ToolMessage):
                    try:
                        tool_result = json.loads(message.content)
                        if "recommendations" in tool_result:
                            for song in tool_result["recommendations"]:
                                tid = song.get("track_id")
                                
                                # Cek apakah track_id sudah pernah dimasukkan
                                if tid and tid not in seen_track_ids:
                                    songs.append({
                                        "title": song.get("title", "Unknown"),
                                        "artist": song.get("artist", "Unknown Artist"),
                                        "album": song.get("album", "Unknown Album"),
                                        "genre": song.get("genre", "Unknown"),
                                        "popularity": song.get("popularity", 0),
                                        "track_id": tid
                                    })
                                    seen_track_ids.add(tid)
                    except:
                        continue

            # Ambil 5 lagu pertama yang unik secara ID
            songs = songs[:5]

            return {
                "text": response_text,
                "songs": songs
            }

        except Exception as e:
            return {"text": f"Maaf, terjadi error: {str(e)}"}

# Export agar bisa dipanggil di main.py atau 1_Music.py
__all__ = ['MusicChatbot', 'create_chatbot']
