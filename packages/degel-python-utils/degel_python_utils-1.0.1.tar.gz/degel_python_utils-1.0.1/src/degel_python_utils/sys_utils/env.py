"""
Tools to manage environment variables in a controlled way.

We can't prevent you from calling the global environment directly, but you can use these
accessors for error-checked access, e.g., to catch typos.
"""

import os
from datetime import datetime
from typing import Self

from .log_tools import setup_logger

logger = setup_logger(__name__)
# pylint: disable=logging-fstring-interpolation


class _AppEnv:
    """Manages environment variables in a controlled way."""

    def __init__(self: Self) -> None:
        """Initialize state."""
        self.app_name = "Client of Degel Python Utils"
        self.registered_vars: list[dict[str, str | bool]] = []

    def set_app_name(self: Self, app_name: str) -> None:
        """Register the application name. (For now, used just for logging)."""
        self.app_name = app_name

    def register_env_var(self: Self, var: str, private: bool = False) -> None:
        """
        Register a variable, which we expect to find in the OS environment at runtime.

        [TODO]
        - We may want an option to name the variable different from the OS env var.

        Args:
            var (str): Variable name (both in the OS env and the program variable).
            private (bool, optional): Whether to obscure the value in logs.
        """
        value = os.environ.get(var)
        if value is None:
            logger.warning(f"Environment variable {var} not found.")
        else:
            self.registered_vars.append({"name": var, "private": private})

    def show_env(self: Self) -> None:
        """
        Show the program state and environment variables.

        Typically called at startup.

        Private variables will have their values obscured.
        """
        logger.info("================")
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"{self.app_name} environment at {now_str}")
        for var in self.registered_vars:
            var_name = var["name"]
            var_value = os.environ.get(str(var_name))
            if var_value and var["private"]:
                var_value = obscure_private(var_value, 4)
            logger.info(f"{var_name}: {var_value}")
        logger.info("================")

    def get_env_var(self: Self, var: str) -> str | None:
        """
        Get the value of a registered environment variable.

        Args:
            name (str): The name of the environment variable.

        Returns:
            str | None: The value of the environment variable.
        """
        if any(v["name"] == var for v in self.registered_vars):
            return os.environ.get(var)
        raise ValueError(f"{var} is not a registered environment variable")


def obscure_private(val: str, len_to_show: int) -> str:
    """
    Obscures part of a string, useful for hiding sensitive information in logs.

    Args:
        val (str): The value to obscure.
        len_to_show (int): The number of characters to show at the beginning and end
        of the string.
    Returns:
        str: The obscured string.
    """
    return f"{val[:len_to_show]}...{val[-len_to_show:]}" if val else ""


# Expose only a singleton environment manager
appEnv = _AppEnv()
