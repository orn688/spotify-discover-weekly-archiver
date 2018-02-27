# Spotify Discover Weekly Archiver

AWS lambda function to archive your Spotify Discover Weekly playlist.

## Setup

(Requires Python 3.6+)

1. Set up a local development environment:

    ```sh
    pip install pipenv  # If you don't already have Pipenv installed.
    pipenv --python 3.6
    pipenv install
    ```

2. Create a Spotify API application:
    1. Log in to the [Spotify developer dashboard](https://beta.developer.spotify.com/dashboard/applications) and create an application.
    2. In the application page, click **Edit Settings**, add http://localhost:5000/callback as a redirect URI, and click **Save** at the bottom of the pop-up.

3. Create a `.env` file with your AWS and Spotify credentials:
    1. `cp template.env .env`
    2. Set the necessary values in `.env`
    3. `pipenv run python get_access_token.py`

4. (To be continued...)
