import dotenv


class EnvironmentFile:
    """Class to handle environment variables and environment variable validation."""

    required_variables: list[str]
    """List of environment variables required for validation."""

    environment_variables: dict[str, str]
    """Dictionary of loaded environment variables and their associated values."""

    def __init__(self, required: list[str], path: str | None = None) -> None:
        """
        Constructor for the EnvFile class.

        :param required: The environment variables that are required for the program to pass validation.
        :param path: The path to the .env file. If not provided uses the find_dotenv() function.
        """

        if path:
            dotenv.load_dotenv(dotenv_path=path)
        else:
            dotenv.load_dotenv()

        self.required_variables = required
        self.environment_variables = dotenv.dotenv_values()

    def is_valid(self) -> bool:
        """
        Validates that all environment variable are present in the os environment.

        :return: True if all the required environment variables ae present, False otherwise.
        """

        file_valid: bool = True
        for variable in self.required_variables:
            if not self.environment_variables.get(variable):
                print(f'Could not find environment variable: {variable}')
                file_valid = False

        return file_valid
