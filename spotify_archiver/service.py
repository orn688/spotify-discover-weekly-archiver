# -*- coding: utf-8 -*-
import base64
import json
import os

import requests

BASE_URL = 'https://api.spotify.com/v1'


def handler(event=None, context=None):
    session = get_authenticated_session()

    my_id = get_my_id(session)

    discover_weekly_uri, archive_uri = get_playlist_uris(session, my_id)

    discover_weekly_tracks = get_playlist_tracks(session, my_id,
                                                 discover_weekly_uri)

    add_tracks_to_playlist(session, my_id, archive_uri, discover_weekly_tracks)


def get_my_id(session):
    response = session.get(BASE_URL + '/me')

    me = response.json()

    return me['id']


def get_playlist_uris(session, my_id):
    discover_weekly_uri, archive_uri = None, None
    next_page_url = BASE_URL + '/me/playlists'

    while next_page_url and not (discover_weekly_uri and archive_uri):
        response = session.get('https://api.spotify.com/v1/me/playlists')

        playlists = response.json()['items']

        for playlist in playlists:
            # Includes followed playlists, so owner isn't necessarily me
            if playlist['owner']['id'] != my_id:
                continue

            if playlist['name'] == 'Discover Weekly':
                discover_weekly_uri = playlist['uri']
            elif playlist['name'] == 'Discover Weekly Archive':
                archive_uri = playlist['uri']

            if discover_weekly_uri and archive_uri:
                break

        next_page_url = response.json()['next']

    if not discover_weekly_uri or not archive_uri:
        raise RuntimeError('Unable to find Discovery Weekly and Discover '
                           'Weekly Archive playlists in user\'s account.')

    return discover_weekly_uri, archive_uri


def get_playlist_tracks(session, user_id, playlist_uri):
    url = BASE_URL + f'/users/{user_id}/playlists/{playlist_id}/tracks'
    response = session.get(url)

    playlist_tracks = response.json()['items']

    return [track['track'] for track in playlist_tracks]


def add_tracks_to_playlist(session, user_id, playlist_uri, tracks):
    track_uris = [track['uri'] for track in tracks]

    payload = {
        'uris': ','.join(track_uris)
    }
    url = BASE_URL + f'/users/{user_id}/playlists/{playlist_id}/tracks'

    response = session.post(url, data=payload)

    error = response.json().get('error_description')
    if error:
        raise requests.HTTPError(error_description, response=response)


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

    response = session.post('https://accounts.spotify.com/api/token', payload)

    assert response.status_code == 200, response.text

    access_token = response.json()['access_token']
    session.headers['Authorization'] = f'Bearer: {access_token}'
    session.headers['Content-Type'] = 'application/json'

    return session


if __name__ == '__main__':
    handler()
