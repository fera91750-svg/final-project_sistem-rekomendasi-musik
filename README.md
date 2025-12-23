# 🎬🎵 MELORA - Music & Film Recommendation System

**MELORA** (Music & Film Recommendation) - Streamlit web application untuk rekomendasi musik dan film menggunakan AI/ML dan LLM chatbot.

## 📁 Project Structure

```
streamlit_app/
│
├── main.py                          # Landing page
│
├── pages/
│   ├── 1_Music.py                   # Music recommendation + chatbot
│   └── 2_Film.py                    # Film recommendation + chatbot
│
├── utils/
│   ├── music_engine.py              # Music recommendation engine
│   ├── film_engine.py               # Film recommendation engine
│   ├── chatbot_engine.py            # Music chatbot wrapper
│   ├── film_chatbot_engine.py       # Film chatbot wrapper
│   └── visualizations.py            # Plotly charts
│
├── data/
│   ├── music/
│   │   ├── dataset.csv              # 114K songs dataset
│   │   ├── llm_music_module.py      # Music LLM chatbot
│   │   ├── Llm_Rf_music.ipynb       # Development notebook
│   │   ├── music_mood_model.pkl     # Random Forest model
│   │   └── label_encoder.pkl        # Mood label encoder
│   │
│   └── film/
│       ├── AllMovies_CLEANED.csv    # 7.4K films dataset
│       ├── llm_film_module.py       # Film LLM chatbot
│       └── Llm_Rf_film.ipynb        # Development notebook
│
├── assets/
│   ├── design_mockup.jpeg           # UI/UX design reference
│   └── prediksi mood manual.jpeg    # Mood prediction mockup
│
├── .env.example                     # Environment variables template
├── requirements.txt
├── README.md
└── LLM_MODULE_STRUCTURE.md          # LLM architecture guide
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google API Key (for chatbot features)

### Installation

```bash
# 1. Clone repository (branch monica)
git clone -b monica https://github.com/Bayuarii/Final-Project-DSAI.git
cd Final-Project-DSAI

# 2. Create virtual environment (recommended)
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

### Configuration

1. **Copy `.env.example` to `.env`**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file** and add your Google API Key:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

