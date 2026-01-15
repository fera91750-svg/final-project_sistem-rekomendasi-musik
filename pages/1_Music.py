"""
🎵 Music Recommendation Page
Mood-based music recommendations with visualizations
"""

import streamlit as st
import sys
import os

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
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Music Recommendations",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Professional color scheme
st.markdown("""
<style>
    /* Hide sidebar & Streamlit elements */
    [data-testid="stSidebar"] { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* Global styles */
    .main {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        padding: 2rem 4rem;
    }

    /* Header */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #334155;
    }

    h1 {
        color: #F1F5F9;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }

    /* Filter section */
    .stSelectbox, .stSlider {
        background-color: transparent;
    }

    /* Cards */
    .song-card {
        background: #1E293B;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        transition: all 0.2s;
        border: 1px solid #334155;
    }

    .song-card:hover {
        background: #334155;
        border-color: #6366F1;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        border-bottom: 1px solid #334155;
    }

    .stTabs [data-baseweb="tab"] {
        color: #94A3B8;
        font-weight: 600;
        padding: 0.5rem 0;
    }

    .stTabs [aria-selected="true"] {
        color: #F1F5F9;
        border-bottom: 2px solid #6366F1;
    }

    /* Buttons */
    .stButton > button {
        background-color: transparent;
        color: #000000;
        border: 1px solid #475569;
        border-radius: 500px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s;
    }

    .stButton > button:hover {
        border-color: #6366F1;
        transform: scale(1.02);
    }

    /* Primary button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
        border: none;
        color: #000000;
    }

    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%);
    }
</style>
""", unsafe_allow_html=True)

# Header with back button
col_back, col_title = st.columns([1.5, 10.5])
with col_back:
    st.write("")
    st.write("")  # Double spacing
    if st.button("← Back", key="music_back_home"):
        st.switch_page("main.py")
with col_title:
    st.markdown("# Music Recommendations")

st.divider()

# Initialize engine
@st.cache_resource
def load_music_engine():
    return MusicRecommendationEngine()

@st.cache_resource
def load_chatbot(_engine):
    """Initialize chatbot with music engine"""
    return MusicChatbot(_engine)

with st.spinner("🎵 Loading music library..."):
    engine = load_music_engine()
    chatbot = load_chatbot(engine)

# Filters
st.write("")  # Spacing
col1, col2, col3, col4 = st.columns([3, 3, 3, 2])

with col1:
    mood = st.selectbox("Select Mood", options=engine.get_available_moods(), label_visibility="visible")

with col2:
    genre_options = ["All Genres"] + engine.get_available_genres()
    selected_genre = st.selectbox("Filter by Genre", options=genre_options, label_visibility="visible")
    if selected_genre == "All Genres":
        selected_genre = None

with col3:
    num_recommendations = st.slider("Number of Songs", min_value=5, max_value=50, value=10, step=5, label_visibility="visible")

with col4:
    st.write("")
    st.write("")  # Double spacing to align button
    if st.button("Search", use_container_width=True, key="music_search"):
        st.session_state.show_recommendations = True

st.write("")
st.write("")

# Main content - Tab navigation using radio buttons (persists state)
if 'music_selected_tab' not in st.session_state:
    st.session_state.music_selected_tab = "💬 Chat Assistant"

selected_tab = st.radio(
    "Navigation",
    ["🎵 Recommendations", "🎯 Predict Mood", "💬 Chat Assistant", "📊 Analytics", "ℹ️ About"],
    horizontal=True,
    label_visibility="collapsed",
    key="music_tab_selector",
    index=["🎵 Recommendations", "🎯 Predict Mood", "💬 Chat Assistant", "📊 Analytics", "ℹ️ About"].index(st.session_state.music_selected_tab)
)
st.session_state.music_selected_tab = selected_tab

st.markdown("---")  # Separator line

