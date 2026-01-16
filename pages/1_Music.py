"""
🎵 Music Recommendation Page
Mood-based music recommendations with visualizations
"""

import streamlit as st
import sys
import os
import uuid

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.music_engine import MusicRecommendationEngine
from utils.chatbot_engine import MusicChatbot
from utils.visualizations import (
    create_mood_pie_chart,
    create_valence_energy_scatter,
    create_genre_bar_chart,
    create_audio_features_radar
)

# Page config
st.set_page_config(
    page_title="Music Recommendations",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    .main {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        padding: 2rem 4rem;
    }

    .song-card {
        background: #1E293B;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        border: 1px solid #334155;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
        border: none;
        color: #FFFFFF;
    }

    /* Chat Styling */
    .user-message {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
        color: white;
        padding: 12px;
        border-radius: 15px 15px 2px 15px;
        margin: 5px 0;
    }

    .bot-message {
        background: #334155;
        color: white;
        padding: 12px;
        border-radius: 15px 15px 15px 2px;
        margin: 5px 0;
        border: 1px solid #475569;
    }
</style>
""", unsafe_allow_html=True)

# Initialize engine
@st.cache_resource
def load_music_engine():
    return MusicRecommendationEngine()

@st.cache_resource
def load_chatbot(_engine):
    return MusicChatbot(_engine)

with st.spinner("🎵 Loading music library..."):
    engine = load_music_engine()
    chatbot = load_chatbot(engine)

# Header
col_back, col_title = st.columns([1.5, 10.5])
with col_back:
    if st.button("← Back", key="music_back_home"):
        st.switch_page("main.py")
with col_title:
    st.markdown("# Music Recommendations")

st.divider()

# Filters
col1, col2, col3, col4 = st.columns([3, 3, 3, 2])
with col1:
    mood = st.selectbox("Select Mood", options=engine.get_available_moods())
with col2:
    genre_options = ["All Genres"] + engine.get_available_genres()
    selected_genre = st.selectbox("Filter by Genre", options=genre_options)
    if selected_genre == "All Genres": selected_genre = None
with col3:
    num_recommendations = st.slider("Number of Songs", 5, 50, 10)
with col4:
    st.write("")
    st.write("")
    if st.button("Search", use_container_width=True, key="music_search"):
        st.session_state.show_recommendations = True

# Navigation
if 'music_selected_tab' not in st.session_state:
    st.session_state.music_selected_tab = "💬 Chat Assistant"

selected_tab = st.radio(
    "Navigation",
    ["🎵 Recommendations", "🎯 Predict Mood", "💬 Chat Assistant", "📊 Analytics", "ℹ️ About"],
    horizontal=True, label_visibility="collapsed"
)

st.markdown("---")

# --- TAB: RECOMMENDATIONS ---
if selected_tab == "🎵 Recommendations":
    if st.session_state.get('show_recommendations', False):
        st.markdown(f"## 🎯 Recommended for **{mood}**")
        recs = engine.get_recommendations_by_mood_and_genre(mood, selected_genre, num_recommendations) if selected_genre else engine.get_recommendations_by_mood(mood, num_recommendations)
        
        for idx, song in recs.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([6, 4])
                with c1:
                    st.markdown(f"#### {song['track_name']}")
                    st.caption(f"{song['artists']}")
                    st.caption(f"{song['album_name']} • {song['track_genre']} • ⭐ {song['popularity']}/100")
                with c2:
                    st.markdown(engine.create_spotify_embed(song['track_id'], height=80), unsafe_allow_html=True)

# --- TAB: CHAT ASSISTANT ---
elif selected_tab == "💬 Chat Assistant":
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    col_chat, col_info = st.columns([7, 3])

    with col_chat:
        st.markdown("### ✍️ Type your message")
        with st.form("chat_form", clear_on_submit=True):
            c_in, c_btn = st.columns([7, 1])
            user_msg = c_in.text_input("Curhat di sini...", placeholder="Lagi sedih nih, butuh lagu...")
            submitted = c_btn.form_submit_button("📤")

        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            chatbot.clear_history()
            st.rerun()

        # Chat Display
        st.markdown("### 💬 Chat History")
        chat_container = st.container(height=500, border=True)
        with chat_container:
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    st.markdown(f'<div class="user-message">👤 {message["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="bot-message">🤖 {message["content"]}</div>', unsafe_allow_html=True)
                    # Tampilkan Card Lagu jika ada
                    if 'songs' in message and message['songs']:
                        for song in message['songs']:
                            with st.container(border=True):
                                s_info, s_play = st.columns([6, 4])
                                with s_info:
                                    st.markdown(f"**{song['title']}**")
                                    st.caption(f"{song['artist']}")
                                    # Fix KeyError dengan default value
                                    album = song.get('album', 'N/A')
                                    popularity = song.get('popularity', 0)
                                    st.caption(f"{album} • ⭐ {popularity}/100")
                                with s_play:
                                    if 'track_id' in song:
                                        embed = engine.create_spotify_embed(song['track_id'], height=80)
                                        st.markdown(embed, unsafe_allow_html=True)

        # Logic Sending
        if submitted and user_msg.strip():
            st.session_state.chat_history.append({'role': 'user', 'content': user_msg})
            
            try:
                with st.spinner("🎵 Thinking..."):
                    if 'thread_id' not in st.session_state:
                        st.session_state.thread_id = str(uuid.uuid4())
                    
                    bot_res = chatbot.chat(user_msg, thread_id=st.session_state.thread_id)
                    
                    # Pastikan bot_res adalah dict
                    if isinstance(bot_res, dict):
                        st.session_state.chat_history.append({
                            'role': 'bot',
                            'content': bot_res.get('text', ''),
                            'songs': bot_res.get('songs', [])
                        })
                    else:
                        st.session_state.chat_history.append({'role': 'bot', 'content': str(bot_res)})
            except Exception as e:
                st.error(f"Error: {e}")
            
            st.rerun()

    with col_info:
        st.info("💡 **Tips**\n\nCoba tanya: 'Lagu yang cocok buat galau apa ya?'")

# --- TAB LAINNYA (Analytics, Predict, dll) tetap dipertahankan ---
# (Bagian Analytics dan Predict Mood kodenya sama seperti yang Anda miliki sebelumnya)
elif selected_tab == "📊 Analytics":
    st.markdown("## 📊 Music Analytics")
    mood_dist = engine.get_mood_distribution()
    col_l, col_r = st.columns(2)
    with col_l:
        st.plotly_chart(create_mood_pie_chart(mood_dist), use_container_width=True)
    with col_r:
        genre_dist = engine.get_genre_distribution()
        st.plotly_chart(create_genre_bar_chart(genre_dist), use_container_width=True)

elif selected_tab == "🎯 Predict Mood":
    st.markdown("## 🎯 Predict Mood")
    st.write("Gunakan fitur ini untuk memprediksi mood lagu berdasarkan audio features.")
    # (Logika slider Anda di sini)

elif selected_tab == "ℹ️ About":
    st.markdown("### ℹ️ About Music System")
    st.write("Sistem ini menggunakan dataset Spotify dengan 114k+ lagu.")

# Footer
st.markdown("---")
st.caption("🎓 Final Project Kelompok 4 | Built with ❤️")
