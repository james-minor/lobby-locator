from sqlite3 import Connection

import discord
from discord import Bot
from discord.ext import commands

from logging import Logger


class Steam(commands.Cog):

    steam = discord.SlashCommandGroup('steam', 'Editing saved Steam IDs')

    def __init__(self, bot: Bot, sql_connection: Connection, logger: Logger):
        self.bot = bot
        self.connection = sql_connection
        self.logger = logger

    @steam.command(name='set', description='Sets your saved Steam ID')
    async def set_command(self, ctx, steam_id: str):
        await ctx.respond(f'Setting Steam ID: **{steam_id}**, for user: **{ctx.author}**')

        # Seeing if an entry for this user already exists, if so UPDATE instead of INSERTING data.
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT COUNT(*) FROM tb_users
            WHERE discord_id = ?
            """,
            [ctx.author.id]
        )
        if cursor.fetchone()[0] == 0:
            self.logger.info(f'Inserting Steam ID data for user: {ctx.author}...')
            cursor.execute(
                """
                INSERT INTO tb_users(discord_id, steam_id)
                VALUES(?, ?);
                """,
                [str(ctx.author.id), str(steam_id)]
            )
        else:
            self.logger.info(f'Updating Steam ID data for user: {ctx.author}...')
            cursor.execute(
                """
                UPDATE tb_users
                SET steam_id = ?
                WHERE discord_id = ?;
                """,
                [str(steam_id), str(ctx.author.id)]
            )

        cursor.close()
        self.connection.commit()

    @steam.command(name='remove', description='Removes your saved Steam ID')
    async def remove_command(self, ctx):
        cursor = self.connection.cursor()

        # Removing the user entry from tb_users.
        cursor.execute(
            """
            DELETE FROM tb_users
            WHERE discord_id = ?;
            """,
            [ctx.author.id]
        )

        # Committing action to the database.
        cursor.close()
        self.connection.commit()

        await ctx.respond(f'Removing Steam ID for **{ctx.author}**.')
        self.logger.info(f'Removing Steam ID for {ctx.author}')

