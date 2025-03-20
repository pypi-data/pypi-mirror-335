from argparse import ArgumentParser
from errno import EINVAL, ENOENT, EPERM
from pathlib import Path
from re import Pattern, compile as regex, error as RegexError
from sys import stderr, exit

from token_distance.algorithms.token_distance import from_config, Config
from token_distance.means import supported_means
from token_distance.similarities import get_supported_similarities
from token_distance.weights import get_supported_weights


def compare_files() -> None:
    """
    Calculates token distance between two files.
    """
    parser: ArgumentParser = ArgumentParser('Calculates token distance between two files.')
    parser.add_argument('token', type=Path, help='Path to the first file containing the tokens to search.')
    parser.add_argument('data', type=Path, help='Path to the second file to be searched in.')
    parser.add_argument(
        '--similarity', default='jaro_winkler', choices=set(get_supported_similarities()),
        help='Similarity to calculate token distance (JaroWinkler)'
    )
    parser.add_argument(
        '--weight', default='even_weight', choices=set(get_supported_weights()),
        help='Weight strategy to calculate token weights (Even)'
    )
    parser.add_argument(
        '--mean', default='average', choices=set(supported_means()),
        help='Aggregating function to calculate distance form token distance (Average)'
    )
    parser.add_argument(
        '--exclusive', type=bool, default=False,
        help='Matched words cannot be matched again (False)'
    )
    parser.add_argument('--tokenize-by', default=None, help='Token to split text (Whitespace)')
    parser.add_argument('--regex', default=False, help='Interpret tokenize-by as regex (False)')
    parser.add_argument('--token-encoding', type=str, default='utf-8', help='Token file encoding (UTF8)')
    parser.add_argument('--search-encoding', type=str, default='utf-8', help='Search file encoding (UTF8)')
    parser.add_argument('--errors', type=str, default='replace', help='Encoding error handling. (replace)')
    args = parser.parse_args()
    try:
        with args.token.open(encoding=args.token_encoding, errors=args.errors) as src:
            token_content: str = src.read()
        with args.data.open(encoding=args.search_encoding, errors=args.errors) as src:
            search_content: str = src.read()

        tokenize_by: str | Pattern | None = args.tokenize_by
        if args.regex:
            tokenize_by = regex(tokenize_by) if tokenize_by else None
            if tokenize_by is None:
                print("Warning: Ignoring --regex flag as --tokenize-by is not set", file=stderr)

        distance: float = from_config(
            Config(args.similarity, args.mean, args.weight, tokenize_by, args.exclusive)
        )(token_content, search_content)
        print(f"Token distance: {distance}")
    except RegexError as error:
        print(f"Error parsing regular expression: {error}", file=stderr)
        exit(EINVAL)
    except FileNotFoundError as error:
        print(f"File does not exist: {error}", file=stderr)
        exit(ENOENT)
    except PermissionError as error:
        print(f"Unsufficient rights to open files: {error}", file=stderr)
        exit(EPERM)
    except Exception as error:
        print(f'Error: {error}', file=stderr)
        exit(1)






