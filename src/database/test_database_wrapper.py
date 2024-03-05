import sqlite3
import unittest

from src.database.create_connection import create_connection
from .database_wrapper import DatabaseWrapper


class CreateTablesMethodTests(unittest.TestCase):
    """
    Test cases for the DatabaseWrapper.create_tables() method.
    """

    def setUp(self) -> None:
        self.database = DatabaseWrapper(create_connection(':memory:'))

    def test_calling_with_open_connection(self) -> None:
        try:
            self.database.create_tables()
        except sqlite3.Error as error:
            self.fail(f'Threw an SQLite exception: {error}')

    def test_calling_with_closed_connection(self) -> None:
        self.database.connection.close()

        try:
            self.database.create_tables()
        except sqlite3.Error as error:
            self.fail(f'Threw an SQLite exception: {error}')


class UpdateSteamAppsTableMethodTests(unittest.TestCase):
    """
    Test cases for the DatabaseWrapper.update_steam_apps_table() method.
    """

    def setUp(self) -> None:
        self.database = DatabaseWrapper(create_connection(':memory:'))
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
        self.database.connection.close()
        row_count = self.database.update_steam_apps_table({1: 'app_1'})
        self.assertEqual(row_count, 0)


class SetSteamIDMethodTests(unittest.TestCase):
    """
    Test cases for the DatabaseWrapper.set_steam_user_id() method.
    """

    def setUp(self) -> None:
        self.database = DatabaseWrapper(create_connection(':memory:'))
        self.database.create_tables()

    def test_inserting_steam_id(self) -> None:
        self.database.set_steam_user_id('1', '1')

        row_count = self.database.connection.execute('SELECT COUNT(id) FROM tb_users').fetchone()[0]
        self.assertEqual(row_count, 1)

    def test_multiple_inserts(self) -> None:
        self.database.set_steam_user_id('1', '1')
        self.database.set_steam_user_id('2', '2')
        self.database.set_steam_user_id('3', '3')

        row_count = self.database.connection.execute('SELECT COUNT(id) FROM tb_users').fetchone()[0]
        self.assertEqual(row_count, 3)

    def test_updating_steam_id(self) -> None:
        self.database.set_steam_user_id('1', '1')
        self.database.set_steam_user_id('1', '2')

        row_count = self.database.connection.execute('SELECT COUNT(id) FROM tb_users').fetchone()[0]
        self.assertEqual(row_count, 1)

    def test_setting_existing_steam_id(self):
        self.assertTrue(self.database.set_steam_user_id('1', '1'))
        self.assertFalse(self.database.set_steam_user_id('2', '1'))

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
