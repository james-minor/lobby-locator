import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from .database_wrapper import DatabaseWrapper


class ConnectMethodTests(unittest.TestCase):
    """
    Test cases for the DatabaseWrapper.connect() method.
    """

    def setUp(self) -> None:
        self.database = DatabaseWrapper()

    def test_valid_connection_string(self) -> None:
        # Creating a temporary file.
        temp_file_handle = tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False)
        temp_file_path = temp_file_handle.name

        # Validating the connection.
        connected = self.database.connect(temp_file_path)
        self.assertTrue(connected)

        # Cleaning up the temporary file.
        self.database.disconnect()
        temp_file_handle.close()
        os.unlink(temp_file_path)

    def test_empty_connection_string(self) -> None:
        connected = self.database.connect('')

        self.assertTrue(connected)

    @patch('sqlite3.connect')
    def test_mocking_sqlite_error(self, mock_sqlite_connect) -> None:
        mock_sqlite_connect.side_effect = sqlite3.Error('Mocking an SQLite error.')

        with tempfile.TemporaryFile(suffix='.sqlite') as temp_db_file:
            connected = self.database.connect(temp_db_file.name)

        self.assertFalse(connected)


class DisconnectMethodTests(unittest.TestCase):
    """
    Test cases for the DatabaseWrapper.disconnect() method.
    """

    def setUp(self) -> None:
        self.database = DatabaseWrapper()

    def test_disconnect_with_open_connection(self) -> None:
        self.database.connect(':memory:')

        try:
            self.database.disconnect()
        except sqlite3.Error as error:
            self.fail(f'Threw an SQLite exception: {error}')

    def test_disconnect_with_closed_connection(self) -> None:
        try:
            self.database.disconnect()
        except sqlite3.Error as error:
            self.fail(f'Threw an SQLite exception: {error}')


class CreateTablesMethodTests(unittest.TestCase):
    """
    Test cases for the DatabaseWrapper.create_tables() method.
    """

    def setUp(self) -> None:
        self.database = DatabaseWrapper()
        self.database.connect('')

    def test_creating_tables(self) -> None:
        try:
            self.database.create_tables()
        except sqlite3.Error as error:
            self.fail(f'Threw an SQLite exception: {error}')

    def test_calling_with_closed_connection(self) -> None:
        self.database.disconnect()

        try:
            self.database.create_tables()
        except sqlite3.Error as error:
            self.fail(f'Threw an SQLite exception: {error}')


class UpdateSteamAppsTableMethodTests(unittest.TestCase):
    """
    Test cases for the DatabaseWrapper.update_steam_apps_table() method.
    """

    def setUp(self) -> None:
        self.database = DatabaseWrapper()
        self.database.connect('')
        self.database.create_tables()

    def test_valid_dictionary(self) -> None:
        row_count = self.database.update_steam_apps_table({1: 'app_1', 2: 'app_2', 3: 'app_3'})
        self.assertEqual(row_count, 3)

    def test_empty_dictionary(self) -> None:
        row_count = self.database.update_steam_apps_table({})
        self.assertEqual(row_count, 0)

    def test_multiple_insertions_of_same_key(self) -> None:
        self.database.update_steam_apps_table({1: 'app_1'})
        row_count = self.database.update_steam_apps_table({1: 'app_1'})
        self.assertEqual(row_count, 0)

    def test_calling_with_closed_connection(self) -> None:
        self.database.disconnect()
        row_count = self.database.update_steam_apps_table({1: 'app_1'})
        self.assertEqual(row_count, 0)


class SetSteamIDMethodTests(unittest.TestCase):
    """
    Test cases for the DatabaseWrapper.set_steam_user_id() method.
    """

    def setUp(self) -> None:
        self.database = DatabaseWrapper()
        self.database.connect('')
        self.database.create_tables()

    def test_inserting_steam_id(self) -> None:
        self.database.set_steam_user_id('1', '1')

        row_count = self.database.connection.execute('SELECT COUNT(id) FROM tb_users').fetchone()[0]
        self.assertEqual(row_count, 1)

    def test_multiple_inserts(self) -> None:
        self.database.set_steam_user_id('1', '1')
        self.database.set_steam_user_id('2', '1')
        self.database.set_steam_user_id('3', '2')

        row_count = self.database.connection.execute('SELECT COUNT(id) FROM tb_users').fetchone()[0]
        self.assertEqual(row_count, 3)

    def test_updating_steam_id(self) -> None:
        self.database.set_steam_user_id('1', '1')
        self.database.set_steam_user_id('1', '2')

        row_count = self.database.connection.execute('SELECT COUNT(id) FROM tb_users').fetchone()[0]
        self.assertEqual(row_count, 1)

    def test_inserting_empty_steam_id(self) -> None:
        with self.assertRaises(ValueError):
            self.database.set_steam_user_id('1', '')

    def test_inserting_steam_id_empty_discord_id(self) -> None:
        with self.assertRaises(ValueError):
            self.database.set_steam_user_id('', '1')

    def test_both_ids_empty(self) -> None:
        with self.assertRaises(ValueError):
            self.database.set_steam_user_id('', '')

    def tearDown(self) -> None:
        self.database.disconnect()
