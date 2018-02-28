# Spotify Discover Weekly Archiver

AWS lambda function to archive your Spotify Discover Weekly playlist.

## Setup

(Requires Python 3.6+)

1. Set up a local development environment:

    ```sh
    pip install pipenv  # If you don't already have Pipenv installed
    pipenv install
    ```

2. Create a Spotify API application:
    1. Log in to the [Spotify developer dashboard](https://beta.developer.spotify.com/dashboard/applications) and create an application.
    2. In the application page, click **Edit Settings**, add http://localhost:5000/callback as a redirect URI, and click **Save** at the bottom of the pop-up.

3. Get an access token and secret access key for AWS and make sure that the associated IAM user has lambda access. (TODO: exact permissions needed)

3. Create a `.env` file with your AWS and Spotify credentials:
    1. `cp template.env .env`
    2. Set the AWS credentials and Spotify client ID and client secret in `.env`

4. Get a refresh token for your Spotify account:
  
  ```
  pipenv run get_refresh_token.py
  ```

  This require you to sign into Spotify in your browser, and will automatically add to your `.env` file the refresh token necessary to access your Spotify account via the Spotify API application you made.

5. Deploy! TODO: how?
