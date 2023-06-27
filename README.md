# Looking to Play Discord Bot

[![Minimum Python Version](https://img.shields.io/badge/Python-%3E%3D3.10-green.svg)](https://www.python.org/)
![GitHub repo size](https://img.shields.io/github/repo-size/james-minor/game_seeker_discord_bot)
![GitHub](https://img.shields.io/github/license/james-minor/game_seeker_discord_bot)

## Description

A NodeJS Discord bot to search for players who own specific games, using the Steam Web API.

## Features

- Find players for Steam games, all users have to do is register their Steam ID with the bot.
- Administrators can add custom games to the game database.
- Find players for custom non-steam games!

## Developing

### Creating Virtual Environment

When pulling from the Repository, you will have to build the Virtual Environment from
the `requirements.txt` file. To build the Virtual Environment run the following command:

```bash
pip3 install -r requirements.txt
```

### Gathering API Tokens

For Security reasons, API tokens and keys should obviously **never** be shared in any repository. It is for that reason
that we store any tokens in ```.env``` files, the schema for the ```.env``` files can be found in the ```.env.example``` 
file.

Place any production keys within the ```.env.production``` file, and any development keys within ```.env.development```.