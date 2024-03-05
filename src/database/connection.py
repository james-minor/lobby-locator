import sqlite3


class Connection(sqlite3.Connection):
    """
    Class to extend the functionality of the sqlite3.Connection class.
    """

    def __init__(self, connection_string: str, **kwargs):
        super().__init__(connection_string, **kwargs)

        self._is_open: bool = True
        """
        Is the connection to the database currently open?
        """

    def disconnect(self) -> bool:
        """
        Safely closes the database connection, committing any pending transactions before doing so.

        :return: True if the disconnect was successful, False otherwise.
        """

        # If attempting to commit while the connection is closed, a ProgrammingError will be raised.
        try:
            self.commit()
        except sqlite3.ProgrammingError:
            return False

        self._is_open = False
        self.close()
        return True

    def is_open(self) -> bool:
        """
        :returns: True if the connection is open, False otherwise.
        """
        return self._is_open
