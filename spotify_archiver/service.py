# -*- coding: utf-8 -*-
import base64
import logging
import os

import requests

BASE_URL = 'https://api.spotify.com/v1'
logger = logging.getLogger(__name__)


class SpotifyError(RuntimeError):
    pass


def handler(event=None, context=None):
    session = get_authenticated_session()

    my_id = get_my_id(session)

    # This could be done in two separate calls to a more reusable function,
    # but this avoids unecessary requests to the Spotify API.
    discover_weekly_id, archive_id = get_playlist_ids(session, my_id)

    discover_weekly_tracks = get_playlist_tracks(
        session, user_id='spotify', playlist_id=discover_weekly_id)

    add_tracks_to_playlist(session, my_id, archive_id, discover_weekly_tracks)


def get_my_id(session):
    response = session.get(BASE_URL + '/me')
    me = response.json()

    return me['id']


def get_playlist_ids(session, my_id):
    discover_weekly_id, archive_id = None, None
    next_page_url = BASE_URL + '/me/playlists'

    while next_page_url and not (discover_weekly_id and archive_id):
        response = session.get(next_page_url)

        playlists = response.json()['items']

        for playlist in playlists:
            owner_id = playlist['owner']['id']
            name = playlist['name']

            if owner_id == 'spotify' and name == 'Discover Weekly':
                discover_weekly_id = playlist['id']
            elif owner_id == my_id and name == 'Discover Weekly Archive':
                archive_id = playlist['id']

            if discover_weekly_id and archive_id:
                return discover_weekly_id, archive_id

        next_page_url = response.json()['next']

    raise SpotifyError('Unable to find Discovery Weekly and Discover Weekly '
                       'Archive playlists in user\'s account.')


def get_playlist_tracks(session, user_id, playlist_id, count=None):
    tracks = []

    url_path = f'/users/{user_id}/playlists/{playlist_id}/tracks'
    next_page_url = BASE_URL + url_path

    while next_page_url:
        if count:
            remaining_count = count - len(tracks)

            if remaining_count <= 0:
                break
        else:
            remaining_count = None

        response = session.get(next_page_url)

        page_of_tracks = response.json()['items']
        if remaining_count is not None:
            page_of_tracks = page_of_tracks[:remaining_count]

        tracks.extend(page_of_tracks)

        next_page_url = response.json()['next']

    return [track['track'] for track in tracks]


def add_tracks_to_playlist(session, user_id, playlist_id, tracks):
    # At most 100 tracks can be passed in one request (DW is generally only 30
    # tracks long)
    track_uris = [track['uri'] for track in tracks][:100]

    track_uris = remove_duplicates(session, user_id, playlist_id, track_uris)

    if len(track_uris) == 0:
        logger.info('No new tracks to add; exiting')
        return

    payload = {
        'uris': track_uris,
        'position': 0,
    }
    url = BASE_URL + f'/users/{user_id}/playlists/{playlist_id}/tracks'
    response = session.post(url, json=payload)

    assert response.status_code == 201, response.json()['error']

    logger.info(f'Archived {len(track_uris)} track(s)')


def remove_duplicates(session, user_id, playlist_id, track_uris):
    existing_tracks = get_playlist_tracks(session, user_id, playlist_id)
    existing_track_uris = [track['uri'] for track in existing_tracks]

    filtered_track_uris = set(track_uris).difference(existing_track_uris)

    return list(filtered_track_uris)


def get_authenticated_session():
    """
    Assuming we already have a refresh token, get a new access token and set
    the corresponding auth header in a new session object.
    """
    session = requests.Session()

    client_id = os.environ.get('SPOTIFY_CLIENT_ID')
    client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
    refresh_token = os.environ.get('SPOTIFY_REFRESH_TOKEN')

    raw_auth_header = f'{client_id}:{client_secret}'.encode()
    encoded_auth_header = base64.b64encode(raw_auth_header).decode()

    session.headers['Authorization'] = f'Basic {encoded_auth_header}'

    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
    }
    url = 'https://accounts.spotify.com/api/token'
    response = session.post(url, payload)

    assert response.status_code == 200, response.text

    access_token = response.json()['access_token']
    session.headers['Authorization'] = f'Bearer {access_token}'
    session.headers['Content-Type'] = 'application/json'

    return session


if __name__ == '__main__':
    handler()
