from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import TypeAlias, IO

from requests import get

JSONType: TypeAlias = int | float | str | bool | None | list['JSONType'] | dict[str, 'JSONType']


@dataclass(frozen=True)
class RemoteLocation:
    """A class representing a remote location.

    Attributes:
        url (str): The URL of the remote location.
        verify_ssl (bool): Whether to verify the SSL certificate of the remote location. Defaults to True.
    """
    url: str
    verify_ssl: bool = True

    def open(self, *args) -> IO[bytes]:
        with get(self.url, verify=self.verify_ssl) as response:
            return BytesIO(response.content)


class LocalOrRemoteLocation:
    """
    A class representing a local or remote location.

    Attributes:
        _location (str): The location of the file or resource.

    """
    def __init__(self, location: str | Path):
        self._location: str = str(location)

    def open(self, *args) -> IO[bytes]:
        """
        Args:
            *args: Additional arguments to be passed to the 'open' function if the location is not a remote location.

        Returns:
            IO[bytes]: A file object opened in binary mode for reading the contents of the file at the given location.
        """
        if self._location.startswith('http'):
            return RemoteLocation(self._location).open(*args)
        else:
            return open(self._location, 'rb')

