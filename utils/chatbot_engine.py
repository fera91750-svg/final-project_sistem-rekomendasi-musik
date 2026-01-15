def chat(self, user_text):
        # 1. Prompt LLM untuk menganalisis konteks curhatan user
        prompt = f"""
        User curhat: "{user_text}"
        
        Tugas Anda:
        1. Berikan respon empati, ramah, dan sangat personal dalam Bahasa Indonesia. 
           Jika user menyebut kegiatan khusus (seminar, ujian, dll), berikan semangat untuk itu.
        2. Tentukan satu kategori mood musik yang cocok (Happy, Sad, Calm, Tense).
        
        Format jawaban wajib:
        Kategori: [Nama Mood]
        Respon: [Kalimat dukungan Anda]
        """
        
        try:
            response = self.model.generate_content(prompt).text
            lines = response.split('\n')
            detected_mood = "Happy"
            support_msg = ""
            
            for line in lines:
                if "Kategori:" in line:
                    for m in ["Happy", "Sad", "Calm", "Tense"]:
                        if m.lower() in line.lower(): detected_mood = m
                if "Respon:" in line:
                    support_msg = line.replace("Respon:", "").strip()
            
            if not support_msg: support_msg = response
        except:
            detected_mood = "Happy"
            support_msg = "Semangat ya! Apapun yang kamu hadapi, kamu pasti bisa melaluinya."

        # 2. Ambil lagu dari music_engine berdasarkan mood
        songs_df = self.engine.get_recommendations_by_mood(detected_mood, n=5)
        
        # 3. Susun Pesan Teks dan List Data Lagu Lengkap
        full_text = f"{support_msg}\n\n**Rekomendasi lagu untukmu:**\n"
        songs_list = []
        
        if not songs_df.empty:
            for i, row in songs_df.iterrows():
                # Tambahkan ke tampilan teks chat
                full_text += f"{i+1}. **{row['track_name']}** - {row['artists']}\n"
                
                # Masukkan SEMUA data ke list agar UI tidak KeyError
                songs_list.append({
                    "title": row["track_name"],
                    "artist": row["artists"],
                    "album": row["album_name"],  # Ini yang tadi bikin error karena hilang
                    "genre": row["track_genre"], # Ini juga dibutuhkan oleh UI Anda
                    "popularity": row["popularity"],
                    "track_id": row["track_id"]
                })
        else:
            full_text += "Maaf, saat ini saya tidak menemukan lagu yang pas. Coba ceritakan hal lain!"

        return {
            "text": full_text, 
            "songs": songs_list
        }
