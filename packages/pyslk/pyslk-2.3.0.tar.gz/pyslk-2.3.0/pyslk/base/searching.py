import inspect
import json
import re
import subprocess
import typing
from typing import Union

from ..pyslk_exceptions import PySlkException
from ..raw import (
    search_immediately_raw,
    search_incomplete_raw,
    search_raw,
    search_status_raw,
    search_successful_raw,
    searchid_exists_raw,
    total_number_search_results_raw,
)

__all__ = [
    "is_search_incomplete",
    "is_search_successful",
    "search",
    "search_immediately",
    "get_search_status",
    "searchid_exists",
    "total_number_search_results",
]


def search(search_string: str) -> int:
    """Performs a search based on a search_string can be provided.
    returns search id

    search_string has to be a valid JSON search string as described in the
    SLK-CLI manual. Simple double quotes have to be used in the JSON
    expression (no escaped double quotes, no escaped special characters).

    :param search_string: JSON search query string
    :type search_string: ``str``
    :returns: search id of the performed search
    :rtype: ``int``

    .. rubric:: Examples

    .. code-block:: python

        search_string='{"resources.mtime": {"$gt": "2021-09-02"}}'
    """
    if not isinstance(search_string, str):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'search_string' has wrong type; need 'str' but got "
            + f"{type(search_string).__name__}"
        )

    output: subprocess.CompletedProcess = search_raw(search_string, return_type=2)

    if output.returncode != 0:
        # an error
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )

    # no error /  get stdout
    stdout = output.stdout.decode("utf-8").rstrip()
    # if output has length 0 and does not contain a search id
    #  => we probably have an error in the search query
    if len(stdout) == 0:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: 'slk search' did not return any output. Probably, there is a tipo "
            + "in the JSON search query which is not properly captured by 'slk search'. Please verify your "
            + "JSON expression (e.g. via the command line tool 'jq'. You provided the search query "
            + f"'{search_string}'."
        )
    search_id_re = re.search("Search ID: [0-9]*", stdout)

    if search_id_re is not None:
        return int(search_id_re.group(0)[11:])

    raise PySlkException(
        f"pyslk.{inspect.stack()[0][3]}: search returned unexpected output: '{stdout}'. The search query was "
        + f"'{search_string}'."
    )


def search_immediately(search_string: str) -> int:
    """Performs a search based on a search_string and directly returns a search id while search is in progress

    search_string has to be a valid JSON search string as described in the
    SLK-CLI manual. Simple double quotes has to be used in the JSON
    expression (no escaped double quotes, no escaped special characters).

    :param search_string: JSON search query string
    :type search_string: ``str``
    :returns: search id of the performed search
    :rtype: ``int``

    .. rubric:: Examples

    .. code-block:: python

        search_string='{"resources.mtime": {"$gt": "2021-09-02"}}'
    """
    if not isinstance(search_string, str):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'search_string' has wrong type; need 'str' but got "
            + f"{type(search_string).__name__}"
        )

    output: subprocess.CompletedProcess = search_immediately_raw(
        search_string, return_type=2
    )

    if output.returncode != 0:
        # an error
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )

    # no error /  get stdout
    stdout = output.stdout.decode("utf-8").rstrip()
    # if output has length 0 and does not contain a search id
    #  => we probably have an error in the search query
    if len(stdout) == 0:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: 'slk search' did not return any output. Probably, there is a tipo "
            + "in the JSON search query which is not properly captured by 'slk search'. Please verify your "
            + "JSON expression (e.g. via the command line tool 'jq'. You provided the search query "
            + f"'{search_string}'."
        )

    try:
        return int(stdout)
    except ValueError:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: search returned unexpected output: '{stdout}'. The search query was "
            + f"'{search_string}'."
        )


def search_simple(fields_dict: dict) -> int:
    """Performs a search; key-value pairs from input dict are connected by AND;
    returns search id

    :param fields_dict: dict with "metadata-field: metadata-value" pairs
    :type fields_dict: ``dict``
    :returns: search id of the performed search
    :rtype: ``int``
    """
    # check if 'path' field is set
    if "path" in fields_dict:
        if not isinstance(fields_dict["path"], dict):
            if isinstance(fields_dict["path"], str):
                fields_dict["path"] = {"$gte": fields_dict["path"]}
            else:
                raise TypeError(
                    f"pyslk.{inspect.stack()[0][3]}: value of key 'path' has wrong type; has to be 'str' or 'dict' but "
                    + f"is of type '{type(fields_dict['path']).__name__}' with value '{fields_dict['path']}'."
                )
    # generate search string
    search_string = (
        '{"$and": ' + json.dumps([{k: v} for (k, v) in fields_dict.items()]) + "}"
    )
    return search(search_string)


def searchid_exists(search_id: Union[str, int]) -> bool:
    """Get path for a resource id

    :param search_id: a search_id
    :type search_id: ``str`` or ``int``
    :returns: whether provided search id exists (True) or not (False)
    :rtype: ``bool``
    """
    output: subprocess.CompletedProcess = searchid_exists_raw(search_id, return_type=2)
    if output.returncode == 0:
        return True
    elif output.returncode == 1:
        return False
    else:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )


def is_search_incomplete(search_id: int) -> bool:
    """
    check if search is still running

    :param search_id: search id
    :type search_id: `int`
    :return: True if search is still running; False otherwise (might also be failed)
    :rtype: `bool`
    """
    output: subprocess.CompletedProcess = search_incomplete_raw(
        search_id, return_type=2
    )
    if output.returncode == 0:
        return True
    elif output.returncode == 1:
        return False
    else:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )


def is_search_successful(search_id: int) -> bool:
    """
    check if search was successfully finished

    :param search_id: search id
    :type search_id: `int`
    :return: True if search finished successfully; False if still running; False if search failed
    :rtype: `bool`
    """
    output: subprocess.CompletedProcess = search_successful_raw(
        search_id, return_type=2
    )
    if output.returncode == 0:
        return True
    elif output.returncode == 1:
        return False
    else:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )


def total_number_search_results(search_id: [int, str]) -> typing.Optional[int]:
    """Print the total number of search results regardless of read permissions of the current user

    :param search_id: a search_id
    :type search_id: ``str`` or ``int``
    :returns: total number of search results
    :rtype: ``int`` or ``None``
    """
    if not isinstance(search_id, (int, str)):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'search_id' has to be of type 'str' or 'int' but is "
            + f"{type(search_id).__name__}"
        )
    if isinstance(search_id, str):
        try:
            search_id = int(search_id)
        except ValueError:
            raise ValueError(
                f"pyslk.{inspect.stack()[0][3]}: cannot convert 'search_id' from 'str' to 'int'"
            )
    # search id does  not exist
    if not searchid_exists(search_id):
        return None
    # run the actual wrapper function
    output: str = total_number_search_results_raw(search_id, return_type=0)
    # return 'None' if output is 'None'
    if output is None:
        return None
    # else convert output to int and return it
    return int(output)


def get_search_status(search_id: int) -> dict:
    """
    return status of a search as dictionary

    :param search_id: search id
    :type search_id: `int`
    :return: dictionary which contains the search status and, if failed, a detailed error message
    :rtype: `dict`
    """
    output: subprocess.CompletedProcess = search_status_raw(
        search_id, json=True, return_type=2
    )
    if output.returncode in [0, 1]:
        return json.loads(output.stdout.decode("utf-8").rstrip())
    else:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )
