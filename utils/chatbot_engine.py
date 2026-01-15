"""
Music Chatbot Engine for Streamlit
Wrapper that imports from data/music/llm_music_module.py

This file acts as a bridge between the LLM module and Streamlit UI
"""

import sys
import os

import google.generativeai as genai

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise RuntimeError(
        "GOOGLE_API_KEY tidak ditemukan. "
        "Set di Streamlit Cloud → Settings → Secrets"
    )

genai.configure(api_key=GOOGLE_API_KEY)

# Add data/music folder to path
data_music_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'music')
sys.path.insert(0, data_music_folder)

# Import from music module
from llm_music_module import MusicLLMChatbot, create_chatbot


class MusicChatbot(MusicLLMChatbot):
    """
    Streamlit-specific wrapper for MusicLLMChatbot
    Inherits all functionality from the music module
    """

    def __init__(self, music_engine):
        """
        Initialize chatbot with MusicRecommendationEngine

        Args:
            music_engine: MusicRecommendationEngine instance from Streamlit
        """
        # Extract components from engine
        music_df = music_engine.df
        model = music_engine.model
        label_encoder = music_engine.label_encoder

        # Initialize parent class
        super().__init__(music_df, model, label_encoder)


# Export for easy import in Streamlit
__all__ = ['MusicChatbot', 'create_chatbot']
