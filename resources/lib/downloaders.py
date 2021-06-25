
# -*- coding: utf-8 -*-

import requests
import xbmc
import xbmcgui
from resources.lib.helper import ADDON, ADDON_ID, DIALOG, ERROR, INFO, log


RADARR_BASE_URL = ADDON.getSetting('radarr-base-url')
RADARR_API_KEY = ADDON.getSetting('radarr-api-key')
SONARR_BASE_URL = ADDON.getSetting('sonarr-base-url')
SONARR_API_KEY = ADDON.getSetting('sonarr-api-key')
RADARR_ICON = ADDON.getAddonInfo('path') + '\\resources\\radarr.png'
SONARR_ICON = ADDON.getAddonInfo('path') + '\\resources\\sonarr.png'

if not RADARR_BASE_URL.endswith('/'):
    RADARR_BASE_URL += '/'
if not SONARR_BASE_URL.endswith('/'):
    SONARR_BASE_URL += '/'
RADARR_HOST_URL = RADARR_BASE_URL + 'api/v3'
SONARR_HOST_URL = SONARR_BASE_URL + 'api'


RADARR_ICON = ADDON.getAddonInfo('path') + '\\resources\\radarr.png'
SONARR_ICON = ADDON.getAddonInfo('path') + '\\resources\\sonarr.png'

TMDB_API = '67cba0fa98b536f194c6a20c3b686447'
TMDB_BASE_URL = 'https://api.themoviedb.org/3'


class RadarrAPI(object):
    # Radarr API

    def __init__(self):
        """Constructor requires Host-URL and API-KEY"""
        self.host_url = RADARR_HOST_URL
        self.api_key = RADARR_API_KEY

    # ENDPOINT CALENDAR
    def get_calendar(self):
        # optional params: start (date) & end (date)
        """Gets upcoming episodes, if start/end are not supplied episodes airing today and tomorrow will be returned"""
        url = f'{self.host_url}/calendar?apikey={self.api_key}'
        res = self.request_get(url)
        return res

    # ENDPOINT DISKSPACE
    def get_diskspace(self):
        """Return Information about Diskspace"""
        url = f'{self.host_url}/diskspace?apikey={self.api_key}'
        res = self.request_get(url)
        return res

    # ENDPOINT QUEUE
    def get_queue(self):
        """Gets current downloading info"""
        url = f'{self.host_url}/queue?apikey={self.api_key}'
        res = self.request_get(url)
        return res

    # ENDPOINT PROFILE
    def get_quality_profiles(self):
        """Gets all quality profiles"""
        url = f'{self.host_url}/qualityProfile?apikey={self.api_key}'
        res = self.request_get(url)
        return res

    # ENDPOINT ROOTFOLDER
    def get_root_folder(self):
        """Returns the Root Folder"""
        url = f'{self.host_url}/rootfolder?apikey={self.api_key}'
        res = self.request_get(url)
        return res

    # ENDPOINT MOVIES
    def get_movies(self):
        """Return all movies in your collection"""
        url = f"{self.host_url}/movie?apikey={self.api_key}"
        res = self.request_get(url)
        return res

    def get_movie_by_id(self, movie_id):
        """Return the movie with the matching ID or 404 if no matching series is found"""
        url = f'{self.host_url}/movie/{movie_id}?apikey={self.api_key}'
        res = self.request_get(url)
        return res

    def add_movie(self, data):
        """Add a new movie to your collection"""
        url = f'{self.host_url}/movie?apikey={self.api_key}'
        res = self.request_post(url, data)
        title = res.get('title')
        return title

    def delete_movie(self, movie_id, rem_files=False):
        """Delete a movie from your collection"""
        data = {
            # 'id': series_id,
            'deleteFiles': 'true'
        }
        url = f'{self.host_url}/movie/{movie_id}?apikey={self.api_key}'
        res = self.request_del(url, data)
        return res

    # ENDPOINT MOVIE LOOKUP
    def lookup_movie(self, movie_id):
        """Searches for new movie on radarr"""
        url = f"{self.host_url}/movie/lookup/tmdb?tmdbId={movie_id}&apikey={self.api_key}"
        log("Lookup URL: " + str(url), ERROR)
        res = self.request_get(url)
        return res

    # ENDPOINT SYSTEM-STATUS
    def get_system_status(self):
        """Returns the System Status"""
        url = f'{self.host_url}/system/status?apikey={self.api_key}'
        res = self.request_get(url)
        return res

    # REQUESTS STUFF
    def request_get(self, url, data=None):
        """Wrapper on the requests.get"""
        if data is None:
            data = {}
        try:
            res = requests.get(url, json=data).json()
        except Exception as err:
            log(str(err), ERROR)
            DIALOG.notification('Radarr', 'Double check your Settings', RADARR_ICON, 5000)
            return None
        else:
            return res

    def request_post(self, url, data):
        """Wrapper on the requests.post"""
        try:
            res = requests.post(url, json=data).json()
        except Exception as err:
            log(str(err), ERROR)
            DIALOG.notification('Radarr', 'Double check your Settings', RADARR_ICON, 5000)
            return None
        else:
            return res

    def request_put(self, url, data):
        """Wrapper on the requests.put"""
        try:
            res = requests.put(url, json=data)
        except Exception as err:
            log(str(err), ERROR)
            DIALOG.notification('Radarr', 'Double check your Settings', RADARR_ICON, 5000)
            return None
        else:
            return res

    def request_del(self, url, data):
        """Wrapper on the requests.delete"""
        try:
            res = requests.delete(url, json=data).json()
        except Exception as err:
            log(str(err), ERROR)
            DIALOG.notification('Radarr', 'Double check your Radarr Settings', RADARR_ICON, 5000)
            return None
        else:
            return res


