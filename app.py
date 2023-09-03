from flask import Flask, request, url_for, session, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import pandas as pd


app = Flask(__name__)

app.secret_key = "KdjklmdJDOecm"
app.config['SESSION_COOKIE_NAME'] = 'Zachs Cookie'
TOKEN_INFO = "token_info"


@app.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    print(auth_url)
    return redirect(auth_url)


@app.route('/redirect')
def redirectPage():
    sp_oauth = create_spotify_oauth()
    session.clear
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["token info"] = token_info
    return redirect(url_for('getTracks', _external=True))


@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')


@app.route('/getTracks')
def getTracks():
    session['token_info'] = get_token()
    authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect("/")
    sp = spotipy.Spotify(auth=session.get('token info').get('access_token'))
    results = []
    iter = 0
    while True:
        offset = iter * 50
        iter += 1
        currGroup = sp.current_user_saved_tracks(limit=50, offset=offset)['items']
        for idx, item in enumerate(currGroup):
            track = item['track']
            val = track['name'] + " - " + track['artists'][0]['name']
            results += [val]
        if len(currGroup) < 50:
            break
    df = pd.DataFrame(results, columns=["song names"])
    df.to_csv('songs.csv', index=False)
    return "done"


def get_token():
    token_valid = False
    token_info = session.get("token_info", {})
    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid
    now = int(time.time())
    is_expired = session.get('token_info').get('expires_at') - now < 60
    if is_expired:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))
    token_valid = True
    return token_info


def create_spotify_oauth():
    return SpotifyOAuth(
            client_id="ed51073e2e4b4c67912e0f92ffb2b2cb",
            client_secret="c284da2e346f4b66a23ed1c3a6c464ca",
            redirect_uri=url_for('redirectPage', _external=True),
            scope="user-library-read")

