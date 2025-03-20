import inspect
import json
import subprocess
import typing
import warnings
from pathlib import Path
from typing import Union

from ..pyslk_exceptions import PySlkException
from ..raw import (
    is_on_tape_raw,
    iscached_raw,
    print_rcrs_raw,
    tape_barcode_raw,
    tape_exists_raw,
    tape_id_raw,
    tape_status_raw,
)
from .resource_extras import _check_resource, _check_resource_and_search_id

__all__ = [
    "_cached",
    "is_cached",
    "is_cached_details",
    "_on_tape",
    "is_on_tape",
    "is_on_tape_details",
    "get_tape_barcode",
    "get_tape_status",
    "tape_exists",
    "get_tape_id",
    "get_storage_information",
    "get_rcrs",
    "tape_status",
    "is_tape_available",
]


def _cached(
    resource: Union[str, int, Path, None] = None,
    search_id: Union[str, int, None] = None,
    details: bool = False,
) -> typing.Optional[Union[bool, dict[str, list[Path]]]]:
    """Check if whether file(s) is/are in HSM cache or not; returns True/False or a dict with keys 'cached' and
        'not_cached', depending on 'details'

    :param resource: a resource id or a resource path
    :type resource: ``str`` or ``int`` or ``path-like``
    :param search_id: id of a search
    :type search_id: ``int`` or ``str``
    :param details: print caching status of each file; if not set, output is False if not file in cache and else True
    :type details: ``bool``
    :returns: True if file is in cache; False otherwise; if 'details': dictionary with an entry per file
    :rtype: ``bool`` or ``dict`` or ``None``
    """
    # check a parse the input values
    check_result = _check_resource_and_search_id(
        inspect.stack()[0][3], resource, search_id
    )
    # if we received None=> return None
    if check_result is None:
        return None
    # extract values from resource path, resource id and search id
    resource_path, resource_id, search_id = check_result
    # run raw function
    output: subprocess.CompletedProcess = iscached_raw(
        resource_path,
        resource_id,
        search_id,
        recursive=True,
        verbose=False,
        double_verbose=details,
        return_type=2,
    )
    if output.returncode in [0, 1]:
        if not details:
            if output.returncode == 0:
                return True
            elif output.returncode == 1:
                return False
        else:
            # [:-1] because we drop the last row
            return {
                "cached": [
                    Path(o.split(" ")[0])
                    for o in output.stdout.decode("utf-8").split("\n")[:-2]
                    if len(o) > 0 and "not" not in o and "unclear" not in o
                ],
                "not_cached": [
                    Path(o.split(" ")[0])
                    for o in output.stdout.decode("utf-8").split("\n")[:-2]
                    if len(o) > 0 and "not" in o
                ],
                "unclear": [
                    Path(o.split(" ")[0])
                    for o in output.stdout.decode("utf-8").split("\n")[:-2]
                    if len(o) > 0 and "unclear" in o
                ],
            }
    else:
        # output.returncode is neither 0 nor 1
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )


def is_cached(
    resource: Union[str, int, Path, None] = None,
    search_id: Union[str, int, None] = None,
) -> bool:
    """Check if whether file(s) is/are in HSM cache or not; returns True/False

    :param resource: a resource id or a resource path
    :type resource: ``str`` or ``int`` or ``path-like``
    :param search_id: id of a search
    :type search_id: ``int`` or ``str``
    :returns: True if all files are in cache; False otherwise
    :rtype: ``bool``
    """
    return _cached(resource, search_id, details=False)


def is_cached_details(
    resource: Union[str, int, Path, None] = None,
    search_id: Union[str, int, None] = None,
) -> dict[str, list[Path]]:
    """Check if whether file(s) is/are in HSM cache or not; returns dict with keys 'cached' and 'not_cached'

    :param resource: a resource id or a resource path
    :type resource: ``str`` or ``int`` or ``path-like``
    :param search_id: id of a search
    :type search_id: ``int`` or ``str``
    :returns: dictionary with two keys 'cached' and 'not_cached' which each have a list of files as value
    :rtype: ``dict[str, list[Path]]``
    """
    return _cached(resource, search_id, details=True)


