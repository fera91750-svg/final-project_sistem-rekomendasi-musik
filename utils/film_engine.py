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
    Can work with or without trained models
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
            current_dir = os.path.dirname(__file__)
            data_dir = os.path.join(current_dir, "..", "data", "music")

            # Load dataset
            dataset_path = os.path.join(data_dir, "dataset.csv")
            _self.df = pd.read_csv(dataset_path)

            # Try to load trained models
            try:
                model_path = os.path.join(data_dir, "music_mood_model.pkl")
                encoder_path = os.path.join(data_dir, "label_encoder.pkl")

                _self.model = joblib.load(model_path)
                _self.label_encoder = joblib.load(encoder_path)

                print("Trained models loaded successfully!")
            except Exception as e:
                print(f"Models not loaded, using rule-based classification: {e}")
                _self.model = None
                _self.label_encoder = None

            _self._add_mood_column()
            _self.genres = sorted(_self.df['track_genre'].unique().tolist())

            print(f"Dataset loaded: {len(_self.df)} songs, {len(_self.genres)} genres")

        except Exception as e:
            print(f"Error loading data: {e}")
            raise

    def _classify_mood_rule_based(self, row):
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
        if self.model is not None and self.label_encoder is not None:
            try:
                features = ['danceability', 'energy', 'valence', 'tempo',
                           'acousticness', 'instrumentalness', 'loudness', 'speechiness']
                X = self.df[features]
                mood_encoded = self.model.predict(X)
                self.df['mood'] = self.label_encoder.inverse_transform(mood_encoded)
                print("Using model-based mood classification")
            except Exception as e:
                print(f"Model prediction failed: {e}")
                self.df['mood'] = self.df.apply(self._classify_mood_rule_based, axis=1)
        else:
            self.df['mood'] = self.df.apply(self._classify_mood_rule_based, axis=1)

    # --- BAGIAN PERBAIKAN UTAMA (ANTI-DUPLIKAT & SINKRONISASI) ---

    def get_recommendations_by_mood(self, mood, n=5):
        """Get song recommendations by mood - FIXED: Unique titles & synced track_ids"""
        if mood not in self.moods:
            raise ValueError(f"Mood must be one of {self.moods}")

        filtered = self.df[self.df['mood'] == mood].copy()
        if filtered.empty:
            return pd.DataFrame()

        # 1. Hapus Duplikat Judul sebelum Sampling
        # Ini memastikan satu baris data (Judul + track_id) tetap sinkron
        filtered = filtered.sort_values(by='popularity', ascending=False)
        filtered = filtered.drop_duplicates(subset=['track_name'], keep='first')

        # 2. Ambil pool lagu terpopuler yang sudah unik
        pool_size = min(len(filtered), 100)
        top_pool = filtered.head(pool_size)
        
        # 3. Ambil n lagu secara acak dari pool unik
        sample_size = min(len(top_pool), n)
        recommendations = top_pool.sample(n=sample_size).sort_values(by='popularity', ascending=False)

        return recommendations[['track_name', 'artists', 'album_name',
                               'track_id', 'popularity', 'track_genre', 'mood']]

    def get_recommendations_by_genre(self, genre, n=5):
        """Get song recommendations by genre - FIXED: Unique titles & synced track_ids"""
        filtered = self.df[self.df['track_genre'] == genre].copy()
        if filtered.empty:
            return pd.DataFrame()

        # Hapus Duplikat Judul agar tidak muncul berulang
        filtered = filtered.sort_values(by='popularity', ascending=False)
        filtered = filtered.drop_duplicates(subset=['track_name'], keep='first')

        pool_size = min(len(filtered), 50)
        top_pool = filtered.head(pool_size)
        
        sample_size = min(len(top_pool), n)
        recommendations = top_pool.sample(n=sample_size).sort_values(by='popularity', ascending=False)

        return recommendations[['track_name', 'artists', 'album_name',
                               'track_id', 'popularity', 'track_genre', 'mood']]

    @staticmethod
    def create_spotify_embed(track_id, width="100%", height=80):
        # Menggunakan height=80 agar tampilan compact seperti di screenshot Anda
        return f'''
        <iframe src="https://open.spotify.com/embed/track/{track_id}"
                width="{width}"
                height="{height}"
                frameborder="0"
                allowtransparency="true"
                allow="encrypted-media"
                style="border-radius: 8px;">
        </iframe>
        '''

    
    @staticmethod
    def create_spotify_search_link(track_name, artist):
        query = f"{track_name} {artist}".replace(" ", "+")
        return f"https://open.spotify.com/search/{query}"

    def get_available_genres(self):
        return self.genres

    def get_available_moods(self):
        return self.moods

    def get_dataset_info(self):
        return {
            'total_songs': len(self.df),
            'total_genres': len(self.genres),
            'total_artists': self.df['artists'].nunique(),
            'moods': self.get_mood_distribution()
        }
