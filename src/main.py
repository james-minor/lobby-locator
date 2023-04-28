import difflib
import os

import discord
import dotenv
import requests
import json


# Gathers the name and App ID of every game on Steam.
def get_steam_app_data():
    response = requests.get('https://api.steampowered.com/ISteamApps/GetAppList/v0002')
    if response.status_code == 200:
        print('Acquired application data from Steam!')

        # Converting the acquired JSON data to a Python dictionary.
        return {d['appid']: d['name'] for d in json.loads(response.content)['applist']['apps']}
    else:
        print('Could not acquire application data from Steam servers, aborting bot startup...')
        quit()


# Getting the API keys from the dotEnv file.
dotenv.load_dotenv()

# Setting the bot intents and initializing the bot.
intents = discord.Intents.all()  # TODO: enable proper intents, we dont need all of them (helps with development)
bot = discord.Bot(intents=intents)

# Dictionary to hold all Steam application data.
steam_app_data = get_steam_app_data()
print(f'Got {len(steam_app_data)} applications from Steam...')


@bot.event
async def on_ready():
    print(f'{bot.user} is now online!')


@bot.slash_command(name='set', description='Sets your saved Steam ID')
async def set_id_command(ctx, steam_id: str):
    await ctx.respond(f'Setting Steam ID: **{steam_id}**, for user: **{ctx.author}**')
    print(f'Setting Steam ID: {steam_id}, for user: {ctx.author}')

    file_path = os.path.join(os.getcwd(), '../accounts.json')
    if os.path.exists(file_path):
        with open(file_path, 'r+') as user_data_file:
            user_data = json.load(user_data_file)

            # Seeing if the user account already exists.
            user_discord_tag = ctx.author.name + '#' + ctx.author.discriminator
            user_exists = False
            for index, account in enumerate(user_data['accounts']):
                if account['discord_tag'] == user_discord_tag:
                    user_data['accounts'][index] = {
                        'discord_tag': user_discord_tag,
                        'discord_id': ctx.author.id,
                        'steam_id': steam_id
                    }
                    user_exists = True

            # Appending the user data if they don't have an entry in the users array.
            if not user_exists:
                user_data['accounts'].append(
                    {'discord_tag': user_discord_tag, 'steam_id': steam_id}
                )

            # Writing JSON data back to the file.
            user_data_file.seek(0)
            user_data_file.truncate()
            json.dump(user_data, user_data_file)
    else:
        print('File could not be found: ' + file_path)


@bot.slash_command(name='remove', description='Removes your saved Steam ID')
async def remove_id_command(ctx):
    await ctx.respond(f'Removing Steam ID for **{ctx.author}**.')
    # TODO: remove the saved steam id.


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


@bot.slash_command(name='ping', description='Pings any users who own a game')
async def ping_command(ctx, game_title: str):
    app_name_list = list(steam_app_data.values())  # List that contains the name of every app on Steam.

    # Finding the closest match to the passed game title.
    closest_matches = difflib.get_close_matches(game_title, app_name_list, 5)
    print(f'{ctx.author} searched for "{game_title}", and got {len(closest_matches)} matches.')

    # Validating that there are games in the closest_matches array.
    if len(closest_matches) == 0:
        await ctx.respond(f'Sorry, I could not find any games matching **{game_title}**.')
        return

    if game_title in closest_matches:
        # Getting the users that own the selected game.
        valid_users = get_users_who_own_game(get_game_id(game_title))
        if len(valid_users) == 0:
            await ctx.send(f'Uh oh! It looks like no one with a set Steam ID owns **{game_title}**.')
            return

        # Generating the string of user pings for valid users.
        user_pings = ''
        for user_id in valid_users:
            if user_id != ctx.author.id:
                user_pings += '<@' + str(user_id) + '> '
        if user_pings == '':
            await ctx.send(f'Uh oh! It looks like no one with a set Steam ID owns **{game_title}**, besides you!')
            return

        await ctx.send(f'**{ctx.author}** is seeking players for **{game_title}** {user_pings}')
        return

    # Creating a new GameSelectView if the game_title did not have an exact match.
    view = discord.ui.View(timeout=10)
    view.add_item(GameSelectView(closest_matches))

    await ctx.send('Please select a game to find players for:', view=view)


# Returns the Steam ID for the passed game title. If the game title could not be found returns 0.
def get_game_id(game_title: str):
    for game_id in steam_app_data:
        if steam_app_data[game_id] == game_title:
            return game_id
    return 0


# Returns a list of user Discord tags if their steam account owns the passed Steam game ID.
def get_users_who_own_game(game_id: str):
    valid_users = list()

    # Getting the user data from accounts.json
    user_accounts = None
    file_path = os.path.join(os.getcwd(), '../accounts.json')
    if os.path.exists(file_path):
        with open(file_path, 'r') as user_data_file:
            user_accounts = json.load(user_data_file)['accounts']
    else:
        print('File could not be found: ' + file_path)

    # Contacting the Steam Web API to see if each user owns the passed game ID.
    for user in user_accounts:
        steam_id = user['steam_id']
        api_uri = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={os.getenv("STEAM_API_KEY")}&steamid={steam_id}'
        response = requests.get(api_uri)
        if response.status_code == 200:
            user_games = {d['appid'] for d in json.loads(response.content)['response']['games']}

            if game_id in user_games:
                valid_users.append(user['discord_id'])

        else:
            print('Could not acquire user data from Steam servers...')

    return valid_users


def get_ping_string(game_title: str):
    print('hello world')


bot.run(os.getenv('DISCORD_TOKEN'))
