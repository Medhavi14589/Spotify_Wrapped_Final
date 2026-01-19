"""
Spotify Wrapped Analysis API - RATING-BASED RECOMMENDATIONS
User rates 10 random songs, gets personalized recommendations
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timezone
import io
import base64
from werkzeug.utils import secure_filename
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the recommender class
from ml.recommender import SpotifyMusicRecommender

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global variables
df = None  # User's uploaded playlist data
recommender = None  # Pre-trained recommender model

# Set plotting style
plt.style.use("default")
sns.set_context("notebook")

# ============================================================================
# LOAD PRE-TRAINED RECOMMENDER AT STARTUP
# ============================================================================

print("\n" + "="*70)
print("🎵 LOADING PRE-TRAINED RECOMMENDER MODEL...")
print("="*70)

try:
    # Load the pre-trained model from ml/ directory
    model_dir = os.path.join(os.path.dirname(__file__), '..', 'ml')
    recommender = SpotifyMusicRecommender.load_model(model_dir)
    print("✅ Recommender loaded successfully!")
    print(f"   Available tracks: {len(recommender.df)}")
except Exception as e:
    print(f"⚠️  WARNING: Could not load recommender model: {str(e)}")
    print("   Recommendation endpoints will not work.")
    print("   Please run 'python backend/train_recommender.py' first.")

print("="*70 + "\n")


# ============================================================================
# HELPER FUNCTIONS - NO HARDCODED VALUES
# ============================================================================

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_required_features(features, required_keys):
    """
    Validate that all required features are present
    
    Returns: (is_valid, missing_keys)
    """
    missing = [key for key in required_keys if key not in features or features[key] is None]
    return len(missing) == 0, missing


def predict_mood(song_features):
    """
    Predict mood based on song audio features - NO DEFAULTS
    
    Parameters:
    -----------
    song_features : dict
        Must contain: Danceability, Energy, Valence, Acousticness, Tempo
        All values must be present (no defaults)
    
    Returns:
    --------
    tuple: (mood_label, probabilities_dict) or (None, error_message)
    """
    # Required features - NO DEFAULTS ALLOWED
    required = ['Danceability', 'Energy', 'Valence', 'Acousticness', 'Tempo']
    is_valid, missing = validate_required_features(song_features, required)
    
    if not is_valid:
        return None, f"Missing required features: {', '.join(missing)}"
    
    # Extract features - NO DEFAULT VALUES
    try:
        danceability = float(song_features['Danceability'])
        energy = float(song_features['Energy'])
        valence = float(song_features['Valence'])
        acousticness = float(song_features['Acousticness'])
        tempo = float(song_features['Tempo'])
    except (ValueError, TypeError) as e:
        return None, f"Invalid feature values: {str(e)}"
    
    # Initialize mood scores
    mood_scores = {
        'Happy': 0,
        'Sad': 0,
        'Energetic': 0,
        'Chill': 0
    }
    
    # Calculate mood scores based on audio features
    mood_scores['Happy'] = (valence * 40) + (energy * 20) + (danceability * 20)
    mood_scores['Sad'] = ((1 - valence) * 40) + ((1 - energy) * 25) + (acousticness * 15)
    mood_scores['Energetic'] = (energy * 35) + (danceability * 20) + (min(tempo / 180, 1) * 25)
    mood_scores['Chill'] = (acousticness * 30) + ((1 - energy) * 25) + (abs(0.5 - valence) * 15)
    
    # Normalize to percentages
    total = sum(mood_scores.values())
    if total > 0:
        probabilities = {mood: round((score / total) * 100, 2) for mood, score in mood_scores.items()}
    else:
        return None, "Unable to calculate mood scores from provided features"
    
    # Determine dominant mood
    dominant_mood = max(probabilities, key=probabilities.get)
    
    return dominant_mood, probabilities


def calculate_listening_age(data):
    """Calculate listener age - uses actual data only"""
    if 'Release Year' not in data.columns:
        return None, "Release Year column not found in data"
    
    current_year = datetime.now().year
    data_copy = data.copy()
    data_copy["age"] = current_year - data_copy["Release Year"]
    
    # Remove invalid ages
    data_copy = data_copy[data_copy["age"] >= 0]
    
    if len(data_copy) == 0:
        return None, "No valid release years found"
    
    listener_age_estimate = int(data_copy["age"].mean().round())
    return listener_age_estimate, None


def calculate_playlist_age(data):
    """Calculate playlist age - uses actual data only"""
    if 'Added At' not in data.columns:
        return None, "Added At column not found in data"
    
    try:
        first_addn_time = data['Added At'].sort_values().iloc[0]
        current_time = datetime.now(timezone.utc)
        time_diff = (current_time - first_addn_time).total_seconds() / (365.25 * 24 * 60 * 60)
        return round(time_diff, 2), None
    except Exception as e:
        return None, f"Error calculating playlist age: {str(e)}"


def classify_popularity(popularity):
    """Classify song popularity - thresholds can be customized"""
    try:
        pop = float(popularity)
        if pop < 40:
            return 'Low'
        elif pop < 70:
            return 'Medium'
        else:
            return 'High'
    except (ValueError, TypeError):
        return None


# ============================================================================
# API ENDPOINTS - RATING-BASED RECOMMENDATIONS (PRE-TRAINED MODEL)
# ============================================================================

@app.route('/start-rating-session', methods=['GET'])
def start_rating_session():
    """Get 10 random songs for user to rate"""
    global recommender
    
    if recommender is None:
        return jsonify({'error': 'Recommender model not loaded'}), 500
    
    try:
        # Get 10 random songs
        random_songs = recommender.get_random_songs(n=10)
        
        # Format response
        songs_to_rate = []
        for idx, (df_idx, row) in enumerate(random_songs.iterrows()):
            song_info = {
                'id': idx,  # 0-9 for frontend display
                'df_index': int(df_idx),  # Actual dataframe index for backend
                'track_name': row.get('track_name') or row.get('name', 'Unknown'),
                'artists': row.get('artists') or row.get('artist_name(s)', 'Unknown'),
                'track_genre': row.get('track_genre') or row.get('genre', 'Unknown')
            }
            
            # Add optional fields if available
            if 'popularity' in row:
                song_info['popularity'] = int(row['popularity'])
            if 'year' in row:
                song_info['year'] = int(row['year'])
            
            songs_to_rate.append(song_info)
        
        return jsonify({
            'songs': songs_to_rate,
            'total': len(songs_to_rate),
            'message': 'Rate each song from 1-5 stars'
        })
    
    except Exception as e:
        return jsonify({'error': f'Failed to get random songs: {str(e)}'}), 500


@app.route('/submit-ratings-and-recommend', methods=['POST'])
def submit_ratings_and_recommend():
    """Accept user ratings and return personalized recommendations"""
    global recommender
    
    if recommender is None:
        return jsonify({'error': 'Recommender model not loaded'}), 500
    
    data = request.get_json()
    
    if not data or 'ratings' not in data:
        return jsonify({'error': 'ratings array is required in request body'}), 400
    
    ratings_data = data['ratings']
    top_k = data.get('top_k', 10)
    
    # Validate ratings format
    if not isinstance(ratings_data, list) or len(ratings_data) != 10:
        return jsonify({'error': 'ratings must be an array of 10 items'}), 400
    
    try:
        # Extract df_indices and ratings
        df_indices = []
        ratings = []
        
        for rating_item in ratings_data:
            if 'df_index' not in rating_item or 'rating' not in rating_item:
                return jsonify({'error': 'Each rating must have df_index and rating'}), 400
            
            df_indices.append(rating_item['df_index'])
            rating_value = rating_item['rating']
            
            # Validate rating value
            if not isinstance(rating_value, (int, float)) or rating_value < 1 or rating_value > 5:
                return jsonify({'error': 'Rating must be between 1 and 5'}), 400
            
            ratings.append(rating_value)
        
        # Get recommendations using the new method
        recommendations = recommender.recommend_from_ratings(
            rated_indices=df_indices,
            ratings=ratings,
            n_recommendations=top_k
        )
        
        if recommendations.empty:
            return jsonify({'error': 'Could not generate recommendations'}), 500
        
        # Format response
        result = []
        for _, row in recommendations.iterrows():
            rec_info = {
                'track_name': row.get('track_name') or row.get('name', 'Unknown'),
                'artists': row.get('artists') or row.get('artist_name(s)', 'Unknown'),
                'track_genre': row.get('track_genre') or row.get('genre', 'Unknown'),
                'similarity_score': round(float(row['similarity_score']), 4) if 'similarity_score' in row else None
            }
            
            # Add optional fields if available
            if 'popularity' in row:
                rec_info['popularity'] = int(row['popularity'])
            if 'year' in row:
                rec_info['year'] = int(row['year'])
            
            result.append(rec_info)
        
        return jsonify({
            'recommendations': result,
            'count': len(result),
            'based_on': 'Your ratings of 10 songs',
            'source': 'Weighted KNN model'
        })
    
    except Exception as e:
        return jsonify({'error': f'Recommendation failed: {str(e)}'}), 500


# ============================================================================
# API ENDPOINTS - USER DATA ANALYSIS (REQUIRES UPLOAD)
# ============================================================================

@app.route('/', methods=['GET'])
def home():
    """API home page"""
    return jsonify({
        'message': 'Spotify Wrapped Analysis API - Rating-Based Recommendations',
        'version': '4.0',
        'note': 'Upload your playlist for personalized analysis. Rate songs for recommendations.',
        'recommender_status': 'loaded' if recommender is not None else 'not loaded',
        'endpoints': {
            'RECOMMENDATIONS (Pre-trained - No upload needed)': {
                'GET /start-rating-session': 'Get 10 random songs to rate',
                'POST /submit-ratings-and-recommend': 'Submit ratings and get recommendations'
            },
            'USER ANALYSIS (Requires CSV upload)': {
                'POST /upload': 'Upload your Spotify CSV data',
                'GET /stats': 'Get YOUR statistics',
                'GET /top-artists': 'Get YOUR top artists',
                'GET /top-tracks': 'Get YOUR top tracks',
                'GET /mood-distribution': 'YOUR mood distribution',
                'GET /listening-age': 'YOUR listening age',
                'GET /playlist-age': 'YOUR playlist age',
                'GET /popularity-distribution': 'YOUR popularity distribution',
                'GET /explicit-analysis': 'YOUR explicit content analysis',
                'GET /temporal-analysis': 'YOUR listening trends'
            },
            'UTILITY': {
                'GET /health': 'Health check'
            }
        }
    })


@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload Spotify CSV data - processes YOUR actual data"""
    global df
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Read CSV file
            df = pd.read_csv(file)
            
            if len(df) == 0:
                return jsonify({'error': 'CSV file is empty'}), 400
            
            # Data preprocessing - using actual data
            if 'Added At' in df.columns:
                df['Added At'] = pd.to_datetime(df['Added At'], errors='coerce')
            
            if 'Release Date' in df.columns:
                df['Release Date'] = pd.to_datetime(df['Release Date'], errors='coerce')
                df['Release Year'] = df['Release Date'].dt.year
            
            # Add popularity classification using actual data
            if 'Popularity' in df.columns:
                df['Popularity Class'] = df['Popularity'].apply(classify_popularity)
            
            # Add mood prediction for each track using actual features
            required_mood_cols = ['Danceability', 'Energy', 'Valence', 'Acousticness', 'Tempo']
            if all(col in df.columns for col in required_mood_cols):
                moods = []
                for _, row in df.iterrows():
                    features = {
                        'Danceability': row['Danceability'],
                        'Energy': row['Energy'],
                        'Valence': row['Valence'],
                        'Acousticness': row['Acousticness'],
                        'Tempo': row['Tempo']
                    }
                    mood, error = predict_mood(features)
                    moods.append(mood if mood else 'Unknown')
                df['Mood'] = moods
            
            return jsonify({
                'message': 'File uploaded and processed successfully',
                'rows': len(df),
                'columns': list(df.columns),
                'preview': {
                    'first_track': df.iloc[0]['Track Name'] if 'Track Name' in df.columns else None,
                    'total_duration_ms': int(df['Duration (ms)'].sum()) if 'Duration (ms)' in df.columns else None,
                    'date_range': {
                        'earliest': str(df['Added At'].min()) if 'Added At' in df.columns else None,
                        'latest': str(df['Added At'].max()) if 'Added At' in df.columns else None
                    }
                }
            })
        
        except Exception as e:
            return jsonify({'error': f'Failed to process file: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file type. Only CSV files are allowed'}), 400


