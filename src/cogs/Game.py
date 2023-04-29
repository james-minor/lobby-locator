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
        cursor = self.connection.cursor()

        # Validating that the custom game exists in tb_custom_games.
        cursor.execute(
            """
            SELECT COUNT(*) FROM tb_custom_games
            WHERE game_title = ?;
            """,
            [game_title]
        )
        if cursor.fetchone()[0] == 0:
            await ctx.respond(
                f'**{game_title}** is not a recognized title, contact an admin to add it to the custom game library.'
            )
            print(f'{ctx.author} tried to register non-added game "{game_title}"...')
            return

        # Validating that this game is NOT already registered to the current user.
        cursor.execute(
            """
            SELECT COUNT(*) FROM tb_owned_custom_games
            WHERE game_title = ?
                AND discord_id = ?;
            """,
            [game_title, ctx.author.id]
        )

        # If the user does not have this game registered, register this game to their account.
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                """
                INSERT INTO tb_owned_custom_games(game_title, discord_id)
                VALUES(?, ?)
                """,
                [game_title, ctx.author.id]
            )

            await ctx.respond(f'Registered custom game **{game_title}** for **{ctx.author}**.')
            print(f'Registered custom game {game_title} for {ctx.author}...')
        else:
            await ctx.respond(f'Your account is already registered for **{game_title}**!')

        # Committing action to the database.
        cursor.close()
        self.connection.commit()

    @game.command(name="unregister", description="Unregisters a custom game as connected to your account.")
    async def register_custom_game_command(self, ctx, game_title: str):
        await ctx.respond(f'Unregistering custom game **{game_title}** for **{ctx.author}**.')
        # TODO: implement behavior