# Show content based on selection
if selected_tab == "🎵 Recommendations":
    st.markdown("## 🎵 Music Recommendations")
    st.write("")
    if st.session_state.get('show_recommendations', False):
        st.markdown(f"## 🎯 Recommended Songs for **{mood}** Mood")

        # Get recommendations
        if selected_genre:
            recommendations = engine.get_recommendations_by_mood_and_genre(
                mood, selected_genre, num_recommendations
            )
            if recommendations.empty:
                st.warning(f"No songs found for {mood} mood and {selected_genre} genre. Try different filters.")
        else:
            recommendations = engine.get_recommendations_by_mood(mood, num_recommendations)

        if not recommendations.empty:
            st.success(f"Found {len(recommendations)} songs!")

            # Display songs - Spotify-inspired minimal design
            for idx, song in recommendations.iterrows():
                with st.container(border=True):
                    col_info, col_player_section = st.columns([6, 4])

                    with col_info:
                        # Spotify style: Title, gray artist, compact details
                        st.markdown(f"#### {song['track_name']}")
                        st.caption(f"{song['artists']}")
                        st.caption(f"{song['album_name']} • {song['track_genre']} • {song['mood']} • ⭐ {song['popularity']}/100")

                    with col_player_section:
                        # Vertical centering
                        st.write("")
                        # Spotify player
                        track_id = song['track_id']
                        spotify_embed = engine.create_spotify_embed(track_id, width=350, height=80)
                        st.markdown(spotify_embed, unsafe_allow_html=True)

            # Download button
            st.markdown("---")
            csv = recommendations.to_csv(index=False)
            st.download_button(
                label="📥 Download Playlist (CSV)",
                data=csv,
                file_name=f"{mood}_mood_playlist.csv",
                mime="text/csv",
                use_container_width=True
            )
    else:
        st.info("👈 Select your mood and click 'Get Recommendations' to see personalized song suggestions!")

        # Show sample stats
        st.markdown("### 📊 Quick Stats")
        col1, col2, col3 = st.columns(3)

        mood_dist = engine.get_mood_distribution()
        with col1:
            st.metric("Happy Songs", f"{mood_dist.get('Happy', 0):,}")
        with col2:
            st.metric("Sad Songs", f"{mood_dist.get('Sad', 0):,}")
        with col3:
            st.metric("Calm Songs", f"{mood_dist.get('Calm', 0):,}")

