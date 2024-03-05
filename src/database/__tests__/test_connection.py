import unittest

from src.database.connection import Connection


class DisconnectMethodTests(unittest.TestCase):
    """
    Test cases for the Connection.disconnect() method.
    """

    def setUp(self) -> None:
        self.connection: Connection = Connection(':memory:')

    def test_disconnect_on_open_connection(self):
        self.assertTrue(self.connection.disconnect())

    def test_disconnect_on_closed_connection(self):
        self.connection.close()
        self.assertFalse(self.connection.disconnect())
