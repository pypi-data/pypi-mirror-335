from collections.abc import Callable, Collection, Sequence
from dataclasses import replace, dataclass
from functools import partial
from operator import attrgetter
from re import Pattern
from typing import Protocol

from token_distance.similarities import RecordingSimilarity, as_recording, Similarity, jaro_winkler, \
    get_similarity_by_name
from token_distance.types.registry import get_if_needed
from token_distance.types.token import WeightedToken, RecordingToken, Token, split_text_by, parse_token
from token_distance.weights import Weight, even_weight, get_weight_by_name


class TokenMatchingAlgorithm(Protocol):
    """
    TokenMatchingAlgorithm is a protocol for classes implementing the token matching algorithm.

    The protocol requires the class to define a __call__ method that takes two string arguments,
    'left' and 'right', and returns a collection of RecordingToken objects.

    Attributes:
        - left (str): The left string for token matching.
        - right (str): The right string for token matching.

    Returns:
        Collection[RecordingToken]: A collection of RecordingToken objects.

    """
    def __call__(self, left: str, right: str) -> Collection[RecordingToken]:
        ...


def match_tokens(
    similarity: Similarity,
    weight: Weight,
    exclusive: bool,
    tokens: Collection[Token],
    candidates: Collection[str]
) -> Collection[RecordingToken]:
    """
    Match Tokens

    Matches tokens against a collection of candidates using similarity and weight.

    Args:
        similarity (Similarity): The similarity function to compare tokens and candidates.
        weight (Weight): The weight function to assign weights to tokens.
        exclusive (bool, optional): If set to True, only one candidate will be matched per token. Defaults to False.
        tokens (Collection[Token]): The collection of tokens to be matched.
        candidates (Collection[str]): The collection of candidates to match against.


    Returns:
        Collection[RecordingToken]: The collection of matched tokens with additional recording information.

    """
    remaining_candidates: list[str] = list(candidates)
    recording_sim: RecordingSimilarity = as_recording(similarity)
    weighted_tokens: list[WeightedToken] = sorted(weight(tokens), key=attrgetter('weight'), reverse=True)
    evaluated_tokens: list[RecordingToken] = list()
    for token in weighted_tokens:
        if not remaining_candidates:
            evaluated_tokens.append(RecordingToken.matched_from(similarity(token, ''), None))
        else:
            evaluate: Callable[[str], RecordingToken] = partial(recording_sim, token)
            best: RecordingToken = max(map(evaluate, remaining_candidates))
            evaluated_tokens.append(
                replace(
                    best,
                    matched_token_position=remaining_candidates.index(best.matched_with)
                ) if best.matched_with else best
            )
            if best.matched_with is not None and exclusive:
                remaining_candidates.remove(best.matched_with)
    return evaluated_tokens


@dataclass
class MatchConfig:
    """
    The MatchConfig class represents the configuration for matching operations.

    Attributes:
        similarity (Similarity | str): The similarity function or strategy to use for matching. Defaults to "jaro_winkler".
        weight (Weight | str): The weighting strategy to use for matching. Defaults to "even_weight".
        tokenize (Callable[[str], Sequence[str]] | Pattern | str | None): The tokenizer function, regular expression pattern,
            or string separator to use for tokenization. Defaults to None.
        exclusive (bool): Indicates whether the matching should be exclusive, i.e., matching results should only include
            exact matches. Defaults to False.
    """
    similarity: Similarity | str = jaro_winkler
    weight: Weight | str = even_weight
    tokenize: Callable[[str], Sequence[str]] | Pattern | str | None = None
    exclusive: bool = False


def match_from_config(config: MatchConfig) -> TokenMatchingAlgorithm:
    """
    Args:
        config: MatchConfig object that holds the configuration settings for the token matching algorithm.

    Returns:
        TokenMatchingAlgorithm object that performs token matching based on the given configuration.

    """
    base_algorithm: Callable[
        [Collection[Token], Collection[str]], Collection[RecordingToken]
    ] = partial(
        match_tokens,
        get_if_needed(get_similarity_by_name, config.similarity),
        get_if_needed(get_weight_by_name, config.weight),
        config.exclusive
    )

    def matching(left: str, right: str) -> Collection[RecordingToken]:
        """
        Args:
            left: Token text
            right: Text to search in

        Returns:
            Collection of matched tokens

        """
        tokens = list(map(parse_token, split_text_by(left, config.tokenize)))
        candidates = split_text_by(right, config.tokenize)
        return base_algorithm(tokens, candidates)

    return matching