elif selected_tab == "🎯 Predict Mood":
    st.markdown("## 🎯 Prediksi Mood Manual")
    st.info("Ubah slider di bawah untuk melihat bagaimana model memprediksi mood.")

    st.write("")

    # Audio features sliders
    col1, col2, col3 = st.columns(3)

    with col1:
        danceability = st.slider(
            "Danceability",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.01,
            help="How suitable a track is for dancing (0.0 = least danceable, 1.0 = most danceable)"
        )

    with col2:
        energy = st.slider(
            "Energy",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.01,
            help="Intensity and activity level (0.0 = calm, 1.0 = energetic)"
        )

    with col3:
        valence = st.slider(
            "Valence",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.01,
            help="Musical positiveness (0.0 = sad/negative, 1.0 = happy/positive)"
        )

    st.write("")

    col4, col5, col6 = st.columns(3)

    with col4:
        acousticness = st.slider(
            "Acousticness",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.01,
            help="Confidence that the track is acoustic (0.0 = not acoustic, 1.0 = acoustic)"
        )

    with col5:
        instrumentalness = st.slider(
            "Instrumentalness",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.01,
            help="Predicts whether a track contains no vocals (0.0 = vocals, 1.0 = instrumental)"
        )

    with col6:
        tempo = st.slider(
            "Tempo (BPM)",
            min_value=0,
            max_value=250,
            value=120,
            step=1,
            help="Overall tempo in beats per minute (BPM)"
        )

    st.write("")

    # Predict button (centered, wider like Search Films)
    col1, col2, col3 = st.columns([3, 6, 3])
    with col2:
        predict_button = st.button("🎯 Prediksi Mood", use_container_width=True, type="primary", key="music_predict")

    st.write("")

    # Process prediction
    if predict_button:
        # Prepare features for prediction
        import numpy as np

        # Features in correct order for model
        features = np.array([[
            danceability,
            energy,
            valence,
            tempo,
            acousticness,
            instrumentalness,
            0.5,  # loudness (default)
            0.1   # speechiness (default)
        ]])

        # Predict mood
        if engine.model is not None and engine.label_encoder is not None:
            prediction = engine.model.predict(features)[0]
            predicted_mood = engine.label_encoder.inverse_transform([prediction])[0]
        else:
            # Rule-based fallback
            if valence >= 0.5 and energy >= 0.5:
                predicted_mood = 'Happy'
            elif valence < 0.5 and energy < 0.5:
                predicted_mood = 'Sad'
            elif valence >= 0.5 and energy < 0.5:
                predicted_mood = 'Calm'
            else:
                predicted_mood = 'Tense'

        # Display result - Full page design
        st.write("")
        st.write("")
        st.markdown("---")

        # Color mapping for moods
        mood_colors = {
            'Happy': '#10B981',   # Green
            'Sad': '#3B82F6',     # Blue
            'Calm': '#8B5CF6',    # Purple
            'Tense': '#EF4444'    # Red
        }

        mood_emojis = {
            'Happy': '😊',
            'Sad': '😢',
            'Calm': '😌',
            'Tense': '😰'
        }

        mood_color = mood_colors.get(predicted_mood, '#6366F1')
        mood_emoji = mood_emojis.get(predicted_mood, '🎵')

        # Big mood result card
        st.markdown(f"""
        <div style='text-align: center; padding: 3rem 2rem; background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border-radius: 16px; border: 2px solid {mood_color};'>
            <div style='font-size: 5rem; margin-bottom: 1rem;'>{mood_emoji}</div>
            <h1 style='color: {mood_color}; font-size: 3rem; margin-bottom: 0.5rem;'>{predicted_mood}</h1>
            <p style='color: #94A3B8; font-size: 1.2rem;'>Mood Terprediksi</p>
        </div>
        """, unsafe_allow_html=True)

        st.write("")
        st.write("")

        # Feature values summary
        st.markdown("### 📊 Audio Features Summary")
        col1, col2, col3 = st.columns(3)

        with col1:
            with st.container(border=True):
                st.metric("Danceability", f"{danceability:.2f}")
                st.metric("Energy", f"{energy:.2f}")

        with col2:
            with st.container(border=True):
                st.metric("Valence", f"{valence:.2f}")
                st.metric("Acousticness", f"{acousticness:.2f}")

        with col3:
            with st.container(border=True):
                st.metric("Instrumentalness", f"{instrumentalness:.2f}")
                st.metric("Tempo", f"{tempo} BPM")

        st.write("")
        st.write("")

        # Show recommendations based on predicted mood
        st.markdown(f"### 🎵 Recommended Songs for {predicted_mood} Mood")
     recommendations = engine.get_recommendations_by_mood(predicted_mood, 10)

        for idx, song in recommendations.iterrows():
            with st.container(border=True):
                col_song, col_player = st.columns([6, 4])

                with col_song:
                    st.markdown(f"#### {song['track_name']}")
                    st.caption(f"{song['artists']}")
                    st.caption(f"{song['album_name']} • {song['track_genre']} • ⭐ {song['popularity']}/100")

                with col_player:
                    st.write("")
                    track_id = song['track_id']
                    spotify_embed = engine.create_spotify_embed(track_id, width=350, height=80)
                    st.markdown(spotify_embed, unsafe_allow_html=True)

    st.write("")
    st.write("")

    # Feature explanation
    with st.expander("ℹ️ Penjelasan Audio Features"):
        st.markdown("""
        **Audio features** adalah karakteristik yang digunakan model untuk memprediksi mood:

        - **Danceability**: Seberapa cocok lagu untuk menari
        - **Energy**: Tingkat intensitas dan aktivitas
        - **Valence**: Tingkat kepositifan emosi (happy vs sad)
        - **Acousticness**: Seberapa akustik suara lagu
        - **Instrumentalness**: Seberapa banyak vokal dalam lagu
        - **Tempo**: Kecepatan lagu dalam BPM (beats per minute)

        **Mood Classification:**
        - **Happy**: Valence tinggi + Energy tinggi
        - **Sad**: Valence rendah + Energy rendah
        - **Calm**: Valence tinggi + Energy rendah
        - **Tense**: Valence rendah + Energy tinggi
        """)

