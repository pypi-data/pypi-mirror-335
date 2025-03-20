from functools import partial, wraps
from operator import attrgetter
from typing import Protocol

from token_distance.similarities.base import levenshtein, jaro_winkler, jaccard
from token_distance.types.registry import AlgorithmRegistry, HasName
from token_distance.types.token import WeightedToken, EvaluatedToken, RecordingToken


class Similarity(HasName, Protocol):
    """

    Protocol `Similarity` defines the contract for calculating similarity between a `WeightedToken` and a string.

    The `Similarity` class implements the `__call__` method, which takes a `WeightedToken` object as `left` and a string
    as `right`, and returns an `EvaluatedToken` object.

    """
    def __call__(self, left: WeightedToken, right: str) -> EvaluatedToken:
        ...


class RecordingSimilarity(Similarity, Protocol):
    """
    Module: RecordingSimilarity

    This module provides the class `RecordingSimilarity` which is responsible for calculating the similarity between a
    `WeightedToken` and a `str` recording the match.
    """
    def __call__(self, left: WeightedToken, right: str) -> RecordingToken:
        ...


def as_recording(similarity: Similarity) -> RecordingSimilarity:
    """
    Creates a RecordingSimilarity from an ordinary Similarity.

    Args:
        similarity: The similarity function to be wrapped.

    Returns:
        A RecordingSimilarity object that wraps around the similarity function and returns RecordingToken objects.
    """
    @wraps(similarity)
    def _wrapped(left: WeightedToken, right: str) -> RecordingToken:
        return RecordingToken.matched_from(similarity(left, right), right)
    return _wrapped


_KNOWN_SIMILARITIES: AlgorithmRegistry[Similarity] = AlgorithmRegistry[Similarity](
    levenshtein, jaro_winkler, jaccard
)

get_supported_similarities = partial(attrgetter('supported'), _KNOWN_SIMILARITIES)
get_similarity_by_name = _KNOWN_SIMILARITIES.__getitem__


