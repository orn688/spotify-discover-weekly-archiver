# -*- coding: utf-8 -*-
import base64
import os

import requests

BASE_URL = 'https://api.spotify.com/v1'


def handler(event, context):
    session = get_authenticated_session()

    my_id = get_my_id(session)

    discover_weekly_uri, archive_uri = get_playlist_uris(session, my_id)

    discover_weekly_tracks = get_playlist_tracks(session, my_id,
                                                 discover_weekly_uri)

    add_tracks_to_playlist(session, my_id, archive_uri, discover_weekly_tracks)


def get_playlist_tracks(session, user_id, playlist_uri):
    url = BASE_URL + f'/users/{user_id}/playlists/{playlist_id}'
    response = session.get(url)
    # TODO



def add_tracks_to_playlist(session, user_id, playlist_uri, tracks):
    url = BASE_URL + f'/users/{user_id}/playlists/{playlist_id}/tracks'
    session.post(url, json={})
    # TODO


def get_authenticated_session():
    """
    Assuming we already have a refresh token, get a new access token and set
    the corresponding auth header in a new session.
    """
    session = requests.Session()

    client_id = os.environ.get('SPOTIFY_CLIENT_ID')
    client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
    refresh_token = os.environ.get('SPOTIFY_REFRESH_TOKEN')

    auth_header = base64.b64encode(f'{client_id}:{client_secret}')
    session.headers['Authorization'] = f'Basic {auth_header}'

    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
    }
    response = session.post(
        'https://accounts.spotify.com/api/token',
        json=payload
    )

    assert response.status_code == 200

    access_token = response.data['access_token']
    session.headers['Authorization'] = f'Bearer: {access_token}'

    return session


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
