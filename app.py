from flask import Flask, render_template, request
from spotify import DB, Artists
from spotify import gather_artist_recs
from os import getenv
from dotenv import load_dotenv

load_dotenv()
APP = Flask(__name__)

APP.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URI')
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

DB.init_app(APP)
APP.app_context().push()


@APP.route("/")
def home():
    songs = Artists.query.all()
    return render_template('home.html', message='Spotify Recommender', song=songs)


@APP.route('/reset')
def reset():
    DB.drop_all()
    DB.create_all()
    return render_template('base.html', message='Reset DB')


@APP.route('/recommend', methods=['GET', 'POST'])
def recommend():
    artist = request.values.get('artist_name')
    combined = gather_artist_recs(artist)
    recommendations = combined
    return render_template('base.html',
                           message='Spotify Recommender',
                           recommendations=recommendations)
