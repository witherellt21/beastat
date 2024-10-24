from typing import Iterable


def concatenate_exceptions(excs: list[Exception]):
    """
    Format a list of exceptions into one output.
    """
    message = f"There were {len(excs)} errors in execution:\n\n"

    message += "\n\n".join([f"{exc.__class__.__name__} : {str(exc)}" for exc in excs])

    return message


class ImproperlyConfigured(Exception):
    """App is somehow improperly configured"""

    pass


class AppRegistryNotReady(Exception):
    """App is somehow improperly configured"""

    pass


class IllegalArgumentException(Exception):
    """The arguments pass to the function are not valid."""

    def __init__(
        self, argument_name: str, expected_type: type, actual_type: type, *args: object
    ) -> None:
        message: str = (
            f"'{argument_name}' must be of type '{expected_type}'. got '{actual_type}'"
        )

        super().__init__(message, *args)


class StageEmpty(Exception):
    """There is no staged data to push."""

    pass


class ColumnDoesNotExist(Exception):
    def __init__(self, column_name: str, columns: Iterable[str], *args):
        super().__init__(f"'{column_name}' not found in {columns}", *args)


class DataInsertionError(Exception):
    pass


class DataStagingError(Exception):
    pass
