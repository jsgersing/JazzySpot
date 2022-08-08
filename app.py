from flask import Flask, render_template, request
from spotify import gather_artist_recs
from dotenv import load_dotenv
from mongo_interface_component import MongoDB
# from spotify import process_mpd
from spotify import create_recommender_model
import pandas as pd
from joblib import load

load_dotenv()
APP = Flask(__name__)

db = MongoDB("jazzy_spot")
# playlists = '/Users/jasongersing/Downloads/spotify_million_playlist_dataset/test_directory'
# tuples = process_mpd(playlists)
# db.create_many("uris", tuples)

# uris = [item.get("track_uri") for item in db.read("uris")]
#
# print(uris[:5])
# track_features = extract_tracks_features(uris[0])
# print(track_features)
# db.create_many("tracks_features", tracks_features)


@APP.route("/")
def home():
    # artists = db.read("artists")
    return render_template('home.html', message='Spotify Recommender')


@APP.route('/reset')
def reset():
    # db.delete("artists", {})
    return render_template('base.html', message='Reset DB')


@APP.route('/recommend', methods=['GET', 'POST'])
def recommend():
    # artist = request.values.get('artist_name')
    song = request.values.get('song_title')
    recommendations = create_recommender_model(song)
    return render_template('base.html',
                           message='Spotify Recommender',
                           recommendations=recommendations)