@app.route('/stats', methods=['GET'])
def get_stats():
    """Get statistics from YOUR uploaded data"""
    global df
    
    if df is None:
        return jsonify({'error': 'No data loaded. Upload a file first using POST /upload'}), 400
    
    stats = {
        'total_tracks': len(df),
        'data_source': 'Your uploaded CSV file'
    }
    
    # Add stats only if columns exist in YOUR data
    if 'Artist Name(s)' in df.columns:
        stats['unique_artists'] = int(df['Artist Name(s)'].nunique())
    
    if 'Duration (ms)' in df.columns:
        total_ms = df['Duration (ms)'].sum()
        stats['total_duration'] = {
            'milliseconds': int(total_ms),
            'hours': round(total_ms / (1000 * 60 * 60), 2),
            'days': round(total_ms / (1000 * 60 * 60 * 24), 2)
        }
    
    if 'Popularity' in df.columns:
        stats['popularity'] = {
            'average': round(float(df['Popularity'].mean()), 2),
            'median': round(float(df['Popularity'].median()), 2),
            'min': int(df['Popularity'].min()),
            'max': int(df['Popularity'].max())
        }
    
    if 'Explicit' in df.columns:
        explicit_count = int(df['Explicit'].sum())
        stats['explicit'] = {
            'count': explicit_count,
            'percentage': round((explicit_count / len(df)) * 100, 2)
        }
    
    if 'Added At' in df.columns:
        stats['timeline'] = {
            'earliest_add': str(df['Added At'].min()),
            'latest_add': str(df['Added At'].max())
        }
    
    if 'Release Year' in df.columns:
        stats['release_years'] = {
            'earliest': int(df['Release Year'].min()),
            'latest': int(df['Release Year'].max()),
            'average': round(float(df['Release Year'].mean()), 1)
        }
    
    return jsonify(stats)


