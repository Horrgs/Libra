from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import AuthorizedSession
import json
import logging
from google.oauth2.credentials import Credentials
from libra import Settings
import random
from pathlib2 import Path


class Album:
    album_json = None
    media_items_json = None
    session = None

    """
    session - Authorized Session object for Google.
    album_name - str. Name of album to get.
    page_tokens - dict. Default to None, one key is 'album', one is 'media_items'. 
    """
    def __init__(self, session, album_title):
        self.session = session

        def get_album_id(page_token=None):
            params = {
                'pageSize': 50
            }
            if not isinstance(page_token, type(None)):
                params['pageToken'] = page_token

            while True:
                albums_list = session.get('https://photoslibrary.googleapis.com/v1/albums', params=params).json()
                if 'albums' in albums_list:
                    for album in albums_list['albums']:
                        if 'title' in album and 'id' in album:
                            if str(album['title']).lower() == str(album_title).lower():
                                self.album_json = album
                                return album['id']
                    if 'nextPageToken' in albums_list:
                        get_album_id(albums_list['nextPageToken'])
                    else:
                        pass
                        #album not found.
                else:
                    pass  #404

        def get_media_items(album_id, page_token=None, response=None):
            if isinstance(response, type(None)):
                response = []
            params = {
                'pageSize': 100,
                'albumId': album_id
            }
            if not isinstance(page_token, type(None)):
                params['pageToken'] = page_token

            while True:
                media_items = session.post('https://photoslibrary.googleapis.com/v1/mediaItems:search', params=params) \
                    .json()
                if 'mediaItems' in media_items:
                    for media_item in media_items['mediaItems']:
                        response.append(media_item)
                    if 'nextPageToken' in media_items:
                        get_media_items(album_id, media_items['nextPageToken'], response)
                    else:
                        return response
                else:
                    return response
                return response

        album_id_ = get_album_id()
        self.media_items_json = get_media_items(album_id_)

    def get_media_items(self):
        return self.media_items_json

    def get_album_json(self):
        return self.album_json

    def get_album_title(self):
        album = self.get_album_json()
        if not isinstance(album, type(None)):
            if 'title' in album:
                return album['title']


class PhotoConnect:
    settings_ref = None

    def __init__(self):
        self.settings_ref = Settings()

    @staticmethod
    def auth(scopes):
        path = Path.home()
        flow = InstalledAppFlow.from_client_secrets_file(
            '%s/Documents/Libra/client_secret.json' % path,
            scopes=scopes)
        credentials = flow.run_local_server(host='localhost',
                                            port=8080,
                                            authorization_prompt_message="",
                                            success_message='The auth flow is complete; you may close this window.',
                                            open_browser=True)

        return credentials

    @staticmethod
    def save_credentials(credentials, auth_file):
        credentials_dict = {
            'refresh_token': credentials.refresh_token,
            'token': credentials.token,
            'id_token': credentials.id_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'scopes': credentials.scopes,
            'client_secret': credentials.client_secret
        }

        with open(auth_file, 'w') as f:
            print(json.dumps(credentials_dict), file=f)

    def get_authorized_session(self):
        auth_token_file = Path("%s/Documents/Libra/oauth_session.json" % Path.home())
        scopes = ['https://www.googleapis.com/auth/photoslibrary',
                  'https://www.googleapis.com/auth/photoslibrary.readonly']
        cred = None
        if auth_token_file:
            try:
                cred = Credentials.from_authorized_user_file(auth_token_file, scopes)
            except OSError as err:
                logging.debug("Error opening auth token file - {0}".format(err))
            except ValueError:
                logging.debug("Error loading auth tokens - Incorrect format")

        if not cred:
            cred = self.auth(scopes)
        session = AuthorizedSession(cred)
        if auth_token_file:
            try:
                self.save_credentials(cred, auth_token_file)
            except OSError as err:
                logging.debug("Could not save auth tokens - {0}".format(err))
        return session

    #NOT to be confused w/ Libra/__init__.py#setup.
    # This actually deals with the JSON contents, and not the existence itself.
    def cache_photos(self, session, album_title, page_token=None):
        new_cache = []
        if self.settings_ref.has_internet():
            album = Album(session, album_title)
            media_items = album.get_media_items()
            lim = 100 if len(media_items) > 100 else len(media_items)
            for i in range(0, lim):
                new_cache.append(media_items[i])
                i += 1
            self.settings_ref.write_cache_from_objs(new_cache)
        else:
            raise SystemError("No internet connection available for caching.")
