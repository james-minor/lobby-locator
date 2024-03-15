from src.controllers.controller import Controller
from src.lobby_locator import LobbyLocator


class SteamController(Controller):
    def __init__(self, bot: LobbyLocator) -> None:
        super().__init__(bot)

    def set_command(self, discord_id: str, steam_id: str):
        """
        Handles the business logic for the /steam set command.
        """

        # Checking to see if the user has an old user ID.
        with self.bot.database.connection as connection:
            old_steam_id = connection.execute(
                '''
                SELECT steam_user_id FROM tb_users 
                WHERE discord_id = ?
                ''',
                [discord_id]
            ).fetchone()

            # Dropping any user owned game entries (if the user already had a Steam ID set).
            if old_steam_id:
                self.bot.database.drop_users_owned_games(old_steam_id)

        # Updating new user data.
        self.bot.database.set_steam_user_id(discord_id, steam_id)
        self.bot.database.update_owned_games_table(self.bot.steam_api.fetch_owned_games(steam_id), steam_id)

    def remove_command(self, discord_id: str):
        """
        Handles the business logic for the /steam remove command.
        """

        self.bot.database.remove_user(discord_id)

    def refresh_command(self, discord_id: str):
        """
        Handles the business logic for the /steam refresh command.
        """

        raise NotImplementedError