def _on_tape(
    resource: Union[str, int, Path, None] = None,
    search_id: Union[str, int, None] = None,
    details: bool = False,
) -> typing.Optional[Union[bool, dict[str, list[Path]]]]:
    """Check if whether file(s) is/are stored on tape or not; returns True/False or a dict with keys 'on_tape' and
        'not_on_tape', depending on 'details'

    :param resource: a resource id or a resource path
    :type resource: ``str`` or ``int`` or ``path-like``
    :param search_id: id of a search
    :type search_id: ``int`` or ``str``
    :param details: print tape storage status of each file; if not set, output is False if not file on tape
    :type details: ``bool``
    :returns: True if file is on tape; False otherwise; if 'details': dictionary with an entry per file
    :rtype: ``bool`` or ``dict`` or ``None``
    """
    # check a parse the input values
    check_result = _check_resource_and_search_id(
        inspect.stack()[0][3], resource, search_id
    )
    # if we received None=> return None
    if check_result is None:
        return None
    # extract values from resource path, resource id and search id
    resource_path, resource_id, search_id = check_result
    # run raw function
    output: subprocess.CompletedProcess = is_on_tape_raw(
        resource_path,
        resource_id,
        search_id,
        recursive=True,
        verbose=False,
        double_verbose=details,
        return_type=2,
    )
    if output.returncode in [0, 1]:
        if not details:
            if output.returncode == 0:
                return True
            elif output.returncode == 1:
                return False
        else:
            # [:-1] because we drop the last row
            return {
                "on_tape": [
                    Path(o.split(" ")[0])
                    for o in output.stdout.decode("utf-8").split("\n")[:-2]
                    if len(o) > 0 and "not" not in o
                ],
                "not_on_tape": [
                    Path(o.split(" ")[0])
                    for o in output.stdout.decode("utf-8").split("\n")[:-2]
                    if len(o) > 0 and "not" in o
                ],
            }
    else:
        # output.returncode is neither 0 nor 1
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )


def is_on_tape(
    resource: Union[str, int, Path, None] = None,
    search_id: Union[str, int, None] = None,
) -> bool:
    """Check if whether file(s) is/are stored on tape; returns True/False

    :param resource: a resource id or a resource path
    :type resource: ``str`` or ``int`` or ``path-like``
    :param search_id: id of a search
    :type search_id: ``int`` or ``str``
    :returns: True if all files are stored on tape; False otherwise
    :rtype: ``bool``
    """
    return _on_tape(resource, search_id, details=False)


def is_on_tape_details(
    resource: Union[str, int, Path, None] = None,
    search_id: Union[str, int, None] = None,
) -> dict[str, list[Path]]:
    """Check if whether file(s) is/are stored on tape or not; returns dict with keys 'on_tape' and 'not_on_tape'

    :param resource: a resource id or a resource path
    :type resource: ``str`` or ``int`` or ``path-like``
    :param search_id: id of a search
    :type search_id: ``int`` or ``str``
    :returns: dictionary with two keys 'on_tape' and 'not_on_tape' which each have a list of files as value
    :rtype: ``dict[str, list[Path]]``
    """
    return _on_tape(resource, search_id, details=True)


def get_tape_barcode(tape_id: Union[int, str]) -> typing.Optional[str]:
    """return tape barcode for provided tape id

    :param tape_id: id of a tape in the tape library
    :type tape_id: ``int`` or ``str``
    :returns: True if tape exists; False otherwise
    :rtype: ``bool``
    """
    if not isinstance(tape_id, int):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: wrong input type; need 'int'; got '{type(tape_id).__name__}'"
        )
    output: subprocess.CompletedProcess = tape_barcode_raw(tape_id, return_type=2)
    if output.returncode == 0:
        return output.stdout.decode("utf-8").rstrip()
    elif output.returncode == 1:
        return None
    else:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )


def tape_exists(tape: Union[int, str]) -> bool:
    """Check if tape exists

    :param tape: id or barcode of a tape in the tape library
    :type tape: ``int`` or ``str``
    :returns: True if tape exists; False otherwise
    :rtype: ``bool``
    """
    if not isinstance(tape, (str, int)):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: wrong input type; need 'str' or 'int'; got '{type(tape).__name__}'"
        )
    tape_id: Union[int, None] = None
    tape_barcode: Union[str, None] = None
    if isinstance(tape, int):
        tape_id = tape
    elif isinstance(tape, str):
        # tape can either be a tape id or a tape barcode
        try:
            tape_id = int(tape)
        except ValueError:
            tape_barcode = tape
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'tape' has wrong type; need 'str' or 'int' but "
            + f"got {type(tape).__name__}"
        )

    output: subprocess.CompletedProcess = tape_exists_raw(
        tape_id, tape_barcode, return_type=2
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


def get_library(tape: Union[int, str]) -> str:
    """Check in which library a tape is located

    :param tape: id or barcode of a tape in the tape library
    :type tape: ``int`` or ``str``
    :returns: name of the library in which the tape is located
    :rtype: ``str``
    """
    if not isinstance(tape, (str, int)):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: wrong input type; need 'str' or 'int'; got '{type(tape).__name__}'"
        )
    tape_id: Union[int, None] = None
    tape_barcode: Union[str, None] = None
    input_type: str
    if isinstance(tape, int):
        tape_id = tape
        input_type = "tape id"
    elif isinstance(tape, str):
        # tape can either be a tape id or a tape barcode
        try:
            tape_id = int(tape)
            input_type = "tape id"
        except ValueError:
            tape_barcode = tape
            input_type = "tape barcode"
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'tape' has wrong type; need 'str' or 'int' but "
            + f"got {type(tape).__name__}"
        )

    output: subprocess.CompletedProcess = tape_exists_raw(
        tape_id, tape_barcode, return_type=2
    )
    if output.returncode == 0:
        return output.stdout.decode("utf-8").rstrip()
    elif output.returncode == 1:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: tape not found: {tape} (interpreted as {input_type})"
        )
    else:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )


