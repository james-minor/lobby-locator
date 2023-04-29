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
        await ctx.respond(f'Adding custom game **{game_title}**.')
        # TODO: implement behavior

    @game.command(name='remove', description="Removes a custom game from the games database.")
    @commands.has_permissions(administrator=True)
    async def remove_game_command(self, ctx, game_title: str):
        await ctx.respond(f'Removing custom game **{game_title}**.')
        # TODO: implement behavior

    @game.command(name="register", description="Registers a custom game as connected to your account.")
    async def register_user_command(self, ctx, game_title: str):
        await ctx.respond(f'Registering custom game **{game_title}** for **{ctx.author}**.')
        # TODO: implement behavior

    @game.command(name="unregister", description="Unregisters a custom game as connected to your account.")
    async def register_custom_game_command(self, ctx, game_title: str):
        await ctx.respond(f'Unregistering custom game **{game_title}** for **{ctx.author}**.')
        # TODO: implement behavior