elif selected_tab == "💬 Chat Assistant":
    st.markdown("## 💬 Music Chat Assistant")

    # Check if API key is available
    if not os.getenv("GOOGLE_API_KEY"):
        st.error("⚠️ **GOOGLE_API_KEY not found!**")
        with st.container(border=True):
            st.markdown("""
            ### Setup Instructions:
            1. Create a `.env` file in the `streamlit_app` directory
            2. Add your Google API key: `GOOGLE_API_KEY=your_api_key_here`
            3. Get your API key from: [Google AI Studio](https://aistudio.google.com/app/apikey)
            4. Restart the Streamlit app
            """)
    else:
        # Initialize chat history in session state
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

        # Main layout: Chat + Sidebar info
        col_chat, col_info = st.columns([7, 3])

        with col_chat:
            # Custom CSS for modern chat bubbles
            st.markdown("""
            <style>
            .chat-message {
                display: flex;
                margin: 16px 0;
                animation: fadeIn 0.3s ease-in;
            }

            .user-bubble-container {
                justify-content: flex-end;
            }

            .bot-bubble-container {
                justify-content: flex-start;
            }

            .message-content {
                max-width: 70%;
                position: relative;
            }

            .user-message {
                background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
                color: #FFF;
                padding: 14px 18px;
                border-radius: 20px 20px 4px 20px;
                box-shadow: 0 2px 8px rgba(99, 102, 241, 0.4);
                font-size: 0.95rem;
                line-height: 1.5;
            }

            .bot-message {
                background: linear-gradient(135deg, #334155 0%, #1E293B 100%);
                color: #F1F5F9;
                padding: 14px 18px;
                border-radius: 20px 20px 20px 4px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
                font-size: 0.95rem;
                line-height: 1.5;
                border: 1px solid #475569;
            }

            .message-avatar {
                width: 32px;
                height: 32px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.1rem;
                margin: 0 10px;
                flex-shrink: 0;
            }

            .user-avatar {
                background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
                box-shadow: 0 2px 6px rgba(99, 102, 241, 0.4);
            }

            .bot-avatar {
                background: linear-gradient(135deg, #64748B 0%, #475569 100%);
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
            }

            .message-time {
                font-size: 0.7rem;
                color: #888;
                margin-top: 4px;
                text-align: right;
            }

            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            </style>
            """, unsafe_allow_html=True)

            # Input section at TOP
            st.markdown("### ✍️ Type your message")

            # Chat form - prevents intermediate reruns
            with st.form("chat_form", clear_on_submit=True):
                col_input, col_send = st.columns([7, 1])

                with col_input:
                    user_message = st.text_input(
                        "Type your message...",
                        key="chat_input",
                        label_visibility="collapsed",
                        placeholder="e.g., Saya sedang sedih, rekomendasikan lagu dong"
                    )

                with col_send:
                    send_button = st.form_submit_button("📤", use_container_width=True, help="Send message")

            # Clear button OUTSIDE form
            if st.button("🗑️ Clear Chat", use_container_width=True, help="Clear chat history", key="music_clear_chat"):
                st.session_state.chat_history = []
                chatbot.clear_history()
                # No st.rerun() needed - state change triggers auto-update

            st.write("")

            # Chat messages container BELOW input
            st.markdown("### 💬 Chat History")
            chat_container = st.container(height=450, border=True)

            with chat_container:
                if len(st.session_state.chat_history) == 0:
                    st.info("👋 Hi! Ask me for music recommendations based on your mood!")
                else:
                    for message in st.session_state.chat_history:
                        if message['role'] == 'user':
                            st.markdown(f'''
                            <div class="chat-message user-bubble-container">
                                <div class="message-content">
                                    <div class="user-message">{message["content"]}</div>
                                </div>
                                <div class="message-avatar user-avatar">👤</div>
                            </div>
                            ''', unsafe_allow_html=True)
                        else:
                            st.markdown(f'''
                            <div class="chat-message bot-bubble-container">
                                <div class="message-avatar bot-avatar">🤖</div>
                                <div class="message-content">
                                    <div class="bot-message">{message["content"]}</div>
                                </div>
                            </div>
                            ''', unsafe_allow_html=True)

                            # Display full song cards if songs exist
                            songs = message.get('songs', [])
                            if songs:
                                st.write("")  # Spacing
                                for song in songs:
                                    with st.container(border=True):
                                        col_song, col_player = st.columns([6, 4])

                                        with col_song:
                                            st.markdown(f"#### {song['title']}")
                                            st.caption(f"{song['artist']}")
                                            st.caption(f"{song['album']} • {song['genre']} • ⭐ {song['popularity']}/100")

                                        with col_player:
                                            st.write("")
                                            track_id = song['track_id']
                                            spotify_embed = engine.create_spotify_embed(track_id, width=350, height=80)
                                            st.markdown(spotify_embed, unsafe_allow_html=True)
                                st.write("")  # Spacing
                    st.write("")  # Auto-scroll spacing

            # Handle send message
            if send_button and user_message.strip():
                # Prevent duplicate processing on rerun
                if 'processing_msg' not in st.session_state:
                    st.session_state.processing_msg = True

                    # Add user message to history
                    st.session_state.chat_history.append({
                        'role': 'user',
                        'content': user_message
                    })

                    # Get bot response with error handling
                    try:
                        with st.spinner("🎵 Thinking..."):
                            # Generate unique thread_id per session
                            if 'thread_id' not in st.session_state:
                                import uuid
                                st.session_state.thread_id = str(uuid.uuid4())

                            bot_response = chatbot.chat(user_message, thread_id=st.session_state.thread_id)

                        # Handle dictionary response (with text and optional songs)
                        if isinstance(bot_response, dict):
                            response_text = bot_response.get("text", "")
                            songs = bot_response.get("songs", [])
                        else:
                            # Fallback for backward compatibility
                            response_text = str(bot_response)
                            songs = []

                        # Add bot response to history
                        st.session_state.chat_history.append({
                            'role': 'bot',
                            'content': response_text,
                            'songs': songs
                        })
                    except Exception as e:
                        error_msg = str(e)
                        if "429" in error_msg or "quota" in error_msg.lower():
                            st.error("⚠️ **API Quota Exceeded!** Try again in a few minutes.")
                        else:
                            st.error(f"⚠️ **Error:** {error_msg}")

                        st.session_state.chat_history.append({
                            'role': 'bot',
                            'content': f"Sorry, error: {error_msg}"
                        })

                    del st.session_state.processing_msg
                    st.rerun()  # Force UI update to display new messages

        with col_info:
            # Tips card
            with st.container(border=True):
                st.markdown("### 💡 Tips")
                st.markdown("""
                **Try asking:**
                - "Saya sedang sedih"
                - "I'm feeling happy!"
                - "Lagu untuk mood calm"
                - "Rekomendasi musik energik"
                """)

            st.write("")

            # Info card
            with st.container(border=True):
                st.markdown("### ℹ️ About")
                st.markdown("""
                This AI assistant helps you find music from our **114K+ songs** dataset.

                **Features:**
                - Mood detection
                - Smart recommendations
                - Bilingual support
                - Music-only responses
                """)

            st.write("")

            # Stats card
            with st.container(border=True):
                st.markdown("### 📊 Stats")
                st.metric("Messages", len(st.session_state.chat_history))
                st.metric("Model", "Gemini 2.5")
                st.caption("Powered by Google AI")

