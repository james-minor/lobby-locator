import os

from . LogLevel import LogLevel
from datetime import datetime


class Logger:
    """
    Custom logger for the Discord bot.
    """

    _log_directory: str
    """
    The directory where log files should be stored.
    """

    _log_to_console: bool
    """
    If True, the Logger will log any information it receives to the console as well as writing to the log file.
    """

    def __init__(self, log_directory: str, log_to_console: bool = True):
        """
        Constructor for the Logger class.

        :param log_directory:
        :param log_to_console:
        """

        self._log_directory = log_directory
        self._log_to_console = log_to_console

    def info(self, message: str) -> None:
        """
        Logs a message with the INFO tag to the log file.

        :param message: The info / debug message to log.
        :return: None
        """
        self._log(LogLevel.INFO, message)

    def warn(self, message: str) -> None:
        """
        Logs a message with the WARN tag to the log file.

        :param message: The warning message to log.
        :return: None
        """
        self._log(LogLevel.WARN, message)

    def critical(self, message: str) -> None:
        """
        Logs a message with the CRITICAL tag to the log file.

        :param message: The error message to log.
        :return: None
        """
        self._log(LogLevel.CRITICAL, message)

    def _log(self, log_level: LogLevel, message: str) -> None:
        """
        The internal logging method that is used to log messages to the current logging file.

        :param log_level: The LogLevel of the message to log.
        :param message: The message to log.
        :return: None
        """
        with open(os.path.join(self._log_directory, datetime.today().strftime('%m-%d-%Y') + '.log'), 'a') as file:
            date_time_tag = f'[{datetime.today().strftime("%m-%d-%Y %H:%M:%S")}]'
            file.write(date_time_tag + f'[{log_level.value[0]}]: {message}\n')

            if self._log_to_console:
                print(date_time_tag + f'[{log_level.value[0]}]: {message}')
