import json
import os
from typing import List, Dict, Any

import pandas as pd
from numpy.testing import verbose

import random
import spotipy
from sklearn.neighbors import NearestNeighbors
from spotipy import SpotifyClientCredentials
from os import getenv
from dotenv import load_dotenv
from mongo_interface_component import MongoDB

load_dotenv()
client_credentials_manager = SpotifyClientCredentials(
                                client_id=getenv("CID"),
                                client_secret=getenv("SECRET"))
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


db = MongoDB("jazzy_spot")


def retrieve_track_name(uri: str) -> str:
    track_found = sp.track(uri)
    track_name = track_found['name']
    return track_name


def gather_artist_recs(artist: str) -> List[list]:
    artist_results = sp.search(q=f'artist: {artist}', limit=20)
    items = artist_results['tracks']['items']
    item = [item for item in items]
    albums = [item[i] for i, _ in enumerate(item)]
    artists = [albums[i]['artists'][0] for i, _ in enumerate(albums)]
    searched_artist_id = artists[0]['id']
    searched_artist_name = artists[0]['name']
    track_id = [item['id'] for item in item]
    print(track_id)
    artist_recommendations = [sp.recommendations(seed_artists=[searched_artist_id]) for _ in track_id]
    artist_id = \
        [artist_recommendations[i]['tracks'][0]['album']['artists'][0]['id']
         for i, _ in enumerate(artist_recommendations)]
    artist_name = [artist_recommendations[i]['tracks'][0]['album']['artists'][0]['name'] for i, _ in
                   enumerate(artist_recommendations)]
    album_urls = \
        [artist_recommendations[i]['tracks'][0]['album']['artists'][0]['external_urls']['spotify']
         for i, _ in enumerate(artist_recommendations)]
    all_three = set([tuple(b) for b in zip(artist_id, artist_name, album_urls)])
    for lst in all_three:
        a_id = lst[0]
        a_name = lst[1]
        al_url = lst[2]
        my_dict = {'artist_id': a_id, "artist_name": a_name, "album_url": al_url}
        db_list = db.read("artists", {"artist_id": my_dict.get("artist_id")})
        if db_list:
            pass
        else:
            db.create("artists", my_dict)
    combined = [list(a) for a in zip(artist_name, album_urls) if list(a)[0] not in searched_artist_name]
    sample = random.sample(combined, 10)
    output = []
    while len(output) < 5:
        for item in sample:
            if item not in output:
                output.append(item)
                break
    return output


def extract_tracks_features(uris: List[str]) -> List[dict]:
    # track_uris = [uri for uri in uris]
    tracks_features = []
    for track_uri in uris:
        popularity = sp.track(track_uri)['popularity']
        track_url = list(sp.track(track_uri)['external_urls'].values())[0]
        artist_name = sp.track(track_uri)['artists'][0]['name']
        danceability = sp.audio_features(track_uri)[0]['danceability']
        energy = sp.audio_features(track_uri)[0]['energy']
        key = sp.audio_features(track_uri)[0]['key']
        loudness = sp.audio_features(track_uri)[0]['loudness']
        speechiness = sp.audio_features(track_uri)[0]['speechiness']
        acousticness = sp.audio_features(track_uri)[0]['acousticness']
        instrumentalness = sp.audio_features(track_uri)[0]['instrumentalness']
        tempo = sp.audio_features(track_uri)[0]['tempo']
        valence = sp.audio_features(track_uri)[0]['valence']
        duration = sp.audio_features(track_uri)[0]['duration_ms']
        title = retrieve_track_name(track_uri)
        tracks_features.append(
            {'track_uri': track_uri, 'title': title, 'danceability': danceability, 'energy': energy, 'key': key,
             'loudness': loudness, 'speechiness': speechiness, 'acousticness': acousticness,
             'instrumentalness': instrumentalness,
             'tempo': tempo, 'valence': valence, 'duration': duration, 'popularity': popularity,
             'track_url': track_url, 'artist_name': artist_name})
    return tracks_features


def process_mpd(path: str) -> List[Dict[str, Any]]:
    tuples = []
    filenames = os.listdir(path)
    for i, filename in enumerate(sorted(filenames)):
        if filename.startswith("mpd.slice.") and filename.endswith(".json"):
            if verbose:
                print(f" {i:4d} of {len(filenames):4d} {filename}")
            fullpath = os.sep.join((path, filename))
            f = open(fullpath)
            js = f.read()
            f.close()
            slyce = json.loads(js)
            for playlist in slyce["playlists"]:
                for track in playlist['tracks']:
                    entry = {
                        'artist_uri': track['artist_uri'],
                        'album_uri': track['album_uri'], 'track_uri': track['track_uri']}
                    tuples.append(entry)
    print(tuples)
    return tuples


def retrieve_track_uri(track: str) -> str:
    track_found = sp.search(q=f'track: {track}', limit=1)
    track_uri = track_found['tracks']['items'][0]['uri']
    return track_uri


def create_recommender_model(song: str) -> List[str]:
    df = pd.DataFrame(db.read("all_features", {'popularity': {'$gt': 30}}))
    print(df.head())
    df = df.drop_duplicates(subset='track_uri')
    columns = ['danceability', 'energy', 'key', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'tempo',
               'valence', 'duration']
    x = df[columns]
    neigh = NearestNeighbors(n_neighbors=5, n_jobs=-1)
    neigh.fit(x.values)
    track_index = df[df['title'] == song].index[0]
    print(track_index)
    track_data = x.iloc[track_index]
    track_data = track_data.values.reshape(1, -1)
    distances, song_indexes = neigh.kneighbors(track_data, 6)
    distances, song_indexes = distances.tolist(), song_indexes.tolist()
    indexes = [index for index in song_indexes][0]
    print(indexes)
    recommendations = [df.iloc[index][['title', 'artist_name', 'track_url']].tolist() for index in indexes][1:6]

    print(recommendations)
    return recommendations


def extract_and_input_genres():
    artists = db.read('artists')
    artists_ids = [item['artist_id'] for item in artists]
    genres = [sp.artist(item)['genres'] for item in artists_ids]
    return genres


def get_artists_from_all_features():
    artists = [item.get('artist_name') for item in db.read('all_features')]
    return artists


def extract_artist_id_from_all_features(artists: List[str]) -> List[str]:
    search_results = [sp.search(q=f'artist: {artist}', limit=1) for artist in artists]
    track_items = [result['tracks']['items'] for result in search_results]
    if not track_items:
        return []
    else:
        artist_id = [album[0]['artists'][0]['id'] for album in track_items]
        return artist_id


def extract_genres_from_artist_id(ids: List[str]) -> List[str]:
    if ids:
        genres = [sp.artist(i_d)['genres'] for i_d in ids]
        return genres
    else:
        return []


def artist_name_to_genres():
    artist_name_dicts = db.read('all_features', {}, projection={'_id': False, 'artist_name': True})
    name = list(map(lambda a: a['artist_name'], artist_name_dicts))
    artist_id = extract_artist_id_from_all_features(name)
    genres = extract_genres_from_artist_id(artist_id)
    genres_dict = list(map(lambda a, b, c: {'genres': a, 'name': b, 'id': c}, genres, name, artist_id))
    db.create_many('genres', genres_dict)
