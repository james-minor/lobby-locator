from sqlite3 import Connection

import discord
from discord import Bot
from discord.ext import commands

from logging import Logger


class Game(commands.Cog):

    game = discord.SlashCommandGroup('game', 'Commands handling custom non-steam games')

    def __init__(self, bot: Bot, sql_connection: Connection, logger: Logger):
        self.bot = bot
        self.connection = sql_connection
        self.logger = logger

    @game.command(name='add', description="Adds a custom game to the games database.")
    @commands.has_permissions(administrator=True)
    async def add_game_command(self, ctx, game_title: str):
        # Seeing if an entry for this game already exists.
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT COUNT(*) FROM tb_games
            WHERE game_title = ?;
            """,
            [game_title]
        )

        # Only adding the entry if it does not already exist.
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                """
                INSERT INTO tb_games(game_title, game_title_lower)
                VALUES(?, ?);
                """,
                [game_title, game_title.lower()]
            )

            # Committing action to the database.
            cursor.close()
            self.connection.commit()

            await ctx.respond(f'Added custom game **{game_title}**.')
            self.logger.info(f'{ctx.author} added custom game "{game_title}"...')
        else:
            await ctx.respond(f'Custom game **{game_title}** already exists!', ephemeral=True)
            self.logger.info(f'{ctx.author} attempted to add custom game "{game_title}", but game already existed...')

    @game.command(name='remove', description="Removes a custom game from the games database.")
    @commands.has_permissions(administrator=True)
    async def remove_game_command(self, ctx, game_title: str):
        cursor = self.connection.cursor()

        # Seeing if the requested game exists.
        cursor.execute(
            """
            SELECT COUNT(*) FROM tb_games
            WHERE game_title = ?
                AND steam_id IS NULL;
            """,
            [game_title]
        )
        if cursor.fetchone()[0] != 1:
            await ctx.respond(f'Custom game **{game_title}** does not exist!', ephemeral=True)
            self.logger.info(f'{ctx.author} attempted to remove non-existent custom game "{game_title}"...')
            return

        # Removing any entries from tb_owned_games table.
        cursor.execute(
            """
            DELETE FROM tb_owned_games
            WHERE game_title = ?;
            """,
            [game_title]
        )

        # Removing the custom game entry from the tb_games table.
        cursor.execute(
            """
            DELETE FROM tb_games
            WHERE game_title = ?
                AND steam_id IS NULL;
            """,
            [game_title]
        )

        # Committing action to the database.
        cursor.close()
        self.connection.commit()

        await ctx.respond(f'Removed custom game **{game_title}**.')
        self.logger.info(f'{ctx.author} removed custom game "{game_title}"...')

    @game.command(name="register", description="Registers a custom game as connected to your account.")
    async def register_user_command(self, ctx, game_title: str):
        cursor = self.connection.cursor()

        # Validating that the custom game exists in tb_custom_games.
        cursor.execute(
            """
            SELECT COUNT(*) FROM tb_games
            WHERE game_title = ?
                AND steam_id IS NULL;
            """,
            [game_title]
        )
        if cursor.fetchone()[0] == 0:
            await ctx.respond(
                f'**{game_title}** is not a recognized title, contact an admin to add it to the custom game library.',
                ephemeral=True
            )
            self.logger.info(f'{ctx.author} tried to register non-added game "{game_title}"...')
            return

        # Validating that this game is NOT already registered to the current user.
        cursor.execute(
            """
            SELECT COUNT(*) FROM tb_owned_games
            WHERE game_title = ?
                AND discord_id = ?;
            """,
            [game_title, ctx.author.id]
        )

        # If the user does not have this game registered, register this game to their account.
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                """
                INSERT INTO tb_owned_games(game_title, discord_id)
                VALUES(?, ?)
                """,
                [game_title, ctx.author.id]
            )

            await ctx.respond(f'Registered custom game **{game_title}** for **{ctx.author}**.')
            self.logger.info(f'Registered custom game {game_title} for {ctx.author}...')
        else:
            await ctx.respond(f'Your account is already registered for **{game_title}**!')

        # Committing action to the database.
        cursor.close()
        self.connection.commit()

    @game.command(name="unregister", description="Unregisters a custom game as connected to your account.")
    async def unregister_custom_game_command(self, ctx, game_title: str):
        cursor = self.connection.cursor()

        # Checking to see if the requested custom game title exists.
        cursor.execute(
            """
            SELECT COUNT(*) FROM tb_games
            WHERE game_title = ?
                AND steam_id IS NULL;
            """,
            [game_title]
        )
        if cursor.fetchone()[0] == 0:
            cursor.close()
            await ctx.respond(
                f'**{game_title}** is not a recognized title, contact an admin to add it to the custom game library.',
                ephemeral=True
            )
            return

        # If the custom game exists, deleting the user's custom game entry.
        cursor.execute(
            """
            DELETE FROM tb_owned_games
            WHERE game_title = ?
                AND discord_id = ?;
            """,
            [game_title, ctx.author.id]
        )

        # Committing action to the database.
        cursor.close()
        self.connection.commit()

        await ctx.respond(f'Unregistered **{game_title}** from your account.', ephemeral=True)
        self.logger.info(f'{ctx.author} unregistered "{game_title}" from their account...')

    @game.command(name="list", description="Lists the game titles in the custom games library")
    async def list_custom_game_command(self, ctx):
        self.logger.info(f'{ctx.author} requested the custom games list.')
        title_cursor = self.connection.cursor()

        # Validating that there are any custom games.
        title_cursor.execute('SELECT COUNT(*) FROM tb_games WHERE steam_id IS NULL')
        if title_cursor.fetchone()[0] == 0:
            title_cursor.close()
            await ctx.respond(
                'There are no custom games, please contact an admin to add to the custom game library.',
                ephemeral=True
            )
            return

        # Fetching all the game titles from tb_custom_games.
        title_cursor.row_factory = lambda cursor, row: row[0]
        title_cursor.execute('SELECT game_title FROM tb_games WHERE steam_id IS NULL;')

        # Creating a string list of every custom game title.
        output_string = '```' + '\n' + 'Custom Game Library Titles:\n'
        for title in title_cursor.fetchall():
            output_string += '- ' + str(title) + '\n'
        output_string += '```'

        title_cursor.close()
        await ctx.respond(output_string, ephemeral=True)