@app.route('/top-artists', methods=['GET'])
def get_top_artists():
    """Get YOUR top artists from YOUR data"""
    global df
    
    if df is None:
        return jsonify({'error': 'No data loaded'}), 400
    
    n = request.args.get('n', default=10, type=int)
    
    if n <= 0:
        return jsonify({'error': 'Parameter n must be positive'}), 400
    
    if 'Artist Name(s)' not in df.columns:
        return jsonify({'error': 'Artist Name(s) column not found in your data'}), 400
    
    top_artists = df['Artist Name(s)'].value_counts().head(n)
    
    return jsonify({
        'top_artists': [
            {
                'rank': idx + 1,
                'artist': artist,
                'track_count': int(count),
                'percentage': round((count / len(df)) * 100, 2)
            }
            for idx, (artist, count) in enumerate(top_artists.items())
        ],
        'total_unique_artists': int(df['Artist Name(s)'].nunique())
    })


@app.route('/top-tracks', methods=['GET'])
def get_top_tracks():
    """Get YOUR top tracks from YOUR data"""
    global df
    
    if df is None:
        return jsonify({'error': 'No data loaded'}), 400
    
    n = request.args.get('n', default=10, type=int)
    
    if n <= 0:
        return jsonify({'error': 'Parameter n must be positive'}), 400
    
    if 'Track Name' not in df.columns:
        return jsonify({'error': 'Track Name column not found in your data'}), 400
    
    if 'Popularity' not in df.columns:
        return jsonify({'error': 'Popularity column not found in your data'}), 400
    
    # Get top tracks
    top_tracks = df.nlargest(n, 'Popularity')
    
    result = []
    for idx, row in enumerate(top_tracks.iterrows(), 1):
        track = row[1]
        track_info = {
            'rank': idx,
            'track_name': track['Track Name'],
            'popularity': int(track['Popularity'])
        }
        
        # Add optional fields if they exist
        if 'Artist Name(s)' in df.columns:
            track_info['artist'] = track['Artist Name(s)']
        if 'Release Year' in df.columns and pd.notna(track['Release Year']):
            track_info['release_year'] = int(track['Release Year'])
        if 'Album Name' in df.columns:
            track_info['album'] = track['Album Name']
        
        result.append(track_info)
    
    return jsonify({
        'top_tracks': result,
        'based_on': 'Popularity scores from your data'
    })


