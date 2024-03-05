import unittest

from src.database.connection import Connection


class CloseMethodTests(unittest.TestCase):
    """
    Test cases for the Connection.disconnect() method.
    """

    def setUp(self) -> None:
        self.connection: Connection = Connection(':memory:')

    def test_close_on_open_connection(self):
        self.assertTrue(self.connection.close())

    def test_close_on_closed_connection(self):
        self.connection.close()
        self.assertFalse(self.connection.close())


class IsOpenMethodTests(unittest.TestCase):
    """
    Test cases for the Connection.is_open() method.
    """

    def setUp(self) -> None:
        self.connection: Connection = Connection(':memory:')

    def test_after_initialization(self) -> None:
        self.assertTrue(self.connection.is_open())

    def test_after_close(self) -> None:
        self.connection.close()
        self.assertFalse(self.connection.is_open())
