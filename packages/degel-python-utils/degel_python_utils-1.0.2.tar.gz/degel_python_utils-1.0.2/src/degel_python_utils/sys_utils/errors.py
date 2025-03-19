"""
This module defines custom exceptions for the degel_python_utils library.

The base exception class `DegelUtilsError` is defined to serve as the root for all
custom exceptions in this library. Specific error types are derived from this base class
to handle different error scenarios.

"""

from typing import Self


class DegelUtilsError(Exception):
    """Base exception class for all degel_python_utils errors."""

    def __init__(self: Self, message: str = "An error occurred in degel_utils") -> None:
        """Init."""
        super().__init__(message)


class ExternalApiError(DegelUtilsError):
    """Exception raised by calls to external APIs."""

    def __init__(
        self: Self, message: str = "An API error occurred in degel_utils"
    ) -> None:
        """Init."""
        super().__init__(message)


class UnsupportedError(DegelUtilsError):
    """Exception indicating feature not yet supported by Degel Utils."""

    def __init__(self: Self, feature: str) -> None:
        """Init."""
        message = f"The Degel Utils Library does not yet support '{feature}'"
        super().__init__(message)