@app.route('/mood-distribution', methods=['GET'])
def mood_distribution():
    """Get YOUR mood distribution from YOUR data"""
    global df
    
    if df is None:
        return jsonify({'error': 'No data loaded. Upload a file first using POST /upload'}), 400
    
    if 'Mood' not in df.columns:
        return jsonify({
            'error': 'Mood data not available. Upload a file with audio features (Danceability, Energy, Valence, etc.)'
        }), 400
    
    mood_counts = df['Mood'].value_counts().to_dict()
    
    return jsonify({
        'mood_distribution': {
            mood: {
                'count': int(count),
                'percentage': round((count / len(df)) * 100, 2)
            }
            for mood, count in mood_counts.items()
        },
        'total_tracks': len(df),
        'note': 'Moods predicted from audio features in your data'
    })


@app.route('/listening-age', methods=['GET'])
def listening_age():
    """Calculate YOUR listening age from YOUR data"""
    global df
    
    if df is None:
        return jsonify({'error': 'No data loaded'}), 400
    
    age, error = calculate_listening_age(df)
    
    if error:
        return jsonify({'error': error}), 400
    
    current_year = datetime.now().year
    avg_release_year = int(df['Release Year'].mean())
    
    return jsonify({
        'listening_age': age,
        'average_release_year': avg_release_year,
        'current_year': current_year,
        'interpretation': f'Your music taste is approximately {age} years old',
        'note': 'Calculated from release years in your data'
    })


