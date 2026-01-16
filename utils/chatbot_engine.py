import streamlit as st
from engine.music_engine import MusicRecommendationEngine
from engine.music_chatbot_engine import MusicChatbot

# 1. Inisialisasi Engine
if 'music_engine' not in st.session_state:
    st.session_state.music_engine = MusicRecommendationEngine()

if 'chatbot' not in st.session_state:
    st.session_state.chatbot = MusicChatbot(st.session_state.music_engine)

# 2. Inisialisasi Riwayat Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- TAMPILAN CHAT ---
st.title("🎵 Music AI Chatbot")

# Menampilkan pesan dari riwayat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Jika ada data rekomendasi di pesan ini, tampilkan kartunya
        if "recommendations" in message:
            for _, row in message["recommendations"].iterrows():
                with st.container(border=True): # Membuat box putih seperti di gambar
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.subheader(row['track_name'])
                        st.write(f"{row['artists']}")
                        st.caption(f"{row['track_genre']} • ⭐ {row['popularity']}/100")
                    with col2:
                        # Menampilkan Embed Spotify
                        st.components.v1.html(
                            st.session_state.music_engine.create_spotify_embed(row['track_id']),
                            height=80
                        )

# 3. Input Chat
if prompt := st.chat_input("Lagi pengen denger lagu apa hari ini?"):
    # Tampilkan pesan user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Ambil respon dari Chatbot Engine
    # Asumsi: chatbot.process_message mengembalikan teks respon DAN dataframe lagu
    response_text, rec_df = st.session_state.chatbot.process_message(prompt)

    # Simpan dan tampilkan respon bot
    with st.chat_message("assistant"):
        st.markdown(response_text)
        
        if not rec_df.empty:
            for _, row in rec_df.iterrows():
                with st.container(border=True):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.subheader(row['track_name'])
                        st.write(f"{row['artists']}")
                        st.caption(f"{row['track_genre']} • ⭐ {row['popularity']}/100")
                    with col2:
                        st.components.v1.html(
                            st.session_state.music_engine.create_spotify_embed(row['track_id']),
                            height=80
                        )
    
    # Simpan ke riwayat
    st.session_state.messages.append({
        "role": "assistant", 
        "content": response_text,
        "recommendations": rec_df
    })
