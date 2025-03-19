"""File system helpers."""

import os


def append_to_filename(filename: str, suffix: str) -> str:
    """
    Append a suffix to the filename before the file extension.

    :param filename: The original filename.
    :param suffix: The suffix to append.
    :return: The modified filename with the suffix appended.
    """
    name, ext = os.path.splitext(filename)
    return f"{name}{suffix}{ext}"
