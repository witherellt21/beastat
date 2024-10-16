import os
from typing import Optional


def find_file(file_name: str, path: str = ".") -> Optional[str]:
    """
    Search for a file in the given path.
    """
    for root, dirs, files in os.walk(path):
        if file_name in files:
            return os.path.join(root, file_name)


def enforce_file_type(file_name: str, file_type: str):
    """
    Add an extension to the file name if it does not exist.

    Arguments:
        file_name (`str`): The name of the source file.
        file_type (`str`): The file type to fix to the source file.

    Returns:
        A string representation of the file name with an file type appended to it.
    """
    file_parts = file_name.split(".")

    # If there is not already an extension
    if len(file_parts) != 2:
        file_name += "." + file_type

    elif file_parts[1] != file_type:
        raise Exception(
            "Tried to enforce a file type that does not correspond with the existing file type."
        )

    return file_name
