import os
import fileinput
import sys
import uuid
import webbrowser
from collections import OrderedDict

import requests
from flask import Flask, redirect, request

app = Flask(__name__)
CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')


def get_redirect_uri(request):
    return request.url_root + 'callback'


@app.route('/')
def index():
    query_params = dict(
        client_id=CLIENT_ID,
        response_type='code',
        redirect_uri=get_redirect_uri(request),
        state=str(uuid.uuid4()),
        scope=' '.join(['playlist-read-private', 'playlist-modify-private']),
    )
    query_string = '&'.join(f'{key}={val}' for key, val in query_params.items())
    return redirect('https://accounts.spotify.com/authorize?' + query_string)


@app.route('/callback')
def callback():
    code = request.args.get('code')

    if not code:
        error_message = request.args['error']
        return 'Spotify authorization failed: ' + error_message

    access_token_url = 'https://accounts.spotify.com/api/token'
    response = requests.post(access_token_url, data=dict(
        grant_type='authorization_code',
        code=code,
        redirect_uri=get_redirect_uri(request),
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    ))

    assert response.status_code == 200

    body = response.json()
    refresh_token = body['refresh_token']

    env_file_name = '.env'

    with open(env_file_name) as env_file:
        env_vars = OrderedDict(line.split('=', 1) for line in env_file if '=' in line)

    env_vars['SPOTIFY_REFRESH_TOKEN'] = refresh_token

    with open(env_file_name, 'w') as env_file:
        new_contents = ''.join(f'{key}={val}\n' for key, val in env_vars.items())
        env_file.write(new_contents)

    return 'Spotify authorization succeeded; saved refresh token to .env file.'


if __name__ == '__main__':
    port = 5000
    webbrowser.open_new_tab('http://localhost:{0}/'.format(port))
    app.run(debug=True, port=port)
