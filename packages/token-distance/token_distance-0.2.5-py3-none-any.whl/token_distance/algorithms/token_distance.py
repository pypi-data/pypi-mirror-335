from collections.abc import Collection, Callable, Sequence
from dataclasses import dataclass
from functools import partial
from re import Pattern
from typing import TypeVar, Protocol

from token_distance.algorithms.token_matching import match_tokens
from token_distance.means import Mean, average, get_mean_by_name
from token_distance.similarities import Similarity, jaro_winkler, get_similarity_by_name
from token_distance.types.registry import get_if_needed
from token_distance.types.token import WeightedToken, Token, EvaluatedToken, split_text_by, parse_token
from token_distance.weights import Weight, even_weight, get_weight_by_name


def token_distance(
    similarity: Similarity,
    mean: Mean,
    weight: Weight,
    tokens: Collection[Token],
    candidates: Collection[str]
) -> float:
    """
    Calculate the token distance between a collection of tokens and a collection of candidates.

    Args:
        similarity (Similarity): A function that calculates the similarity between two tokens.
        mean (Mean): A function that calculates the mean value of a collection of values.
        weight (Weight): A function that assigns weights to tokens.
        tokens (Collection[Token]): A collection of tokens.
        candidates (Collection[str]): A collection of candidate strings.

    Returns:
        float: The token distance between the tokens and candidates.
    """
    weighted_tokens: Collection[WeightedToken] = weight(tokens)
    evaluated_tokens: Collection[EvaluatedToken] = [
        max(similarity(token, candidate) for candidate in candidates)
        for token in weighted_tokens
    ]
    return mean(evaluated_tokens)




def exclusive_token_distance(
    similarity: Similarity,
    mean: Mean,
    weight: Weight,
    tokens: Collection[Token],
    candidates: Collection[str]
) -> float:
    """
    Calculate the token distance between a collection of tokens and a collection of candidates.
    If a token gets matched to a candidate, this candidate will no longer be matchable for other tokens,
    if not multiple instances of candidate exist in the text.

    Args:
        similarity: A Similarity instance used for calculating token similarity.
        mean: A Mean instance used for calculating the mean of evaluated tokens.
        weight: A Weight instance used for weighting tokens.
        tokens: A collection of Token instances representing the tokens to be evaluated.
        candidates: A collection of strings representing the candidate tokens to compare with.

    Returns:
        float: The result of applying the mean function to the evaluated tokens.

    """
    return mean(match_tokens(similarity, weight, True, tokens, candidates))


@dataclass
class Config:
    """
    Config represents the configuration options for token distance.

    Attributes:
        similarity (Similarity | str): The similarity metric to be used. Defaults to 'jaro_winkler'.
        mean (Mean | str): The mean calculation method to be used. Defaults to 'average'.
        weight (Weight | str): The weighting method to be used. Defaults to 'even_weight'.
        tokenize (Callable[[str], Sequence[str]] | Pattern | str | None): The tokenization method to be used.
            Defaults to None.
        exclusive (bool): Whether exclusive matching should be used. Defaults to False.
    """
    similarity: Similarity | str = jaro_winkler
    mean: Mean | str = average
    weight: Weight | str = even_weight
    tokenize: Callable[[str], Sequence[str]] | Pattern | str | None = None
    exclusive: bool = False


_T = TypeVar('_T')





class TokenDistanceAlgorithm(Protocol):
    """
    This class represents a token distance algorithm.

    Methods:
    - __call__: Calculates the token distance between two strings.

    """
    def __call__(self, left: str, right: str) -> float:
        ...



def from_config(config: Config = Config()) -> TokenDistanceAlgorithm:
    """
    Constructs a TokenDistanceAlgorithm function based on the provided configuration.

    Args:
        config: A Config object containing the algorithm configuration.

    Returns:
        A TokenDistanceAlgorithm function that calculates the distance between two strings.
    """
    base_algorithm: Callable[
        [Similarity, Mean, Weight, Collection[Token], Collection[str]],
        float
    ] = exclusive_token_distance if config.exclusive else token_distance

    algorithm: Callable[[Collection[Token], Collection[str]], float] = partial(
        base_algorithm,
        get_if_needed(get_similarity_by_name, config.similarity),
        get_if_needed(get_mean_by_name, config.mean),
        get_if_needed(get_weight_by_name, config.weight),
    )

    def distance(left: str, right: str) -> float:
        """
        Args:
            left: A string representing the left text.
            right: A string representing the right text.

        Returns:
            A float representing the token distance between the left and right texts.
        """
        return algorithm(
            tuple(map(parse_token, split_text_by(left, config.tokenize))),
            split_text_by(right, config.tokenize)
        )

    return distance



