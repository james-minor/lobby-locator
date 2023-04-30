import os

from src.logging.LogLevel import LogLevel
from datetime import datetime


class Logger:

    def __init__(self, log_directory: str, log_to_console: bool = True):
        self._log_directory = log_directory
        self.log_to_console = log_to_console

    def info(self, message: str) -> None:
        self.log(LogLevel.INFO, message)

    def warn(self, message: str) -> None:
        self.log(LogLevel.WARN, message)

    def critical(self, message: str) -> None:
        self.log(LogLevel.CRITICAL, message)

    def log(self, log_level: LogLevel, message: str) -> None:
        with open(os.path.join(self._log_directory, datetime.today().strftime('%d-%m-%Y') + '.log'), 'a') as file:
            date_time_tag = f'[{datetime.today().strftime("%d-%m-%Y %H:%M:%S")}]'
            file.write(date_time_tag + f'[{log_level}]: {message}\n')

            if self.log_to_console:
                print(date_time_tag + f'[{log_level}]: {message}')