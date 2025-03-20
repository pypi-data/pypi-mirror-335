from collections.abc import Callable, Sequence, Collection
from dataclasses import dataclass
from re import Pattern
from typing import NewType

Token = NewType('Token', str)


def parse_token(value: str) -> Token:
    return Token(value)

@dataclass(frozen=True)
class WeightedToken:
    """
    A class representing a weighted token.

    Attributes:
        token (Token): The token object.
        weight (float): The weight of the token.

    Raises:
        AttributeError: If the weight is not a positive number.

    Example usage:
        token = Token(value='apple')
        weighted_token = WeightedToken(token=token, weight=0.5)
    """
    token: Token
    weight: float

    def __post_init__(self):
        if self.weight <= 0:
            raise AttributeError('Weights must be positive numbers.')

    def __str__(self) -> str:
        return str(self.token)


@dataclass(frozen=True)
class EvaluatedToken(WeightedToken):
    """
    Data class representing an evaluated token.

    Attributes:
        similarity (float): The similarity value of the token.
        is_distance (bool): Flag indicating whether the similarity represents a distance.
    """
    similarity: float
    is_distance: bool = False

    def __lt__(self, other) -> bool:
        if self.is_distance:
            return other.similarity < self.similarity
        else:
            return self.similarity < other.similarity

    def __float__(self) -> float:
        return float(self.similarity * self.weight)

    @classmethod
    def add_similarity(cls, token: WeightedToken, similarity: float, *, is_distance: bool = False) -> 'EvaluatedToken':
        """Adds similarity to a weighted token and returns an evaluated token.

        Args:
            token: A WeightedToken object representing the token.
            similarity: A float representing the similarity value to be added.
            is_distance: An optional boolean indicating whether the similarity value is a distance measure
                         (default is False).

        Returns:
            An evaluated token object with the updated similarity value.
        """
        return cls(token.token, token.weight, similarity, is_distance)


@dataclass(frozen=True)
class RecordingToken(EvaluatedToken):
    """
    The `RecordingToken` class is a subclass of `EvaluatedToken` and represents a token that has been matched with a
    specific value.

    Attributes:
        token (Token): The token object.
        weight (float): The weight of the token.
        similarity (float): The similarity value of the token.
        is_distance (bool): Flag indicating whether the similarity represents a distance.
        matched_with (str | None): The value the token has been matched with.
        matched_token_position (int | None): The position of the matched token in the recording.
    """
    matched_with: str | None = None
    matched_token_position: int | None = None

    @classmethod
    def matched_from(cls, token: EvaluatedToken, match: str | None) -> 'RecordingToken':
        """
        Args:
            token: An instance of the EvaluatedToken class representing the token.
            match: A string representing the match value.

        Returns:
            An instance of the RecordingToken class.

        """
        return RecordingToken(token.token, token.weight, token.similarity, token.is_distance, match)



def split_text_by(
    text: str,
    by: Callable[[str], Sequence[str]] | Pattern | str | None = None
) -> Collection[str]:
    """
    Splits the given text by a specific delimiter.

    Args:
        text: A string representing the text to be split.
        by: A delimiter for splitting the text. It can be a callable function, a regular expression pattern,
            a string, or None. If None is provided, the text is split using whitespace.

    Returns:
        A collection of strings obtained by splitting the text according to the specified delimiter.

    Raises:
        ValueError: If the 'by' argument is not a valid type.

    Note:
        The 'by' argument can be one of the following types:
            - Callable: A function that takes a string as input and returns a sequence of strings.
            - Pattern: A regular expression pattern object.
            - str: A string representing the delimiter to split the text.
            - None: If None is provided, the text is split using whitespace.
    """
    if by is None:
        return text.split()
    if isinstance(by, Pattern):
        return by.split(text)
    if isinstance(by, str):
        return text.split(by)
    if callable(by):
        return by(text)
    else:
        raise ValueError("Invalid 'by' argument")