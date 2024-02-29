import sqlite3
from sqlite3 import Error, Connection


class DatabaseWrapper:
    """Wrapper class to assist in communicating with the SQL database."""

    connection: None | Connection
    """The connection to the SQL database."""

    def __init__(self):
        self.connection = None

    def connect(self, connection_string: str) -> bool:
        """
        Creates a connection to an SQLite database via the passed connection_string parameter.

        :param connection_string: The connection string for the database.
        :return: True if the connection was successful, False otherwise.
        """

        # Attempting to cleanly open an SQLite connection.
        try:
            self.connection = sqlite3.connect(connection_string)
        except sqlite3.Error as error:
            print(f'SQLite error while creating database connection: {error}')
            self.disconnect()  # Cleaning up active connection if error thrown.

            return False

        return True

    def disconnect(self) -> None:
        """Safely closes the SQLite database connection."""

        if self.connection:
            self.connection.commit()
            self.connection.close()
            self.connection = None

    def create_tables(self) -> bool:
        """
        Creates the tables in the database.

        :return: True if the tables were created successfully, False otherwise.
        """

        # Safeguard if a connection is not open.
        if self.connection is None:
            return False

        # Creating the SQL tables.
        cursor = self.connection.cursor()
        cursor.executescript(
            """
            -- Table to hold user data.
            CREATE TABLE IF NOT EXISTS tb_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id VARCHAR(18) NOT NULL,
                steam_id VARCHAR(17)
            );

            -- Table to hold Steam app data for every app on Steam.
            CREATE TABLE IF NOT EXISTS tb_steam_apps(
                steam_id INTEGER PRIMARY KEY,
                game_title VARCHAR(100) NOT NULL UNIQUE
            );
            
            -- Table to hold data for games owned by registered users.
            CREATE TABLE IF NOT EXISTS tb_owned_games(
                steam_id INTEGER PRIMARY KEY
            );
            """
        )
        cursor.close()

        return True

    def update_steam_apps_table(self, steam_apps: dict[int, str]) -> int:
        """
        Updates the Steam apps table.

        :param steam_apps: Dictionary of steam_apps to insert into the tb_steam_apps table.
        :return: The number of steam apps added to the database.
        """

        cursor = self.connection.cursor()

        # Getting the initial table size.
        table_start_size = cursor.execute('SELECT COUNT(steam_id) FROM tb_steam_apps').fetchone()[0]

        # Inserting new data into the steam games table.
        for app_id in steam_apps:
            cursor.execute(
                """
                INSERT OR IGNORE INTO tb_steam_apps(steam_id, game_title) 
                VALUES (?, ?)
                """,
                [
                    app_id,
                    steam_apps[app_id]
                ]
            )

        # Committing the transaction to prevent the database from locking.
        self.connection.commit()

        return cursor.execute('SELECT COUNT(steam_id) FROM tb_steam_apps').fetchone()[0] - table_start_size