3. **Get your API key** from [Google AI Studio](https://aistudio.google.com/app/apikey)

### Run Application

```bash
# Run the Streamlit
streamlit run main.py

```

The app will open at `http://localhost:8501`

**Note:**
- Chatbot features require a valid Google API key
- Music and Film recommendation features work without API key
- Do NOT commit your `.env` file to Git (already in `.gitignore`)

## ✨ Features

### 🎵 Music Recommendation
- **Mood-based recommendation** (Happy, Sad, Calm, Tense)
  - ML-powered mood classification using Random Forest
  - 114 genres available
- **Manual Mood Prediction**
  - Adjust audio features (danceability, energy, valence, etc.)
  - Real-time mood prediction
- **AI Chat Assistant** 🤖
  - Powered by Google Gemini 2.5 Flash
  - Natural language music queries
  - Strict dataset-only responses
- **Spotify Integration**
  - Embedded Spotify player for direct playback
  - 114K+ songs with preview
- **Interactive Analytics**
  - Mood distribution charts
  - Valence vs Energy scatter plot
  - Audio features radar chart
  - Genre distribution analysis

### 🎬 Film Recommendation
- **Smart Search**
  - Search by title with fuzzy matching
  - Filter by rating (0-10)
  - Filter by release year
  - Multi-genre selection
- **Content-Based Filtering**
  - Similar film recommendations using TF-IDF
  - Cosine similarity scoring
- **AI Chat Assistant** 🤖
  - Powered by Google Gemini 2.5 Flash
  - Natural language film queries
  - RAG-enhanced context retrieval
  - Search by actor, director, genre, year
- **Platform Recommendations**
  - Netflix, Disney+, Prime Video, HBO Max, etc.
  - Color-coded platform badges
- **Rich Analytics**
  - Rating distribution
  - Genre analysis
  - Films per year timeline
  - Top rated films

## 📊 Data Sources

- **Music Dataset**: 114,000+ songs from Spotify
  - Audio features: valence, energy, danceability, tempo, etc.
  - Metadata: title, artist, album, genre, popularity

- **Film Dataset**: 7,432 movies
  - Metadata: title, description, rating, votes
  - Cast: actors, directors
  - Details: genre, year, duration

## 🤖 AI Chatbot Features

### Music Chatbot
- **Model**: Google Gemini 2.5 Flash
- **Framework**: LangChain + LangGraph
- **Tools**:
  - `predict_mood()`: ML-based mood prediction
  - `recommend_music()`: Dataset-based recommendations
- **Features**:
  - Automatic mood detection from text
  - Bilingual support (Indonesian/English)
  - Conversation context (LangGraph memory)
  - Strict dataset-only responses

### Film Chatbot
- **Model**: Google Gemini 2.5 Flash
- **Framework**: LangChain Agent
- **Tools**:
  - `search_movie()`: Search film by title
  - `recommend_movie()`: Content-based similar films
  - `search_free()`: Advanced filtering (genre, year, rating, actor)
- **Features**:
  - RAG retrieval for context-aware responses
  - Fuzzy title matching
  - Multi-criteria search
  - Strict dataset-only responses

## 🔧 Technologies

### Frontend & UI
- **Streamlit** - Web framework
- **Custom CSS** - Professional color scheme (Indigo/Violet/Pink gradients)
- **Plotly** - Interactive visualizations

### Data Processing & ML
- **Pandas & NumPy** - Data manipulation
- **Scikit-learn** - ML models & TF-IDF vectorization
  - Random Forest for mood classification
  - TF-IDF + Cosine Similarity for film recommendations

### AI & LLM
- **LangChain** - LLM orchestration framework
- **LangGraph** - Agent workflow (Music chatbot)
- **Google Gemini AI** - gemini-2.5-flash model
- **Python dotenv** - Environment management

## 🎨 Design

**Color Scheme:**
- Background: Slate gradient (#0F172A → #1E293B)
- Primary: Indigo (#6366F1)
- Secondary: Violet (#8B5CF6)
- Accent: Pink (#EC4899)
- Text: Slate (#F1F5F9)

**UI Features:**
- Modern gradient backgrounds
- Chat bubbles with animations
- Platform-specific color badges
- Responsive layout
- Dark mode optimized

## 📝 Documentation

- **`README.md`** - This file (quick start guide)
- **`LLM_MODULE_STRUCTURE.md`** - Detailed LLM architecture and development guide
- **Notebooks**:
  - `data/music/Llm_Rf_music.ipynb` - Music chatbot development
  - `data/film/Llm_Rf_film.ipynb` - Film chatbot development

## 🔐 Environment Variables

The project uses environment variables for API keys. Follow these steps:

1. **Copy the template**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env`** and add your API key:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

3. **Get API key** from [Google AI Studio](https://aistudio.google.com/app/apikey)

**Security Notes:**
- ✅ `.env.example` is committed to Git (template only)
- ❌ `.env` is in `.gitignore` (never commit this!)
- 🔒 Keep your API keys private

## 🚧 Development

### Testing Chatbots
```bash
# Open notebooks for development
jupyter notebook data/music/Llm_Rf_music.ipynb
jupyter notebook data/film/Llm_Rf_film.ipynb
```

### Module Structure
- **Development**: Edit `.ipynb` notebooks
- **Production**: Export to `llm_*_module.py`
- **Integration**: Use wrappers in `utils/`

See `LLM_MODULE_STRUCTURE.md` for detailed workflow.

## 👥 Team

**Final Project Kelompok 4**

## 📄 License

Educational Project - Built with ❤️ using Streamlit & ML
