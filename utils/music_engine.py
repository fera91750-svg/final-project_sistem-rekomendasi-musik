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

            # Add mood column using rule-based or model-based classification
            _self._add_mood_column()

            # Get unique genres
            _self.genres = sorted(_self.df['track_genre'].unique().tolist())

            print(f"Dataset loaded: {len(_self.df)} songs, {len(_self.genres)} genres")

        except Exception as e:
            print(f"Error loading data: {e}")
            raise

    def _classify_mood_rule_based(self, row):
        """
        Rule-based mood classification
        Based on valence and energy values
        """
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
        """Add mood column to dataframe"""
        if self.model is not None and self.label_encoder is not None:
            # Use trained model
            try:
                features = ['danceability', 'energy', 'valence', 'tempo',
                           'acousticness', 'instrumentalness', 'loudness', 'speechiness']
                X = self.df[features]
                mood_encoded = self.model.predict(X)
                self.df['mood'] = self.label_encoder.inverse_transform(mood_encoded)
                print("Using model-based mood classification")
            except Exception as e:
                print(f"Model prediction failed, falling back to rule-based: {e}")
                self.df['mood'] = self.df.apply(self._classify_mood_rule_based, axis=1)
        else:
            # Use rule-based classification
            self.df['mood'] = self.df.apply(self._classify_mood_rule_based, axis=1)
            print("Using rule-based mood classification")
    def get_recommendations_by_mood(self, mood, n=10):
        if mood not in self.moods:
            raise ValueError(f"Mood must be one of {self.moods}")

        # Filter berdasarkan mood
        filtered = self.df[self.df['mood'] == mood]

        # AMBIL TOP 50 DULU, LALU ACAK n LAGU DARI SANA
        # Agar tetap merekomendasikan lagu bagus, tapi tidak itu-itu saja
        top_pool = filtered.nlargest(50, 'popularity') 
        recommendations = top_pool.sample(min(n, len(top_pool)))

        return recommendations[['track_name', 'artists', 'album_name',
                           'track_id', 'popularity', 'valence',
                           'energy', 'track_genre', 'mood']]
 
    def get_recommendations_by_genre(self, genre, n=10):
        """
        Get song recommendations by genre

        Args:
            genre (str): Music genre
            n (int): Number of recommendations

        Returns:
            DataFrame: Recommended songs
        """
        # Filter by genre
        filtered = self.df[self.df['track_genre'] == genre]

        if filtered.empty:
            return pd.DataFrame()

        # Sort by popularity
        recommendations = filtered.nlargest(n, 'popularity')

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

    # Ambil pool yang agak besar (misal 30 lagu), lalu acak
    pool_size = max(n * 3, 30)
    top_pool = filtered.nlargest(pool_size, 'popularity')
    recommendations = top_pool.sample(min(n, len(top_pool)))

    return recommendations[['track_name', 'artists', 'album_name',
                           'track_id', 'popularity', 'valence',
                           'energy', 'track_genre', 'mood']]
    
    def get_mood_distribution(self):
        """
        Get mood distribution for visualization

        Returns:
            dict: Mood counts
        """
        return self.df['mood'].value_counts().to_dict()

    def get_genre_distribution(self, mood=None):
        """
        Get genre distribution, optionally filtered by mood

        Args:
            mood (str, optional): Filter by mood

        Returns:
            dict: Genre counts
        """
        if mood:
            filtered = self.df[self.df['mood'] == mood]
        else:
            filtered = self.df

        return filtered['track_genre'].value_counts().head(20).to_dict()

    def get_mood_stats(self):
        """
        Get statistical summary of moods

        Returns:
            DataFrame: Mood statistics
        """
        stats = self.df.groupby('mood').agg({
            'valence': 'mean',
            'energy': 'mean',
            'danceability': 'mean',
            'acousticness': 'mean',
            'popularity': 'mean'
        }).round(3)

        return stats

    @staticmethod
    def create_spotify_embed(track_id, width=300, height=380):
        """
        Create Spotify embed HTML

        Args:
            track_id (str): Spotify track ID
            width (int): Player width
            height (int): Player height

        Returns:
            str: HTML iframe code
        """
        return f'''
        <iframe src="https://open.spotify.com/embed/track/{track_id}"
                width="{width}"
                height="{height}"
                frameborder="0"
                allowtransparency="true"
                allow="encrypted-media">
        </iframe>
        '''

    @staticmethod
    def create_spotify_search_link(track_name, artist):
        """
        Create Spotify search link

        Args:
            track_name (str): Song title
            artist (str): Artist name

        Returns:
            str: Spotify search URL
        """
        query = f"{track_name} {artist}".replace(" ", "+")
        return f"https://open.spotify.com/search/{query}"

    def get_available_genres(self):
        """Get list of available genres"""
        return self.genres

    def get_available_moods(self):
        """Get list of available moods"""
        return self.moods

    def get_dataset_info(self):
        """Get dataset information"""
        return {
            'total_songs': len(self.df),
            'total_genres': len(self.genres),
            'total_artists': self.df['artists'].nunique(),
            'moods': self.get_mood_distribution()
        }
