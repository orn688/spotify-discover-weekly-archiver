# Spotify Discover Weekly Archiver

AWS lambda function to archive your Spotify Discover Weekly playlist.

## Setup

Set up a Spotify API application:

1. Log in to the [Spotify developer dashboard](https://beta.developer.spotify.com/dashboard/applications) and create an application.
2. In the application page, click **Edit Settings**, add https://localhost/redirect as a redirect URIs, and click **Save** at the bottom of the pop-up.

Set up a local development environment:

```sh
$ pip install pipenv # If you don't already have Pipenv installed.
$ pipenv --python 3.6
$ pipenv install
$ pipenv run python setup.py # And follow the instructions presented.
```
