import os
from dotenv import load_dotenv

load_dotenv()


def get_env_var(name: str) -> str:
    """
    Retrieves the value of an environment variable,
    raising an error if not found.

    Args:
        name (str): The name of the environment variable to retrieve.

    Returns:
        str: The value of the requested environment variable.

    Raises:
        EnvironmentError: If the environment variable is not set.
    """
    value = os.getenv(name)
    if value is None:
        raise EnvironmentError(
            f"Missing required environment variable: {name}"
        )
    return value
