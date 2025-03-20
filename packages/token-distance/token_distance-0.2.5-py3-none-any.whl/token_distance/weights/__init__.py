from collections.abc import Collection
from functools import partial
from operator import attrgetter
from typing import Protocol

from token_distance.types.registry import AlgorithmRegistry, HasName
from token_distance.types.token import Token, WeightedToken
from token_distance.weights.common import even_weight, length_based_weight


class Weight(HasName, Protocol):
    """ An interface representing a weight calculator for tokens. """
    def __call__(self, tokens: Collection[Token]) -> Collection[WeightedToken]:
        ...


_KNOWN_WEIGHTS: AlgorithmRegistry[Weight] = AlgorithmRegistry[Weight](
    even_weight, length_based_weight
)

get_supported_weights = partial(attrgetter('supported'), _KNOWN_WEIGHTS)
get_weight_by_name = _KNOWN_WEIGHTS.__getitem__

