"""
Visualization Functions
Creates interactive charts using Plotly and Matplotlib
"""

import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


# Color scheme
COLORS = {
    'primary': '#00FF9F',
    'secondary': '#00D9FF',
    'background': '#000000',
    'text': '#FFFFFF',
    'happy': '#FFD700',
    'sad': '#4B0082',
    'calm': '#008080',
    'tense': '#B22222'
}


def create_mood_pie_chart(mood_distribution):
    """
    Create mood distribution pie chart

    Args:
        mood_distribution (dict): Mood counts

    Returns:
        plotly.graph_objects.Figure
    """
    mood_colors = {
        'Happy': COLORS['happy'],
        'Sad': COLORS['sad'],
        'Calm': COLORS['calm'],
        'Tense': COLORS['tense']
    }

    labels = list(mood_distribution.keys())
    values = list(mood_distribution.values())
    colors = [mood_colors.get(mood, COLORS['primary']) for mood in labels]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors),
        hole=0.4,
        textinfo='label+percent',
        textfont=dict(size=14, color='white'),
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])

    fig.update_layout(
        title={
            'text': '🎭 Mood Distribution',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': COLORS['primary']}
        },
        paper_bgcolor=COLORS['background'],
        plot_bgcolor=COLORS['background'],
        font=dict(color=COLORS['text']),
        showlegend=True,
        height=400
    )

    return fig


def create_valence_energy_scatter(df):
    """
    Create scatter plot of valence vs energy (mood quadrants)

    Args:
        df (DataFrame): Music dataframe with valence, energy, mood columns

    Returns:
        plotly.graph_objects.Figure
    """
    mood_colors = {
        'Happy': COLORS['happy'],
        'Sad': COLORS['sad'],
        'Calm': COLORS['calm'],
        'Tense': COLORS['tense']
    }

    # Sample data if too large
    if len(df) > 5000:
        df_sample = df.sample(5000, random_state=42)
    else:
        df_sample = df

    fig = px.scatter(
        df_sample,
        x='valence',
        y='energy',
        color='mood',
        color_discrete_map=mood_colors,
        opacity=0.6,
        hover_data=['track_name', 'artists', 'mood'],
        title='🎯 Mood Map: Valence vs Energy'
    )

    # Add quadrant lines
    fig.add_hline(y=0.5, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=0.5, line_dash="dash", line_color="gray", opacity=0.5)

    # Add quadrant labels
    fig.add_annotation(x=0.75, y=0.75, text="Happy", showarrow=False,
                      font=dict(size=16, color=COLORS['happy']))
    fig.add_annotation(x=0.25, y=0.25, text="Sad", showarrow=False,
                      font=dict(size=16, color=COLORS['sad']))
    fig.add_annotation(x=0.75, y=0.25, text="Calm", showarrow=False,
                      font=dict(size=16, color=COLORS['calm']))
    fig.add_annotation(x=0.25, y=0.75, text="Tense", showarrow=False,
                      font=dict(size=16, color=COLORS['tense']))

    fig.update_layout(
        paper_bgcolor=COLORS['background'],
        plot_bgcolor='#1a1a1a',
        font=dict(color=COLORS['text']),
        xaxis_title="Valence (Positivity)",
        yaxis_title="Energy",
        height=500,
        title={'x': 0.5, 'xanchor': 'center'}
    )

    return fig


def create_genre_bar_chart(genre_distribution, top_n=15):
    """
    Create bar chart for genre distribution

    Args:
        genre_distribution (dict): Genre counts
        top_n (int): Number of top genres to show

    Returns:
        plotly.graph_objects.Figure
    """
    # Get top N genres
    sorted_genres = sorted(genre_distribution.items(), key=lambda x: x[1], reverse=True)[:top_n]
    genres = [item[0] for item in sorted_genres]
    counts = [item[1] for item in sorted_genres]

    fig = go.Figure(data=[
        go.Bar(
            x=counts,
            y=genres,
            orientation='h',
            marker=dict(
                color=counts,
                colorscale=[[0, COLORS['secondary']], [1, COLORS['primary']]],
                showscale=False
            ),
            text=counts,
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>Count: %{x}<extra></extra>'
        )
    ])

    fig.update_layout(
        title={
            'text': f'🎸 Top {top_n} Genres',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': COLORS['primary']}
        },
        paper_bgcolor=COLORS['background'],
        plot_bgcolor='#1a1a1a',
        font=dict(color=COLORS['text']),
        xaxis_title="Number of Songs",
        yaxis_title="Genre",
        height=500,
        yaxis={'categoryorder': 'total ascending'}
    )

    return fig


