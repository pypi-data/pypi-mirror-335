from collections.abc import Collection
from functools import reduce
from operator import attrgetter, mul

from token_distance.types.token import EvaluatedToken


def average(values: Collection[EvaluatedToken]) -> float:
    """
    Calculates the average of a collection of evaluated tokens.

    Args:
        values: A collection of evaluated tokens.

    Returns:
        The average value as a float.

    """
    if not values:
        return 0.0
    return sum(map(float, values)) / sum(map(attrgetter('weight'), values))


def geometric(values: Collection[EvaluatedToken]) -> float:
    """
    Calculate the geometric mean of a collection of evaluated tokens.

    Args:
        values (Collection[EvaluatedToken]): A collection of evaluated tokens.

    Returns:
        float: The geometric mean of the given collection of evaluated tokens. If the collection is empty, 0.0 is
        returned.

    Note:
        The geometric mean is calculated by multiplying all the token values, converting them to floats, and then taking
        the nth root, where n is the sum of the weights of the tokens.
    """
    if not values:
        return 0.0
    weights: float = sum(map(attrgetter('weight'), values))
    return reduce(mul, (value.similarity ** value.weight for value in values)) ** (1.0 / weights)


def harmonic(values: Collection[EvaluatedToken]) -> float:
    """
    Calculates the harmonic mean of a collection of evaluated tokens.

    Args:
        values: A collection of evaluated tokens.

    Returns:
        The harmonic mean as a float.
    """
    if not values:
        return 0.0
    weights: float = sum(map(attrgetter('weight'), values))
    try:
        return weights / sum(token.weight / token.similarity for token in values)
    except ZeroDivisionError:
        return 0.0