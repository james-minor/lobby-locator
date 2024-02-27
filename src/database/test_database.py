import os
import unittest

from database_wrapper import DatabaseWrapper


class ConnectionTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.database = DatabaseWrapper()

    def test_opening_connection(self):
        self.assertTrue(self.database.connect('test.sqlite'))

    def test_closing_connection(self):
        self.database.connect('test.sqlite')
        self.database.disconnect()
        self.assertIsNone(self.database.connection)

    def tearDown(self):
        self.database.disconnect()

    @classmethod
    def tearDownClass(cls):
        os.remove('test.sqlite')


class CreateTablesTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.database = DatabaseWrapper()

    def test_bad_connection(self):
        self.assertFalse(self.database.create_tables())

    def test_all_tables_created(self):
        self.database.connect('test.sqlite')
        self.assertTrue(self.database.create_tables())

    def tearDown(self):
        self.database.disconnect()

    @classmethod
    def tearDownClass(cls):
        os.remove('test.sqlite')


class RefreshingSteamGamesTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.database = DatabaseWrapper()
        self.database.connect('test.sqlite')
        self.database.create_tables()

    def test_empty_games_dictionary(self):
        self.database.refresh_steam_games({0: 'test 1', 1: 'test 2', 2: 'test 3'})
        self.assertEqual(self.database.refresh_steam_games({}), 0)

    def test_all_games_refreshed(self):
        self.assertEqual(self.database.refresh_steam_games({0: 'test 1', 1: 'test 2', 2: 'test 3'}), 3)

    def tearDown(self):
        self.database.disconnect()

    @classmethod
    def tearDownClass(cls):
        os.remove('test.sqlite')