elif selected_tab == "📊 Analytics":
    st.markdown("## 📊 Music Analytics")
    st.write("")

    # Quick Stats Cards at the top
    mood_dist = engine.get_mood_distribution()
    total_songs = sum(mood_dist.values())

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        with st.container(border=True):
            st.markdown("### 🎵")
            st.metric("Total Songs", f"{total_songs:,}")

    with col2:
        with st.container(border=True):
            st.markdown("### 😊")
            st.metric("Happy", f"{mood_dist.get('Happy', 0):,}")

    with col3:
        with st.container(border=True):
            st.markdown("### 😢")
            st.metric("Sad", f"{mood_dist.get('Sad', 0):,}")

    with col4:
        with st.container(border=True):
            st.markdown("### 😌")
            st.metric("Calm", f"{mood_dist.get('Calm', 0):,}")

    with col5:
        with st.container(border=True):
            st.markdown("### 😰")
            st.metric("Tense", f"{mood_dist.get('Tense', 0):,}")

    st.write("")
    st.write("")

    # Two-column layout for charts
    col_left, col_right = st.columns(2)

    with col_left:
        with st.container(border=True):
            st.markdown("#### 🎭 Mood Distribution")
            fig_pie = create_mood_pie_chart(mood_dist)
            st.plotly_chart(fig_pie, use_container_width=True)

    with col_right:
        with st.container(border=True):
            st.markdown("#### 🎸 Top Genres")
            genre_filter_mood = st.selectbox(
                "Filter by mood:",
                options=["All Moods"] + engine.get_available_moods(),
                key="genre_filter"
            )

            if genre_filter_mood == "All Moods":
                genre_dist = engine.get_genre_distribution()
            else:
                genre_dist = engine.get_genre_distribution(mood=genre_filter_mood)

            fig_genre = create_genre_bar_chart(genre_dist, top_n=10)
            st.plotly_chart(fig_genre, use_container_width=True)

    st.write("")

    # Full width: Valence vs Energy scatter
    with st.container(border=True):
        st.markdown("#### 🎯 Mood Quadrants: Valence vs Energy")
        st.caption("Distribution of songs across different moods based on emotional valence and energy levels")
        fig_scatter = create_valence_energy_scatter(engine.df)
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.write("")

    # Full width: Audio features radar
    with st.container(border=True):
        st.markdown("#### 🎵 Audio Features by Mood")
        st.caption("Average audio characteristics comparison across different moods")
        mood_stats = engine.get_mood_stats()
        fig_radar = create_audio_features_radar(mood_stats)
        st.plotly_chart(fig_radar, use_container_width=True)

    st.write("")

    # Mood statistics table
    with st.container(border=True):
        st.markdown("#### 📈 Detailed Mood Statistics")
        st.dataframe(
            mood_stats.style.background_gradient(cmap='Greens'),
            use_container_width=True,
            height=300
        )

