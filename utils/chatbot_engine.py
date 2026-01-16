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
            # Get the correct path
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

            # Add mood column
            _self._add_mood_column()

            # Get unique genres
            _self.genres = sorted(_self.df['track_genre'].unique().tolist())

            print(f"Dataset loaded: {len(_self.df)} songs, {len(_self.genres)} genres")

        except Exception as e:
            print(f"Error loading data: {e}")
            raise

    def _classify_mood_rule_based(self, row):
        """Rule-based mood classification based on valence and energy"""
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

    # --- BAGIAN REKOMENDASI DENGAN RANDOMISASI AGAR TIDAK BERULANG ---

    def get_recommendations_by_mood(self, mood, n=10):
        if mood not in self.moods:
            raise ValueError(f"Mood must be one of {self.moods}")

        filtered = self.df[self.df['mood'] == mood]
        if filtered.empty:
            return pd.DataFrame()

        # Ambil pool 100 terpopuler agar kualitas terjaga
        pool_size = min(len(filtered), 100)
        top_pool = filtered.nlargest(pool_size, 'popularity')
        
        # Ambil n secara acak dan RESET INDEX agar chatbot bisa menampilkan data
        recommendations = top_pool.sample(n=min(len(top_pool), n)).reset_index(drop=True)

        return recommendations[['track_name', 'artists', 'album_name',
                               'track_id', 'popularity', 'valence',
                               'energy', 'track_genre', 'mood']]

    def get_recommendations_by_genre(self, genre, n=10):
        filtered = self.df[self.df['track_genre'] == genre]
        if filtered.empty:
            return pd.DataFrame()

        pool_size = min(len(filtered), 50)
        top_pool = filtered.nlargest(pool_size, 'popularity')
        
        recommendations = top_pool.sample(n=min(len(top_pool), n)).reset_index(drop=True)

        return recommendations[['track_name', 'artists', 'album_name',
                               'track_id', 'popularity', 'valence',
                               'energy', 'track_genre', 'mood']]

    def get_recommendations_by_mood_and_genre(self, mood, genre, n=10):
        filtered = self.df[
            (self.df['mood'] == mood) & 
            (self.df['track_genre'] == genre)
        ]
        if filtered.empty:
            return pd.DataFrame()

        # Acak langsung dari hasil filter dan reset index
        recommendations = filtered.sample(n=min(len(filtered), n)).reset_index(drop=True)

        return recommendations[['track_name', 'artists', 'album_name',
                               'track_id', 'popularity', 'valence',
                               'energy', 'track_genre', 'mood']]

    # --- FUNGSI STATISTIK DAN UTILITY ---

    def get_mood_distribution(self):
        return self.df['mood'].value_counts().to_dict()

    def get_genre_distribution(self, mood=None):
        filtered = self.df[self.df['mood'] == mood] if mood else self.df
        return filtered['track_genre'].value_counts().head(20).to_dict()

    def get_mood_stats(self):
        return self.df.groupby('mood').agg({
            'valence': 'mean', 'energy': 'mean', 'danceability': 'mean',
            'acousticness': 'mean', 'popularity': 'mean'
        }).round(3)

    # --- FUNGSI UNTUK TAMPILAN SPOTIFY (AUDIO) ---

    @staticmethod
    def create_spotify_embed(track_id, width="100%", height=80):
        """Menghasilkan iframe Spotify Player untuk Chatbot"""
        if not track_id or pd.isna(track_id):
            return ""
        # URL diperbaiki agar mengarah ke embed resmi
        return f'''
        <iframe src="https://open.spotify.com/embed/track/{track_id}"
                width="{width}"
                height="{height}"
                frameborder="0"
                allowtransparency="true"
                allow="encrypted-media; clipboard-write; picture-in-picture">
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