@app.route('/playlist-age', methods=['GET'])
def playlist_age():
    """Calculate YOUR playlist age from YOUR data"""
    global df
    
    if df is None:
        return jsonify({'error': 'No data loaded'}), 400
    
    age, error = calculate_playlist_age(df)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'playlist_age_years': age,
        'first_song_added': str(df['Added At'].min()),
        'latest_song_added': str(df['Added At'].max()),
        'interpretation': f'You started this playlist {age} years ago',
        'note': 'Calculated from timestamps in your data'
    })


@app.route('/popularity-distribution', methods=['GET'])
def popularity_distribution():
    """Get YOUR popularity distribution from YOUR data"""
    global df
    
    if df is None:
        return jsonify({'error': 'No data loaded'}), 400
    
    if 'Popularity Class' not in df.columns:
        if 'Popularity' not in df.columns:
            return jsonify({'error': 'Popularity data not found in your file'}), 400
        # Generate it on the fly
        df['Popularity Class'] = df['Popularity'].apply(classify_popularity)
    
    distribution = df['Popularity Class'].value_counts().to_dict()
    
    return jsonify({
        'distribution': {
            class_name: {
                'count': int(count),
                'percentage': round((count / len(df)) * 100, 2)
            }
            for class_name, count in distribution.items()
        },
        'total_tracks': len(df),
        'classification': {
            'Low': '0-39',
            'Medium': '40-69',
            'High': '70-100'
        }
    })


@app.route('/explicit-analysis', methods=['GET'])
def explicit_analysis():
    """Analyze YOUR explicit content from YOUR data"""
    global df
    
    if df is None:
        return jsonify({'error': 'No data loaded'}), 400
    
    if 'Explicit' not in df.columns:
        return jsonify({'error': 'Explicit column not found in your data'}), 400
    
    explicit_count = int(df['Explicit'].sum())
    clean_count = int((~df['Explicit']).sum())
    total = len(df)
    
    result = {
        'explicit_tracks': explicit_count,
        'clean_tracks': clean_count,
        'total_tracks': total,
        'explicit_percentage': round((explicit_count / total) * 100, 2),
        'clean_percentage': round((clean_count / total) * 100, 2)
    }
    
    # Add popularity comparison if available
    if 'Popularity' in df.columns:
        avg_pop_explicit = float(df[df['Explicit'] == True]['Popularity'].mean())
        avg_pop_clean = float(df[df['Explicit'] == False]['Popularity'].mean())
        
        result['popularity_comparison'] = {
            'explicit_avg': round(avg_pop_explicit, 2),
            'clean_avg': round(avg_pop_clean, 2),
            'difference': round(avg_pop_explicit - avg_pop_clean, 2)
        }
    
    return jsonify(result)


@app.route('/temporal-analysis', methods=['GET'])
def temporal_analysis():
    """Analyze YOUR listening trends from YOUR data"""
    global df
    
    if df is None:
        return jsonify({'error': 'No data loaded'}), 400
    
    if 'Added At' not in df.columns:
        return jsonify({'error': 'Added At column not found in your data'}), 400
    
    # Create a copy for temporal analysis
    df_temp = df.copy()
    df_temp['Added Month'] = df_temp['Added At'].dt.to_period('M')
    
    # Monthly counts
    monthly_counts = df_temp.groupby('Added Month').size()
    
    # Yearly counts
    df_temp['Added Year'] = df_temp['Added At'].dt.year
    yearly_counts = df_temp.groupby('Added Year').size()
    
    return jsonify({
        'monthly_trends': [
            {
                'month': str(month),
                'track_count': int(count)
            }
            for month, count in monthly_counts.items()
        ],
        'yearly_trends': [
            {
                'year': int(year),
                'track_count': int(count)
            }
            for year, count in yearly_counts.items()
        ],
        'total_tracks': len(df),
        'note': 'Based on "Added At" timestamps in your data'
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'user_data_loaded': df is not None,
        'user_data_rows': len(df) if df is not None else 0,
        'recommender_loaded': recommender is not None,
        'recommender_tracks': len(recommender.df) if recommender is not None else 0,
        'version': '4.0-rating-based'
    })


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print("🎵 Spotify Wrapped Analysis API v4.0")
    print("=" * 70)
    print("✅ Rating-based recommendations")
    print("✅ User upload for personalized analysis")
    print("=" * 70)
    print(f"Starting server on port {port}")
    print("=" * 70)
    app.run(debug=False, host='0.0.0.0', port=port)