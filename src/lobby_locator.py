import discord

from discord.ext import commands, tasks

from src.environment import EnvironmentFile
from src.database import DatabaseWrapper
from src.steam import SteamAPIHandler


class LobbyLocator(commands.Bot):
    """
    Wrapper class for the discord.ext.commands.Bot class.
    """

    def __init__(self, env_file: EnvironmentFile, database: DatabaseWrapper, steam_api: SteamAPIHandler):
        """
        Constructor for the LobbyLocator bot class.

        :param env_file: The EnvironmentFile object to attach to the bot.
        :param database: The DatabaseWrapper object to attach to the bot.
        :param steam_api: The SteamAPIHandler object to attach to the bot.
        """

        # TODO: Get proper intents, using all intents for development.
        # Initializing the Discord intents.
        intents = discord.Intents.all()

        # Initializing parent class.
        super().__init__(intents=intents)

        # Setting object values.
        self.env_file = env_file
        self.database = database
        self.steam_api = steam_api

    def load_cogs(self, cogs: [str]) -> int:
        """
        Loads cogs for the LobbyLocator bot at runtime.

        :param cogs: A list of dot-qualified import paths for each cog to load.
        :return int: Number of cogs that were successfully loaded.
        """

        loaded_cogs = 0

        for cog in cogs:
            try:
                if self.load_extension(cog, store=True):
                    print(f'Successfully loaded extension: {cog}.')
                    loaded_cogs += 1
            except discord.ExtensionNotFound:
                print(f'Extension {cog} not loaded. Reason: Could not find extension.')
            except discord.ExtensionAlreadyLoaded:
                print(f'Extension {cog} not loaded. Reason: Extension already loaded.')
            except discord.NoEntryPointError:
                print(f'Extension {cog} not loaded. Reason: Extension does not have a setup function.')
            except discord.ExtensionFailed:
                print(f'Extension {cog} not loaded. Reason: Execution error within extension.')

        return loaded_cogs

    @tasks.loop(hours=24)
    async def daily_background_tasks(self):
        """
        Function that contains tasks that should automatically run every 24 hours.
        """

        print('Running daily background tasks...')

        # Refreshing the Steam app list.
        self.database.update_steam_apps_table(self.steam_api.fetch_app_list())

    async def on_ready(self):
        """
        The on_ready event for the Discord Bot class.
        """

        # Starting background task loops.
        self.daily_background_tasks.start()

        print(f'Logged in as user {self.user}.')
