from collections import Counter
from itertools import chain

from jellyfish import jaro_winkler_similarity, levenshtein_distance

from token_distance.types.token import WeightedToken, EvaluatedToken


def jaro_winkler(left: WeightedToken, right: str) -> EvaluatedToken:
    """
    Args:
        left: A WeightedToken object representing the left token.
        right: A string representing the right token.

    Returns:
        An EvaluatedToken object representing the token with the computed Jaro-Winkler similarity added.

    """
    return EvaluatedToken.add_similarity(left, jaro_winkler_similarity(left.token, right))


def levenshtein(left: WeightedToken, right: str) -> EvaluatedToken:
    """
    Args:
        left: A WeightedToken object representing the left token.
        right: A string representing the right token.

    Returns:
        An EvaluatedToken object after calculating and adding the similarity between the left and right tokens using the
        Levenshtein distance algorithm. The similarity is added as a distance value.
    """
    return EvaluatedToken.add_similarity(left, levenshtein_distance(left.token, right), is_distance=True)


def jaccard(left: WeightedToken, right: str) -> EvaluatedToken:
    """
    Calculates the Jaccard distance between a weighted token and a string.

    Args:
        left: WeightedToken object representing the weighted token.
        right: String representing the second token.

    Returns:
        EvaluatedToken object with the calculated similarity.
    """
    left_counts: Counter = Counter(left.token)
    right_counts: Counter = Counter(right)
    difference: int = sum(
        abs(left_counts.get(key, 0) - right_counts.get(key, 0))
        for key in set(chain(left_counts, right_counts))
    )
    return EvaluatedToken.add_similarity(left, difference / max(len(left.token), len(right)), is_distance=True)