class SonarrAPI(object):
    # Sonarr API

    def __init__(self):
        """Constructor requires Host-URL and API-KEY"""
        self.host_url = SONARR_HOST_URL
        self.api_key = SONARR_API_KEY

    # ENDPOINT CALENDAR
    def get_calendar(self):
        # optional params: start (date) & end (date)
        """Gets upcoming episodes, if start/end are not supplied episodes airing today and tomorrow will be returned"""
        url = f'{self.host_url}/calendar?apikey={self.api_key}'
        res = self.request_get(url)
        return res

    # ENDPOINT DISKSPACE
    def get_diskspace(self):
        """Return Information about Diskspace"""
        url = f'{self.host_url}/diskspace?apikey={self.api_key}'
        res = self.request_get(url)
        return res

    # ENDPOINT QUEUE
    def get_queue(self):
        """Gets current downloading info"""
        url = f'{self.host_url}/queue?apikey={self.api_key}'
        res = self.request_get(url)
        return res

    # ENDPOINT PROFILE
    def get_quality_profiles(self):
        """Gets all quality profiles"""
        url = f'{self.host_url}/profile?apikey={self.api_key}'
        res = self.request_get(url)
        return res

    # ENDPOINT ROOTFOLDER
    def get_root_folder(self):
        """Returns the Root Folder"""
        url = f'{self.host_url}/rootfolder?apikey={self.api_key}'
        res = self.request_get(url)
        return res

    # ENDPOINT SERIES
    def get_shows(self):
        """Return all shows in your collection"""
        url = f'{self.host_url}/series?apikey={self.api_key}'
        res = self.request_get(url)
        return res

    def get_show_by_id(self, show_id):
        """Return the show with the matching ID or 404 if no matching series is found"""
        url = f'{self.host_url}/series/{show_id}?apikey={self.api_key}'
        res = self.request_get(url)
        return res

    def add_show(self, data):
        """Add a new show to your collection"""
        url = f'{self.host_url}/series?apikey={self.api_key}'
        res = self.request_post(url, data)
        title = res.get('title')
        return title

    def delete_show(self, show_id, rem_files=False):
        """Delete a series from your collection"""
        data = {
            'id': show_id,
            'deleteFiles': 'true'
        }
        url = f'{self.host_url}/series/{show_id}?apikey={self.api_key}'
        res = self.request_del(url, data)
        return res

    # ENDPOINT SHOW LOOKUP
    def lookup_show(self, series_id):
        """Searches for new show on sonarr"""
        tmdb_url = f'{TMDB_BASE_URL}/tv/{series_id}/external_ids?api_key={TMDB_API}'
        result = requests.get(tmdb_url).json()
        series_id = result['tvdb_id']
        url = f'{self.host_url}/series/lookup?term=tvdb:{series_id}&apikey={self.api_key}'
        res = self.request_get(url)[0]
        return res

    # ENDPOINT SYSTEM-STATUS
    def get_system_status(self):
        """Returns the System Status"""
        url = f'{self.host_url}/system/status?apikey={self.api_key}'
        res = self.request_get(url)
        return res

    # REQUESTS STUFF
    def request_get(self, url, data=None):
        """Wrapper on the requests.get"""
        if data is None:
            data = {}
        try:
            res = requests.get(url, json=data).json()
        except Exception as err:
            log(str(err), ERROR)
            DIALOG.notification('Sonarr', 'Double check your Settings', SONARR_ICON, 5000)
            return None
        else:
            return res

    def request_post(self, url, data):
        """Wrapper on the requests.post"""
        try:
            res = requests.post(url, json=data).json()
        except Exception as err:
            log(str(err), ERROR)
            DIALOG.notification('Sonarr', 'Double check your Settings', SONARR_ICON, 5000)
            return None
        else:
            return res

    def request_put(self, url, data):
        """Wrapper on the requests.put"""
        try:
            res = requests.put(url, json=data)
        except Exception as err:
            log(str(err), ERROR)
            DIALOG.notification('Sonarr', 'Double check your Settings', SONARR_ICON, 5000)
            return None
        else:
            return res

    def request_del(self, url, data):
        """Wrapper on the requests.delete"""
        try:
            res = requests.delete(url, json=data).json()
        except Exception as err:
            log(str(err), ERROR)
            DIALOG.notification('Sonarr', 'Double check your Settings', SONARR_ICON, 5000)
            return None
        else:
            return res


