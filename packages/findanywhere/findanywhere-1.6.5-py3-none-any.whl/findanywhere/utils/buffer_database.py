from collections.abc import Sequence
from dataclasses import asdict
from functools import partial
from operator import itemgetter, attrgetter
from pathlib import Path
from typing import TypeVar, Generic, Protocol, ClassVar, Any

from dacite import from_dict
from sqlalchemy import Integer, String, JSON, Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, mapped_column, Mapped
from toolz import compose


class Base(DeclarativeBase):
    pass


class Position(Base):
    """

    Class representing a position.

    Attributes:
        id (int): The ID of the position.
        path (str): The path of the position.
        data (JSON): The data associated with the position.

    """
    __tablename__ = 'position'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    path: Mapped[str] = mapped_column(String)
    data: Mapped[JSON] = mapped_column(JSON)


class _Dataclass(Protocol):
    """
    Protocol representing a data class.
    """
    __dataclass_fields__: ClassVar[dict[str, Any]]


_T = TypeVar('_T', bound=_Dataclass)


class BufferDatabase(Generic[_T]):
    """

    This class is a database manager for storing and retrieving entries of a specific data type.

    Attributes:
        _db_url (str): The URL of the SQLite database file.
        _engine (Engine): The SQLAlchemy engine used for connecting to the database.
        _create_session (sessionmaker): A sessionmaker object for creating sessions.
        _counter (int): A counter for generating unique IDs for each entry.
        _type (type[_T]): The type of data being stored in the database.
    """
    def __init__(self, path: Path, data_type: type[_T]):
        """
        Args:
            path (Path): The path to the directory where the buffer database file will be created.
            data_type (type[_T]): The type of data that will be stored in the buffer.

        """
        self._db_url: str = path.joinpath(
            'buffer.sqlite'
        ).absolute().as_uri().replace('file://', 'sqlite:///')
        self._engine: Engine = create_engine(self._db_url)
        self._create_session: sessionmaker = sessionmaker(self._engine)
        self._counter: int = 0
        self._type: type[_T] = data_type
        Base.metadata.create_all(self._engine, checkfirst=True)

    def add_entry(self, path: str, entry: _T):
        """
        Args:
            path: The path where the entry will be added.
            entry: The entry object to be added.

        """
        with self._create_session() as session:
            session.add(Position(id=self._counter, path=path, data=asdict(entry)))
            session.commit()
        self._counter += 1

    def get_unique_paths(self) -> Sequence[str]:
        """
        Retrieves the sorted set of paths from the database.

        Returns:
            A sequence of strings representing the unique paths.

        """
        with self._create_session() as session:
            return sorted(map(itemgetter(0), session.query(Position.path.distinct())))

    def get_all_with_path(self, path: str) -> Sequence[_T]:
        """
        Args:
            path (str): The path to query for positions.

        Returns:
            Sequence[_T]: A sequence of positions that match the given path.
        """
        with self._create_session() as session:
            return list(
                map(
                    compose(partial(from_dict, self._type), attrgetter('data')),
                    session.query(Position).filter(Position.path == path).order_by(Position.id)
                )
            )
