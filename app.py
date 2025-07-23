from flask import Flask, request, redirect, session, render_template_string, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
import secrets

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # For session management

# Spotify OAuth setup
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://127.0.0.1:5000/callback')

SCOPE = 'user-read-private user-read-email user-read-playback-state user-modify-playback-state user-read-currently-playing playlist-read-private playlist-modify-public user-library-read'

def get_spotify_oauth():
    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE
    )

def get_spotify_client():
    token_info = session.get('token_info')
    if not token_info:
        return None
    
    try:
        sp_oauth = get_spotify_oauth()
        if sp_oauth.is_token_expired(token_info):
            token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
            session['token_info'] = token_info
        
        return spotipy.Spotify(auth=token_info['access_token'])
    except Exception as e:
        print(f"Error creating Spotify client: {e}")
        return None

@app.route('/')
def home():
    return render_template_string('''
    <html>
        <head>
            <title>Spotify Python App</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; text-align: center; }
                .login-btn { 
                    background: #1db954; color: white; padding: 15px 30px; 
                    text-decoration: none; border-radius: 25px; font-size: 16px; 
                }
                .login-btn:hover { background: #1ed760; }
            </style>
        </head>
        <body>
            <h1>🎵 Spotify Python Integration</h1>
            <p>Connect your Spotify account to get started</p>
            <a href="/login" class="login-btn">Login with Spotify</a>
        </body>
    </html>
    ''')

@app.route('/login')
def login():
    sp_oauth = get_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    sp_oauth = get_spotify_oauth()
    code = request.args.get('code')
    
    if code:
        try:
            token_info = sp_oauth.get_access_token(code)
            session['token_info'] = token_info
            return redirect('/dashboard')
        except Exception as e:
            return f'<h1>Error: {str(e)}</h1>'
    else:
        return '<h1>Error: No authorization code received</h1>'

@app.route('/dashboard')
def dashboard():
    sp = get_spotify_client()
    if not sp:
        return redirect('/login')
    
    try:
        # Get user profile
        user_profile = sp.current_user()
        if not user_profile:
            return '<h1>Error: Could not retrieve user profile</h1>'
        
        # Get current playback (this might be None if nothing is playing)
        current_playback = sp.current_playback()
        
        # Get user's playlists
        playlists = sp.current_user_playlists(limit=5)
        if not playlists:
            playlists = {'items': []}  # Provide empty list if no playlists
        
        return render_template_string('''
        <html>
            <head>
                <title>Spotify Dashboard</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; }
                    .card { background: #f8f9fa; padding: 20px; margin: 15px 0; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                    .controls button { 
                        background: #1db954; color: white; border: none; padding: 10px 20px; 
                        margin: 5px; border-radius: 20px; cursor: pointer; font-size: 14px;
                    }
                    .controls button:hover { background: #1ed760; }
                    .search-section input { width: 300px; padding: 10px; margin: 10px 0; border-radius: 5px; border: 1px solid #ddd; }
                    .track-item { 
                        background: white; padding: 15px; margin: 10px 0; border-radius: 8px; 
                        display: flex; justify-content: space-between; align-items: center;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    }
                    .track-info { flex-grow: 1; }
                    .track-info strong { color: #333; }
                    .track-info .artist { color: #666; font-size: 14px; }
                    .play-btn { 
                        background: #1db954; color: white; border: none; padding: 8px 16px; 
                        border-radius: 15px; cursor: pointer;
                    }
                    .currently-playing { background: linear-gradient(135deg, #1db954, #1ed760); color: white; }
                </style>
            </head>
            <body>
                <h1>🎵 Welcome, {{ user_profile.display_name }}!</h1>
                
                <div class="card">
                    <h3>👤 Your Profile</h3>
                    <p><strong>Email:</strong> {{ user_profile.email or 'Not available' }}</p>
                    <p><strong>Followers:</strong> {{ user_profile.followers.total if user_profile.followers else 0 }}</p>
                    <p><strong>Country:</strong> {{ user_profile.country or 'Not specified' }}</p>
                    <p><strong>Subscription:</strong> {{ user_profile.product or 'Not available' }}</p>
                </div>
                
                <div class="card {% if current_playback and current_playback.item %}currently-playing{% endif %}">
                    <h3>🎶 Now Playing</h3>
                    {% if current_playback and current_playback.item %}
                        <p><strong>{{ current_playback.item.name }}</strong></p>
                        <p class="artist">by {{ current_playback.item.artists[0].name if current_playback.item.artists else 'Unknown Artist' }}</p>
                        <p>Device: {{ current_playback.device.name if current_playback.device else 'Unknown Device' }}</p>
                        <p>Status: {{ "Playing" if current_playback.is_playing else "Paused" }}</p>
                    {% else %}
                        <p>No music currently playing. Start playing music on Spotify to see it here!</p>
                    {% endif %}
                </div>
                
                <div class="card">
                    <h3>🎮 Playback Controls</h3>
                    <div class="controls">
                        <button onclick="controlPlayback('previous')">⏮️ Previous</button>
                        <button onclick="controlPlayback('play')">▶️ Play</button>
                        <button onclick="controlPlayback('pause')">⏸️ Pause</button>
                        <button onclick="controlPlayback('next')">⏭️ Next</button>
                        <button onclick="controlPlayback('shuffle')">🔀 Shuffle</button>
                    </div>
                </div>
                
                <div class="card">
                    <h3>🔍 Search & Play</h3>
                    <div class="search-section">
                        <input type="text" id="searchQuery" placeholder="Search for songs, artists, or albums...">
                        <button onclick="searchTracks()" style="background: #1db954; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">Search</button>
                    </div>
                    <div id="searchResults"></div>
                </div>
                
                <div class="card">
                    <h3>📝 Your Playlists</h3>
                    {% if playlists and playlists.items %}
                        {% for playlist in playlists.items %}
                            <div class="track-item">
                                <div class="track-info">
                                    <strong>{{ playlist.name }}</strong>
                                    <div class="artist">{{ playlist.tracks.total if playlist.tracks else 0 }} tracks</div>
                                </div>
                                <button class="play-btn" onclick="playPlaylist('{{ playlist.uri }}')">Play</button>
                            </div>
                        {% endfor %}
                    {% else %}
                        <p>No playlists found. Create some playlists in Spotify to see them here!</p>
                    {% endif %}
                </div>
                
                <script>
                    async function controlPlayback(action) {
                        try {
                            const response = await fetch('/api/playback/' + action, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' }
                            });
                            const result = await response.text();
                            console.log(result);
                            // Refresh page after 1 second to show updated status
                            setTimeout(() => location.reload(), 1000);
                        } catch (error) {
                            console.error('Error:', error);
                            alert('Error: Make sure Spotify is open and playing on a device');
                        }
                    }
                    
                    async function searchTracks() {
                        const query = document.getElementById('searchQuery').value;
                        if (!query) return;
                        
                        try {
                            const response = await fetch('/api/search', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ query: query })
                            });
                            const results = await response.json();
                            
                            const resultsDiv = document.getElementById('searchResults');
                            resultsDiv.innerHTML = results.map(track => 
                                `<div class="track-item">
                                    <div class="track-info">
                                        <strong>${track.name}</strong>
                                        <div class="artist">by ${track.artists[0].name}</div>
                                    </div>
                                    <button class="play-btn" onclick="playTrack('${track.uri}')">Play</button>
                                </div>`
                            ).join('');
                        } catch (error) {
                            console.error('Error:', error);
                        }
                    }
                    
                    async function playTrack(uri) {
                        try {
                            const response = await fetch('/api/play', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ uri: uri })
                            });
                            console.log('Playing track');
                            setTimeout(() => location.reload(), 1000);
                        } catch (error) {
                            console.error('Error:', error);
                            alert('Error: Make sure Spotify is open on a device');
                        }
                    }
                    
                    async function playPlaylist(uri) {
                        try {
                            const response = await fetch('/api/play', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ uri: uri })
                            });
                            console.log('Playing playlist');
                            setTimeout(() => location.reload(), 1000);
                        } catch (error) {
                            console.error('Error:', error);
                            alert('Error: Make sure Spotify is open on a device');
                        }
                    }
                </script>
            </body>
        </html>
        ''', user_profile=user_profile, current_playback=current_playback, playlists=playlists)
    
    except Exception as e:
        return f'<h1>Error loading dashboard: {str(e)}</h1>'

