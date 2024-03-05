import json
from typing import List, Dict

import requests


class SteamAPIHandler:
    """
    Class that handles sending requests to the Steam API.
    """

    _api_root: str = 'https://api.steampowered.com'
    """
    The root for the Steam API.
    """

    def __init__(self, api_key: str):
        """
        Constructor for the SteamAPIHandler class.

        :param api_key: The Steam API key to connect to Steam with.
        """

        self._api_key = api_key
        """
        The Steam API key.
        """

    def is_valid_id(self, steam_id: str) -> bool:
        """
        Checks if a passed Steam ID is connected to an existing Steam account.

        :param steam_id: The Steam ID to validate.
        :return: True if the passed Steam ID is connected to a Steam account, False otherwise. Note that this will
        return true if passed a valid Steam profile URL that contains a valid Steam ID.
        """

        request_uri = f'{self._api_root}/ISteamUser/GetPlayerSummaries/v0002/?key={self._api_key}&steamids={steam_id}'

        # Catching ConnectionErrors (for example, if the Steam API is down for maintenance).
        try:
            response = requests.get(request_uri)
        except requests.exceptions.ConnectionError:
            return False

        # Parsing the API response.
        if response.status_code == 200:
            data = response.json()
            return len(data['response']['players']) != 0

        return False

    def get_id_from_url(self, steam_url: str) -> str:
        """
        Converts a Steam Profile URL to a Steam ID. Can accept both vanity and default steam profiles,
        for example both of the following are considered valid Steam profile URLs:

        https://steamcommunity.com/id/_M1nor

        https://steamcommunity.com/profiles/76561198103635351

        :param steam_url: The Steam profile URL to convert.
        :return: A Steam ID string, if no Steam ID could be resolved an empty string is returned.
        """

        # Trimming the trailing slash from the URL, if it exists.
        if steam_url.endswith('/'):
            trimmed_url = steam_url[:-1]
        else:
            trimmed_url = steam_url

        # If a non-custom Steam URL is set, returns the ID within the URL.
        if trimmed_url.startswith('https://steamcommunity.com/profiles/'):
            return trimmed_url.split('/')[-1]

        # If there is a custom Steam profile URL.
        if trimmed_url.startswith('https://steamcommunity.com/id/'):
            vanity_url = trimmed_url.split('/')[-1]
            request_uri = f'{self._api_root}/ISteamUser/ResolveVanityURL/v1/?key={self._api_key}&vanityurl={vanity_url}'

            # Parsing the API response.
            response = requests.get(request_uri)
            if response.status_code == 200:
                data = response.json()

                if data['response']['success'] == 1:
                    return data['response']['steamid']

        return ''

    def fetch_app_list(self) -> Dict[int, str]:
        """
        A function that fetches a list of every app from Steam.

        :return: A dictionary of the Steam app list. Keys are the Steam App ID, values are the Steam App names.
        """

        # Catching ConnectionErrors (for example, if the Steam API is down for maintenance).
        try:
            response = requests.get(f'{self._api_root}/ISteamApps/GetAppList/v0002')
        except requests.exceptions.ConnectionError:
            return {}

        # Parsing the API response.
        if response.status_code == 200:
            apps: dict[int, str] = {}

            for app in json.loads(response.content)['applist']['apps']:
                if app['name'] == '':
                    continue

                apps[int(app['appid'])] = str(app['name'])

            return apps

        return {}

    def fetch_owned_games(self, steam_id: str) -> List[int]:
        """
        A method that gets the ID of every game a Steam user owns.

        :param steam_id: The Steam ID of the user to get the owned games for.
        :return: A list of Steam application IDs.
        """

        request_uri = f'{self._api_root}/IPlayerService/GetOwnedGames/v0001/?key={self._api_key}&steamid={steam_id}'
        try:
            response = requests.get(request_uri)
        except requests.exceptions.ConnectionError:
            return []

        if response.status_code == 200:
            apps = []
            data = response.json()

            for app in data['response']['games']:
                apps.append(int(app['appid']))

            return apps

        return []
