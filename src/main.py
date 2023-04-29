import difflib
import os

import dotenv
import requests
import json

import sqlite3
from sqlite3 import Error

import discord
from src.cogs.Game import Game
from src.cogs.Steam import Steam

# Creating the data folder, if it doesn't already exist.
# TODO: do that ^

# Attempting to connect to the SQLite database.
sql_connection = None
try:
    # TODO: unlink this sqlite file from this file path specifically.
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
            FOREIGN KEY(game_title) REFERENCES tb_custom_games(game_title)
        );
        """
    )
    cursor.close()


# Initializing the SQLite database tables.
create_database_tables()


def get_steam_app_data() -> None:
    """
    Gathers the name and App ID of every application on Steam.
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


class GameSelectView(discord.ui.Select):
    def __init__(self, context, game_titles):
        self.context = context

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
        # TODO: ping users who own the selected game using self.context


@bot.slash_command(name='ping', description='Pings any users who own the specified game title')
async def ping_command(ctx, game_title: str):
    game_title_cursor = sql_connection.cursor()

    # Getting a list of every registered game name (both from steam and custom games).
    game_title_cursor.row_factory = lambda cursor, row: row[0]
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

    # If there is an exact match for the game title, ping all users who own that game.
    if game_title in closest_matches:
        # TODO: ping users when an exact match is found.
        await ctx.respond(f'TODO: ping users when an exact match is found.')
        return

    # Creating a new GameSelectView if the game title did not have an exact match.
    select_menu = discord.ui.View(timeout=10)
    select_menu.add_item(GameSelectView(ctx, closest_matches))

    await ctx.respond('Please select a game to find players for:', view=select_menu)


# Adding cogs to the bot.
bot.add_cog(Steam(bot, sql_connection))
bot.add_cog(Game(bot, sql_connection))

# Starting the bot.
bot.run(os.getenv('DISCORD_TOKEN'))