# API Routes
@app.route('/api/playback/<action>', methods=['POST'])
def control_playback(action):
    sp = get_spotify_client()
    if not sp:
        return 'Unauthorized - Please login again', 401
    
    try:
        if action == 'play':
            sp.start_playback()
        elif action == 'pause':
            sp.pause_playback()
        elif action == 'next':
            sp.next_track()
        elif action == 'previous':
            sp.previous_track()
        elif action == 'shuffle':
            current = sp.current_playback()
            if current:
                new_shuffle_state = not current['shuffle_state']
                sp.shuffle(new_shuffle_state)
            else:
                return 'No active playback device found', 400
        
        return f'Playback {action} successful'
    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 404:
            return 'No active device found. Please start playing music on Spotify first.', 404
        elif e.http_status == 403:
            return 'Premium subscription required for this action', 403
        else:
            return f'Spotify API Error: {str(e)}', 500
    except Exception as e:
        return f'Error: {str(e)}', 500

@app.route('/api/search', methods=['POST'])
def search_tracks():
    sp = get_spotify_client()
    if not sp:
        return 'Unauthorized', 401
    
    data = request.get_json()
    query = data.get('query')
    
    try:
        results = sp.search(q=query, type='track', limit=10)
        tracks = []
        
        for track in results['tracks']['items']:
            tracks.append({
                'name': track['name'],
                'artists': track['artists'],
                'uri': track['uri'],
                'preview_url': track['preview_url']
            })
        
        return jsonify(tracks)
    except Exception as e:
        return f'Error: {str(e)}', 500

@app.route('/api/play', methods=['POST'])
def play_track():
    sp = get_spotify_client()
    if not sp:
        return 'Unauthorized', 401
    
    data = request.get_json()
    uri = data.get('uri')
    
    try:
        if uri.startswith('spotify:track:'):
            sp.start_playback(uris=[uri])
        elif uri.startswith('spotify:playlist:'):
            sp.start_playback(context_uri=uri)
        
        return 'Playing track/playlist'
    except Exception as e:
        return f'Error: {str(e)}', 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    print("🎵 Starting Spotify Python App...")
    print(f"📍 Visit: http://127.0.0.1:5000")
    print(f"🔑 Make sure your Spotify app redirect URI is: {REDIRECT_URI}")
    app.run(debug=True, host='127.0.0.1', port=5000)