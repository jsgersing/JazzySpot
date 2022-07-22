from flask import Flask, render_template, request
from spotify import gather_artist_recs
from dotenv import load_dotenv
from mongo_interface_component import MongoDB

load_dotenv()
APP = Flask(__name__)

db = MongoDB("jazzy_spot")


@APP.route("/")
def home():
    # artists = db.read("artists")
    return render_template('home.html', message='Spotify Recommender')


@APP.route('/reset')
def reset():
    db.delete("artists", {})
    return render_template('base.html', message='Reset DB')


@APP.route('/recommend', methods=['GET', 'POST'])
def recommend():
    artist = request.values.get('artist_name')
    combined = gather_artist_recs(artist)
    recommendations = combined
    return render_template('base.html',
                           message='Spotify Recommender',
                           recommendations=recommendations)
