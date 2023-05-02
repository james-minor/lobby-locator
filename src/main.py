import difflib
import os
import sys

import dotenv
import requests
import json

import sqlite3
from sqlite3 import Error

import discord
from discord import LoginFailure

from cogs.Game import Game
from cogs.Steam import Steam

from bot_logging.Logger import Logger

# Defining constants.
ROOT_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
try:
    ENVIRONMENT_TYPE = os.environ['ENVIRONMENT_TYPE']
except KeyError:
    print('No ENVIRONMENT_TYPE environment variable present, setting bot to DEVELOPMENT mode.')
    ENVIRONMENT_TYPE = 'DEVELOPMENT'

# Initializing the logger.
if ENVIRONMENT_TYPE == 'PRODUCTION':
    logger = Logger(os.path.join(ROOT_DIRECTORY, 'logs'), False)
else:
    logger = Logger(os.path.join(ROOT_DIRECTORY, 'logs'))

# Setting the bot intents and initializing the bot.
intents = discord.Intents.default()
bot = discord.Bot(intents=intents)


def validate_environment_variables() -> bool:
    environment_variables = [
        'DISCORD_TOKEN',
        'STEAM_API_KEY'
    ]

    file_valid = True
    for variable in environment_variables:
        if not os.getenv(variable):
            logger.critical(f'Environment variable not found: "{variable}".')
            file_valid = False

    return file_valid


