import inspect
import json
from pathlib import Path
from typing import Union

from ..constants import SEARCH_QUERY_OPERATORS
from ..raw import gen_file_query_raw, gen_search_query_raw
from .resource_extras import is_namespace

__all__ = [
    "gen_file_query",
    "gen_search_query",
    "gen_file_query_as_dict",
]


def gen_file_query(
    resources: Union[str, list[str], set[str], Path, list[Path], set[Path]],
    recursive: bool = False,
    cached_only: bool = False,
    not_cached: bool = False,
    tape_barcodes: Union[list[str], str, None] = None,
) -> str:
    """Generates a search query that searches for the listed resources

    A search query will be generated which connects all elements of
    'resources' with and 'or'. A 'resource' (an element of 'resources')
    might be one of these:

    - a filename with full path (e.g. /arch/bm0146/k204221/INDEX.txt)
    - a filename without full path (e.g. INDEX.txt)
    - a regex describing a filename (e.g. /arch/bm0146/k204221/.*.txt)
    - a namespace (e.g. /arch/bm0146/k204221 or /arch/bm0146/k204221/)

    Details are given in the slk_helpers documentation at https://docs.dkrz.de

    :param resources: list of resources to be searched for
    :type resources: ``str`` or ``list`` or ``set`` or ``Path``
    :param recursive: do recursive search in the namespaces
    :type recursive: ``bool``
    :param cached_only: do recursive search in the namespaces
    :type cached_only: ``bool``
    :param not_cached: do recursive search in the namespaces
    :type not_cached: ``bool``
    :param tape_barcodes: do recursive search in the namespaces
    :type tape_barcodes: ``list[str]``
    :returns: generated search query
    :rtype: ``str``
    """
    if isinstance(resources, (str, Path)):
        if is_namespace(resources) and not recursive:
            raise ValueError(
                f"pyslk.{inspect.stack()[0][3]}: when 'resources' points to a namespace, 'recursive' has to be set "
                + "to 'True'"
            )
    if isinstance(resources, (list, set)):
        if any([is_namespace(r) for r in resources]) and not recursive:
            raise ValueError(
                f"pyslk.{inspect.stack()[0][3]}: when 'resources' points to at least one namespace, 'recursive' has to "
                + "be set to 'True'"
            )

    output = gen_file_query_raw(
        resources, recursive, True, cached_only, not_cached, tape_barcodes
    )
    return output


def gen_search_query(
    key_value_pairs: Union[str, list[str], set[str]],
    recursive: bool = False,
    search_query: Union[str, None] = None,
) -> str:
    """Generates a search query that searches for the listed resources

    A search query will be generated which connects all elements of
    'resources' with and 'or'. A 'resource' (an element of 'resources')
    might be one of these:

    - a filename with full path (e.g. /arch/bm0146/k204221/INDEX.txt)
    - a filename without full path (e.g. INDEX.txt)
    - a regex describing a filename (e.g. /arch/bm0146/k204221/.*.txt)
    - a namespace (e.g. /arch/bm0146/k204221 or /arch/bm0146/k204221/)

    Details are given in the slk_helpers documentation at https://docs.dkrz.de

    :param key_value_pairs: list of key-value pairs connected via an operator
    :type key_value_pairs: ``str`` or ``list`` or ``set``
    :param recursive: do recursive search in the namespaces
    :type recursive: ``bool``
    :param search_query: an existing search query to be extended
    :type search_query: ``str``
    :returns: generated search query
    :rtype: ``str``
    """
    # type checking and check key-value-pairs for completeness
    if isinstance(key_value_pairs, str):
        if not any([o in key_value_pairs for o in SEARCH_QUERY_OPERATORS]):
            raise ValueError(
                f"pyslk.{inspect.stack()[0][3]}: argument 'key_value_pairs' has to be a triple of key-operator-value "
                + f"where the operator has one of these values: {', '.join(SEARCH_QUERY_OPERATORS)}"
            )
    elif isinstance(key_value_pairs, (list, set)):
        if not all([isinstance(kvp, str) for kvp in key_value_pairs]):
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: argument 'key_value_pairs' has to be 'str' or 'list' of 'str' but it"
                + "is 'list' which contains at least elements of these other types: "
                + f"'{', '.join([type(kvp).__name__ for kvp in key_value_pairs if not isinstance(kvp, str)])}'"
            )
        bad_key_values: list[str] = [
            kvp
            for kvp in key_value_pairs
            if not any([o in kvp for o in SEARCH_QUERY_OPERATORS])
        ]
        if len(bad_key_values) > 0:
            raise ValueError(
                f"pyslk.{inspect.stack()[0][3]}: argument 'key_value_pairs' has to be a triple of key-operator-value "
                + f"where the operator has one of these values: {', '.join(SEARCH_QUERY_OPERATORS)}; this triples "
                + f"have no matching operator: {', '.join(bad_key_values)}"
            )
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'key_value_pairs' has to be 'str' or 'list' of 'str' but is "
            + f"'{type(key_value_pairs).__name__}'"
        )
    if not isinstance(recursive, bool):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'recursive' has to be 'bool' but is "
            + f"'{type(search_query).__name__}'"
        )
    if search_query is not None:
        if not isinstance(search_query, str):
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: argument 'search_query' has to be 'str' but is "
                + f"'{type(search_query).__name__}'"
            )

    output: str = gen_search_query_raw(key_value_pairs, recursive, search_query)
    return output


def gen_file_query_as_dict(
    resources: Union[str, list[str], set[str], Path, list[Path], set[Path]],
    recursive: bool = False,
    cached_only: bool = False,
    not_cached: bool = False,
    tape_barcodes: Union[list[str], str, None] = None,
) -> dict:
    """Generates a search query that searches for the listed resources

    A search query will be generated which connects all elements of
    'resources' with and 'or'. A 'resource' (an element of 'resources')
    might be one of these:

    - a filename with full path (e.g. /arch/bm0146/k204221/INDEX.txt)
    - a filename without full path (e.g. INDEX.txt)
    - a regex describing a filename (e.g. /arch/bm0146/k204221/.*.txt)
    - a namespace (e.g. /arch/bm0146/k204221 or /arch/bm0146/k204221/)

    Details are given in the slk_helpers documentation at https://docs.dkrz.de

    :param resources: list of resources to be searched for
    :type resources: ``str`` or ``list`` or ``set`` or ``Path``
    :param recursive: do recursive search in the namespaces
    :type recursive: ``bool``
    :param cached_only: do recursive search in the namespaces
    :type cached_only: ``bool``
    :param not_cached: do recursive search in the namespaces
    :type not_cached: ``bool``
    :param tape_barcodes: do recursive search in the namespaces
    :type tape_barcodes: ``list[str]``
    :returns: generated search query
    :rtype: ``dict``
    """
    return json.loads(
        gen_file_query(
            resources=resources,
            recursive=recursive,
            cached_only=cached_only,
            not_cached=not_cached,
            tape_barcodes=tape_barcodes,
        )
    )
