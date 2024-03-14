import sqlite3
from typing import List

from .connection import Connection


class DatabaseWrapper:
    """Wrapper class to assist in communicating with the SQL database."""

    def __init__(self, connection: Connection):
        """
        Initializes the DatabaseWrapper class.

        :param connection: The connection to the SQLite database.
        """

        self.connection: Connection = connection

    def _get_table_rows(self, table: str) -> int:
        """
        Gets the amount of rows in a database table. Note that due to how the table string needs to be concatenated in
        the statement string, this method is vulnerable to SQLite injection, use with caution.

        :param table: The table to get the rowcount of.
        :return: The amount of rows in the table.
        """

        if not self.connection.is_open():
            return 0

        with self.connection:
            try:
                return self.connection.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
            except sqlite3.Error:
                return 0

    def create_tables(self) -> bool:
        """
        Creates the tables in the database.

        :return: True if the tables were created successfully, False otherwise.
        """

        # Safeguard if the connection is not open.
        if not self.connection.is_open():
            return False

        # Creating the SQL tables.
        with self.connection:
            self.connection.executescript(
                """
                -- Table to hold user data.
                CREATE TABLE IF NOT EXISTS tb_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    discord_id VARCHAR(18) NOT NULL UNIQUE,
                    steam_user_id VARCHAR(17) NOT NULL UNIQUE
                );
    
                -- Table to hold Steam app data for every app on Steam.
                CREATE TABLE IF NOT EXISTS tb_steam_apps(
                    steam_app_id INTEGER PRIMARY KEY,
                    game_title VARCHAR(100) NOT NULL UNIQUE
                );
                
                -- Table to hold data for games owned by registered users.
                CREATE TABLE IF NOT EXISTS tb_owned_games(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    steam_app_id INTEGER NOT NULL,
                    steam_user_id VARCHAR(17) NOT NULL,
                    FOREIGN KEY (steam_app_id) REFERENCES tb_steam_apps(steam_app_id),
                    FOREIGN KEY (steam_user_id) REFERENCES tb_users(steam_user_id)
                );
                
                -- Table to hold autocomplete data for games owned by registered users.
                CREATE TABLE IF NOT EXISTS tb_games_autocomplete(
                    steam_app_id INTEGER PRIMARY KEY,
                    game_title VARCHAR(100) NOT NULL UNIQUE,
                    FOREIGN KEY (steam_app_id) REFERENCES tb_steam_apps(steam_app_id),
                    FOREIGN KEY (game_title) REFERENCES tb_steam_apps(game_title)
                );
                """
            )

        return True

    def create_triggers(self) -> bool:
        """
        Creates triggers for the database.

        :return: True if the triggers were created successfully, False otherwise.
        """

        # Safeguard if the connection is not open.
        if not self.connection.is_open():
            return False

        # Creating the SQL triggers.
        with self.connection:
            self.connection.executescript(
                """
                -- Trigger to add games to the autocomplete table when owned games are added.
                CREATE TRIGGER IF NOT EXISTS tr_add_games_autocomplete 
                AFTER INSERT ON tb_owned_games
                BEGIN
                    INSERT OR IGNORE INTO tb_games_autocomplete (steam_app_id, game_title)
                    SELECT NEW.steam_app_id, game_title
                    FROM tb_steam_apps
                    WHERE tb_steam_apps.steam_app_id = NEW.steam_app_id;
                END;

                -- Trigger to remove games in the autocomplete table when owned games are deleted.
                CREATE TRIGGER IF NOT EXISTS tr_remove_games_autocomplete
                AFTER DELETE ON tb_owned_games
                BEGIN
                    DELETE FROM tb_games_autocomplete
                    WHERE steam_app_id = OLD.steam_app_id
                    AND NOT EXISTS (
                        SELECT 1 FROM tb_owned_games
                        WHERE steam_app_id = OLD.steam_app_id
                    );
                END;
                """
            )

        return True

    def update_steam_apps_table(self, steam_apps: dict[int, str]) -> int:
        """
        Updates the Steam apps table.

        :param steam_apps: Dictionary of steam_apps to insert into the tb_steam_apps table.
        :return: The number of steam apps added to the database.
        """

        # Safeguard if the connection is not open.
        if not self.connection.is_open():
            return False

        with self.connection:

            # Getting the initial table size.
            table_start_size = self._get_table_rows('tb_steam_apps')

            # Inserting new data into the steam games table.
            self.connection.executemany(
                '''
                    INSERT OR IGNORE INTO tb_steam_apps(steam_app_id, game_title) 
                    VALUES (?, ?)
                ''',
                zip(steam_apps.keys(), steam_apps.values())
            )

            # Committing the transaction to prevent the database from locking.
            self.connection.commit()

            return self._get_table_rows('tb_steam_apps') - table_start_size

    def set_steam_user_id(self, discord_id: str, steam_user_id: str) -> bool:
        """
        Associates a user's Discord ID with a passed Steam ID.

        :param discord_id: The Discord ID to set the Steam ID of.
        :param steam_user_id: The Steam 64 ID to associate with the Discord ID.
        :raises ValueError: If either discord_id or steam_id are empty strings.
        :return: True if the Steam ID was set successfully, False otherwise.
        """

        # Validating parameters.
        if discord_id == '':
            raise ValueError('Parameter discord_id cannot be empty string.')
        if steam_user_id == '':
            raise ValueError('Parameter steam_id cannot be empty string.')

        with self.connection:
            try:
                self.connection.execute(
                    '''
                    INSERT INTO tb_users (discord_id, steam_user_id)
                    VALUES (?, ?)
                    ON CONFLICT (discord_id)
                    DO UPDATE SET steam_user_id = excluded.steam_user_id
                    ''',
                    [discord_id, steam_user_id]
                )
            except sqlite3.IntegrityError:
                return False

        return True

    def update_owned_games_table(self, steam_apps: List[int], steam_user_id: str) -> int:
        """
        Inserts a users owned games into the owned games table.

        :param steam_apps: A list of Steam application IDs to insert into the table.
        :param steam_user_id: The Steam ID of the user who owns the games in the steam_apps list.
        :return: The number of games inserted into the owned games table.
        """

        with self.connection:

            # Getting the initial table size.
            table_start_size = self._get_table_rows('tb_owned_games')

            # Inserting the steam app data into the table.
            for steam_app_id in steam_apps:
                self.connection.execute(
                    '''
                        INSERT OR IGNORE INTO tb_owned_games (steam_app_id, steam_user_id) 
                        VALUES (?, ?)
                    ''',
                    [
                        steam_app_id,
                        steam_user_id
                    ]
                )

            return self._get_table_rows('tb_owned_games') - table_start_size