def initialize_database_tables() -> None:
    """
    Initializes the SQL database tables if they have not been created already.
    :return: None
    """

    cursor = sql_connection.cursor()
    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS tb_steam_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_id VARCHAR(18) NOT NULL,
            steam_id VARCHAR(17)
        );
        
        CREATE TABLE IF NOT EXISTS tb_games(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            steam_id VARCHAR(10),
            game_title VARCHAR(100) NOT NULL,
            game_title_lower VARCHAR(100) NOT NULL
        );
        
        DELETE FROM tb_games
            WHERE steam_id IS NOT NULL;

        CREATE TABLE IF NOT EXISTS tb_owned_games(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_title VARCHAR(100) NOT NULL,
            discord_id VARCHAR(18) NOT NULL,
            FOREIGN KEY(game_title) REFERENCES tb_custom_games(game_title)
        );
        """
    )
    cursor.close()


def get_steam_app_data() -> None:
    """
    Gathers the name and App ID of every application on Steam.
    :return: None
    """
    response = requests.get('https://api.steampowered.com/ISteamApps/GetAppList/v0002')
    if response.status_code == 200:
        logger.info('Acquired application data from Steam!')

        # Converting the acquired JSON data to a Python dictionary.
        cursor = sql_connection.cursor()
        game_count = 0
        for app in json.loads(response.content)['applist']['apps']:
            if app['name'] == '':
                continue

            cursor.execute(
                """
                INSERT INTO tb_games(steam_id, game_title, game_title_lower)
                VALUES(?, ?, ?);
                """,
                [app['appid'], app['name'], app['name'].lower()]
            )
            game_count += 1

        cursor.close()
        logger.info(f'Inserted {game_count} game IDs into tb_steam_games...')
    else:
        logger.critical('Could not acquire application data from Steam servers, aborting bot startup...')
        sys.exit('Could not acquire application data from Steam servers')


@bot.event
async def on_ready():
    logger.info(f'{bot.user} is now online!')


class GameSelectView(discord.ui.Select):

    options = list()

    def __init__(self, context, game_titles: list):
        self.context = context
        self.options = list()
        for title in game_titles:
            self.options.append(discord.SelectOption(label=str(title)))

        super().__init__(
            placeholder='Choose a game title!',
            min_values=1,
            max_values=1,
            options=self.options
        )

    async def callback(self, interaction):
        discord_ids = get_discord_ids_for_game(self.values[0])

        # Checking to see if anyone besides the context author owns the game.
        if len(discord_ids) == 0:
            await interaction.response.send_message(f'Uh oh! It looks like nobody owns **{self.values[0]}**.', ephemeral=True)
            return
        elif len(discord_ids) == 1 and discord_ids[0] == str(interaction.user.id):
            await interaction.response.send_message(f'You are the only person who owns **{self.values[0]}**.', ephemeral=True)
            return

        # Generating a string of user pings to append to the  message.
        ping_string = ''
        for discord_id in discord_ids:
            if discord_id != str(interaction.user.id):
                ping_string += f'<@{str(discord_id)}> '
        await interaction.response.send_message(f'**{interaction.user}** is looking to play **{self.values[0]}** ' + ping_string)


@bot.slash_command(name='ping', description='Pings any users who own the specified game title')
async def ping_command(ctx, game_title: str):
    game_title_cursor = sql_connection.cursor()

    # Getting a list of every registered game name (both from steam and custom games).
    game_title_cursor.row_factory = lambda cursor, row: row[0]
    game_title_cursor.execute(
        """
        SELECT game_title_lower FROM tb_games
        """
    )
    lowercase_game_title_list = game_title_cursor.fetchall()
    game_title_cursor.close()

    # Finding the closest match to the passed game title.
    closest_matches = difflib.get_close_matches(game_title.lower(), lowercase_game_title_list, 5)
    logger.info(f'{ctx.author} searched for "{game_title}", and got {len(closest_matches)} matches.')

    # Validating that there are games in the closest_matches array.
    if len(closest_matches) == 0:
        await ctx.respond(f'Sorry, I could not find any games matching **{game_title}**.')
        return

    # If there is an exact match for the game title, ping all users who own that game.
    if game_title.lower() in closest_matches:
        # Fetching the actual game title from the database.
        actual_game_title = get_actual_game_title(game_title.lower())

        # Getting the Discord IDs for players who own the actual game title.
        discord_ids = get_discord_ids_for_game(actual_game_title)

        # Checking to see if anyone besides the context author owns the game.
        if len(discord_ids) == 0:
            await ctx.respond(f'Uh oh! It looks like nobody owns **{actual_game_title}**.')
            return
        elif len(discord_ids) == 1 and discord_ids[0] == str(ctx.author.id):
            await ctx.respond(f'It looks like you are the only person who owns **{actual_game_title}**.')
            return

        # Generating a string of user pings to append to the  message.
        ping_string = ''
        for discord_id in discord_ids:
            if discord_id != str(ctx.author.id):
                ping_string += f'<@{str(discord_id)}> '
        await ctx.respond(f'**{ctx.author}** is looking to play **{actual_game_title}** ' + ping_string)

        return

    # Getting a list of actual game titles.
    closest_matches_actual_titles = list()
    for title in closest_matches:
        closest_matches_actual_titles.append(get_actual_game_title(str(title)))

    # Creating a new GameSelectView if the game title did not have an exact match.
    select_menu = discord.ui.View(timeout=10)
    select_menu.add_item(GameSelectView(ctx, closest_matches_actual_titles))

    await ctx.respond('Please select a game to find players for:', view=select_menu, ephemeral=True)


def get_discord_ids_for_game(game_title) -> list:
    """
    Returns a list of Discord IDs who own a passed game title.
    :param game_title: The game title to gather IDs for.
    :return: A string list of Discord IDs.
    """

    type_cursor = sql_connection.cursor()

    # Seeing if the game is a custom game.
    type_cursor.execute(
        """
        SELECT COUNT(*) FROM tb_games
        WHERE game_title = ?
            AND steam_id IS NULL;
        """,
        [game_title]
    )

    # The game is a custom game, gather Discord IDs from tb_owned_custom_games.
    if type_cursor.fetchone()[0] != 0:
        game_cursor = sql_connection.cursor()
        game_cursor.row_factory = lambda cursor, row: row[0]
        game_cursor.execute(
            """
            SELECT discord_id FROM tb_owned_games
            WHERE game_title = ?;
            """,
            [game_title]
        )

        discord_ids = game_cursor.fetchall()
        type_cursor.close()
        game_cursor.close()
        return discord_ids

    # The game is a Steam game, gather data for users from tb_steam_games.
    output = list()

    # Getting the Steam game ID.
    steam_cursor = sql_connection.cursor()
    steam_cursor.execute(
        """
        SELECT steam_id FROM tb_games
        WHERE game_title = ?;
        """,
        [game_title]
    )
    steam_game_id = steam_cursor.fetchone()[0]

    # Fetching all user data from the users table.
    user_cursor = sql_connection.cursor()
    user_cursor.execute(
        """
        SELECT discord_id, steam_id FROM tb_steam_users;
        """
    )
    users = user_cursor.fetchall()

    # Seeing if the user owns the Steam game via the Steam API.
    for user in users:
        api_uri = f'https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={os.getenv("STEAM_API_KEY")}&steamid={user[1]}'
        response = requests.get(api_uri)

        if response.status_code == 200:
            user_game_ids = [str(d['appid']) for d in json.loads(response.content)['response']['games']]

            if str(steam_game_id) in user_game_ids:
                output.append(user[0])

    type_cursor.close()
    steam_cursor.close()
    user_cursor.close()
    return output


def get_actual_game_title(lowercase_game_title: str) -> str:
    """
    Gets the actual game title from a lowercase version of the game title.

    :param lowercase_game_title: The lowercase version of the game title.
    :return: The actual game title within the database.
    """

    cursor = sql_connection.cursor()
    cursor.execute(
        """
        SELECT game_title FROM tb_games
            WHERE game_title_lower = ?;
        """,
        [lowercase_game_title]
    )
    actual_game_title = cursor.fetchone()[0]
    cursor.close()

    return actual_game_title


if __name__ == '__main__':
    # Creating the logs directory, if it doesn't already exist.
    if not os.path.exists(os.path.join(ROOT_DIRECTORY, 'logs')):
        os.makedirs(os.path.join(ROOT_DIRECTORY, 'logs'))
        logger.info('Created logs directory!')

    # Creating the data directory, if it doesn't already exist.
    if not os.path.exists(os.path.join(ROOT_DIRECTORY, 'data')):
        os.makedirs(os.path.join(ROOT_DIRECTORY, 'data'))
        logger.info('Created data directory!')

    # Getting the API keys from the dotEnv file.
    if ENVIRONMENT_TYPE == 'PRODUCTION':
        environment_file_path = os.path.join(ROOT_DIRECTORY, '.env.production')
        logger.info('Attempting to load production .env file...')
    else:
        environment_file_path = os.path.join(ROOT_DIRECTORY, '.env.development')
        logger.info('Attempting to load development .env file...')

    if not dotenv.load_dotenv(environment_file_path):
        logger.critical('No .env file found! Aborting bot startup...')
        sys.exit('No .env file found')
    else:
        logger.info('Loaded .env file!')

    # Validating all environment variables exist.
    if not validate_environment_variables():
        logger.critical('Not all environment variables present! Aborting bot startup...')
        sys.exit('Not all environment variables present')
    else:
        logger.info('Environment variables validated!')

    # Attempting to connect to the SQLite database.
    sql_connection = None
    try:
        sql_connection = sqlite3.connect(os.path.join(ROOT_DIRECTORY, 'data', 'database.sqlite'))
    except Error as error:
        logger.critical('DATABASE ERROR: ' + str(error))
        logger.critical('Aborting bot startup...')
        sys.exit('Internal database error')
    logger.info('Successfully created a connection to the database!')

    # Initializing the SQLite database tables.
    initialize_database_tables()

    # Gathering the Steam application data.
    get_steam_app_data()
    sql_connection.commit()

    # Adding cogs to the bot.
    bot.add_cog(Steam(bot, sql_connection, logger))
    bot.add_cog(Game(bot, sql_connection, logger))

    # Starting the bot.
    try:
        bot.run(os.getenv('DISCORD_TOKEN'))
    except LoginFailure as error:
        logger.critical(f'Bot failed to login: "{error}".')
        sys.exit('Discord bot failed to login')
    except Error as error:
        logger.critical(f'Discord bot threw an Error while starting: "{error}".')
        sys.exit('Could not start Discord bot')
