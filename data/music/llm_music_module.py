"""
Music LLM Chatbot Module
Exported from Llm_Rf_music.ipynb for use in Streamlit app

This module contains the chatbot logic using LangChain + LangGraph + Gemini AI
"""

import os
import json
from matplotlib import text
import numpy as np
from typing import Dict, Any, List
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver


class MusicLLMChatbot:
    """
    Music recommendation chatbot using Gemini 2.5 Flash Lite
    """

    def __init__(self, music_df, model=None, label_encoder=None, api_key=None):
        """
        Initialize chatbot with music data and model

        Args:
            music_df: DataFrame with music data
            model: Trained ML model for mood prediction (optional)
            label_encoder: Label encoder for mood classes (optional)
            api_key: Google API key (optional, can use env var)
        """
        self.music_df = music_df
        self.model = model
        self.label_encoder = label_encoder
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.llm = None
        self.agent = None
        self.chat_history = []

        # System prompt (from notebook cell-22)
        self.system_prompt = """

Kamu adalah Chatbot Rekomendasi Musik berbasis Dataset.
Tugas utamamu adalah memahami cerita, konteks, dan kebutuhan user,
lalu memberikan rekomendasi lagu dari DATASET melalui tools yang tersedia.

Kamu BOLEH menjelaskan rekomendasi secara naratif dan manusiawi,
NAMUN kamu TIDAK BOLEH menyebut lagu atau artis yang tidak berasal dari dataset.

=================================================
🎧 ATURAN UTAMA
=================================================

1. Jika user:
   - mengekspresikan perasaan (sedih, bahagia, stres, capek, patah hati)
   - atau menyebut aktivitas (belajar, kerja, santai, istirahat)

   Maka:
   - Pahami konteks dan cerita user terlebih dahulu
   - Tentukan satu mood utama: Sad, Happy, Calm, atau Tense
   - WAJIB memanggil tool: recommend_music(mood)

2. Setelah tool selesai:
   - Berikan 1–2 kalimat penjelasan singkat tentang
     KENAPA mood tersebut cocok untuk kondisi user
   - Lalu tampilkan SEMUA hasil rekomendasi lagu dari tool
   - Tutup dengan 1 kalimat empatik yang alami

3. Semua judul lagu, artis, dan metadata:
   - HARUS 100% berasal dari hasil tool
   - DILARANG mengarang atau menambahkan lagu di luar dataset

=================================================
🎧 KAMU BOLEH
=================================================
- Menjelaskan karakter musik secara UMUM
  (misalnya: tempo tenang, energi rendah, cocok untuk fokus)
- Menyesuaikan bahasa dengan cerita user
- Mengelompokkan rekomendasi berdasarkan konteks (belajar, semangat, santai)

=================================================
🎧 KAMU DILARANG
=================================================
- Menyebut artis atau lagu dari pengetahuan pribadi
- Memberi rekomendasi tanpa memanggil tool
- Menjawab topik non-musik (cuaca, politik, sejarah, teknologi)
- Mengurangi atau melewatkan hasil rekomendasi dari tool

=================================================
🎧 DETEKSI MOOD OTOMATIS
=================================================
Sad   → sedih, galau, patah hati, kecewa, ditinggal
Happy → senang, bahagia, semangat, excited
Calm  → capek, ingin tenang, belajar, fokus, santai, relax
Tense → stres, cemas, panik, pusing, deadline

=================================================
🎧 FORMAT OUTPUT WAJIB
=================================================

[1–2 kalimat penjelasan singkat sesuai cerita user]

**Rekomendasi Lagu untuk Mood [Mood]:**

1. **[Judul Lagu]** – [Artis]  
   Genre: [genre] | Popularity: [angka]

2. **[Judul Lagu]** – [Artis]  
   Genre: [genre] | Popularity: [angka]

3. **[Judul Lagu]** – [Artis]  
   Genre: [genre] | Popularity: [angka]

4. **[Judul Lagu]** – [Artis]  
   Genre: [genre] | Popularity: [angka]

5. **[Judul Lagu]** – [Artis]  
   Genre: [genre] | Popularity: [angka]

[1 kalimat empatik penutup, singkat dan manusiawi]

=================================================
🎧 GAYA BAHASA
=================================================
- Gunakan bahasa yang sama dengan user
- Hangat, natural, seperti asisten pribadi
- Tidak lebay
- Tidak kaku
- Tetap profesional dan informatif

=================================================
🎧 MISI UTAMA
=================================================
Memberikan rekomendasi musik berbasis dataset
yang relevan dengan kondisi dan cerita user,
dengan penjelasan yang alami dan mudah dipahami.
"""

        # Initialize if API key available
        if self.api_key:
            self._initialize_llm()

    def _initialize_llm(self):
        """Initialize LLM and agent"""
        try:
            # Initialize Gemini 2.5 Flash (free tier compatible)
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash-lite",
                temperature=0.3,
                api_key=self.api_key,
                thinking_budget=0,      # Disable thinking to prevent internal reasoning exposure
                include_thoughts=False  # Ensure thoughts are not included in response
            )

            # Create tools
            tools = self._create_tools()

            # Build LangGraph agent
            self.agent = self._build_agent(tools)

            return True
        except Exception as e:
            print(f"Error initializing LLM: {e}")
            return False

    def _create_tools(self):
        """Create LangChain tools for the chatbot"""
        @tool
        def predict_mood(features_json: str) -> Dict[str, Any]:
            """Prediksi mood lagu berdasarkan fitur audio dalam format JSON."""
            order = [
                'danceability', 'energy', 'valence', 'tempo', 'acousticness',
                'instrumentalness', 'loudness', 'speechiness'
            ]

            try:
                data = json.loads(features_json)
                x = np.array([float(data[f]) for f in order]).reshape(1, -1)

                # Use model if available, otherwise rule-based
                if self.model is not None and self.label_encoder is not None:
                    pred = self.model.predict(x)[0]
                    mood = self.label_encoder.inverse_transform([pred])[0]
                else:
                    # Rule-based fallback
                    valence = float(data['valence'])
                    energy = float(data['energy'])

                    if valence >= 0.5 and energy >= 0.5:
                        mood = 'Happy'
                    elif valence < 0.5 and energy < 0.5:
                        mood = 'Sad'
                    elif valence >= 0.5 and energy < 0.5:
                        mood = 'Calm'
                    else:
                        mood = 'Tense'

                return {"predicted_mood": mood}
            except Exception as e:
                return {"error": f"Error predicting mood: {str(e)}"}

        @tool
        def recommend_music(mood: str) -> Dict[str, Any]:
            """Rekomendasi 5 lagu berdasarkan mood tertentu."""
            try:
                mood = mood.strip().capitalize()

                # Validate mood
                valid_moods = ['Happy', 'Sad', 'Calm', 'Tense']
                if mood not in valid_moods:
                    return {"error": f"Mood harus salah satu dari: {', '.join(valid_moods)}"}

                # Get recommendations from dataset
                mood_songs = self.music_df[self.music_df['mood'] == mood].copy()

                if mood_songs.empty:
                    return {"error": f"Tidak ada lagu dengan mood {mood}."}

                # Sort by popularity and get top 5
                recommendations = mood_songs.nlargest(5, 'popularity')

                # Format results
                songs = []
                for _, row in recommendations.iterrows():
                    songs.append({
                        "title": row['track_name'],
                        "artist": row['artists'],
                        "album": row.get('album_name', 'Unknown Album'),
                        "genre": row['track_genre'],
                        "popularity": int(row['popularity']),
                        "track_id": row['track_id']
                    })

                return {"recommendations": songs}
            except Exception as e:
                return {"error": f"Error getting recommendations: {str(e)}"}

        return [predict_mood, recommend_music]

    def _build_agent(self, tools):
        """Build LangGraph agent workflow"""

        class AgentState(dict):
            messages: list

        tool_node = ToolNode(tools)

        def call_llm(state: AgentState):
            """Call LLM with system prompt and messages"""
            messages = state["messages"]

            # Add system prompt if first message
            if len(messages) == 0 or not isinstance(messages[0], SystemMessage):
                messages = [SystemMessage(content=self.system_prompt)] + messages

            # Bind tools to LLM
            llm_with_tools = self.llm.bind_tools(tools)
            response = llm_with_tools.invoke(messages)

            return {"messages": [response]}

        def should_continue(state: AgentState):
            """Check if we should continue or end"""
            messages = state["messages"]
            last_message = messages[-1]

            # If LLM makes a tool call, continue to tools
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                return "tools"
            # Otherwise end
            return END

        # Build graph
        workflow = StateGraph(MessagesState)

        # Add nodes
        workflow.add_node("agent", call_llm)
        workflow.add_node("tools", tool_node)

        # Set entry point
        workflow.add_edge(START, "agent")

        # Add conditional edges
        workflow.add_conditional_edges("agent", should_continue, ["tools", END])
        workflow.add_edge("tools", "agent")

        # Compile with memory
        memory = MemorySaver()
        app = workflow.compile(checkpointer=memory)

        return app

    def is_music_related(self, text: str) -> bool:
        """Check if query is music-related"""
        keywords = [
            "musik", "lagu", "song", "music", "rekomendasi", "recommend",
            "sedih", "senang", "happy", "sad", "calm", "tense", "galau",
            "mood", "genre", "artist", "album", "spotify"
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in keywords)

    def chat(self, user_message: str, thread_id: str = "default") -> Dict[str, Any]:
        """
        Main chat function

        Args:
            user_message: User's message
            thread_id: Thread ID for conversation (default: "default")

        Returns:
            Dictionary with 'text' and optionally 'songs' (full song data)
        """
        if not self.llm or not self.agent:
            return {"text": "Error: Chatbot belum diinisialisasi. Pastikan GOOGLE_API_KEY sudah diset."}

        # Check if music-related
        if not self.is_music_related(user_message):
            return {"text": "Maaf, saya hanya dapat membantu rekomendasi musik berdasarkan mood. Coba tanya tentang musik yuk! 🎵"}

        try:
            # Invoke agent
            config = {"configurable": {"thread_id": thread_id}}
            result = self.agent.invoke(
                {"messages": [HumanMessage(content=user_message)]},
                config=config
            )

            # Get last message
            last_message = result["messages"][-1]
            response_text = last_message.content

            # Extract full song data from tool results
            songs = []
            for message in result["messages"]:
                if isinstance(message, ToolMessage):
                    # Check if this is a recommend_music tool result
                    try:
                        # Parse the tool result
                        tool_result = json.loads(message.content)
                        if "recommendations" in tool_result:
                            # Extract full song data from recommendations
                            for song in tool_result["recommendations"]:
                                songs.append({
                                    "title": song.get("title", "Unknown"),
                                    "artist": song.get("artist", "Unknown Artist"),
                                    "album": song.get("album", "Unknown Album"),
                                    "genre": song.get("genre", "Unknown"),
                                    "popularity": song.get("popularity", 0),
                                    "track_id": song.get("track_id", "")
                                })
                    except (json.JSONDecodeError, TypeError, KeyError):
                        # If parsing fails, skip this message
                        continue

            # Return both text and full song data
            response = {"text": response_text}
            if songs:
                response["songs"] = songs

            return response

        except Exception as e:
            return {"text": f"Maaf, terjadi error: {str(e)}"}

    def clear_history(self):
        """Clear chat history"""
        self.chat_history = []


# Convenience function for easy import
def create_chatbot(music_df, model=None, label_encoder=None, api_key=None):
    """
    Create a music chatbot instance

    Args:
        music_df: DataFrame with music data
        model: Trained ML model (optional)
        label_encoder: Label encoder (optional)
        api_key: Google API key (optional)

    Returns:
        MusicLLMChatbot instance
    """
    return MusicLLMChatbot(music_df, model, label_encoder, api_key)
