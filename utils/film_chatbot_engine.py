"""
Film Chatbot Engine for Streamlit
Wrapper that imports from data/film/llm_film_module.py

This file acts as a bridge between the LLM module and Streamlit UI
"""

import sys
import os

# Add data/film folder to path
data_film_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'film')
sys.path.insert(0, data_film_folder)

# Import from film module
from llm_film_module import FilmLLMChatbot, create_chatbot


class FilmChatbot(FilmLLMChatbot):
    """
    Streamlit-specific wrapper for FilmLLMChatbot
    Inherits all functionality from the film module
    """

    def __init__(self, film_engine):
        """
        Initialize chatbot with FilmRecommendationEngine

        Args:
            film_engine: FilmRecommendationEngine instance from Streamlit
        """
        # Extract components from engine
        film_df = film_engine.df
        tfidf_matrix = film_engine.tfidf_matrix
        cosine_sim = film_engine.cosine_sim

        # Initialize parent class
        super().__init__(film_df, tfidf_matrix, cosine_sim)


# Export for easy import in Streamlit
__all__ = ['FilmChatbot', 'create_chatbot']