elif selected_tab == "ℹ️ About":
    st.markdown("## ℹ️ About Music Recommendation System")

    st.markdown("""
    ### 🎵 How It Works

    This music recommendation system uses machine learning and audio feature analysis to suggest songs based on your mood:

    **1. Mood Classification:**
    - Songs are classified into 4 moods: Happy, Sad, Calm, and Tense
    - Classification is based on **Valence** (positivity) and **Energy** levels
    - Uses Random Forest classifier trained on audio features

    **2. Audio Features:**
    - **Valence**: Musical positiveness (0.0 = negative, 1.0 = positive)
    - **Energy**: Intensity and activity (0.0 = calm, 1.0 = energetic)
    - **Danceability**: How suitable for dancing (0.0 to 1.0)
    - **Acousticness**: Confidence that track is acoustic (0.0 to 1.0)
    - **Speechiness**: Presence of spoken words (0.0 to 1.0)
    - **Tempo**: Speed in BPM (beats per minute)

    **3. Recommendation Algorithm:**
    - Filter songs by selected mood
    - Optional genre filtering for more specific results
    - Rank by popularity score
    - Return top N recommendations

    ### 📊 Dataset
    - **Total Songs**: 114,000+
    - **Genres**: 114 different genres
    - **Source**: Spotify Dataset (CSV)
    - **Features**: 20+ audio features per song

    ### 🎯 Mood Quadrants

    | Mood | Valence | Energy | Description |
    |------|---------|--------|-------------|
    | 😊 Happy | High (≥0.5) | High (≥0.5) | Upbeat, energetic, positive |
    | 😢 Sad | Low (<0.5) | Low (<0.5) | Melancholic, slow, emotional |
    | 😌 Calm | High (≥0.5) | Low (<0.5) | Peaceful, relaxing, soothing |
    | 😰 Tense | Low (<0.5) | High (≥0.5) | Aggressive, intense, dark |

    ### 🎧 Spotify Integration
    - **Embedded Player**: Direct playback using Spotify Embed Player (FREE, no API key needed)
    - **Track ID**: Each song has a unique Spotify track ID for playback
    - **Requirements**: Spotify account (free or premium) to play songs

    ### 🤖 AI Chat Assistant
    - **Model**: Google Gemini 2.5 Flash
    - **Features**: Mood detection, smart recommendations from dataset
    - **Language**: Bilingual support (Indonesian/English)
    - **Strict Mode**: Only recommends songs from the 114K+ dataset
    """)

    st.markdown("---")
    st.info("💡 **Tip**: Try different mood-genre combinations to discover new music!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🎓 Final Project Kelompok 4 | Built with ❤️ using Streamlit & ML</p>
</div>
""", unsafe_allow_html=True)
