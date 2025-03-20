from pathlib import Path
from typing import Any


class XsUtil:
    """

    Class for managing common Xs shortcuts and functionality.

    """
    @staticmethod
    def bool(val: Any) -> str:
        """
        Transform a value into an XS boolean

        Args:
            val: The value to check

        Returns:
            'true' if val is truthy, 'false' otherwise
        """
        return 'true' if val else 'false'

    @staticmethod
    def file(path: str) -> str:
        """
        Read a file from the XS folder within this repo and return its contents

        Args:
            path: The path of the XS file within the XS folder

        Returns:
            The content of the file as string
        """
        with (Path(__file__).parent.parent / 'xs' / path).open() as file:
            return file.read()

    @staticmethod
    def constant(name: str) -> str:
        """
        Change a given name to an XS constant name

        Args:
            name: The name to update

        Returns:
            The updated string as an XS constant
        """
        xs_name = ' '.join(filter(lambda e: e, name.split(' ')))
        return xs_name.upper().replace(' ', '_')