def get_default_quality(app):
    if app == 'radarr':
        app_api = RadarrAPI()
    elif app == 'sonarr':
        app_api = SonarrAPI()
    else:
        return

    default_quality = ADDON.getSetting(f'{app}-default-quality')
    data = app_api.get_quality_profiles()
    profiles = [{'name': profile['name'], 'id': str(profile['id'])} for profile in data]
    profiles_name_list = [profile['name'] for profile in profiles]
    default_quality_id = next((item['id'] for item in profiles if item['name'] == default_quality), None)
    if default_quality_id is not None:
        return default_quality_id
    else:
        selection = DIALOG.select('Choose Default Quality', profiles_name_list)
        if selection == -1:
            return None
        selected_profile_id = profiles[selection]['id']
        selected_profile_name = profiles[selection]['name']
        setting = f'{app}-default-quality'
        ADDON.setSetting(setting, selected_profile_name)
        return selected_profile_id


def get_default_folder(app):
    if app == 'radarr':
        app_api = RadarrAPI()
    elif app == 'sonarr':
        app_api = SonarrAPI()
    else:
        return
    default_folder = ADDON.getSetting(f'{app}-default-folder')
    data = app_api.get_root_folder()
    root_paths = [folder['path'] for folder in data]
    if default_folder in root_paths:
        return default_folder
    else:
        selection = DIALOG.select('Choose Default Folder:', root_paths)
        if selection == -1:
            return None
        selected_folder = root_paths[selection]
        setting = f'{app}-default-folder'
        ADDON.setSetting(setting, str(selected_folder))
        return selected_folder


def get_default_search(app):
    default_search = ADDON.getSetting(f'{app}-default-search')
    if default_search in ['false', 'False', 'no']:
        default_search = False
    if default_search in ['true', 'True', 'yes']:
        default_search = True
    return default_search
