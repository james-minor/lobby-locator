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
        Connects to an SQL database via the passed connection_string parameter, returns True if the connection is
        successful, False otherwise.

        :param connection_string: The connection string for the database.
        """

        try:
            self.connection = sqlite3.connect(connection_string)
            return True
        except Error as error:
            print(error)

        return False

    def disconnect(self) -> None:
        """Safely closes the SQLite database connection."""

        if self.connection is not None:
            self.connection.commit()
            self.connection.close()
            self.connection = None

    def create_tables(self) -> bool:
        """
        Creates the tables in the database.

        :return: True if the tables were created successfully, False otherwise.
        """

        if self.connection is None:
            return False

        cursor = self.connection.cursor()
        cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS tb_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id VARCHAR(18) NOT NULL,
                steam_id VARCHAR(17)
            );

            CREATE TABLE IF NOT EXISTS tb_steam_games(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                steam_id INTEGER NOT NULL,
                game_title VARCHAR(100) NOT NULL,
                game_title_lower VARCHAR(100) NOT NULL,
                UNIQUE(steam_id)
            );
            """
        )
        cursor.close()

        return True

    def refresh_steam_games(self, steam_apps: dict[int, str]) -> int:
        """
        Deletes and then repopulates the steam_games database table.

        :param steam_apps: Dictionary of steam_apps to repopulate with. If passed an empty dictionary, the table
        will not be emptied, and the current state of the table will be maintained.

        :return: The number of steam games added to the database.
        """

        cursor = self.connection.cursor()

        # Getting the initial table size.
        table_start_size = cursor.execute('SELECT COUNT(id) FROM tb_steam_games').fetchone()[0]

        # Inserting new data into the steam games table.
        for app_id in steam_apps:
            cursor.execute(
                """
                INSERT OR IGNORE INTO tb_steam_games(steam_id, game_title, game_title_lower) 
                VALUES (?, ?, ?)
                """,
                [
                    app_id,
                    steam_apps[app_id],
                    steam_apps[app_id].lower()
                ]
            )

        # Committing the transaction to prevent the database from locking.
        self.connection.commit()

        return cursor.execute('SELECT COUNT(id) FROM tb_steam_games').fetchone()[0] - table_start_size
