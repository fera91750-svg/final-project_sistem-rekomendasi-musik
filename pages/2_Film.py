"""
🎬 Film Recommendation Page
Search and filter films with platform recommendations
"""

import streamlit as st
import sys
import os
import pandas as pd

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.film_engine import FilmRecommendationEngine
from utils.film_chatbot_engine import FilmChatbot
from utils.visualizations import (
    create_rating_histogram,
    create_year_line_chart,
    create_genre_film_bar
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Film Recommendations",
    page_icon="🎬",
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
    h1 {
        color: #F1F5F9;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }

    /* Film cards */
    .film-card {
        background: #1E293B;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.2s;
        border: 1px solid #334155;
    }

    .film-card:hover {
        background: #334155;
        border-color: #6366F1;
    }

    /* Platform badges */
    .platform-badge {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        border-radius: 15px;
        margin: 0.2rem;
        font-weight: bold;
        font-size: 0.85rem;
    }

    .netflix { background: #E50914; color: white; }
    .disney { background: #113CCF; color: white; }
    .disney+ { background: #113CCF; color: white; }
    .prime { background: #00A8E1; color: white; }
    .primevideo { background: #00A8E1; color: white; }
    .hbo { background: #7D2EBE; color: white; }
    .hbomax { background: #7D2EBE; color: white; }
    .apple { background: #000000; color: white; border: 1px solid white; }
    .appletv+ { background: #000000; color: white; border: 1px solid white; }
    .viu { background: #FFB800; color: black; }

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
        border-bottom: 2px solid #EC4899;
    }

    /* Buttons */
    .stButton > button {
        background-color: transparent;
        color: #F1F5F9;
        border: 1px solid #475569;
        border-radius: 500px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s;
    }

    .stButton > button:hover {
        border-color: #EC4899;
        transform: scale(1.02);
    }

    /* Primary button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #EC4899 0%, #8B5CF6 100%);
        border: none;
        color: #FFFFFF;
    }

    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%);
    }
</style>
""", unsafe_allow_html=True)

# Header with back button
col_back, col_title = st.columns([1.5, 10.5])
with col_back:
    st.write("")
    st.write("")  # Double spacing
    if st.button("← Back", key="film_back_home"):
        st.switch_page("main.py")
with col_title:
    st.markdown("# Film Recommendations")

st.divider()

# Initialize engine
@st.cache_resource
def load_film_engine():
    return FilmRecommendationEngine()

@st.cache_resource
def load_film_chatbot(_engine):
    """Initialize chatbot with film engine"""
    return FilmChatbot(_engine)

with st.spinner("🎬 Loading film database..."):
    engine = load_film_engine()
    film_chatbot = load_film_chatbot(engine)

# Horizontal filters at top
st.write("")  # Spacing
col1, col2, col3 = st.columns([3, 3, 3])

with col1:
    rating_range = st.slider(
        "Rating Range (Min - Max)",
        min_value=0.0,
        max_value=10.0,
        value=(6.0, 10.0),
        step=0.5,
        label_visibility="visible",
        help="Set minimum and maximum rating range to filter films"
    )

with col2:
    search_query = st.text_input(
        "Search by Title",
        placeholder="e.g., Inception, Avatar...",
        label_visibility="visible"
    )

with col3:
    selected_year = st.selectbox(
        "Release Year",
        options=["All Years"] + engine.get_available_years(),
        label_visibility="visible"
    )
    if selected_year == "All Years":
        selected_year = None

# Genre filter (full width)
selected_genres = st.multiselect(
    "Filter by Genre (optional)",
    options=engine.get_available_genres(),
    placeholder="Select genres...",
    label_visibility="visible"
)

st.write("")

# Search button (centered, wider)
col1, col2, col3 = st.columns([3, 6, 3])
with col2:
    if st.button("🔍 Search Films", use_container_width=True, type="primary", key="film_search"):
        st.session_state.show_films = True

st.write("")

# Main tabs - Tab navigation using radio buttons (persists state)
if 'film_selected_tab' not in st.session_state:
    st.session_state.film_selected_tab = "💬 Chat Assistant"

selected_tab = st.radio(
    "Navigation",
    ["🎬 Recommendations", "💬 Chat Assistant", "📊 Analytics", "ℹ️ About"],
    horizontal=True,
    label_visibility="collapsed",
    key="film_tab_selector",
    index=["🎬 Recommendations", "💬 Chat Assistant", "📊 Analytics", "ℹ️ About"].index(st.session_state.film_selected_tab)
)
st.session_state.film_selected_tab = selected_tab

st.markdown("---")  # Separator line

# Show content based on selection
if selected_tab == "🎬 Recommendations":
    st.markdown("## 🎬 Film Recommendations")
    st.write("")
    if st.session_state.get('show_films', False):

        st.markdown(f"## 🎯 Film Results")

        # Apply filters
        if search_query:
            # Search by title
            results = engine.search_by_title(search_query, fuzzy=True)

            if not results.empty:
                st.success(f"Found {len(results)} film(s) matching '{search_query}'")

                # Show main film
                main_film = results.iloc[0]

                with st.container(border=True):
                    st.markdown(f"### {main_film['title']}")
                    st.caption(f"📅 {int(main_film['release_year'])} • 🎭 {', '.join(main_film['genres_list'])}")
                    st.write("")
                    st.markdown(f"**📖 Description:**")
                    st.write(main_film['description'])
                    st.write("")
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.caption(f"⭐ **Rating:** {main_film['rating']}/10 ({main_film['votes']} votes)")
                        st.caption(f"🎬 **Director:** {main_film['directors']}")
                    with col_info2:
                        st.caption(f"⏱️ **Duration:** {main_film['runtime_minutes']}")

                    # Platform recommendations inside the same container
                    st.write("")
                    st.markdown("**Watch on:**")
                    platforms = engine.get_platform_recommendation(main_film)
                    platform_html = '<div style="text-align: center;">'
                    for platform in platforms:
                        platform_class = platform.lower().replace(" ", "").replace("+", "")
                        platform_html += f'<span class="platform-badge {platform_class}">{platform}</span> '
                    platform_html += '</div>'
                    st.markdown(platform_html, unsafe_allow_html=True)

                st.write("")

                # Similar films
                st.markdown("### 🎬 Similar Films")

                similar_films = engine.get_similar_films(main_film['title'], n=5)

                if not similar_films.empty:
                    for _, film in similar_films.iterrows():
                        with st.container(border=True):
                            col1, col2 = st.columns([7, 3])

                            with col1:
                                st.markdown(f"#### {film['title']}")
                                st.caption(f"{int(film['release_year'])} • {', '.join(film['genres_list'])}")
                                st.caption(f"⭐ {film['rating']}/10 • Match: {film['similarity_score']:.0%}")

                            with col2:
                                platforms_similar = engine.get_platform_recommendation(film)
                                st.markdown("**Watch on:**")
                                platform_html = '<div style="text-align: center;">'
                                for p in platforms_similar[:3]:
                                    p_class = p.lower().replace(" ", "").replace("+", "")
                                    platform_html += f'<span class="platform-badge {p_class}">{p}</span> '
                                platform_html += '</div>'
                                st.markdown(platform_html, unsafe_allow_html=True)
                else:
                    st.info("Similar films computation in progress...")

            else:
                st.warning(f"No films found matching '{search_query}'. Try a different search term.")

        else:
            # Filter mode (by rating, year, genre)
            results = engine.filter_combined(
                min_rating=rating_range[0],
                max_rating=rating_range[1],
                year=selected_year,
                genres=selected_genres if selected_genres else None
            )

            if not results.empty:
                st.success(f"Found {len(results)} film(s) matching your criteria")

                # Display top results
                display_count = min(20, len(results))

                for idx, film in results.head(display_count).iterrows():
                    with st.container(border=True):
                        col1, col2 = st.columns([7, 3])

                        with col1:
                            st.markdown(f"### {film['title']}")
                            st.caption(f"{int(film['release_year'])} • {', '.join(film['genres_list'])}")
                            st.caption(f"⭐ {film['rating']}/10 ({film['votes']} votes) • 🎬 {film['directors']}")
                            st.write(film['description'][:150] + "...")

                        with col2:
                            st.write("")
                            platforms = engine.get_platform_recommendation(film)
                            st.markdown("**Watch on:**")
                            platform_html = '<div style="text-align: center;">'
                            for p in platforms[:3]:
                                p_class = p.lower().replace(" ", "").replace("+", "")
                                platform_html += f'<span class="platform-badge {p_class}">{p}</span> '
                            platform_html += '</div>'
                            st.markdown(platform_html, unsafe_allow_html=True)

                if len(results) > display_count:
                    st.info(f"Showing top {display_count} results. Refine filters for more specific results.")

            else:
                st.warning("No films found matching your criteria. Try adjusting the filters.")

    else:
        st.info("👈 Use the filters above and click 'Search' to find films!")

        # Show quick stats
        st.markdown("### 📊 Quick Stats")
        info = engine.get_dataset_info()
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Films", f"{info['total_films']:,}")
        with col2:
            st.metric("Average Rating", f"{info['avg_rating']}/10")
        with col3:
            st.metric("Year Range", f"{info['year_range'][0]} - {info['year_range'][1]}")

elif selected_tab == "💬 Chat Assistant":
    st.markdown("## 💬 Film Chat Assistant")

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
        if 'film_chat_history' not in st.session_state:
            st.session_state.film_chat_history = []

        # Initialize thread ID for conversation memory
        if 'film_thread_id' not in st.session_state:
            import uuid
            st.session_state.film_thread_id = str(uuid.uuid4())

        # Main layout: Chat + Sidebar info
        col_chat, col_info = st.columns([7, 3])

        with col_chat:
            # Custom CSS for modern chat bubbles (reuse from Music)
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
                background: linear-gradient(135deg, #EC4899 0%, #8B5CF6 100%);
                color: #FFF;
                padding: 14px 18px;
                border-radius: 20px 20px 4px 20px;
                box-shadow: 0 2px 8px rgba(236, 72, 153, 0.4);
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
                background: linear-gradient(135deg, #EC4899 0%, #8B5CF6 100%);
                box-shadow: 0 2px 6px rgba(236, 72, 153, 0.4);
            }

            .bot-avatar {
                background: linear-gradient(135deg, #64748B 0%, #475569 100%);
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
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
            with st.form("film_chat_form", clear_on_submit=True):
                col_input, col_send = st.columns([7, 1])

                with col_input:
                    user_message = st.text_input(
                        "Type your message...",
                        key="film_chat_input",
                        label_visibility="collapsed",
                        placeholder="e.g., Rekomendasi film action tahun 2020"
                    )

                with col_send:
                    send_button = st.form_submit_button("📤", use_container_width=True, help="Send message")

            # Clear button OUTSIDE form
            if st.button("🗑️ Clear Chat", use_container_width=True, help="Clear chat history", key="film_clear_chat"):
                st.session_state.film_chat_history = []
                film_chatbot.clear_history()
                # No st.rerun() needed - state change triggers auto-update

            st.write("")

            # Chat messages container BELOW input
            st.markdown("### 💬 Chat History")
            chat_container = st.container(height=450, border=True)

            with chat_container:
                if len(st.session_state.film_chat_history) == 0:
                    st.info("👋 Hi! Ask me for film recommendations!")
                else:
                    for message in st.session_state.film_chat_history:
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

                            # Display film cards if available (COMPACT VERSION)
                            films = message.get('films', [])
                            if films:
                                for film in films:
                                    with st.container(border=True):
                                        # Title and Rating (inline, compact)
                                        col1, col2 = st.columns([7, 3])
                                        with col1:
                                            st.markdown(f"**{film.get('title', 'Unknown')}**")
                                        with col2:
                                            rating = film.get('rating', 0)
                                            st.markdown(f"⭐ **{rating}/10**")

                                        # Genre, Year (compact, single line)
                                        genres = film.get('genres_list', 'Unknown')
                                        year = film.get('year', 'N/A')
                                        st.caption(f"🎭 {genres} • 📅 {year}")

                                        # Platform badges (compact, inline)
                                        genres_for_platform = genres
                                        if isinstance(genres_for_platform, str):
                                            genres_for_platform = [g.strip() for g in genres_for_platform.split(',')]

                                        film_series = pd.Series({
                                            'genres_list': genres_for_platform,
                                            'rating': rating
                                        })

                                        platforms = engine.get_platform_recommendation(film_series)

                                        # Compact platform badges
                                        platform_html = '🎬 '
                                        for platform in platforms:
                                            platform_class = platform.lower().replace(" ", "").replace("+", "")
                                            platform_html += f'<span class="platform-badge {platform_class}">{platform}</span> '
                                        st.markdown(platform_html, unsafe_allow_html=True)

                    st.write("")  # Auto-scroll spacing

            # Handle send message
            if send_button and user_message.strip():
                # Prevent duplicate processing on rerun
                if 'film_processing_msg' not in st.session_state:
                    # Store the user message for processing
                    st.session_state.film_processing_msg = user_message

                    # Add user message to history
                    st.session_state.film_chat_history.append({
                        'role': 'user',
                        'content': user_message
                    })

                    # Add temporary "thinking" bubble to prevent transparency
                    st.session_state.film_chat_history.append({
                        'role': 'bot',
                        'content': '🎬 Thinking...'
                    })

                    # Trigger rerun to show user message + thinking bubble
                    st.rerun()

            # Handle bot response processing (runs after rerun)
            if 'film_processing_msg' in st.session_state and isinstance(st.session_state.film_processing_msg, str):
                # Check if last message is the thinking placeholder
                if (len(st.session_state.film_chat_history) > 0 and
                    st.session_state.film_chat_history[-1]['role'] == 'bot' and
                    st.session_state.film_chat_history[-1]['content'] == '🎬 Thinking...'):

                    # Get the user message to process
                    user_msg_to_process = st.session_state.film_processing_msg

                    # Get bot response with error handling
                    try:
                        with st.spinner("🎬 Thinking..."):
                            bot_response = film_chatbot.chat(user_msg_to_process, thread_id=st.session_state.film_thread_id)

                        # Handle dictionary response
                        if isinstance(bot_response, dict):
                            response_text = bot_response.get("text", "")
                            films = bot_response.get("films", [])
                        else:
                            response_text = str(bot_response)
                            films = []

                        # Replace thinking message with actual response
                        st.session_state.film_chat_history[-1] = {
                            'role': 'bot',
                            'content': response_text,
                            'films': films
                        }
                    except Exception as e:
                        error_msg = str(e)
                        if "429" in error_msg or "quota" in error_msg.lower():
                            error_response = "⚠️ **API Quota Exceeded!** Try again in a few minutes."
                        else:
                            error_response = f"⚠️ **Error:** {error_msg}"

                        # Replace thinking message with error
                        st.session_state.film_chat_history[-1] = {
                            'role': 'bot',
                            'content': error_response,
                            'films': []
                        }

                    # Clear processing flag
                    del st.session_state.film_processing_msg
                    st.rerun()  # Force UI update to display actual response

        with col_info:
            # Tips card
            with st.container(border=True):
                st.markdown("### 💡 Tips")
                st.markdown("""
                **Try asking:**
                - "Film Inception"
                - "Rekomendasi film mirip Avatar"
                - "Film action terbaik"
                - "Film tahun 2023"
                """)

            st.write("")

            # Info card
            with st.container(border=True):
                st.markdown("### ℹ️ About")
                st.markdown("""
                This AI assistant helps you find films from our **7,400+ films** dataset.

                **Features:**
                - Film search by title
                - Similar film recommendations
                - Genre/year/rating filtering
                - Bilingual support
                """)

            st.write("")

            # Stats card
            with st.container(border=True):
                st.markdown("### 📊 Stats")
                st.metric("Messages", len(st.session_state.film_chat_history))
                st.metric("Model", "Gemini 2.5")
                st.caption("Powered by Google AI")

elif selected_tab == "📊 Analytics":
    st.markdown("## 📊 Film Analytics Dashboard")
    st.write("")

    # Quick Stats Cards at the top
    info = engine.get_dataset_info()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        with st.container(border=True):
            st.markdown("### 🎬")
            st.metric("Total Films", f"{info['total_films']:,}")

    with col2:
        with st.container(border=True):
            st.markdown("### 🎭")
            st.metric("Genres", info['total_genres'])

    with col3:
        with st.container(border=True):
            st.markdown("### ⭐")
            st.metric("Avg Rating", f"{info['avg_rating']}/10")

    with col4:
        with st.container(border=True):
            st.markdown("### 📅")
            st.metric("Years", f"{info['year_range'][0]}-{info['year_range'][1]}")

    st.write("")
    st.write("")

    # Two-column layout for charts
    col_left, col_right = st.columns(2)

    with col_left:
        with st.container(border=True):
            st.markdown("#### ⭐ Rating Distribution")
            fig_rating = create_rating_histogram(engine.df)
            st.plotly_chart(fig_rating, use_container_width=True)

    with col_right:
        with st.container(border=True):
            st.markdown("#### 🎭 Top Genres")
            genre_dist = engine.get_genre_distribution()
            fig_genre = create_genre_film_bar(genre_dist, top_n=10)
            st.plotly_chart(fig_genre, use_container_width=True)

    st.write("")

    # Full width: Films per year
    with st.container(border=True):
        st.markdown("#### 📅 Films Released Per Year")
        st.caption("Timeline of film releases in the dataset")
        fig_year = create_year_line_chart(engine.df)
        st.plotly_chart(fig_year, use_container_width=True)

    st.write("")

    # Top rated films
    with st.container(border=True):
        st.markdown("#### 🏆 Top 10 Highest Rated Films")
        top_films = engine.get_top_rated(n=10)

        for idx, film in top_films.iterrows():
            col_rank, col_info = st.columns([1, 11])
            with col_rank:
                st.markdown(f"**#{idx+1}**")
            with col_info:
                st.markdown(f"**{film['title']}** ({int(film['release_year'])})")
                st.caption(f"⭐ {film['rating']}/10 • {', '.join(film['genres_list'])}")
            st.write("")

elif selected_tab == "ℹ️ About":
    st.markdown("## ℹ️ About Film Recommendation System")

    st.markdown("""
    ### 🎬 How It Works

    This film recommendation system uses content-based filtering to suggest movies based on:

    **1. Content-Based Filtering:**
    - Uses TF-IDF (Term Frequency-Inverse Document Frequency) vectorization
    - Analyzes film descriptions, genres, directors, and actors
    - Computes similarity using cosine similarity
    - Recommends films with similar content profiles

    **2. Filtering Options:**
    - **Rating**: Filter by IMDb rating (0-10)
    - **Title Search**: Find films by name (fuzzy matching)
    - **Year**: Filter by release year
    - **Genre**: Multiple genre selection

    **3. Platform Recommendations (Rule-Based):**
    - Suggests streaming platforms based on genre and rating
    - Uses smart rules for platform assignment
    - Future: Integration with JustWatch API for real-time availability

    ### 📊 Dataset
    - **Total Films**: 7,432 movies
    - **Year Range**: 2001 - 2024
    - **Genres**: 20+ different genres
    - **Features**: Title, description, rating, actors, directors, runtime

    ### 🎯 Similarity Algorithm

    **How Similar Films are Found:**
    1. Combine description + actors + directors + genres into "soup"
    2. Convert text to numerical vectors using TF-IDF
    3. Calculate cosine similarity between all films
    4. Return most similar films (highest similarity score)

    **Example:** If you like "Inception" (Sci-Fi, Thriller, Christopher Nolan), the system will recommend:
    - Other Christopher Nolan films
    - Films with similar plot themes (dreams, reality-bending)
    - Movies in Sci-Fi/Thriller genres

    ### 📺 Platform Recommendation Rules

    | Genre | Recommended Platforms |
    |-------|----------------------|
    | Animation, Family | Disney+ |
    | Horror, Thriller | Netflix |
    | Action, Sci-Fi | Prime Video |
    | Drama, Romance | Netflix, Viu |
    | High Rating (≥8.0) | HBO Max |

    ### 💬 AI Chatbot (Coming Soon!)
    An AI-powered chatbot for film recommendations is in development! Similar to the Music chatbot,
    it will use Google Gemini AI to provide personalized film suggestions based on your preferences.

    **Current Status:** UI ready, awaiting LLM integration

    ### 🔮 Other Future Enhancements
    - Real-time platform availability via API
    - User rating and review system
    - Collaborative filtering (user-based recommendations)
    - Trailer integration (YouTube)
    - Watch history tracking
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🎓 Final Project Kelompok 4 | Built with ❤️ using Streamlit & ML</p>
</div>
""", unsafe_allow_html=True)