def get_tape_id(tape_barcode: str) -> typing.Optional[int]:
    """return tape id for provided tape barcode

    :param tape_barcode: barcode of a tape in the tape library
    :type tape_barcode: ``str``
    :returns: tape id; None otherwise
    :rtype: ``int``
    """
    if not isinstance(tape_barcode, str):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: wrong input type; need 'str'; got '{type(tape_barcode).__name__}'"
        )
    output: subprocess.CompletedProcess = tape_id_raw(tape_barcode, return_type=2)
    if output.returncode == 0:
        return int(output.stdout.decode("utf-8").rstrip())
    elif output.returncode == 1:
        return None
    else:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )


def tape_status(tape: Union[int, str], details: bool = False) -> typing.Optional[str]:
    """Check the status of a tape

    :param tape: id  or barcode of a tape in the tape library
    :type tape: ``int`` or ``str``
    :param details: print a more detailed description of the retrieval status
    :type details: ``bool``
    :returns: status of the tape; None if tape does not exist
    :rtype: ``str`` or ``None``
    """
    return get_tape_status(tape, details)


def get_tape_status(
    tape: Union[int, str], details: bool = False
) -> typing.Optional[str]:
    """Check the status of a tape

    :param tape: id  or barcode of a tape in the tape library
    :type tape: ``int`` or ``str``
    :param details: print a more detailed description of the retrieval status
    :type details: ``bool``
    :returns: status of the tape; None if tape does not exist
    :rtype: ``str`` or ``None``
    """
    if not tape_exists(tape):
        return None
    tape_id: Union[int, None] = None
    tape_barcode: Union[str, None] = None
    if isinstance(tape, int):
        tape_id = tape
    elif isinstance(tape, str):
        # tape can either be a tape id or a tape barcode
        try:
            tape_id = int(tape)
        except ValueError:
            tape_barcode = tape
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'tape' has wrong type; need 'str' or 'int' but "
            + f"got {type(tape).__name__}"
        )

    output: subprocess.CompletedProcess = tape_status_raw(
        tape_id, tape_barcode, details, return_type=2
    )
    if output.returncode in [0, 1]:
        if not details:
            return output.stdout.decode("utf-8").rstrip()
        else:
            return output.stdout.decode("utf-8").split("\n")[1]
    else:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )


def is_tape_available(tape: int) -> typing.Optional[bool]:
    """Check if tape is available

    :param tape: id  or barcode of a tape in the tape library
    :type tape: ``int`` or ``str``
    :returns: True if tape is available for recalls/retrievals; else False; None if tape does not exist
    :rtype: ``bool`` or ``None``
    """
    if not tape_exists(tape):
        return None
    tape_id: Union[int, None] = None
    tape_barcode: Union[str, None] = None
    if isinstance(tape, int):
        tape_id = tape
    elif isinstance(tape, str):
        # tape can either be a tape id or a tape barcode
        try:
            tape_id = int(tape)
        except ValueError:
            tape_barcode = tape
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'tape' has wrong type; need 'str' or 'int' but "
            + f"got {type(tape).__name__}"
        )
    output: subprocess.CompletedProcess = tape_status_raw(
        tape_id, tape_barcode, details=False, return_type=2
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


def get_storage_information(resource: Union[str, int, Path]) -> typing.Optional[dict]:
    """prints resource content record (rcr) information

    :param resource: a resource id or a resource path
    :type resource: ``str`` or ``int`` or ``path-like``
    :returns: True if tape exists; False otherwise
    :rtype: ``bool``
    """
    return get_rcrs(resource)


def get_rcrs(resource: Union[str, int, Path]) -> typing.Optional[dict]:
    """prints resource content record (rcr) information

    :param resource: a resource id or a resource path
    :type resource: ``str`` or ``int`` or ``path-like``
    :returns: storage information when exists; None otherwise
    :rtype: ``dict``
    """
    # check a parse the input values
    check_result = _check_resource(inspect.stack()[0][3], resource)
    # if we received None=> return None
    if check_result is None:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: parameter 'resource' not properly specified: {resource}"
        )
    # extract values from resource path, resource id and search id
    resource_path, resource_id = check_result
    output: subprocess.CompletedProcess = print_rcrs_raw(
        resource_path, resource_id, json=True, return_type=2
    )
    if output.returncode == 0:
        return json.loads(output.stdout.decode("utf-8").rstrip())
    elif output.returncode == 1:
        warnings.warn(
            f"pyslk.{inspect.stack()[0][3]}: storage information incomplete; returning what is available"
        )
        return json.loads(output.stdout.decode("utf-8").rstrip())
    else:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )
