from collections.abc import Iterator, Callable
from typing import TypeVar, Generic, Sequence, runtime_checkable, Protocol


@runtime_checkable
class HasName(Protocol):
    __name__: str


_T = TypeVar('_T', bound=HasName)


class AlgorithmRegistry(Generic[_T]):
    """
    Class representing a registry for algorithms.

    This class is used to store and retrieve algorithms by their names. It provides functionality to add algorithms to
    the registry and retrieve them using indexing.

    Attributes:
        _algorithms (dict[str, _T]): A dictionary to store the algorithms with their names as keys.

    Methods:
        __init__(*algorithms: _T): Initializes a new AlgorithmRegistry instance with the specified algorithms.
        supported() -> Sequence[str]: Returns a sorted sequence of names of supported algorithms.
        __getitem__(name: str) -> _T: Retrieves the algorithm with the specified name from the registry.

    Example usage:
        # Create an AlgorithmRegistry instance with two algorithms
        registry = AlgorithmRegistry(algorithm1, algorithm2)

        # Get the names of supported algorithms
        supported_algorithms = registry.supported()

        # Retrieve an algorithm by its name
        algorithm = registry['algorithm1']
    """
    def __init__(self, *algorithms: _T):
        self._algorithms: dict[str, _T] = dict(
            (algo.__name__, algo)
            for algo in algorithms
        )

    def __iter__(self) -> Iterator[_T]:
        return iter(self._algorithms.values())

    @property
    def supported(self) -> Sequence[str]:
        """
        Returns a sorted sequence of supported algorithms.

        Returns:
            Sequence[str]: A sorted sequence of supported algorithms.
        """
        return sorted(self._algorithms)

    def __getitem__(self, name: str) -> _T:
        try:
            return self._algorithms[name]
        except KeyError:
            raise NameError(f'{name} not known. Supported names are {", ".join(self.supported)}')


def get_if_needed(get: Callable[[str], _T], value: _T | str) -> _T:
    """
    Args:
        get: A callable function that takes a string as input and returns a value.
        value: Either a value of type _T or a string. If it is a string, it will be passed to the "get" function to
        retrieve the corresponding value.

    Returns:
        A value of type _T. If the "value" parameter is not a string, it is returned as is. If it is a string, the
        "get" function is called with the string as input to retrieve the corresponding value, which is then returned.

    """
    return value if not isinstance(value, str) else get(value)