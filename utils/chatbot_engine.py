import streamlit as st
import pandas as pd
from music_engine import MusicRecommendationEngine # Pastikan file music_engine.py ada di folder yang sama

# Inisialisasi Engine
engine = MusicRecommendationEngine()

# --- FUNGSI DETEKSI MOOD DARI TEKS ---
def deteksi_mood_user(teks):
    teks = teks.lower()
    
    # Kamus kata kunci sederhana
    if any(word in teks for word in ['sedih', 'galau', 'sad', 'nangis', 'kecewa', 'duka']):
        return 'Sad'
    elif any(word in teks for word in ['senang', 'happy', 'bahagia', 'gembira', 'ceria', 'mantap']):
        return 'Happy'
    elif any(word in teks for word in ['tenang', 'santai', 'calm', 'rileks', 'adem', 'istirahat']):
        return 'Calm'
    elif any(word in teks for word in ['tense', 'tegang', 'marah', 'stres', 'stress', 'energi', 'semangat']):
        return 'Tense'
    
    return None

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="VibeTune Chatbot", page_icon="🎵")
st.title("🎵 VibeTune: Music Mood Chatbot")
st.markdown("Halo! Ceritakan perasaanmu sekarang, dan aku akan carikan lagu yang cocok.")

# Inisialisasi Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Menampilkan chat lama dari history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "songs" in message:
            for track_id in message["songs"]:
                st.components.v1.html(engine.create_spotify_embed(track_id), height=80)

# --- LOGIKA INPUT USER ---
if prompt := st.chat_input("Apa yang kamu rasakan?"):
    # 1. Tampilkan pesan user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Deteksi mood berdasarkan input user yang baru saja diketik
    mood_terdeteksi = deteksi_mood_user(prompt)

    # 3. Buat respon Bot
    with st.chat_message("assistant"):
        if mood_terdeteksi:
            # Ambil rekomendasi dari engine berdasarkan mood yang baru terdeteksi
            recs = engine.get_recommendations_by_mood(mood_terdeteksi, n=5)
            
            # Template respon dinamis
            template_respon = {
                'Happy': "Wah, senang mendengarnya! ✨ Tetap semangat ya, ini lagu biar harimu makin ceria:",
                'Sad': "Aku mengerti perasaamu... 🌧️ Tak apa merasa sedih sesekali. Ini beberapa lagu untuk menemanimu:",
                'Calm': "Waktunya bersantai... 🍃 Tarik napas dalam-dalam, dan nikmati ketenangan ini:",
                'Tense': "Energi kamu lagi tinggi ya! 🔥 Ini lagu yang cocok buat mood kamu yang lagi tegang/semangat:"
            }
            
            response_text = template_respon[mood_terdeteksi]
            st.markdown(response_text)
            
            # Tampilkan Iframe Spotify dan simpan list ID lagu untuk history
            list_track_id = []
            for _, row in recs.iterrows():
                st.components.v1.html(engine.create_spotify_embed(row['track_id']), height=80)
                list_track_id.append(row['track_id'])
            
            # Simpan ke history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response_text,
                "songs": list_track_id
            })
            
        else:
            # Jika mood tidak terdeteksi
            error_msg = "Aku belum yakin apa moodmu. Bisa coba ceritakan lebih spesifik seperti 'aku lagi sedih' atau 'aku butuh yang tenang'?"
            st.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
