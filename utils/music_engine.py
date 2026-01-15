"""
Music Recommendation Engine
Anti-duplicate, unlimited recommendations, Spotify full embed
"""

import pandas as pd
import joblib
import os
import streamlit as st


class MusicRecommendationEngine:

    def __init__(self):
        self.df = None
        self.model = None
        self.label_encoder = None
        self.genres = []
        self.moods = ['Happy', 'Sad', 'Calm', 'Tense']
        self._load_data()

    # ===================== LOAD DATA =====================
    @st.cache_resource
    def _load_data(_self):
        try:
            current_dir = os.path.dirname(__file__)
            data_dir = os.path.join(current_dir, "..", "data", "music")

            dataset_path = os.path.join(data_dir, "dataset.csv")
            _self.df = pd.read_csv(dataset_path)

            # Load ML model if exists
            try:
                model_path = os.path.join(data_dir, "music_mood_model.pkl")
                encoder_path = os.path.join(data_dir, "label_encoder.pkl")
                _self.model = joblib.load(model_path)
                _self.label_encoder = joblib.load(encoder_path)
                print("✅ Model loaded")
            except:
                _self.model = None
                _self.label_encoder = None
                print("⚠️ Model not found, using rule-based")

            _self._add_mood_column()

            # 🔥 ANTI DUPLIKAT GLOBAL
            _self.df = _self.df.drop_duplicates(subset="track_id")

            _self.genres = sorted(_self.df['track_genre'].unique().tolist())
            print(f"🎵 Dataset: {len(_self.df)} unique songs")

        except Exception as e:
            raise RuntimeError(f"Load error: {e}")

    # ===================== MOOD CLASSIFICATION =====================
    def _classify_mood_rule_based(self, row):
        if row['valence'] >= 0.5 and row['energy'] >= 0.5:
            return 'Happy'
        elif row['valence'] < 0.5 and row['energy'] < 0.5:
            return 'Sad'
        elif row['valence'] >= 0.5 and row['energy'] < 0.5:
            return 'Calm'
        else:
            return 'Tense'

    def _add_mood_column(self):
        if self.model is not None:
            try:
                features = [
                    'danceability', 'energy', 'valence', 'tempo',
                    'acousticness', 'instrumentalness',
                    'loudness', 'speechiness'
                ]
                X = self.df[features]
                encoded = self.model.predict(X)
                self.df['mood'] = self.label_encoder.inverse_transform(encoded)
                return
            except:
                pass

        self.df['mood'] = self.df.apply(self._classify_mood_rule_based, axis=1)

    # ===================== RECOMMENDATION CORE =====================
    def _shuffle_unique(self, df):
        """
        Shuffle + anti duplicate Spotify ID
        """
        return (
            df.drop_duplicates(subset="track_id")
              .sample(frac=1, random_state=None)
              .reset_index(drop=True)
        )

    def recommend_by_mood(self, mood):
        filtered = self.df[self.df['mood'] == mood]
        return self._shuffle_unique(filtered)

    def recommend_by_genre(self, genre):
        filtered = self.df[self.df['track_genre'] == genre]
        return self._shuffle_unique(filtered)

    def recommend_by_mood_and_genre(self, mood, genre):
        filtered = self.df[
            (self.df['mood'] == mood) &
            (self.df['track_genre'] == genre)
        ]
        return self._shuffle_unique(filtered)

    # ===================== SPOTIFY EMBED =====================
    @staticmethod
    def spotify_embed(track_id):
        """
        FULL SONG (login Spotify)
        """
        return f"""
        <iframe
            src="https://open.spotify.com/embed/track/{track_id}"
            width="100%"
            height="380"
            frameborder="0"
            allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture">
        </iframe>
        """

    # ===================== UTIL =====================
    def get_available_moods(self):
        return self.moods

    def get_available_genres(self):
        return self.genres

    def get_dataset_info(self):
        return {
            "total_songs": len(self.df),
            "unique_artists": self.df["artists"].nunique(),
            "genres": len(self.genres)
        }
