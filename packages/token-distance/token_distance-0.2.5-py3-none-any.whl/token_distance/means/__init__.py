from collections.abc import Collection
from functools import partial
from operator import attrgetter
from typing import Protocol

from token_distance.means.base import average, harmonic, geometric
from token_distance.types.registry import AlgorithmRegistry, HasName
from token_distance.types.token import EvaluatedToken


class Mean(HasName, Protocol):
    """
    Calculate the mean value of a collection of evaluated tokens.

    This class defines a protocol for calculating the mean value of a collection of evaluated tokens.
    The `__call__` method takes a collection of evaluated tokens as input and returns the mean value as a float.

    Example usage:
        mean = Mean()
        values = [0.5, 1.5, 2.5]
        result = mean(values) # returns 1.5
    """
    def __call__(self, values: Collection[EvaluatedToken]) -> float:
        ...


_KNOWN_MEANS: AlgorithmRegistry[Mean] = AlgorithmRegistry[Mean](
    average, harmonic, geometric
)


supported_means = partial(attrgetter('supported'), _KNOWN_MEANS)
get_mean_by_name = _KNOWN_MEANS.__getitem__

