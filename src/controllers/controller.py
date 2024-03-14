from abc import ABC

from src.lobby_locator import LobbyLocator


class Controller(ABC):
    """
    Abstract base class for Controller classes.
    """

    def __init__(self, bot: LobbyLocator):
        self.bot = bot
