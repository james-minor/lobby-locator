import sqlite3

from src.database.connection import Connection


def create_connection(connection_string: str) -> Connection | None:
    """
    Attempts to safely create a connection to an SQLite database via the passed connection_string parameter.

    :param connection_string: The connection string for the database.
    :return: The Connection object if the connection to the database is successful, returns None otherwise.
    """

    # Attempting to cleanly open an SQLite connection.
    try:
        connection = Connection(connection_string)
        return connection
    except sqlite3.OperationalError as error:
        print(f'SQLite error while creating database connection: {error}')
    except sqlite3.Error as error:
        print(f'SQLite error while creating database connection: {error}')

    return None
