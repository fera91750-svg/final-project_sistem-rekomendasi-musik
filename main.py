"""
🎵 MELORA - Music Recommendation System
Landing Page - User chooses Music recommendation
"""

import streamlit as st
from PIL import Image
import os
import base64

# Page configuration
st.set_page_config(
    page_title="MELORA - Music Recommendation System",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }

    .main { background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); }

    .block-container { padding-top: 3rem; padding-bottom: 3rem; max-width: 1000px; }

    .hero-container { text-align: center; padding: 2rem 0 3rem 0; }

    .hero-logo {
        width: 250px;
        height: 250px;
        border-radius: 50%;
        object-fit: cover;
        margin: 0 auto 1.5rem auto;
        display: block;
        box-shadow: 0 10px 40px rgba(99, 102, 241, 0.3);
    }

    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6366F1 0%, #EC4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        letter-spacing: 0.1em;
    }

    .hero-subtitle {
        font-size: 1.5rem;
        color: #FFFFFF;
        margin-bottom: 3rem;
    }

    .feature-card {
        background: linear-gradient(145deg, #1E293B, #0F172A);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 2.5rem 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }

    .feature-card:hover {
        border-color: #6366F1;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.2);
    }

    .stButton>button {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
        color: #000000;
        font-weight: 700;
        font-size: 0.95rem;
        padding: 0.75rem 2rem;
        border-radius: 500px;
        border: none;
        transition: all 0.2s ease;
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 1rem;
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%);
        transform: scale(1.05);
        box-shadow: 0 5px 20px rgba(99, 102, 241, 0.4);
    }

    .feature-icon { font-size: 4rem; margin-bottom: 1.5rem; }
    .feature-title { font-size: 1.8rem; font-weight: 700; color: #F1F5F9; margin-bottom: 1rem; }
    .feature-description { font-size: 0.95rem; color: #CBD5E1; line-height: 1.6; }

    .footer { text-align: center; color: #64748B; font-size: 0.85rem; padding: 3rem 0 1rem 0; margin-top: 4rem; }
</style>
""", unsafe_allow_html=True)

# Hero section with logo
logo_path = os.path.join(os.path.dirname(__file__), 'assets', 'logo.jpeg')
if os.path.exists(logo_path):
    with open(logo_path, "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode()

    st.markdown(f"""
    <div style="
        display: flex;
        justify-content: center;
        margin-top: 20px;
        margin-bottom: 1rem;
    ">
        <img src="data:image/jpeg;base64,{img_base64}"
             style="width: 200px; height: 200px; border-radius: 50%;
                    object-fit: cover; box-shadow: 0 8px 30px rgba(99, 102, 241, 0.3);">
    </div>
    """, unsafe_allow_html=True)

# Subtitle
st.markdown("""
<div style="text-align: center;">
    <div class="hero-subtitle">Music Recommendation System</div>
</div>
""", unsafe_allow_html=True)

# Music Card
st.markdown("""
<div class="feature-card">
    <div class="feature-icon">🎵</div>
    <div class="feature-title">Music</div>
    <div class="feature-description">
        Discover songs based on your mood<br>
        • Mood-based filtering<br>
        • 114,000+ songs<br>
        • Interactive analytics
    </div>
</div>
""", unsafe_allow_html=True)

if st.button("Explore Music", key="music_btn", use_container_width=True):
    st.switch_page("pages/1_Music.py")

# Footer
st.markdown("""
<div class="footer">
    MELORA • Final Project Kelompok 4 • AI-Powered Music Recommendations
</div>
""", unsafe_allow_html=True)
