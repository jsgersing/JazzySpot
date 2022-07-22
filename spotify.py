import random
import spotipy
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


def gather_artist_recs(artist):
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
        # lst = Artists(artist_id=a_id, artist_name=a_name, album_url=al_url)
        db_list = db.read("artists", {"artist_id": my_dict.get("artist_id")})
        # db_list = Artists.query.filter(Artists.artist_id == lst.artist_id).all()
        if db_list:
            pass
        else:
            db.create("artists", my_dict)
            # DB.session.add(lst)
            # DB.session.commit()
    combined = [list(a) for a in zip(artist_name, album_urls) if list(a)[0] not in searched_artist_name]
    sample = random.sample(combined, 10)
    output = []
    while len(output) < 5:
        for item in sample:
            if item not in output:
                output.append(item)
                break
    return output
