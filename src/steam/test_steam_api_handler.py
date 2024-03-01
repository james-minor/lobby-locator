import unittest
from unittest.mock import patch

import dotenv
import requests

from steam_api_handler import SteamAPIHandler

# Fetching the Steam API key.
dotenv.load_dotenv()
steam_api_key = dotenv.dotenv_values().get('STEAM_API_KEY')
if not steam_api_key:
    print("No Steam API key found in the .env file, skipping tests.")
    quit()


class IsValidIDMethodTests(unittest.TestCase):
    """
    Test cases for the SteamAPIHandler.is_valid_id() method.
    """

    def setUp(self) -> None:
        self.steam_api = SteamAPIHandler(steam_api_key)

    def test_valid_id(self) -> None:
        is_valid = self.steam_api.is_valid_id('76561198103635351')
        self.assertTrue(is_valid)

    def test_invalid_id(self) -> None:
        is_valid = self.steam_api.is_valid_id('1')
        self.assertFalse(is_valid)

    def test_empty_id(self) -> None:
        is_valid = self.steam_api.is_valid_id('')
        self.assertFalse(is_valid)

    @patch('requests.get')
    def test_mocking_api_is_down(self, mock_requests_get) -> None:
        mock_requests_get.side_effect = requests.exceptions.ConnectionError('Mocking no connection to API.')

        is_valid = self.steam_api.is_valid_id('76561198103635351')
        self.assertFalse(is_valid)


class GetIDFromURLMethodTests(unittest.TestCase):
    """
    Test cases for the SteamAPIHandler.get_id_from_url() method.
    """

    def setUp(self) -> None:
        self.steam_api = SteamAPIHandler(steam_api_key)

    def test_vanity_url(self) -> None:
        steam_id = self.steam_api.get_id_from_url('https://steamcommunity.com/id/_M1nor')
        self.assertEqual(steam_id, '76561198103635351')

    def test_vanity_url_with_trailing_slash(self) -> None:
        steam_id = self.steam_api.get_id_from_url('https://steamcommunity.com/id/_M1nor/')
        self.assertEqual(steam_id, '76561198103635351')

    def test_vanity_url_with_no_endpoint(self) -> None:
        steam_id = self.steam_api.get_id_from_url('https://steamcommunity.com/id')
        self.assertEqual(steam_id, '')

    def test_vanity_url_with_no_endpoint_with_trailing_slash(self) -> None:
        steam_id = self.steam_api.get_id_from_url('https://steamcommunity.com/id/')
        self.assertEqual(steam_id, '')

    def test_id_url_with_missing_id(self) -> None:
        steam_id = self.steam_api.get_id_from_url('https://steamcommunity.com/profiles')
        self.assertEqual(steam_id, '')

    def test_id_url_with_missing_id_with_trailing_slash(self) -> None:
        steam_id = self.steam_api.get_id_from_url('https://steamcommunity.com/profiles/')
        self.assertEqual(steam_id, '')

    def test_url_with_id_url(self) -> None:
        steam_id = self.steam_api.get_id_from_url('https://steamcommunity.com/profiles/76561198103635351')
        self.assertEqual(steam_id, '76561198103635351')

    def test_url_with_id_url_with_trailing_slash(self) -> None:
        steam_id = self.steam_api.get_id_from_url('https://steamcommunity.com/profiles/76561198103635351/')
        self.assertEqual(steam_id, '76561198103635351')

    def test_with_id(self) -> None:
        steam_id = self.steam_api.get_id_from_url('76561198103635351')
        self.assertEqual(steam_id, '')

    def test_non_steam_url(self) -> None:
        steam_id = self.steam_api.get_id_from_url('https://www.example.com/')
        self.assertEqual(steam_id, '')

    def test_empty_url(self) -> None:
        steam_id = self.steam_api.get_id_from_url('')
        self.assertEqual(steam_id, '')


class FetchAppListMethodTests(unittest.TestCase):
    """
    Test cases for the SteamAPIHandler.fetch_app_list() method.
    """

    def setUp(self) -> None:
        self.steam_api = SteamAPIHandler(steam_api_key)

    def test_successful_fetch(self) -> None:
        app_list = self.steam_api.fetch_app_list()
        self.assertGreater(len(app_list), 0)

    @patch('requests.get')
    def test_simulating_404_error(self, mock_requests_get) -> None:
        mock_requests_get.return_value.status_code = 404

        app_list = self.steam_api.fetch_app_list()
        self.assertEqual(len(app_list), 0)

    @patch('requests.get')
    def test_mocking_api_is_down(self, mock_requests_get) -> None:
        mock_requests_get.side_effect = requests.exceptions.ConnectionError('Mocking no connection to API.')

        app_list = self.steam_api.fetch_app_list()
        self.assertEqual(len(app_list), 0)
