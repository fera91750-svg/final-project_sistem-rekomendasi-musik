"""
Film Recommendation Engine
Handles film data loading, filtering, and recommendations
"""

import pandas as pd
import numpy as np
import os
import re
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class FilmRecommendationEngine:
    """
    Modular film recommendation engine
    Supports content-based filtering using TF-IDF and cosine similarity
    """

    def __init__(self):
        self.df = None
        self.cosine_sim = None
        self.tfidf_matrix = None
        self.genres = []
        self.years = []
        self._load_data()

    @st.cache_resource
    def _load_data(_self):
        """Load film dataset and compute similarity matrix (cached)"""
        try:
            # Get the correct path
            current_dir = os.path.dirname(__file__)
            data_dir = os.path.join(current_dir, "..", "data", "film")
            dataset_path = os.path.join(data_dir, "AllMovies_CLEANED.csv")

            # Load dataset
            _self.df = pd.read_csv(dataset_path)

            # Clean data
            _self._clean_data()

            # Create soup for content-based filtering
            _self._create_soup()

            # Compute TF-IDF and cosine similarity
            _self._compute_similarity()

            # Extract unique genres and years
            _self._extract_metadata()

            print(f"Film dataset loaded: {len(_self.df)} films")

        except Exception as e:
            print(f"Error loading film data: {e}")
            raise

    def _clean_data(self):
        """Clean and preprocess data"""
        # Convert genres_list from string to actual list
        self.df['genres_list'] = self.df['genres_list'].apply(eval)

        # Handle missing values
        self.df['description'] = self.df['description'].fillna('')
        self.df['actors'] = self.df['actors'].fillna('Unknown')
        self.df['directors'] = self.df['directors'].fillna('Unknown')

    def _clean_text(self, text):
        """Clean text for TF-IDF"""
        if isinstance(text, str):
            text = text.lower()
            text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
            text = re.sub(r"\s+", " ", text).strip()
            return text
        return ""

    def _create_soup(self):
        """Create 'soup' - combined features for content-based filtering"""
        def clean_actors(x):
            if isinstance(x, str):
                return x.lower().replace(",", " ").replace(" ", "_")
            return ""

        def clean_directors(x):
            if isinstance(x, str):
                return x.lower().replace(",", " ").replace(" ", "_")
            return ""

        def clean_genres(x):
            if isinstance(x, list):
                return " ".join([g.lower().replace(" ", "_") for g in x])
            return ""

        # Create soup
        self.df["soup"] = (
            self.df["description"].apply(self._clean_text) + " " +
            self.df["actors"].apply(clean_actors) + " " +
            self.df["directors"].apply(clean_directors) + " " +
            self.df["genres_list"].apply(clean_genres)
        )

    def _compute_similarity(self):
        """Compute TF-IDF matrix and cosine similarity"""
        try:
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                stop_words='english',
                ngram_range=(1, 3),
                max_features=50000
            )

            # Fit and transform
            self.tfidf_matrix = vectorizer.fit_transform(self.df["soup"])

            # Compute cosine similarity
            self.cosine_sim = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)

            print("Similarity matrix computed successfully")

        except Exception as e:
            print(f"Could not compute similarity: {e}")
            self.cosine_sim = None

    def _extract_metadata(self):
        """Extract unique genres and years"""
        # Get all unique genres
        all_genres = []
        for genres in self.df['genres_list']:
            all_genres.extend(genres)
        self.genres = sorted(list(set(all_genres)))

        # Get unique years (sorted)
        self.years = sorted(self.df['release_year'].dropna().unique().astype(int).tolist(), reverse=True)

    def search_by_title(self, title, fuzzy=True):
        """
        Search films by title

        Args:
            title (str): Film title to search
            fuzzy (bool): Allow fuzzy matching

        Returns:
            DataFrame: Matching films
        """
        if fuzzy:
            # Case-insensitive partial match
            mask = self.df['title'].str.contains(title, case=False, na=False)
        else:
            # Exact match
            mask = self.df['title'].str.lower() == title.lower()

        results = self.df[mask]
        return results.sort_values('rating', ascending=False)

    def filter_by_rating(self, min_rating=0, max_rating=10):
        """Filter films by rating range"""
        filtered = self.df[
            (self.df['rating'] >= min_rating) &
            (self.df['rating'] <= max_rating)
        ]
        return filtered.sort_values('rating', ascending=False)

    def filter_by_year(self, year):
        """Filter films by release year"""
        filtered = self.df[self.df['release_year'] == year]
        return filtered.sort_values('rating', ascending=False)

    def filter_by_genre(self, genres):
        """
        Filter films by genres

        Args:
            genres (list): List of genre names

        Returns:
            DataFrame: Filtered films
        """
        if not genres:
            return self.df

        # Filter films that contain ANY of the selected genres
        mask = self.df['genres_list'].apply(
            lambda x: any(genre in x for genre in genres)
        )
        filtered = self.df[mask]
        return filtered.sort_values('rating', ascending=False)

    def filter_combined(self, min_rating=0, max_rating=10, year=None, genres=None):
        """
        Apply multiple filters at once

        Args:
            min_rating (float): Minimum rating
            max_rating (float): Maximum rating
            year (int, optional): Release year
            genres (list, optional): List of genres

        Returns:
            DataFrame: Filtered films
        """
        filtered = self.df.copy()

        # Rating filter
        filtered = filtered[
            (filtered['rating'] >= min_rating) &
            (filtered['rating'] <= max_rating)
        ]

        # Year filter
        if year:
            filtered = filtered[filtered['release_year'] == year]

        # Genre filter
        if genres:
            mask = filtered['genres_list'].apply(
                lambda x: any(genre in x for genre in genres)
            )
            filtered = filtered[mask]

        return filtered.sort_values('rating', ascending=False)

    def get_similar_films(self, title, n=5):
        """
        Get similar films using cosine similarity

        Args:
            title (str): Film title
            n (int): Number of recommendations

        Returns:
            DataFrame: Similar films
        """
        if self.cosine_sim is None:
            print("Similarity matrix not available")
            return pd.DataFrame()

        try:
            # Create index mapping
            indices = pd.Series(self.df.index, index=self.df['title']).drop_duplicates()

            # Get index of the film
            if title not in indices:
                # Try fuzzy search
                search_results = self.search_by_title(title, fuzzy=True)
                if search_results.empty:
                    return pd.DataFrame()
                title = search_results.iloc[0]['title']

            idx = indices[title]

            # Get similarity scores
            sim_scores = list(enumerate(self.cosine_sim[idx]))

            # Sort by similarity
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

            # Get top N similar films (excluding itself)
            sim_scores = sim_scores[1:n+1]

            # Get film indices
            film_indices = [i[0] for i in sim_scores]

            # Return similar films with similarity scores
            result = self.df.iloc[film_indices].copy()
            result['similarity_score'] = [score[1] for score in sim_scores]

            return result

        except Exception as e:
            print(f"Error getting similar films: {e}")
            return pd.DataFrame()

    def get_platform_recommendation(self, film_data):
        """
        Get streaming platform recommendation (rule-based)

        Args:
            film_data (Series): Film data

        Returns:
            list: Recommended platforms
        """
        platforms = []
        genres = film_data['genres_list']
        rating = film_data['rating']

        # Genre-based rules
        if any(g in ['Animation', 'Family'] for g in genres):
            platforms.append('Disney+')

        if any(g in ['Horror', 'Thriller'] for g in genres):
            platforms.append('Netflix')

        if any(g in ['Action', 'Adventure', 'Sci-Fi'] for g in genres):
            platforms.append('Prime Video')

        if any(g in ['Drama', 'Romance'] for g in genres):
            platforms.extend(['Netflix', 'Viu'])

        if any(g in ['Comedy'] for g in genres):
            platforms.append('Netflix')

        # Rating-based rules
        if rating >= 8.0:
            platforms.append('HBO Max')

        if rating >= 7.0:
            platforms.append('Apple TV+')

        # Remove duplicates and return
        platforms = list(set(platforms))

        # Default if no match
        if not platforms:
            platforms = ['Netflix', 'Prime Video', 'Disney+']

        return platforms[:3]  # Return top 3

    def get_top_rated(self, n=20):
        """Get top rated films"""
        return self.df.nlargest(n, 'rating')

    def get_genre_distribution(self):
        """Get genre distribution"""
        all_genres = []
        for genres in self.df['genres_list']:
            all_genres.extend(genres)

        from collections import Counter
        genre_counts = Counter(all_genres)
        return dict(genre_counts.most_common(20))

    def get_dataset_info(self):
        """Get dataset information"""
        return {
            'total_films': len(self.df),
            'total_genres': len(self.genres),
            'total_directors': self.df['directors'].nunique(),
            'year_range': (int(self.df['release_year'].min()),
                          int(self.df['release_year'].max())),
            'avg_rating': round(self.df['rating'].mean(), 2),
            'genre_distribution': self.get_genre_distribution()
        }

    def get_available_genres(self):
        """Get list of available genres"""
        return self.genres

    def get_available_years(self):
        """Get list of available years"""
        return self.years
