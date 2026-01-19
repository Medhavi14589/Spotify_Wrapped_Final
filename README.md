# 🎵 Spotify Wrapped - Personalized Music Analytics & Recommendations

A full-stack web application that provides personalized Spotify music analytics and AI-powered song recommendations based on user ratings.

## 🌟 Features

### 📊 Personal Analytics (Upload Your Playlist)
- **Mood Analysis**: Analyze the emotional profile of your music (Happy, Sad, Energetic, Chill)
- **Top Artists & Tracks**: See your most played artists and popular tracks
- **Listening Age**: Discover the average age of your music collection
- **Playlist Age**: Track how long you've been building your playlist
- **Temporal Trends**: Visualize your listening habits over time
- **Popularity Distribution**: Understand if you prefer mainstream or underground music
- **Audio Features Analysis**: Deep dive into danceability, energy, valence, and more

### 🎯 AI-Powered Recommendations (No Upload Needed)
- **Rating-Based System**: Rate 10 random songs (1-5 stars)
- **Personalized Suggestions**: Get 10 custom recommendations based on your ratings
- **Weighted KNN Algorithm**: Uses audio features to find similar songs
- **Interactive UI**: One song at a time with star rating interface

## 🏗️ Project Structure

```
Spotify_Wrapped/
├── backend/                          # Flask API Backend
│   ├── spotify_api_dynamic.py        # Main API endpoints
│   ├── train_model.py                # Mood classification model training
│   └── train_recommender.py          # Recommendation system training
│
├── data/                             # Datasets
│   ├── data.csv                      # Training data for mood model
│   ├── dataset.csv                   # Raw Spotify dataset
│   ├── spotify_features_normalized.csv
│   ├── spotify_tracks_final.csv
│   └── user_interactions.csv
│
├── frontend/                         # Streamlit Frontend
│   ├── streamlit_app.py              # Main homepage
│   ├── frontend_config.py            # UI configuration & styling
│   │
│   ├── pages/                        # Multi-page app
│   │   ├── recommendations_page.py   # Rating & recommendations UI
│   │   └── wrapped_page.py           # Personal analytics dashboard
│   │
│   └── utils/                        # Utility modules
│       ├── api_client.py             # API communication
│       ├── visualizations.py         # Plotly charts
│       ├── session_manager.py        # Session state management
│       ├── data_validator.py         # CSV validation
│       └── format_helpers.py         # Data formatting utilities
│
├── ml/                               # Machine Learning Models
│   ├── recommender.py                # Recommendation engine
│   ├── mood_model.py                 # Mood prediction logic
│   ├── preprocessing.py              # Data preprocessing
│   ├── recommender_knn.pkl           # Pre-trained KNN model
│   ├── recommender_scaler.pkl        # Feature scaler
│   └── recommender_data.pkl          # Processed dataset
│
├── notebooks/                        # Jupyter notebooks (for analysis)
├── requirements.txt                  # Python dependencies
└── README.md                         # This file
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Git
- Virtual environment (recommended)

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd Spotify_Wrapped
```

### 2. Create Virtual Environment
**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Train the Recommendation Model (First Time Only)
```bash
python backend/train_recommender.py
```

This will generate:
- `ml/recommender_knn.pkl`
- `ml/recommender_scaler.pkl`
- `ml/recommender_data.pkl`

## 🎮 Running the Application

### Step 1: Start the Flask Backend
```bash
python backend/spotify_api_dynamic.py
```

The API will run on `http://localhost:5000`

### Step 2: Start the Streamlit Frontend (New Terminal)
```bash
streamlit run frontend/streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## 📖 How to Use

### Option 1: Get Recommendations (No Upload)
1. Navigate to the **Recommendations** page
2. Rate 10 random songs using the star rating system (1-5 stars)
3. Click "Get My Recommendations"
4. Discover 10 personalized song suggestions!

### Option 2: Analyze Your Playlist
1. Export your Spotify playlist as CSV (use [Exportify](https://exportify.net/))
2. Upload the CSV on the **Home** page
3. Navigate to **Your Wrapped** page
4. Explore your personalized analytics:
   - Top Songs & Artists
   - Mood Distribution
   - Listening Age
   - Temporal Trends
   - Audio Feature Profiles

## 🛠️ Technology Stack

### Backend
- **Flask** - RESTful API framework
- **Flask-CORS** - Cross-origin resource sharing
- **Pandas** - Data manipulation
- **NumPy** - Numerical computations
- **scikit-learn** - Machine learning (KNN, StandardScaler, Logistic Regression)
- **Matplotlib & Seaborn** - Data visualization

### Frontend
- **Streamlit** - Web app framework
- **Plotly** - Interactive visualizations
- **Requests** - API communication

### Machine Learning
- **K-Nearest Neighbors (KNN)** - Recommendation algorithm
- **Logistic Regression** - Mood classification
- **StandardScaler** - Feature normalization

## 📊 API Endpoints

### Recommendations (No Upload)
- `GET /start-rating-session` - Get 10 random songs to rate
- `POST /submit-ratings-and-recommend` - Submit ratings and get recommendations

### Personal Analytics (Requires Upload)
- `POST /upload` - Upload Spotify CSV
- `GET /stats` - Overall statistics
- `GET /top-artists` - Top artists by track count
- `GET /top-tracks` - Top tracks by popularity
- `GET /mood-distribution` - Mood analysis
- `GET /listening-age` - Average song age
- `GET /playlist-age` - Playlist creation timeline
- `GET /popularity-distribution` - Popularity classification
- `GET /temporal-analysis` - Listening trends over time

### Utility
- `GET /health` - Health check

## 🧪 Model Training

### Mood Classification Model
```bash
python backend/train_model.py
```
Trains a Logistic Regression model to classify songs into moods based on audio features.

### Recommendation Model
```bash
python backend/train_recommender.py
```
Trains a KNN model on audio features for similarity-based recommendations.

## 🎨 Customization

### Change Spotify Theme Colors
Edit `frontend/frontend_config.py`:
```python
COLORS = {
    'primary': '#1DB954',      # Spotify green
    'secondary': '#1ed760',
    'background': '#191414',
    # ... customize more
}
```

### Modify Recommendation Count
In API calls, adjust the `top_k` parameter:
```python
api.submit_ratings_and_recommend(ratings, top_k=20)  # Get 20 recommendations
```

## 🐛 Troubleshooting

### Issue: "Cannot connect to API"
**Solution:** Make sure Flask backend is running on port 5000
```bash
python backend/spotify_api_dynamic.py
```

### Issue: "Recommender model not loaded"
**Solution:** Train the model first
```bash
python backend/train_recommender.py
```

### Issue: "ModuleNotFoundError: No module named 'frontend'"
**Solution:** Run Streamlit from project root
```bash
cd Spotify_Wrapped
streamlit run frontend/streamlit_app.py
```

### Issue: Import errors in streamlit_app.py
**Solution:** Update imports in `frontend/streamlit_app.py`:
```python
try:
    from frontend.frontend_config import API_BASE_URL, APP_TITLE, APP_ICON, PAGE_LAYOUT
except ModuleNotFoundError:
    from frontend_config import API_BASE_URL, APP_TITLE, APP_ICON, PAGE_LAYOUT
```

## 📝 Requirements

See `requirements.txt` for full list. Key dependencies:
- flask
- pandas
- numpy
- scikit-learn
- streamlit
- plotly

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is for educational purposes.

## 📧 Contact

For questions or feedback, please open an issue in the repository.

---

**Made with ❤️ for music lovers** 🎵
