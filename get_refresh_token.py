import os
import fileinput
import sys
import uuid
import webbrowser
from multiprocessing import Process

import requests
from flask import Flask, redirect, request

app = Flask(__name__)
CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')


@app.route('/')
def index():
    return redirect(url_for_code(request.url_root))


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
        redirect_uri=request.url_root + 'callback',
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    ))

    assert response.status_code == 200

    refresh_token = response.json()['refresh_token']
    access_token = response.json()['access_token']
    print(access_token)
    write_token_to_env_file(refresh_token)

    shutdown_server_when_finished()

    return ('Successfully saved Spotify refresh token to .env file. Shutting '
            'down server (it\'s safe to close this page).')


def url_for_code(redirect_uri_hostname):
    query_params = dict(
        client_id=CLIENT_ID,
        response_type='code',
        redirect_uri=redirect_uri_hostname + 'callback',
        state=str(uuid.uuid4()),
        scope=' '.join(['playlist-read-private', 'playlist-modify-private']),
    )

    query_string = '&'.join(f'{key}={val}' for key, val in query_params.items())

    return 'https://accounts.spotify.com/authorize?' + query_string


def write_token_to_env_file(refresh_token):
    refresh_token_name = 'SPOTIFY_REFRESH_TOKEN'
    env_file_name = '.env'

    with open(env_file_name) as env_file:
        lines = env_file.readlines()

    wrote_refresh_token = False

    for i, line in enumerate(lines):
        if '=' in line:
            env_var_name = line.split('=')[0]

            if env_var_name == refresh_token_name:
                lines[i] = f'{refresh_token_name}={refresh_token}\n'
                wrote_refresh_token = True

    if not wrote_refresh_token:
        lines.append(f'{refresh_token_name}={refresh_token}')

    with open(env_file_name, 'w') as env_file:
        env_file.write(''.join(line for line in lines))


def shutdown_server_when_finished():
    # source: http://flask.pocoo.org/snippets/67/
    shutdown_func = request.environ.get('werkzeug.server.shutdown')

    if shutdown_func is None:
        raise RuntimeError('Not running with the Werkzeug Server')

    shutdown_func()


if __name__ == '__main__':
    port = 5000

    webbrowser.open(url_for_code(f'http://localhost:{port}/'))

    app.run(debug=False, port=port)
