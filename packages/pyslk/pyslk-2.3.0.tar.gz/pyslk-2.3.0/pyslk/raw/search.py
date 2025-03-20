import inspect
import subprocess
from pathlib import Path
from typing import Union

from ..constants import PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS, SLK, SLK_HELPERS
from ..pyslk_exceptions import PySlkException
from ..utils import run_slk, which

__all__ = [
    "gen_file_query_raw",
    "gen_search_query_raw",
    "searchid_exists_raw",
    "search_immediately_raw",
    "search_incomplete_raw",
    "search_raw",
    "search_status_raw",
    "search_successful_raw",
    "tnsr_raw",
    "total_number_search_results_raw",
]


def search_raw(
    search_string: Union[str, None] = None,
    group: Union[str, int, None] = None,
    user: Union[str, int, None] = None,
    name: Union[str, None] = None,
    partial: bool = False,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """Creates search and returns search id

    Either group, user and/or name can be set
    or a search_string can be provided.

    search_string has to be a valid JSON search string as described in the
    SLK-CLI manual. Simple double quotes have to be used in the JSON
    expression (no escaped double quotes, no escaped special characters).

    Example for search_string:
      search_string='{"resources.mtime": {"$gt": "2021-09-02"}}'

    :param search_string: JSON search query string
    :type search_string: str
    :param group: search for files belonging to the provided group name or GID
    :type group: str or int
    :param user: search for files belonging to the provided username or UID
    :type user: str or int
    :param name: search files having the provided name
    :type name: str
    :param partial: search for files with 'partial file' flag
    :type partial: bool
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK) is None:
        raise PySlkException(f"pyslk: {SLK}: command not found")

    slk_call = SLK + " search"

    if group is not None:
        if isinstance(group, (str, int)):
            slk_call = slk_call + " -group " + str(group)
        else:
            raise TypeError(
                f'pyslk.{inspect.stack()[0][3]}: argument "group" needs to be "str" or "int" but got '
                + f'"{type(group).__name__}".'
            )
    if user is not None:
        if isinstance(user, (str, int)):
            slk_call = slk_call + " -user " + str(user)
        else:
            raise TypeError(
                f'pyslk.{inspect.stack()[0][3]}: argument "user" needs to be "str" or "int" but got '
                + f'"{type(user).__name__}".'
            )
    if name is not None:
        if isinstance(name, str):
            slk_call = slk_call + " -name " + str(name)
        else:
            raise TypeError(
                f'pyslk.{inspect.stack()[0][3]}: argument "name" needs to be "str" but got "{type(group).__name__}".'
            )
    if partial:
        slk_call = slk_call + " -partial"
    if search_string is not None:
        if isinstance(search_string, str):
            slk_call = slk_call + f" '{search_string}'"
        else:
            raise TypeError(
                f'pyslk.{inspect.stack()[0][3]}: argument "search_string" needs to be "str" but got '
                + f'"{type(search_string).__name__}".'
            )

    if return_type == 0:
        return run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
        )
    elif return_type == 1:
        return run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
            handle_output=False,
        ).returncode
    elif return_type == 2:
        return run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
            handle_output=False,
        )
    else:
        raise ValueError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'return_type' needs to be 0, 1 or 2."
        )


def searchid_exists_raw(
    search_id: Union[str, int], return_type: int = 0
) -> Union[str, int, subprocess.CompletedProcess]:
    """Check if search id exists

    :param search_id: a search_id
    :type search_id: str or int
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    if not isinstance(search_id, (str, int)):
        raise TypeError(
            f'pyslk.{inspect.stack()[0][3]}: "search_id" has to be of type "str" or "int" but is '
            + f"{type(search_id).__name__}"
        )

    slk_call = [SLK_HELPERS, "searchid_exists", str(search_id)]

    if return_type == 0:
        return run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
        )
    elif return_type == 1:
        return run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
            handle_output=False,
        ).returncode
    elif return_type == 2:
        return run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
            handle_output=False,
        )
    else:
        raise ValueError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'return_type' needs to be 0, 1 or 2."
        )


