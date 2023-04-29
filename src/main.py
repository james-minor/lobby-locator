import difflib
import os

import dotenv
import requests
import json

import sqlite3
from sqlite3 import Error, Cursor

import discord
from discord.ext import commands


# Attempting to connect to the SQLite database.
sql_connection = None
try:
    sql_connection = sqlite3.connect(r'C:\Programming\game_seeker_discord_bot\data\database.sqlite')
except Error as error:
    print('DATABASE ERROR: ' + str(error))
    print('Aborting bot startup...')
    quit()
print('Successfully created a connection to the database!')


def create_database_tables() -> None:
    """
    Initializes the SQL database tables if they have not been created already.
    :return: None
    """

    cursor = sql_connection.cursor()
    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS tb_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_tag VARCHAR(100) NOT NULL,
            discord_id VARCHAR(18) NOT NULL,
            steam_id VARCHAR(17)
        );
        
        DROP TABLE IF EXISTS tb_steam_games;
        CREATE TABLE IF NOT EXISTS tb_steam_games(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            steam_id VARCHAR(10),
            game_title VARCHAR(100)
        );
        
        CREATE TABLE IF NOT EXISTS tb_custom_games(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_title VARCHAR(100),
            UNIQUE(game_title)
        );
        
        CREATE TABLE IF NOT EXISTS tb_owned_custom_games(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_title VARCHAR(100) NOT NULL,
            discord_id VARCHAR(18) NOT NULL,
            FOREIGN KEY(game_title) REFERENCES tb_custom_games(game_title),
            FOREIGN KEY(discord_id) REFERENCES tb_users(discord_id)
        );
        """
    )
    cursor.close()


# Initializing the SQLite database tables.
create_database_tables()


def get_steam_app_data() -> None:
    """
    Gathers the name and App ID of every application on Steam.

    :param cursor: The SQL database cursor to use to add to the database.
    :return: None
    """
    response = requests.get('https://api.steampowered.com/ISteamApps/GetAppList/v0002')
    if response.status_code == 200:
        print('Acquired application data from Steam!')

        # Converting the acquired JSON data to a Python dictionary.
        cursor = sql_connection.cursor()
        for app in json.loads(response.content)['applist']['apps']:
            cursor.execute(
                """
                INSERT INTO tb_steam_games(steam_id, game_title)
                VALUES(?, ?);
                """,
                [app['appid'], app['name']]
            )

        cursor.execute("SELECT COUNT(*) FROM tb_steam_games;")
        print(f'Inserted {cursor.fetchone()[0]} game IDs into tb_steam_games...')
        cursor.close()
    else:
        print('Could not acquire application data from Steam servers, aborting bot startup...')
        quit()


# Gathering the Steam application data.
get_steam_app_data()
sql_connection.commit()

# Getting the API keys from the dotEnv file.
dotenv.load_dotenv()

# Setting the bot intents and initializing the bot.
intents = discord.Intents.all()  # TODO: enable proper intents, we dont need all of them (helps with development)
bot = discord.Bot(intents=intents)


@bot.event
async def on_ready():
    print(f'{bot.user} is now online!')


@bot.slash_command(name='set', description='Sets your saved Steam ID')
async def set_id_command(ctx, steam_id: str):
    await ctx.respond(f'Setting Steam ID: **{steam_id}**, for user: **{ctx.author}**')

    # Seeing if an entry for this user already exists, if so UPDATE instead of INSERTING data.
    cursor = sql_connection.cursor()
    cursor.execute(
        """
        SELECT COUNT(*) FROM tb_users
        WHERE discord_id = ?
        """,
        [ctx.author.id]
    )
    if cursor.fetchone()[0] == 0:
        print(f'Inserting Steam ID data for user: {ctx.author}...')
        cursor.execute(
            """
            INSERT INTO tb_users(discord_tag, discord_id, steam_id)
            VALUES(?, ?, ?);
            """,
            [str(ctx.author), str(ctx.author.id), str(steam_id)]
        )
    else:
        print(f'Updating Steam ID data for user: {ctx.author}...')
        cursor.execute(
            """
            UPDATE tb_users
            SET discord_tag = ?, steam_id = ?
            WHERE discord_id = ?;
            """,
            [str(ctx.author), str(steam_id), str(ctx.author.id)]
        )

    cursor.close()
    sql_connection.commit()


@bot.slash_command(name='remove', description='Removes your saved Steam ID')
async def remove_id_command(ctx):
    await ctx.respond(f'Removing Steam ID for **{ctx.author}**.')
    print(f'Removing Steam ID for {ctx.author}')

    cursor = sql_connection.cursor()
    cursor.execute(
        """
        DELETE FROM tb_users
        WHERE discord_id = ?;
        """,
        [ctx.author.id]
    )

    cursor.close()
    sql_connection.commit()


class GameSelectView(discord.ui.Select):
    def __init__(self, game_titles):
        options = list()
        for title in game_titles:
            options.append(discord.SelectOption(label=str(title)))

        super().__init__(
            placeholder='Choose a game title!',
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction):
        await interaction.response.send_message(f'Attempting to ping users who own **{self.values[0]}**...')
        # TODO: ping users who own the game


@bot.slash_command(name='add_custom_game', description="Adds a custom game to the games database.")
@commands.has_permissions(administrator=True)
async def add_custom_game_command(ctx, game_title: str):
    await ctx.respond(f'Adding custom game **{game_title}**.')
    # TODO: implement behavior


@bot.slash_command(name='remove_custom_game', description="Removes a custom game from the games database.")
@commands.has_permissions(administrator=True)
async def remove_custom_game_command(ctx, game_title: str):
    await ctx.respond(f'Removing custom game **{game_title}**.')
    # TODO: implement behavior


@bot.slash_command(name="register_custom_game_for_me", description="Registers a custom game as connected to your account.")
async def register_custom_game_command(ctx, game_title: str):
    await ctx.respond(f'Registering custom game **{game_title}** for **{ctx.author}**.')
    # TODO: implement behavior


@bot.slash_command(name="remove_custom_game_for_me", description="Unregisters a custom game as connected to your account.")
async def register_custom_game_command(ctx, game_title: str):
    await ctx.respond(f'Unregistering custom game **{game_title}** for **{ctx.author}**.')
    # TODO: implement behavior


@bot.slash_command(name='ping', description='Pings any users who own a game')
async def ping_command(ctx, game_title: str):
    game_title_cursor = sql_connection.cursor()

    # Getting a list of every registered game name (both from steam and custom games).
    game_title_cursor.execute(
        """
        SELECT game_title FROM tb_steam_games
        UNION ALL
        SELECT game_title FROM tb_custom_games;
        """
    )
    game_title_list = game_title_cursor.fetchall()

    # Finding the closest match to the passed game title.
    closest_matches = difflib.get_close_matches(game_title, game_title_list, 5)
    print(f'{ctx.author} searched for "{game_title}", and got {len(closest_matches)} matches.')

    # Validating that there are games in the closest_matches array.
    if len(closest_matches) == 0:
        await ctx.respond(f'Sorry, I could not find any games matching **{game_title}**.')
        return

#     # TODO: implement SQLite behavior.
#     return  # TODO: remove line and code below.
#
#     # If there is an exact match for the game title, ping all users who own that game.
#     if game_title in closest_matches:
#         # Getting the users that own the selected game.
#         valid_users = get_users_who_own_game(get_game_id(game_title))
#         if len(valid_users) == 0:
#             await ctx.send(f'Uh oh! It looks like no one with a set Steam ID owns **{game_title}**.')
#             return
#
#         # Generating the string of user pings for valid users.
#         user_pings = ''
#         for user_id in valid_users:
#             if user_id != ctx.author.id:
#                 user_pings += '<@' + str(user_id) + '> '
#         if user_pings == '':
#             await ctx.send(f'Uh oh! It looks like no one with a set Steam ID owns **{game_title}**, besides you!')
#             return
#
#         await ctx.send(f'**{ctx.author}** is seeking players for **{game_title}** {user_pings}')
#         return
#
#     # Creating a new GameSelectView if the game_title did not have an exact match.
#     view = discord.ui.View(timeout=10)
#     view.add_item(GameSelectView(closest_matches))
#
#     await ctx.send('Please select a game to find players for:', view=view)
#
#
# # Returns the Steam ID for the passed game title. If the game title could not be found returns 0.
# def get_game_id(game_title: str):
#     for game_id in steam_app_data:
#         if steam_app_data[game_id] == game_title:
#             return game_id
#     return 0
#
#
# # Returns a list of user Discord tags if their steam account owns the passed Steam game ID.
# def get_users_who_own_game(game_id: str):
#     valid_users = list()
#
#     # Getting the user data from accounts.json
#     user_accounts = None
#     file_path = os.path.join(os.getcwd(), '../accounts.json')
#     if os.path.exists(file_path):
#         with open(file_path, 'r') as user_data_file:
#             user_accounts = json.load(user_data_file)['accounts']
#     else:
#         print('File could not be found: ' + file_path)
#
#     # Contacting the Steam Web API to see if each user owns the passed game ID.
#     for user in user_accounts:
#         steam_id = user['steam_id']
#         api_uri = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={os.getenv("STEAM_API_KEY")}&steamid={steam_id}'
#         response = requests.get(api_uri)
#         if response.status_code == 200:
#             user_games = {d['appid'] for d in json.loads(response.content)['response']['games']}
#
#             if game_id in user_games:
#                 valid_users.append(user['discord_id'])
#
#         else:
#             print('Could not acquire user data from Steam servers...')
#
#     return valid_users
#
#
# def get_ping_string(game_title: str):
#     print('hello world')


bot.run(os.getenv('DISCORD_TOKEN'))
