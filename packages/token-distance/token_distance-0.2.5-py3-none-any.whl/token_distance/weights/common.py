from collections.abc import Collection

from token_distance.types.token import Token, WeightedToken


def even_weight(tokens: Collection[Token]) -> Collection[WeightedToken]:
    """
    Assigns each token a weight of 1.

    Args:
        tokens: A collection of tokens.

    Returns:
        A collection of WeightedToken objects, where each token in the tokens collection is paired with a weight of 1.0.
    """
    return tuple(WeightedToken(token, 1.0) for token in tokens)


def length_based_weight(tokens: Collection[Token]) -> Collection[WeightedToken]:
    """
    Assigns each token it's length as weight

    Args:
        tokens: A collection of tokens.

    Returns:
        Collection[WeightedToken]: A collection of WeightedToken objects, where each object contains a token from the input collection with its corresponding length as the weight.
    """
    return tuple(WeightedToken(token, len(token)) for token in tokens)