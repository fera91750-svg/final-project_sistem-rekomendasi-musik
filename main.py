"""
🎵 MELORA - Music Recommendation System
Landing Page - Focus on Music recommendations
"""

import streamlit as st
import os
import sys
import base64

# --- FIX MODULE NOT FOUND ---
# Menambahkan folder data/music ke path agar modul LLM bisa di-import
root_path = os.path.dirname(os.path.abspath(__file__))
llm_folder = os.path.join(root_path, 'data', 'music')
if llm_folder not in sys.path:
    sys.path.insert(0, llm_folder)
# -----------------------------

# Page configuration
st.set_page_config(
    page_title="MELORA - AI Music System",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    .main {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
    }
    .block-container {
        padding-top: 3rem;
        max-width: 800px;
    }
    .feature-card {
        background: linear-gradient(145deg, #1E293B, #0F172A);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 3rem 2rem;
        text-align: center;
        transition: all 0.3s ease;
        margin: 0 auto;
        max-width: 500px;
    }
    .feature-card:hover {
        border-color: #6366F1;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.2);
    }
    .stButton>button {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
        color: #FFFFFF;
        font-weight: 700;
        padding: 0.75rem 2rem;
        border-radius: 500px;
        border: none;
        transition: all 0.2s ease;
        text-transform: uppercase;
        margin-top: 1.5rem;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%);
        transform: scale(1.05);
    }
    .feature-icon { font-size: 4.5rem; margin-bottom: 1.5rem; }
    .feature-title { font-size: 2rem; font-weight: 700; color: #F1F5F9; margin-bottom: 1rem; }
    .feature-description { font-size: 1.1rem; color: #CBD5E1; line-height: 1.6; }
    .footer { text-align: center; color: #64748B; font-size: 0.85rem; margin-top: 4rem; }
</style>
""", unsafe_allow_html=True)

# Hero section with logo
logo_path = os.path.join(root_path, 'assets', 'logo.jpeg')
if os.path.exists(logo_path):
    with open(logo_path, "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode()

    st.markdown(f"""
    <div style="display: flex; justify-content: center; margin-bottom: 1.5rem;">
        <img src="data:image/jpeg;base64,{img_base64}"
             style="width: 260px; height: 300px; border-radius: 50%;
                    object-fit: cover; box-shadow: 0 10px 40px rgba(99, 102, 241, 0.3);">
    </div>
    """, unsafe_allow_html=True)

# Subtitle
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <div style="font-size: 1.5rem; color: #000000; font-weight: 400;">AI-Powered Music Recommendation System</div>
</div>
""", unsafe_allow_html=True)

# Main Content - Music Card Only
st.markdown("""
<div class="feature-card">
    <div class="feature-icon">🎵</div>
    <div class="feature-title">Music Experience</div>
    <div class="feature-description">
        Temukan musik yang sesuai dengan perasaanmu hari ini.<br><br>
        • AI Chat Assistant (Powered by LLM)<br>
        • Mood-based Filtering<br>
        • 114,000+ Song Database<br>
        • Interactive Music Analytics
    </div>
</div>
""", unsafe_allow_html=True)

# Center the button
col_left, col_btn, col_right = st.columns([1, 2, 1])
with col_btn:
    if st.button("Start Exploring Music", key="music_btn", use_container_width=True):
        st.switch_page("pages/1_Music.py")

# Footer
st.markdown("""
<div class="footer">
    MELORA • Final Project Kelompok 4 • Built with Streamlit & LLM
</div>
""", unsafe_allow_html=True)