def create_rating_histogram(df):
    """
    Create histogram for film ratings

    Args:
        df (DataFrame): Film dataframe with rating column

    Returns:
        plotly.graph_objects.Figure
    """
    fig = px.histogram(
        df,
        x='rating',
        nbins=30,
        title='⭐ Rating Distribution',
        labels={'rating': 'Rating', 'count': 'Number of Films'},
        color_discrete_sequence=[COLORS['primary']]
    )

    fig.update_layout(
        paper_bgcolor=COLORS['background'],
        plot_bgcolor='#1a1a1a',
        font=dict(color=COLORS['text']),
        height=400,
        title={'x': 0.5, 'xanchor': 'center'},
        xaxis_title="Rating (0-10)",
        yaxis_title="Number of Films",
        bargap=0.1
    )

    return fig


def create_year_line_chart(df):
    """
    Create line chart for films per year

    Args:
        df (DataFrame): Film dataframe with release_year column

    Returns:
        plotly.graph_objects.Figure
    """
    year_counts = df['release_year'].value_counts().sort_index()

    fig = go.Figure(data=[
        go.Scatter(
            x=year_counts.index,
            y=year_counts.values,
            mode='lines+markers',
            line=dict(color=COLORS['primary'], width=2),
            marker=dict(size=6),
            fill='tozeroy',
            fillcolor=f'rgba(0, 255, 159, 0.1)',
            hovertemplate='Year: %{x}<br>Films: %{y}<extra></extra>'
        )
    ])

    fig.update_layout(
        title={
            'text': '📅 Films Released Per Year',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': COLORS['primary']}
        },
        paper_bgcolor=COLORS['background'],
        plot_bgcolor='#1a1a1a',
        font=dict(color=COLORS['text']),
        xaxis_title="Year",
        yaxis_title="Number of Films",
        height=400
    )

    return fig


def create_audio_features_radar(mood_stats):
    """
    Create radar chart for audio features by mood

    Args:
        mood_stats (DataFrame): Mood statistics

    Returns:
        plotly.graph_objects.Figure
    """
    categories = ['Valence', 'Energy', 'Danceability', 'Acousticness']

    mood_colors_map = {
        'Happy': COLORS['happy'],
        'Sad': COLORS['sad'],
        'Calm': COLORS['calm'],
        'Tense': COLORS['tense']
    }

    fig = go.Figure()

    for mood in mood_stats.index:
        values = [
            mood_stats.loc[mood, 'valence'],
            mood_stats.loc[mood, 'energy'],
            mood_stats.loc[mood, 'danceability'],
            mood_stats.loc[mood, 'acousticness']
        ]

        # Close the radar chart
        values += values[:1]

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill='toself',
            name=mood,
            line=dict(color=mood_colors_map.get(mood, COLORS['primary']))
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                gridcolor='#333',
                color=COLORS['text']
            ),
            angularaxis=dict(
                gridcolor='#333',
                color=COLORS['text']
            ),
            bgcolor='#1a1a1a'
        ),
        paper_bgcolor=COLORS['background'],
        font=dict(color=COLORS['text']),
        title={
            'text': '🎵 Audio Features by Mood',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': COLORS['primary']}
        },
        height=500,
        showlegend=True
    )

    return fig


def create_genre_film_bar(genre_dist, top_n=15):
    """
    Create bar chart for film genre distribution

    Args:
        genre_dist (dict): Genre distribution
        top_n (int): Number of top genres

    Returns:
        plotly.graph_objects.Figure
    """
    sorted_genres = sorted(genre_dist.items(), key=lambda x: x[1], reverse=True)[:top_n]
    genres = [item[0] for item in sorted_genres]
    counts = [item[1] for item in sorted_genres]

    fig = go.Figure(data=[
        go.Bar(
            x=genres,
            y=counts,
            marker=dict(
                color=counts,
                colorscale=[[0, COLORS['secondary']], [1, COLORS['primary']]],
                showscale=False
            ),
            text=counts,
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
        )
    ])

    fig.update_layout(
        title={
            'text': f'🎭 Top {top_n} Film Genres',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': COLORS['primary']}
        },
        paper_bgcolor=COLORS['background'],
        plot_bgcolor='#1a1a1a',
        font=dict(color=COLORS['text']),
        xaxis_title="Genre",
        yaxis_title="Number of Films",
        height=500,
        xaxis={'tickangle': -45}
    )

    return fig
