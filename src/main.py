import os

from environment import EnvironmentFile
from database import DatabaseWrapper
from src.database import create_connection
from src.lobby_locator import LobbyLocator

from steam import SteamAPIHandler


def main():

    # Validating the environment variables.
    env_file = EnvironmentFile(['DISCORD_BOT_TOKEN', 'STEAM_API_KEY', 'DB_CONNECTION_STRING'])
    if not env_file.is_valid():
        print('The .env file failed validation, aborting bot startup...')
        quit()

    # Attempting to connect to the SQL database.
    with create_connection(env_file.environment_variables.get('DB_CONNECTION_STRING')) as connection:
        if not connection:
            print('Encountered an error while attempting to connect to the SQL database, aborting bot startup...')
            quit()

        database = DatabaseWrapper(connection)

    # Creating the database tables.
    if database.create_tables():
        print('Successfully created database tables.')
    else:
        print('Could not create the database tables, aborting bot startup...')
        quit()

    # Creating the database triggers.
    if database.create_triggers():
        print('Successfully created database triggers.')
    else:
        print('Could not create the database triggers, aborting bot startup...')
        quit()

    # Instantiating Steam API Handler.
    steam_api = SteamAPIHandler(env_file.environment_variables.get('STEAM_API_KEY'))

    # Populating the games table.
    steam_apps = steam_api.fetch_app_list()
    if len(steam_apps) > 0:
        print(f'Fetched {len(steam_apps)} app(s) from Steam.')
    else:
        print('Could not obtain the app list. Steam API may be down for maintenance, try again in a few minutes.')

    print(f'Inserted {database.update_steam_apps_table(steam_apps)} new app(s) into the database.')

    # Getting the cog import paths.
    cogs: [str] = []
    for file in os.listdir('./cogs'):
        if file.endswith('.py'):
            cogs.append(f'cogs.{file.split(".py")[0]}')

    # Initializing and starting the bot.
    bot = LobbyLocator(env_file, database, steam_api)
    bot.load_cogs(cogs)
    bot.run(env_file.environment_variables.get('DISCORD_BOT_TOKEN'))


# Import guard.
if __name__ == '__main__':
    main()
