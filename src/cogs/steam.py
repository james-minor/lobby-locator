import discord
from discord import ApplicationContext
from discord.ext import commands

from src.controllers.steam_controller import SteamController
from src.lobby_locator import LobbyLocator


class Steam(commands.Cog):

    steam_cmd_group = discord.SlashCommandGroup('steam', 'Steam ID commands')

    def __init__(self, bot: LobbyLocator) -> None:
        self.bot = bot
        self.controller = SteamController(self.bot)

    @steam_cmd_group.command(
        name='set',
        description='Sets or updates your saved Steam ID.',
        guild_ids=[1046992676865720420],
        steam_id_or_url=discord.Option(
            str,
            'Your Steam 64 ID or your Steam profile URL.',
            min_length=1,
            max_length=60
        )
    )
    async def set_command(self, ctx: ApplicationContext, steam_id_or_url: str) -> None:
        """
        Sets a users Steam ID in the bot database from a passed Steam ID, or if passed a Steam profile
        URL will attempt to parse the Steam ID and update the database.

        Called when a user invokes the /steam set command.

        :param ctx: The context that the interaction was invoked in.
        :param steam_id_or_url: The Steam ID or Steam profile URL to set the ID with.
        """

        # Checking if the user passed a valid Steam profile URL.
        parsed_id = self.bot.steam_api.get_id_from_url(steam_id_or_url)

        if parsed_id != '':
            self.controller.set_command(str(ctx.interaction.user.id), parsed_id)
            await ctx.respond(f'Set your Steam ID to: {parsed_id}', delete_after=15, ephemeral=True)
            return

        # Checking if the user passed a valid Steam ID.
        if self.bot.steam_api.is_valid_id(steam_id_or_url):
            self.controller.set_command(str(ctx.interaction.user.id), steam_id_or_url)
            await ctx.respond(f'Set your Steam ID to: {steam_id_or_url}', delete_after=15, ephemeral=True)
            return

        # Response message if we could not find a connected Steam account.
        await ctx.respond(
            'Sorry, it looks like I was unable to find your Steam ID!',
            delete_after=15,
            ephemeral=True
        )

    @steam_cmd_group.command(
        name='remove',
        description='Removes your Steam ID from the bot database.',
        guild_ids=[1046992676865720420]
    )
    async def steam_remove(self, ctx: ApplicationContext):
        """
        Removes a user, and all of their accompanying data, from the bot database.

        Called when a user invokes the /steam remove command.

        :param ctx: The context that the interaction was invoked in.
        """

        raise NotImplementedError

    @steam_cmd_group.command(
        name='refresh',
        description='Forces the bot to rescan your library files.',
        guild_ids=[1046992676865720420]
    )
    async def steam_refresh(self, ctx):
        """
        Refreshes a users steam data. Used when a user got a new game and wants the bot database to
        reflect that.

        Called when a user invokes the /steam refresh command.

        :param ctx: The context that the interaction was invoked in.
        """

        raise NotImplementedError


def setup(bot: LobbyLocator):
    bot.add_cog(Steam(bot))
