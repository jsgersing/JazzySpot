from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from spotify import gather_artist_recs
from os import getenv
from dotenv import load_dotenv

load_dotenv()
APP = Flask(__name__)

APP.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URI')
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

DB = SQLAlchemy()
DB.init_app(APP)


class Artists(DB.Model):
    artist_id = DB.Column(DB.String(), primary_key=True)
    artist_name = DB.Column(DB.String(), nullable=True)
    album_url = DB.Column(DB.String(), nullable=True)

    def __init__(self, artist_id, artist_name, album_url):
        self.artist_id = artist_id
        self.artist_name = artist_name
        self.album_url = album_url

    def __repr__(self):
        return f"<Track: {self.artist_name}>"


APP.app_context().push()


@APP.route("/")
def home():
    songs = Track.query.all()
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