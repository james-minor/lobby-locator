# Looking to Play Discord Bot



<div style="text-align: center;">

   [![Minimum Python Version](https://img.shields.io/badge/Python-%3E%3D3.10-green.svg)](https://www.python.org/)

</div>

## Description

A Python-based Discord bot to search for players who own specific games, using the Steam Web API.

## Developing

### Creating Virtual Environment

When pulling from the Repository, you will have to build the Virtual Environment from
the `requirements.txt` file. To build the Virtual Environment run the following command:

```bash
pip3 install -r requirements.txt
```

To generate your `requirements.txt` file from an **existing version** of the repository, run:

```bash
pip3 freeze > requirements.txt
```

### Gathering API Tokens

For Security reasons, API tokens and keys should obviously **never** be shared in any repository. It is for that reason
that we store any tokens in ```.env``` file, the schema for the ```.env``` file can be found in the ```.env.example``` 
file.