def gen_file_query_raw(
    resources: Union[str, list, Path],
    recursive: bool = False,
    no_newline: bool = False,
    cached_only: bool = False,
    not_cached: bool = False,
    tape_barcodes: Union[list[str], str, None] = None,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
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
    :type resources: str or list or Path
    :param recursive: do recursive search in the namespaces
    :type recursive: bool
    :param no_newline: do recursive search in the namespaces
    :type no_newline: bool
    :param cached_only: do recursive search in the namespaces
    :type cached_only: bool
    :param not_cached: do recursive search in the namespaces
    :type not_cached: bool
    :param tape_barcodes: do recursive search in the namespaces
    :type tape_barcodes: list[str]
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    slk_call = [SLK_HELPERS, "gen_file_query"]
    if recursive:
        slk_call.append("-R")
    if isinstance(resources, str):
        slk_call.extend(resources.split(" "))
    elif isinstance(resources, Path):
        slk_call.append(str(resources))
    elif isinstance(resources, list):
        if not all([isinstance(r, (str, Path)) for r in resources]):
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: if argument 'resources' is of type 'list' its items need to be"
                + "of type 'str' or Path-like but got type(s): "
                + f"'{', '.join([type(r).__name__ for r in resources if not isinstance(r, (str, Path))])}'."
            )
        slk_call.extend(resources)
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'resources' has to be 'str' or 'list' of 'str' but is "
            + f"'{type(resources).__name__}'"
        )
    if no_newline:
        slk_call.append("--no-newline")
    if cached_only:
        slk_call.append("--cached-only")
    if not_cached:
        slk_call.append("--not-cached")
    if tape_barcodes is not None:
        slk_call.append("--tape-barcodes")
        if isinstance(tape_barcodes, str):
            slk_call.extend(tape_barcodes.split(" "))
        elif isinstance(tape_barcodes, list):
            slk_call.extend(tape_barcodes)
        else:
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: argument 'tape_barcodes' has to be 'str' or 'list' of 'str' but is "
                + f"'{type(tape_barcodes).__name__}'"
            )

    if return_type == 0:
        return run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
        )
    elif return_type == 1:
        return run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
            handle_output=False,
        ).returncode
    elif return_type == 2:
        return run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
            handle_output=False,
        )
    else:
        raise ValueError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'return_type' needs to be 0, 1 or 2."
        )


