import sqlite3
from sqlite3 import Connection


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
                discord_id VARCHAR(18) NOT NULL UNIQUE,
                steam_user_id VARCHAR(17) NOT NULL
            );

            -- Table to hold Steam app data for every app on Steam.
            CREATE TABLE IF NOT EXISTS tb_steam_apps(
                steam_app_id INTEGER PRIMARY KEY,
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

        # Safeguard if a connection is not open.
        if self.connection is None:
            return 0

        cursor = self.connection.cursor()

        # Getting the initial table size.
        table_start_size = cursor.execute('SELECT COUNT(steam_app_id) FROM tb_steam_apps').fetchone()[0]

        # Inserting new data into the steam games table.
        for app_id in steam_apps:
            cursor.execute(
                """
                INSERT OR IGNORE INTO tb_steam_apps(steam_app_id, game_title) 
                VALUES (?, ?)
                """,
                [
                    app_id,
                    steam_apps[app_id]
                ]
            )

        # Committing the transaction to prevent the database from locking.
        self.connection.commit()

        return cursor.execute('SELECT COUNT(steam_app_id) FROM tb_steam_apps').fetchone()[0] - table_start_size

    def set_steam_user_id(self, discord_id: str, steam_user_id: str) -> None:
        """
        Associates a user's Discord ID with a passed Steam ID.

        :param discord_id: The Discord ID to set the Steam ID of.
        :param steam_user_id: The Steam 64 ID to associate with the Discord ID.
        :raises ValueError: If either discord_id or steam_id are empty strings.
        """

        # Validating parameters.
        if discord_id == '':
            raise ValueError('Parameter discord_id cannot be empty string.')
        if steam_user_id == '':
            raise ValueError('Parameter steam_id cannot be empty string.')

        # Upserting the entry into the database.
        cursor = self.connection.cursor()
        cursor.execute(
            '''
            INSERT INTO tb_users (discord_id, steam_user_id)
            VALUES (?, ?)
            ON CONFLICT (discord_id)
            DO UPDATE SET steam_user_id = excluded.steam_user_id
            ''',
            [discord_id, steam_user_id]
        )

        # Committing and closing cursor.
        self.connection.commit()
        cursor.close()
