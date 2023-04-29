from sqlite3 import Connection

import discord
from discord import Bot
from discord.ext import commands


class Game(commands.Cog):

    game = discord.SlashCommandGroup('game', 'Commands handling custom non-steam games')

    def __init__(self, bot: Bot, sql_connection: Connection):
        self.bot = bot
        self.connection = sql_connection

    @game.command(name='add', description="Adds a custom game to the games database.")
    @commands.has_permissions(administrator=True)
    async def add_game_command(self, ctx, game_title: str):
        # Seeing if an entry for this game already exists.
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT COUNT(*) FROM tb_custom_games
            WHERE game_title = ?;
            """,
            [game_title]
        )

        # Only adding the entry if it does not already exist.
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                """
                INSERT INTO  tb_custom_games(game_title)
                VALUES(?);
                """,
                [game_title]
            )

            # Committing action to the database.
            cursor.close()
            self.connection.commit()

            await ctx.respond(f'Added custom game **{game_title}**.')
            print(f'{ctx.author} added custom game "{game_title}"...')
        else:
            await ctx.respond(f'Custom game **{game_title}** already exists!')
            print(f'{ctx.author} attempted to add custom game "{game_title}", but game already existed...')

    @game.command(name='remove', description="Removes a custom game from the games database.")
    @commands.has_permissions(administrator=True)
    async def remove_game_command(self, ctx, game_title: str):
        cursor = self.connection.cursor()

        # Removing any entries from tb_owned_custom_games table.
        cursor.execute(
            """
            DELETE FROM tb_owned_custom_games
            WHERE game_title = ?;
            """,
            [game_title]
        )

        # Removing the custom game entry from the tb_custom_games table.
        cursor.execute(
            """
            DELETE FROM tb_custom_games
            WHERE game_title = ?;
            """,
            [game_title]
        )

        # Committing action to the database.
        cursor.close()
        self.connection.commit()

        await ctx.respond(f'Removed custom game **{game_title}**.')
        print(f'{ctx.author} removed custom game "{game_title}"...')

    @game.command(name="register", description="Registers a custom game as connected to your account.")
    async def register_user_command(self, ctx, game_title: str):
        await ctx.respond(f'Registering custom game **{game_title}** for **{ctx.author}**.')
        # TODO: implement behavior

    @game.command(name="unregister", description="Unregisters a custom game as connected to your account.")
    async def register_custom_game_command(self, ctx, game_title: str):
        await ctx.respond(f'Unregistering custom game **{game_title}** for **{ctx.author}**.')
        # TODO: implement behavior
