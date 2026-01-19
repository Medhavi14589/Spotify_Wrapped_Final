"""
Spotify Wrapped - Sequential Feature Display
Navigate through your personalized music analysis
"""

import base64
import streamlit as st
import sys
from pathlib import Path

from frontend.frontend_config import (
    SPOTIFY_CSS, 
    WRAPPED_CARD_CSS, 
    WRAPPED_CARD_CONFIG
)

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.api_client import APIClient
from utils.visualizations import Visualizer


def get_base64_image(image_path):
    """Convert local image to base64 for embedding"""
    try:
        with open(image_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode()
        return f"data:image/png;base64,{encoded}"
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return ""


# Page config
st.set_page_config(
    page_title="Your Wrapped",
    page_icon="🎵",
    layout="wide"
)

# Apply Spotify theme + Wrapped Card styling
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #191414 0%, #1a1a1a 100%);
    }
    h2, h3 { color: #1DB954 !important; }
    h1 {color: #FFD700 !important}
    p, li, label { color: #FFFFFF !important; }
    .stButton>button {
        background-color: #1DB954;
        color: white;
        border-radius: 30px;
        padding: 10px 30px;
        font-weight: bold;
    }
    .stButton>button:hover { background-color: #1ed760; }

    @import url('https://fonts.googleapis.com/css2?family=Dela+Gothic+One&display=swap');

    .wrapped-card {
        width: 450px;
        height: 800px;
        margin: 20px auto;
        border-radius: 20px;
        background-size: cover;
        background-position: center;
        display: flex;
        flex-direction: column;
        padding: 40px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.5);
        position: relative;
    }

    .wrapped-card::before {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(180deg, rgba(0,0,0,.4), rgba(0,0,0,.6));
        border-radius: 20px;
        z-index: 1;
    }

    .wrapped-card > * {
        position: relative;
        z-index: 2;
        text-align: center;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize helpers
api = APIClient()
viz = Visualizer()

# Feature definitions
FEATURES = [
    {'id': 'top_songs', 'title': 'Your Top Songs', 'description': 'The tracks that define your music taste'},
    {'id': 'top_artists', 'title': 'Your Top Artists', 'description': "The artists you can't stop listening to"},
    {'id': 'playlist_age', 'title': 'Playlist Age', 'description': "How long you've been curating"},
    {'id': 'listening_age', 'title': 'Listening Age', 'description': 'The era of your taste'},
    {'id': 'temporal', 'title': 'Songs Over Time', 'description': 'Your journey visualized'},
    {'id': 'audio_features', 'title': 'Audio Profile', 'description': 'Your sound characteristics'},
    {'id': 'mood_analysis', 'title': ' Mood Analysis', 'description': 'Your emotional landscape'},
    {'id': 'popularity', 'title': ' Popularity Style', 'description': 'Mainstream or underground?'},
    {'id': 'mood_radar', 'title': ' Mood Radar', 'description': 'Emotional profile at a glance'}
]


def render_feature(feature_idx):
    feature = FEATURES[feature_idx]
    feature_id = feature['id']

    backgrounds = {
        'top_songs': get_base64_image(r"sw4.png"),
        'top_artists': get_base64_image(r"sw4.png"),
        'playlist_age': get_base64_image(r"sw4.png"),
        'listening_age': get_base64_image(r"sw4.png"),
        'temporal': get_base64_image(r"sw4.png"),
        'audio_features': get_base64_image(r"sw4.png"),
        'mood_analysis': get_base64_image(r"sw4.png"),
        'popularity': get_base64_image(r"sw4.png"),
        'mood_radar': get_base64_image(r"sw4.png"),
    }

    bg = backgrounds.get(feature_id, "")

    # ---------- LISTENING AGE ----------
    if feature_id == "listening_age":
        data = api.get_listening_age()
        if data:
            age = data.get('listening_age', 0)
            avg_year = data.get('average_release_year', 'N/A')
            current_year = data.get('current_year', 'N/A')
            
            html = f'''<div class="wrapped-card" style="background-image:url('{bg}');justify-content:space-between;padding:50px 30px"><div style="text-align:center"><h1 style="font-family:'Dela Gothic One';font-size:28px;margin-bottom:15px">{feature['title']}</h1><p style="font-size:16px">{feature['description']}</p></div><div style="text-align:center;margin:50px 0"><h2 style="font-family:'Dela Gothic One';font-size:72px;color:#1DB954;margin:0;color:#1db954">{age}</h2><p style="font-family:'Dela Gothic One';font-size:24px;margin:20px 0">years</p><p style="font-size:16px">Average song age</p></div><div style="background:rgba(0,0,0,0.75);border-radius:15px;padding:25px"><h4 style="font-family:'Dela Gothic One';font-size:18px;margin-bottom:15px">DETAILS</h4><p style="font-size:15px;margin:8px 0"><strong>Avg Release Year:</strong> {avg_year}</p><p style="font-size:15px;margin:8px 0"><strong>Current Year:</strong> {current_year}</p></div></div>'''
            st.markdown(html, unsafe_allow_html=True)
            st.info(f"🎵 {data.get('interpretation', '')}")
        return

    # ---------- PLAYLIST AGE ----------
    elif feature_id == "playlist_age":
        data = api.get_playlist_age()
        if data:
            age = data.get('playlist_age_years', 0)
            first = data.get('first_song_added', 'N/A')
            latest = data.get('latest_song_added', 'N/A')
            
            html = f'''<div class="wrapped-card" style="background-image:url('{bg}');justify-content:space-between;padding:50px 30px"><div style="text-align:center"><h1 style="font-family:'Dela Gothic One';font-size:28px;margin-bottom:15px">{feature['title']}</h1><p style="font-size:16px">{feature['description']}</p></div><div style="text-align:center;margin:50px 0"><h2 style="font-family:'Dela Gothic One';font-size:72px;color:#1DB954;margin:0;color:#1db954">{age:.1f}</h2><p style="font-family:'Dela Gothic One';font-size:24px;margin:20px 0">years</p><p style="font-size:16px">Time since first song</p></div><div style="background:rgba(0,0,0,0.75);border-radius:15px;padding:25px"><h4 style="font-family:'Dela Gothic One';font-size:18px;margin-bottom:15px">TIMELINE</h4><p style="font-size:14px;margin:8px 0"><strong>First Song:</strong><br/>{first}</p><p style="font-size:14px;margin:8px 0"><strong>Latest Song:</strong><br/>{latest}</p></div></div>'''
            st.markdown(html, unsafe_allow_html=True)
            st.info(f"🎵 {data.get('interpretation', '')}")
        return

    # ---------- TOP SONGS ----------
    elif feature_id == "top_songs":
        data = api.get_top_tracks(n=10)
        if data:
            tracks = data.get('top_tracks', [])
            tracks_html = ""
            for t in tracks[:8]:
                artist = t.get('artist', t.get('artists', 'Unknown'))
                tracks_html += f'''<div style="background:rgba(0,0,0,0.6);border-radius:10px;padding:12px;margin:8px 0;display:flex;justify-content:space-between;align-items:center"><div style="text-align:left;flex:1"><p style="font-family:'Dela Gothic One';font-size:14px;margin:0">#{t['rank']} {t['track_name']}</p><p style="font-size:12px;color:rgba(255,255,255,0.7);margin:5px 0 0 0">by {artist}</p></div><div style="background:#1DB954;border-radius:8px;padding:8px 12px"><p style="font-family:'Dela Gothic One';font-size:16px;margin:0">{t['popularity']}</p></div></div>'''
            
            html = f'''<div class="wrapped-card" style="background-image:url('{bg}');justify-content:flex-start;padding:50px 30px;overflow:hidden"><div style="text-align:center;margin-bottom:20px"><h1 style="font-family:'Dela Gothic One';font-size:28px;margin-bottom:15px">{feature['title']}</h1><p style="font-size:16px">{feature['description']}</p></div><div style="overflow-y:auto;max-height:580px">{tracks_html}</div></div>'''
            st.markdown(html, unsafe_allow_html=True)
        return

    # ---------- TOP ARTISTS ----------
    elif feature_id == "top_artists":
        data = api.get_top_artists(n=10)
        if data:
            artists = data.get('top_artists', [])
            artists_html = ""
            for a in artists[:8]:
                artists_html += f'''<div style="background:rgba(0,0,0,0.6);border-radius:10px;padding:15px;margin:10px 0;display:flex;justify-content:space-between;align-items:center"><div style="text-align:left;flex:1"><p style="font-family:'Dela Gothic One';font-size:16px;margin:0">#{a['rank']} {a['artist']}</p><p style="font-size:13px;color:rgba(255,255,255,0.7);margin:5px 0 0 0">{a['percentage']}% of your library</p></div><div style="background:#1DB954;border-radius:8px;padding:10px 15px"><p style="font-family:'Dela Gothic One';font-size:18px;margin:0">{a['track_count']}</p><p style="font-size:10px;margin:2px 0 0 0">tracks</p></div></div>'''
            
            html = f'''<div class="wrapped-card" style="background-image:url('{bg}');justify-content:flex-start;padding:50px 30px;overflow:hidden"><div style="text-align:center;margin-bottom:20px"><h1 style="font-family:'Dela Gothic One';font-size:28px;margin-bottom:15px">{feature['title']}</h1><p style="font-size:16px">{feature['description']}</p></div><div style="overflow-y:auto;max-height:580px">{artists_html}</div></div>'''
            st.markdown(html, unsafe_allow_html=True)
            st.plotly_chart(viz.plot_top_artists(artists), use_container_width=True)
        return

    # ---------- TEMPORAL ----------
    elif feature_id == "temporal":
        data = api.get_temporal_analysis()
        if data:
            html = f'''<div class="wrapped-card" style="background-image:url('{bg}');justify-content:flex-start;padding-top:80px"><h1 style="font-family:'Dela Gothic One';font-size:28px">{feature['title']}</h1><p style="font-size:16px">{feature['description']}</p></div>'''
            st.markdown(html, unsafe_allow_html=True)
            st.plotly_chart(viz.plot_temporal_trends(data["yearly_trends"], data["monthly_trends"]), use_container_width=True)
            st.info(f"📊 Analyzed {data.get('total_tracks', 0)} tracks over time")
        return

    # ---------- AUDIO FEATURES ----------
    elif feature_id == "audio_features":
        data = api.get_stats()
        if data:
            avg_pop = data.get('popularity', {}).get('average', 0)
            total_dur = data.get('total_duration', {}).get('hours', 0)
            explicit = data.get('explicit', {}).get('percentage', 0)
            
            html = f'''<div class="wrapped-card" style="background-image:url('{bg}');justify-content:space-between;padding:50px 30px"><div style="text-align:center"><h1 style="font-family:'Dela Gothic One';font-size:28px;margin-bottom:15px">{feature['title']}</h1><p style="font-size:16px">{feature['description']}</p></div><div style="margin:40px 0"><h2 style="font-family:'Dela Gothic One';font-size:20px;margin-bottom:20px">Key Metrics</h2><div style="background:rgba(0,0,0,0.7);border-radius:15px;padding:20px;margin:15px 0"><p style="font-size:14px;color:rgba(255,255,255,0.8);margin:0">Avg Popularity</p><p style="font-family:'Dela Gothic One';font-size:32px;color:#1DB954;margin:5px 0 0 0">{avg_pop:.0f}</p></div><div style="background:rgba(0,0,0,0.7);border-radius:15px;padding:20px;margin:15px 0"><p style="font-size:14px;color:rgba(255,255,255,0.8);margin:0">Total Duration</p><p style="font-family:'Dela Gothic One';font-size:32px;color:#1DB954;margin:5px 0 0 0">{total_dur:.1f} hrs</p></div><div style="background:rgba(0,0,0,0.7);border-radius:15px;padding:20px;margin:15px 0"><p style="font-size:14px;color:rgba(255,255,255,0.8);margin:0">Explicit</p><p style="font-family:'Dela Gothic One';font-size:32px;color:#1DB954;margin:5px 0 0 0">{explicit}%</p></div></div></div>'''
            st.markdown(html, unsafe_allow_html=True)
            st.plotly_chart(viz.plot_audio_features_radar(data), use_container_width=True)
        return

    # ---------- MOOD ANALYSIS ----------
    elif feature_id == "mood_analysis":
        data = api.get_mood_distribution()
        if data:
            mood_dist = data.get('mood_distribution', {})
            moods = ['Happy', 'Sad', 'Energetic', 'Chill']
            emojis = ['😊', '😢', '⚡', '😌']
            
            mood_html = ""
            for i, m in enumerate(moods):
                if m in mood_dist:
                    pct = mood_dist[m].get('percentage', 0)
                    mood_html += f'''<div style="background:rgba(0,0,0,0.7);border-radius:15px;padding:15px;margin:10px 0"><p style="font-family:'Dela Gothic One';font-size:16px;margin:0">{emojis[i]} {m}</p><p style="font-size:24px;color:#1DB954;margin:5px 0 0 0">{pct:.1f}%</p></div>'''
            
            html = f'''<div class="wrapped-card" style="background-image:url('{bg}');justify-content:flex-start;padding:50px 30px;overflow:hidden"><div style="text-align:center;margin-bottom:20px"><h1 style="font-family:'Dela Gothic One';font-size:28px;margin-bottom:15px">{feature['title']}</h1><p style="font-size:16px">{feature['description']}</p></div><h3 style="font-family:'Dela Gothic One';font-size:18px;margin:20px 0">Mood Breakdown</h3><div style="overflow-y:auto;max-height:500px">{mood_html}</div></div>'''
            st.markdown(html, unsafe_allow_html=True)
            st.plotly_chart(viz.plot_mood_distribution(mood_dist), use_container_width=True)
        return

    # ---------- POPULARITY ----------
    elif feature_id == "popularity":
        data = api.get_popularity_distribution()
        if data:
            dist = data.get('distribution', {})
            high = dist.get('High', {}).get('count', 0)
            med = dist.get('Medium', {}).get('count', 0)
            low = dist.get('Low', {}).get('count', 0)
            
            if high > med and high > low:
                style, emoji, desc = "Mainstream Listener", "🌟", "You love popular hits!"
            elif low > high:
                style, emoji, desc = "Underground Explorer", "🎧", "You discover hidden gems!"
            else:
                style, emoji, desc = "Balanced Listener", "🎵", "Mix of popular and underground!"
            
            html = f'''<div class="wrapped-card" style="background-image:url('{bg}');justify-content:center;padding:50px 30px"><div style="text-align:center"><h1 style="font-family:'Dela Gothic One';font-size:28px;margin-bottom:15px">{feature['title']}</h1><p style="font-size:16px;margin-bottom:60px">{feature['description']}</p><div style="background:rgba(0,0,0,0.75);border-radius:20px;padding:40px"><p style="font-size:48px;margin:0">{emoji}</p><h2 style="font-family:'Dela Gothic One';font-size:24px;color:#1DB954;margin:20px 0">{style}</h2><p style="font-size:18px;margin:10px 0 0 0">{desc}</p></div></div></div>'''
            st.markdown(html, unsafe_allow_html=True)
            st.plotly_chart(viz.plot_popularity_distribution(dist), use_container_width=True)
        return

    # ---------- MOOD RADAR ----------
    elif feature_id == "mood_radar":
        data = api.get_mood_distribution()
        if data:
            mood_dist = data.get('mood_distribution', {})
            if mood_dist:
                dominant = max(mood_dist.items(), key=lambda x: x[1].get('percentage', 0))
                
                html = f'''<div class="wrapped-card" style="background-image:url('{bg}');justify-content:center;padding:50px 30px"><div style="text-align:center"><h1 style="font-family:'Dela Gothic One';font-size:28px;margin-bottom:15px">{feature['title']}</h1><p style="font-size:16px;margin-bottom:80px">{feature['description']}</p><div style="background:rgba(0,0,0,0.75);border-radius:20px;padding:40px"><p style="font-size:16px;color:rgba(255,255,255,0.8);margin:0">Your dominant mood is</p><h2 style="font-family:'Dela Gothic One';font-size:48px;color:#1DB954;margin:20px 0">{dominant[0]}</h2><p style="font-family:'Dela Gothic One';font-size:32px;margin:10px 0 0 0">{dominant[1]["percentage"]:.1f}%</p></div></div></div>'''
                st.markdown(html, unsafe_allow_html=True)
                st.plotly_chart(viz.plot_mood_radar(mood_dist), use_container_width=True)
        return


# ------------------ MAIN ------------------

# Check if data uploaded
if not st.session_state.get('data_uploaded', False):
    st.warning("⚠️ Please upload your playlist data first!")
    st.info("👈 Go back to Home and upload your CSV file")
    st.stop()

# Initialize navigation
if "feature_index" not in st.session_state:
    st.session_state.feature_index = 0

st.progress((st.session_state.feature_index + 1) / len(FEATURES))
st.caption(f"Feature {st.session_state.feature_index + 1} of {len(FEATURES)}")

render_feature(st.session_state.feature_index)

st.markdown("---")

col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.session_state.feature_index > 0:
        if st.button("⬅️ Previous"):
            st.session_state.feature_index -= 1
            st.rerun()

with col3:
    if st.session_state.feature_index < len(FEATURES) - 1:
        if st.button("Next ➡️"):
            st.session_state.feature_index += 1
            st.rerun()
    else:
        st.success("🎉 You've completed your Wrapped!")
        if st.button("🔄 Start Over"):
            st.session_state.feature_index = 0
            st.rerun()