# gVerify

## Overview

A python library for authenticating requests for various google services including ```gmail```, ```youtube```, ```drive``` and ```calendar```.

## Requirements

- Python 3.10+
- Works on Linux, Windows, macOS, BSD

## Getting started

### Getting an access key

To get started with this library, you need a google account in order to obtain access credentials. First, pick a service that you want to use, which could be:
    - ```gmail```
    - ```youtube```
    - ```drive```
    - ```calendar```

#### Installing the library

The next step is to instal the library from pypi:

```sh
pip install gverify
```

#### Authorizing a request

In this case we will use ```youtube``` as the service. We will authorize a request to search ```youtube``` for ```python programming videos```:

```python
from gverify import GoogleOAuth, YouTubeScopes

client_secret_file: str = 'client_secret.json'
api_service_name: str = 'youtube'
api_version: str = 'v3'
credentials_dir: str = '.youtube'
scopes: list[str] = [YouTubeScopes.youtube.value]
oauth: GoogleOAuth = GoogleOAuth(
    secrets_file=secret_file,
    scopes=scopes,
    api_service_name=api_service_name,
    api_version=api_version,
    credentials_dir=credentials_dir
)
youtube_client = oauth.authenticate_google_server()
youtube_find_request = youtube_client.search().list(q='python programming videos', part='id, snippet')
print(youtube_find_request.execute())
```

## Using the Flask Framework

Currently, this library does not intergrate with web frameworks like Flask and fastAPI. To use flask, we use the underlying library:

```python
from flask import Flask, url_for, redirect, request, session
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import os


CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = [
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/youtube'
]
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

app: Flask = Flask(__name__)
app.secret_key = 'secret-key'


@app.route('/')
def home():
    if not session['credentials']:
        redirect(url_for('authorize'))
    return 'Home'


@app.route('/authorize')
def authorize():
    flow = Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE,
      scopes=SCOPES
      )
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    authorization_url, state = flow.authorization_url(
      access_type='offline',
      include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(authorization_url)


def credentials_to_dict(credentials: Credentials) -> dict:
  return {
            'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes
          }


@app.route('/oauth2callback')
def oauth2callback():
    state = session['state']
    flow = Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE,
      scopes=SCOPES,
      state=state
    )
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    credentials: Credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)
    return redirect('/')


if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run('localhost', 5000, debug=True)
```

## How to Contribute

To contribute, chack out the [contribution guideline](CONTRIBUTING.md).

## License

The API uses an [MIT License](LICENSE)

## Developer

Lyle Okoth – [@lyleokoth](https://twitter.com/lyleokoth) on twitter

[lyle okoth](https://medium.com/@lyle-okoth) on medium

My email is <lyceokoth@gmail.com>

Here is my [GitHub Profile](https://github.com/twyle/)

You can also find me on [Linkedin](https://www.linkedin.com/in/lyle-okoth/)
