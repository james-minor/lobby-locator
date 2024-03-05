import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch, Mock

from src.database.connection import Connection
from src.database.create_connection import create_connection


class CreateConnectionFunctionTests(unittest.TestCase):
    """
    Test cases for the create_connection() function.
    """

    def test_file_connection_string(self) -> None:
        # Creating a temporary file.
        temp_file_handle = tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False)
        temp_file_path = temp_file_handle.name

        # Creating the connection
        connection = create_connection(temp_file_path)

        # Validating connection was created.
        if not connection:
            temp_file_handle.close()
            os.unlink(temp_file_path)
            self.fail('Connection was not created.')

        # Cleaning up the temporary file.
        connection.disconnect()
        temp_file_handle.close()
        os.unlink(temp_file_path)

    def test_in_memory_connection_string(self) -> None:
        self.assertIsNotNone(create_connection(':memory:'))

    def test_empty_connection_string(self) -> None:
        self.assertIsNotNone(create_connection(''))

    def test_mocking_sqlite_operational_error(self) -> None:
        with patch.object(Connection, '__init__', Mock(side_effect=sqlite3.OperationalError('Mocking OperationalError'))):
            self.assertIsNone(create_connection(''))

    def test_mocking_sqlite_error(self) -> None:
        with patch.object(Connection, '__init__', Mock(side_effect=sqlite3.Error('Mocking Error'))):
            self.assertIsNone(create_connection(''))
