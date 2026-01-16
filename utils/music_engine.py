"""
Music Recommendation Engine
Handles music data loading, mood classification, and recommendations
"""

import pandas as pd
import numpy as np
import joblib
import os
import streamlit as st

class MusicRecommendationEngine:
    """
    Modular music recommendation engine
    Optimized to prevent duplicate songs in recommendations.
    """

    def __init__(self):
        self.df = None
        self.model = None
        self.label_encoder = None
        self.genres = []
        self.moods = ['Happy', 'Sad', 'Calm', 'Tense']
        self._load_data()

    @st.cache_resource
    def _load_data(_self):
        """Load music dataset and models (cached for performance)"""
        try:
            # Jalur folder data
            current_dir = os.path.dirname(__file__)
            data_dir = os.path.join(current_dir, "..", "data", "music")

            # 1. Load dataset
            dataset_path = os.path.join(data_dir, "dataset.csv")
            df_raw = pd.read_csv(dataset_path)

            # 2. PEMBERSIHAN DUPLIKAT (Penting agar tidak muncul lagu ganda)
            # Menghapus duplikat berdasarkan track_id unik Spotify
            df_cleaned = df_raw.drop_duplicates(subset=['track_id'], keep='first')
            
            # Menghapus duplikat jika lagu yang sama muncul dengan ID berbeda (biasanya beda album)
            df_cleaned = df_cleaned.drop_duplicates(subset=['track_name', 'artists'], keep='first')
            
            _self.df = df_cleaned

            # 3. Load trained models
            try:
                model_path = os.path.join(data_dir, "music_mood_model.pkl")
                encoder_path = os.path.join(data_dir, "label_encoder.pkl")

                _self.model = joblib.load(model_path)
                _self.label_encoder = joblib.load(encoder_path)
                print("Trained models loaded successfully!")
            except Exception as e:
                print(f"Models not loaded, using rule-based: {e}")
                _self.model = None
                _self.label_encoder = None

            # 4. Tambahkan kolom mood
            _self._add_mood_column()

            # 5. Ambil daftar genre unik
            _self.genres = sorted(_self.df['track_genre'].unique().tolist())

            print(f"Dataset loaded: {len(_self.df)} unique songs, {len(_self.genres)} genres")

        except Exception as e:
            print(f"Error loading data: {e}")
            raise

    def _classify_mood_rule_based(self, row):
        """Rule-based mood classification (Valence vs Energy)"""
        valence = row['valence']
        energy = row['energy']

        if valence >= 0.5 and energy >= 0.5:
            return 'Happy'
        elif valence < 0.5 and energy < 0.5:
            return 'Sad'
        elif valence >= 0.5 and energy < 0.5:
            return 'Calm'
        else:
            return 'Tense'

    def _add_mood_column(self):
        """Add mood column to dataframe using model or rules"""
        if self.model is not None and self.label_encoder is not None:
            try:
                features = ['danceability', 'energy', 'valence', 'tempo',
                           'acousticness', 'instrumentalness', 'loudness', 'speechiness']
                X = self.df[features]
                mood_encoded = self.model.predict(X)
                self.df['mood'] = self.label_encoder.inverse_transform(mood_encoded)
            except Exception as e:
                self.df['mood'] = self.df.apply(self._classify_mood_rule_based, axis=1)
        else:
            self.df['mood'] = self.df.apply(self._classify_mood_rule_based, axis=1)

    def get_recommendations_by_mood(self, mood, n=10):
        """Get unique song recommendations by mood"""
        if mood not in self.moods:
            raise ValueError(f"Mood must be one of {self.moods}")

        filtered = self.df[self.df['mood'] == mood]
        recommendations = filtered.nlargest(n, 'popularity')

        return recommendations[['track_name', 'artists', 'album_name',
                               'track_id', 'popularity', 'valence',
                               'energy', 'track_genre', 'mood']]

    def get_recommendations_by_mood_and_genre(self, mood, genre, n=10):
        """Get unique song recommendations by both mood and genre"""
        filtered = self.df[
            (self.df['mood'] == mood) & 
            (self.df['track_genre'] == genre)
        ]

        if filtered.empty:
            return pd.DataFrame()

        recommendations = filtered.nlargest(n, 'popularity')
        return recommendations[['track_name', 'artists', 'album_name',
                               'track_id', 'popularity', 'valence',
                               'energy', 'track_genre', 'mood']]

    @staticmethod
    def create_spotify_embed(track_id, width="100%", height=80):
        """
        Create Spotify embed HTML (Compact Version)
        Menggunakan height=80 untuk 'Compact Player' agar tidak memakan tempat
        """
        return f'''
        <iframe src="https://open.spotify.com/embed/track/{track_id}?utm_source=generator"
                width="{width}"
                height="{height}"
                frameBorder="0"
                allowfullscreen=""
                allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                loading="lazy">
        </iframe>
        '''

    def get_available_genres(self):
        return self.genres

    def get_available_moods(self):
        return self.moods
