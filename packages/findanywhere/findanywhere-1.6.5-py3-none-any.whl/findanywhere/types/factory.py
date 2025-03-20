from collections.abc import Sequence, Iterable
from dataclasses import dataclass, fields, MISSING
from inspect import signature
from operator import attrgetter

from dacite import from_dict
from toolz import first
from typing import TypeVar, Generic, Callable, Any

from findanywhere.types.common import JSONType

_T = TypeVar('_T')
PrimitiveType = str | int | float | bool | None


@dataclass(frozen=True)
class Config:
    """A data class for storing configuration parameters.

    This class represents a configuration object that stores various parameters
    related to a system or application configuration. It is designed to be
    immutable by using the `frozen=True` option from the `dataclass` decorator.


    Note:
        This class is intended to be inherited from and have attributes added to it
        based on the specific needs of the system or application.

    """
    @classmethod
    def required(cls) -> dict[str, type]:
        return dict(
            (field.name, field.type)
            for field in fields(cls)
            if field.default == MISSING and field.default_factory == MISSING
        )

    @classmethod
    def defaults(cls) -> dict[str, Any]:
        return dict(
            (field.name, field.default if field.default != MISSING else field.default_factory)
            for field in fields(cls)
            if field.default != MISSING or field.default_factory != MISSING
        )

    @classmethod
    def from_dict(cls, config: dict[str, JSONType]) -> 'Config':
        return cls(**config)


_C = TypeVar('_C', bound=Config)


@dataclass(frozen=True)
class Factory(Generic[_T, _C]):
    """
    Factory class

    A generic class used to create objects of a given type using a factory function.
    It provides methods to create objects from configuration and dictionary inputs.

    Attributes:
        name (str): The name of the factory.
        factory_function (Callable[[_C], _T]): The function used to create objects of type _T.
        using (Callable[..., Any] | None): A callable object used during object creation (optional).
    """
    name: str
    factory_function: Callable[[_C], _T]
    using: Callable[..., Any] | None = None

    @property
    def config_type(self) -> type[_C]:
        """
        Getter method for the config type used by the `config_type` property.

        Returns:
            The type of the config object.

        """
        return first(signature(self.factory_function).parameters.values()).annotation

    def from_config(self, config: _C) -> _T:
        """
        Args:
            config: The configuration object that provides the necessary information to create the desired object.

        Returns:
            _T: The created object based on the provided configuration.
        """
        return self.factory_function(config)

    def from_dict(self, config: dict[str, Any]) -> _T:
        """
        Args:
            config: A dictionary containing the configuration options for the method.

        Returns:
            An instance of the specified class (_T) created from the configuration options.

        """
        return self.from_config(from_dict(self.config_type, config))


def as_factory(
        name: str,
        using: Callable[..., Any] | None = None
) -> Callable[[Callable[[_C], _T]], Factory[_T, _C]]:
    """
    Args:
        name (str): The name of the factory.
        using (Callable[..., Any] | None, optional): The function or callable object to be used by the factory.
        Defaults to None.

    Returns:
        Callable[[Callable[[_C], _T]], Factory[_T, _C]]: A decorator function that converts a function into a factory.

    Raises:
        None.

    Example Usage:
        def create_car(specs):
            return Car(specs)

        @as_factory(name='CarFactory', using=create_car)
        def build_car(specs: dict) -> Car:
            return create_car(specs)

        car_factory = build_car.build('sedan', 'blue')
        sedan_blue_car = car_factory('sedan', 'blue')
    """
    def _wrapper(func: Callable[[_C], _T]) -> Factory[_T, _C]:
        factory: Factory[_T, _C] = Factory[_T, _C](name, func, using)

        return factory
    return _wrapper


@dataclass(frozen=True)
class FactoryMap(Generic[_T]):
    """
    A class that represents a map of factories.

    Attributes:
        factories (Sequence[Factory[_T, Any]]): A sequence of factories.
    """
    factories: Sequence[Factory[_T, Any]]

    def __getitem__(self, item: str) -> Factory[_T, Any]:
        for factory in self.factories:
            if factory.name == item:
                return factory
        raise NameError(f'No factory found for {item}')

    def config_type_for(self, item: str) -> type:
        """
        Returns the configuration type for the given item.

        Args:
            item: The item for which the configuration type is requested.

        Returns:
            The configuration type of the item.
        """
        return self[item].config_type

    def choices(self) -> Sequence[str]:
        """
        Returns a tuple of names from a sequence of factories.

        Returns:
            Sequence[str]: A tuple of names.
        """
        return tuple(map(attrgetter('name'), self.factories))

    def default(self) -> str:
        """Returns the name of the first factory.

        Returns:
            str: The name of the first factory.

        """
        return first(self.factories).name
