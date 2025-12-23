# LLM Module Structure

Dokumentasi struktur modul LLM untuk Music dan Film chatbot.

## 📁 Folder Structure

```
streamlit_app/                       # 🎯 FOLDER INTI
├── data/
│   ├── music/
│   │   ├── dataset.csv              # Music dataset (114K+ songs)
│   │   ├── llm_music_module.py      # ✨ Music LLM module (ready)
│   │   ├── Llm_Rf_music.ipynb       # 📓 Original notebook (development)
│   │   ├── music_mood_model.pkl     # Trained ML model
│   │   └── label_encoder.pkl        # Label encoder
│   │
│   └── film/
│       ├── AllMovies_CLEANED.csv    # Film dataset (7.4K films)
│       ├── llm_film_module.py       # ✨ Film LLM module (ready)
│       └── Llm_Rf_film.ipynb        # 📓 Original notebook (development)
│
├── utils/
│   ├── chatbot_engine.py            # Music chatbot wrapper
│   ├── music_engine.py              # Music recommendation engine
│   └── film_engine.py               # Film recommendation engine
│
├── pages/
│   ├── 1_Music.py                   # Music page with chatbot
│   └── 2_Film.py                    # Film page (chatbot placeholder)
│
└── main.py                          # Landing page

NOTEBOOKS (inside streamlit_app):
data/music/Llm_Rf_music.ipynb        # Music chatbot development
data/film/Llm_Rf_film.ipynb          # Film chatbot development
```

## 🎵 Music LLM - Ready to Use

### File: `data/music/llm_music_module.py`

**Status:** ✅ **READY**

**Features:**
- Complete chatbot implementation
- Uses LangChain + LangGraph + Gemini AI
- Tools: `predict_mood()`, `recommend_music()`
- Strict dataset-only responses
- Bilingual support (ID/EN)

**Usage in Streamlit:**
```python
from utils.chatbot_engine import MusicChatbot

# Initialize with music engine
chatbot = MusicChatbot(music_engine)

# Chat
response = chatbot.chat("Saya sedang sedih")
```

**Development Reference:**
- Original notebook: `data/music/Llm_Rf_music.ipynb`
- For testing/development, use the notebook
- For production, module (`llm_music_module.py`) is exported from notebook logic

---

## 🎬 Film LLM - Ready to Use

### File: `data/film/llm_film_module.py`

**Status:** ✅ **READY**

**Features:**
- Complete chatbot implementation
- Uses LangChain + Gemini AI (same stack as Music)
- Tools: `search_movie()`, `recommend_movie()`, `search_free()`
- Content-based filtering (TF-IDF + Cosine Similarity)
- RAG retrieval for context
- Strict dataset-only responses
- Bilingual support (ID/EN)

**Usage in Streamlit:**
```python
from utils.film_chatbot_engine import FilmChatbot

# Initialize with film engine
chatbot = FilmChatbot(film_engine)

# Chat
response = chatbot.chat("Film thriller terbaik")
```

**Development Reference:**
- Original notebook: `data/film/Llm_Rf_film.ipynb`
- For testing/development, use the notebook
- For production, module (`llm_film_module.py`) is exported from notebook logic

---

## 🔄 Workflow

### Development Workflow:
1. **Develop in Jupyter Notebook** (`*.ipynb`)
   - Test chatbot logic
   - Experiment with prompts
   - Validate tools

2. **Export to Module** (`llm_*_module.py`)
   - Clean code from notebook
   - Add documentation
   - Structure as reusable module

3. **Import in Streamlit** (`utils/*_chatbot_engine.py`)
   - Thin wrapper layer
   - Bridge between module and Streamlit UI
   - Easy to maintain

### Maintenance:
- **Update notebook** → Test → **Export to module** → **Auto-reflected in Streamlit**
- Single source of truth: Notebook
- Production code: Module
- UI integration: Streamlit wrapper

---

## ⚙️ Configuration

### Environment Variables:
```env
# .env file in streamlit_app/
GOOGLE_API_KEY=your_gemini_api_key_here
```

### Dependencies:
```txt
langchain>=0.1.0
langchain-google-genai>=0.0.5
langgraph>=0.0.20
google-generativeai>=0.3.0
python-dotenv>=1.0.0
```

---

## 📝 Implementation Guide for Film Team

When film LLM data is ready:

### Step 1: Create Notebook
```bash
film/Llm_Rf_film.ipynb
```

### Step 2: Define Tools
```python
@tool
def recommend_film(genre: str, min_rating: float) -> Dict:
    # Filter films by genre & rating
    # Return top 5 films from dataset
    pass
```

### Step 3: System Prompt
```python
system_prompt = """
Kamu adalah Film Chatbot yang HANYA merekomendasikan dari dataset...
[Similar structure to music chatbot]
"""
```

### Step 4: Test in Notebook
- Test various queries
- Validate responses
- Tune prompts

### Step 5: Export to Module
- Copy tested code to `llm_film_module.py`
- Follow same structure as `llm_music_module.py`

### Step 6: Create Streamlit Wrapper
```python
# streamlit_app/utils/film_chatbot_engine.py
from film.llm_film_module import FilmLLMChatbot

class FilmChatbot(FilmLLMChatbot):
    def __init__(self, film_engine):
        super().__init__(film_engine.df)
```

### Step 7: Update Film Page
- Remove placeholder UI
- Enable real chatbot
- Test end-to-end

---

## 🎯 Benefits of This Structure

1. **Separation of Concerns**
   - Development (Notebook) ≠ Production (Module) ≠ UI (Streamlit)

2. **Easy Testing**
   - Test in notebook without running Streamlit
   - Quick iteration

3. **Reusability**
   - Modules can be used outside Streamlit
   - Easy to integrate in other projects

4. **Maintainability**
   - Clear structure
   - Single source of truth
   - Easy to update

5. **Team Collaboration**
   - Music team works on music/
   - Film team works on film/
   - No conflicts

---

## 📚 Reference

- Music Module: `data/music/llm_music_module.py`
- Film Module: `data/film/llm_film_module.py`
- Music Wrapper: `utils/chatbot_engine.py`
- Film Wrapper: `utils/film_chatbot_engine.py`
- Music Notebook: `data/music/Llm_Rf_music.ipynb`
- Film Notebook: `data/film/Llm_Rf_film.ipynb`

---

**Last Updated:** 2025-12-08
**Status:** Music ✅ Ready | Film ✅ Ready