def gen_search_query_raw(
    key_value_pairs: Union[str, list[str]],
    recursive: bool = False,
    search_query: Union[str, None] = None,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """Generates a search query that searches based on the conditions provided as key-values pairs

    These key-value pairs are actually key-operator-value-triples. E.g.

    .. code-block::

        path=/arch/bm0146/k204221/iow
        resources.size < 1024
        resources.created > 2023-01-01

    Details are given in the slk_helpers documentation at https://docs.dkrz.de

    :param key_value_pairs: list of key-value pairs connected via an operator
    :type key_value_pairs: str or list
    :param recursive: do recursive search in the namespaces
    :type recursive: bool
    :param search_query: an existing search query to be extended
    :type search_query: str
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    slk_call = [SLK_HELPERS, "gen_search_query"]
    if recursive:
        slk_call.append("-R")
    if isinstance(key_value_pairs, str):
        slk_call.append(key_value_pairs)
    elif isinstance(key_value_pairs, list):
        slk_call.extend(key_value_pairs)
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'key_value_pairs' has to be 'str' or 'list' of 'str' but is "
            + f"'{type(key_value_pairs).__name__}'"
        )
    if search_query is not None:
        slk_call.append("--search-query")
        if isinstance(search_query, str):
            slk_call.append(search_query)
        else:
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: argument 'search_query' has to be 'str' but is "
                + f"'{type(search_query).__name__}'"
            )

    if return_type == 0:
        return run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
        )
    elif return_type == 1:
        return run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
            handle_output=False,
        ).returncode
    elif return_type == 2:
        return run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
            handle_output=False,
        )
    else:
        raise ValueError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'return_type' needs to be 0, 1 or 2."
        )


def tnsr_raw(
    search_id: Union[str, int],
    quiet: bool = False,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """Print the total number of search results regardless of read permissions of the current user

    :param search_id: a search_id
    :type search_id: str or int
    :param quiet: should the command be quiet or print warnings?
    :type quiet: `bool`
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    return total_number_search_results_raw(search_id, quiet, return_type)


def total_number_search_results_raw(
    search_id: Union[str, int],
    quiet: bool = False,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """Print the total number of search results regardless of read permissions of the current user

    :param search_id: a search_id
    :type search_id: str or int
    :param quiet: should the command be quiet or print warnings?
    :type quiet: `bool`
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    if not isinstance(search_id, (str, int)):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'search_id' has to be of type 'str' or 'int' but is "
            + f"{type(search_id).__name__}"
        )

    slk_call = [SLK_HELPERS, "total_number_search_results", str(search_id)]

    if quiet:
        slk_call.append("-q")

    if return_type == 0:
        return run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
        )
    elif return_type == 1:
        return run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
            handle_output=False,
        ).returncode
    elif return_type == 2:
        return run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
            handle_output=False,
        )
    else:
        raise ValueError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'return_type' needs to be 0, 1 or 2."
        )


def search_immediately_raw(
    search_string: str, return_type: int = 0
) -> Union[str, int, subprocess.CompletedProcess, subprocess.Popen]:
    """
    submits a search query string to StrongLink and immediately returns the search id; search not finished

    :param search_string: JSON search query string
    :type search_string: `str`
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output), 3 (running subproc.)
    :type return_type: `int`
    :returns: stdout of the slk call
    :rtype: `Union[str, int, subprocess.CompletedProcess, subprocess.Popen]`
    """
    if which(SLK_HELPERS) is None:
        raise RuntimeError(f"pyslk: {SLK_HELPERS}: command not found")

    slk_call = SLK_HELPERS + " search_immediately"

    if search_string is None:
        raise ValueError(
            f'pyslk.{inspect.stack()[0][3]}: argument "search_string" has to have a value unequal'
            ' "None"'
        )
    else:
        if isinstance(search_string, str):
            slk_call = slk_call + f" '{search_string}'"
        else:
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: 'search_string' has wrong type; need 'str' but got "
                + f"'{type(search_string).__name__}'"
            )

    if return_type == 0:
        return run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
        )
    elif return_type == 1:
        return run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
            handle_output=False,
        ).returncode
    elif return_type == 2:
        return run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
            handle_output=False,
        )
    elif return_type == 3:
        return run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
            handle_output=False,
            wait_until_finished=False,
        )
    else:
        raise ValueError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'return_type' needs to be 0, 1 or 2."
        )


def search_incomplete_raw(
    search_id: Union[str, int], return_type: int = 0
) -> Union[str, int, subprocess.CompletedProcess]:
    """Check if search is incomplete

    :param search_id: a search_id
    :type search_id: `str` or `int`
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: `int`
    :returns: stdout of the slk call
    :rtype: `Union[str, int, subprocess.CompletedProcess]`
    """
    if which(SLK_HELPERS) is None:
        raise RuntimeError(f"pyslk: {SLK_HELPERS}: command not found")

    if not isinstance(search_id, (str, int)):
        raise TypeError(
            f'pyslk.{inspect.stack()[0][3]}: "search_id" has to be of type "str" or "int" but is '
            + f"{type(search_id).__name__}"
        )
    if isinstance(search_id, str):
        try:
            int(search_id)
        except ValueError:
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: 'search_id' cannot be processed; need 'str', which holds an "
                + f"integer number, or 'int' but got '{type(search_id).__name__}' with value '{search_id}'"
            )

    slk_call = [SLK_HELPERS, "search_incomplete", str(search_id)]

    if return_type == 0:
        return run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
        )
    elif return_type == 1:
        return run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
            handle_output=False,
        ).returncode
    elif return_type == 2:
        return run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
            handle_output=False,
        )
    else:
        raise ValueError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'return_type' needs to be 0, 1 or 2."
        )


def search_status_raw(
    search_id: Union[str, int], json: bool = False, return_type: int = 0
) -> Union[str, int, subprocess.CompletedProcess]:
    """Check if search is successful

    :param search_id: a search_id
    :type search_id: `str` or `int`
    :param json: if the output should be in json format
    :type json: `bool`
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: `int`
    :returns: stdout of the slk call
    :rtype: `Union[str, int, subprocess.CompletedProcess]`
    """
    if which(SLK_HELPERS) is None:
        raise RuntimeError(f"pyslk: {SLK_HELPERS}: command not found")

    if not isinstance(search_id, (str, int)):
        raise TypeError(
            f'pyslk.{inspect.stack()[0][3]}: "search_id" has to be of type "str" or "int" but is '
            + f"{type(search_id).__name__}"
        )
    if isinstance(search_id, str):
        try:
            int(search_id)
        except ValueError:
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: 'search_id' cannot be processed; need 'str', which holds an "
                + f"integer number, or 'int' but got '{type(search_id).__name__}' with value '{search_id}'"
            )

    slk_call = [SLK_HELPERS, "search_status", str(search_id)]

    # --json
    if not isinstance(json, bool):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'json' has wrong type; need 'bool' but got "
            + f"'{type(json).__name__}'"
        )
    if json:
        slk_call.append("--json")

    if return_type == 0:
        return run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
        )
    elif return_type == 1:
        return run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
            handle_output=False,
        ).returncode
    elif return_type == 2:
        return run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
            handle_output=False,
        )
    else:
        raise ValueError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'return_type' needs to be 0, 1 or 2."
        )


def search_successful_raw(
    search_id: Union[str, int], return_type: int = 0
) -> Union[str, int, subprocess.CompletedProcess]:
    """Check if search is successful

    :param search_id: a search_id
    :type search_id: `str` or `int`
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: `int`
    :returns: stdout of the slk call
    :rtype: `Union[str, int, subprocess.CompletedProcess]`
    """
    if which(SLK_HELPERS) is None:
        raise RuntimeError(f"pyslk: {SLK_HELPERS}: command not found")

    if not isinstance(search_id, (str, int)):
        raise TypeError(
            f'pyslk.{inspect.stack()[0][3]}: "search_id" has to be of type "str" or "int" but is '
            + f"{type(search_id).__name__}"
        )
    if isinstance(search_id, str):
        try:
            int(search_id)
        except ValueError:
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: 'search_id' cannot be processed; need 'str', which holds an "
                + f"integer number, or 'int' but got '{type(search_id).__name__}' with value '{search_id}'"
            )

    slk_call = [SLK_HELPERS, "search_successful", str(search_id)]

    if return_type == 0:
        return run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
        )
    elif return_type == 1:
        return run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
            handle_output=False,
        ).returncode
    elif return_type == 2:
        return run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
            handle_output=False,
        )
    else:
        raise ValueError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'return_type' needs to be 0, 1 or 2."
        )
