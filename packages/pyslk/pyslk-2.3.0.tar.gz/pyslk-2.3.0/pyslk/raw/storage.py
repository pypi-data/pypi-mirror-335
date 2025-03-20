import inspect
import subprocess
from pathlib import Path
from typing import Union

from pyslk.constants import PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS, SLK_HELPERS
from pyslk.pyslk_exceptions import PySlkException
from pyslk.utils import run_slk, which

__all__ = [
    "tape_status_raw",
    "tape_id_raw",
    "tape_barcode_raw",
    "tape_exists_raw",
    "tape_library_raw",
    "iscached_raw",
    "is_on_tape_raw",
    "group_files_by_tape_raw",
    "print_rcrs_raw",
]


def tape_status_raw(
    tape_id: Union[int, str, None] = None,
    tape_barcode: Union[str, None] = None,
    details: bool = False,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """Check the status of a tape

    :param tape_id: id of a tape in the tape library
    :type tape_id: int or str or None
    :param tape_barcode: barcode of a tape in the tape library
    :type tape_barcode: str or None
    :param details: print a more detailed description of the retrieval status
    :type details: bool
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    slk_call = [SLK_HELPERS, "tape_status"]

    if tape_id is not None:
        if not isinstance(tape_id, (int, str)):
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: argument 'tape_id' needs to be 'int' or 'str' but got "
                + f"'{type(tape_id).__name__}'."
            )
        slk_call.append(str(tape_id))
    if tape_barcode is not None:
        if not isinstance(tape_barcode, str):
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: argument 'tape_barcode' needs to be 'str' but got "
                + f"'{type(tape_barcode).__name__}'."
            )
        slk_call.append("--tape-barcode")
        slk_call.append(tape_barcode)
    if details:
        slk_call.append("--details")

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


def tape_id_raw(
    tape_barcode: str, return_type: int = 0
) -> Union[str, int, subprocess.CompletedProcess]:
    """return tape id for provided tape barcode

    :param tape_barcode: barcode of a tape in the tape library
    :type tape_barcode: str
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    if not isinstance(tape_barcode, str):
        raise TypeError(
            f'slk.{inspect.stack()[0][3]}: argument "tape_id" needs to be "str" but got '
            + f'"{type(tape_barcode).__name__}".'
        )

    slk_call = [SLK_HELPERS, "tape_id", tape_barcode]

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


def tape_barcode_raw(
    tape_id: Union[int, str], return_type: int = 0
) -> Union[str, int, subprocess.CompletedProcess]:
    """return tape barcode for provided tape id

    :param tape_id: id of a tape in the tape library
    :type tape_id: int or str
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    if not isinstance(tape_id, (int, str)):
        raise TypeError(
            f'slk.{inspect.stack()[0][3]}: argument "tape_id" needs to be "int" or "str" but got '
            + f'"{type(tape_id).__name__}".'
        )

    slk_call = [SLK_HELPERS, "tape_barcode", str(tape_id)]

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


def tape_exists_raw(
    tape_id: Union[int, str, None] = None,
    tape_barcode: Union[str, None] = None,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """Check if tape exists

    :param tape_id: id of a tape in the tape library
    :type tape_id: int or str or None
    :param tape_barcode: barcode of a tape in the tape library
    :type tape_barcode: str or None
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    slk_call = [SLK_HELPERS, "tape_exists"]

    if tape_id is not None:
        if not isinstance(tape_id, (int, str)):
            raise TypeError(
                f"slk.{inspect.stack()[0][3]}: argument 'tape_id' needs to be 'int' or 'str' but got "
                + f"'{type(tape_id).__name__}'."
            )
        slk_call.append(str(tape_id))
    if tape_barcode is not None:
        if not isinstance(tape_barcode, str):
            raise TypeError(
                f"slk.{inspect.stack()[0][3]}: argument 'tape_barcode' needs to be 'str' but got "
                + f"'{type(tape_barcode).__name__}'."
            )
        slk_call.append("--tape-barcode")
        slk_call.append(tape_barcode)

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


def tape_library_raw(
    tape_id: Union[int, str, None] = None,
    tape_barcode: Union[str, None] = None,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """Return the name of the library in which the tape is stored

    :param tape_id: id of a tape in the tape library
    :type tape_id: int or str or None
    :param tape_barcode: barcode of a tape in the tape library
    :type tape_barcode: str or None
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    slk_call = [SLK_HELPERS, "tape_library"]

    if tape_id is not None:
        if not isinstance(tape_id, (int, str)):
            raise TypeError(
                f"slk.{inspect.stack()[0][3]}: argument 'tape_id' needs to be 'int' or 'str' but got "
                + f"'{type(tape_id).__name__}'."
            )
        slk_call.append(str(tape_id))
    if tape_barcode is not None:
        if not isinstance(tape_barcode, str):
            raise TypeError(
                f"slk.{inspect.stack()[0][3]}: argument 'tape_barcode' needs to be 'str' but got "
                + f"'{type(tape_barcode).__name__}'."
            )
        slk_call.append("--tape-barcode")
        slk_call.append(tape_barcode)

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


def iscached_raw(
    resource_path: Union[str, Path, None] = None,
    resource_id: Union[str, int, None] = None,
    search_id: Union[str, int, None] = None,
    recursive: bool = False,
    verbose: bool = False,
    double_verbose: bool = False,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """Get info whether file is in HSM cache or not

    :param resource_path: resource (full path)
    :type resource_path: str or Path or None
    :param resource_id: a resource id
    :type resource_id: str or int or None
    :param search_id: id of a search
    :type search_id: int or str or None
    :param recursive: export metadata from all files in gns_path recursively
    :type recursive: bool
    :param verbose: single verbose mode, Default: False
    :type verbose: bool
    :param double_verbose: double verbose mode, Default: False
    :type double_verbose: bool
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    slk_call = [SLK_HELPERS, "iscached"]

    if resource_path is not None:
        if not isinstance(resource_path, (str, Path)):
            raise TypeError(
                f'pyslk.{inspect.stack()[0][3]}: "resource_path" has to be of type "str" or path-like but is '
                + f"{type(resource_id).__name__}"
            )
        slk_call.append(str(resource_path))
    if resource_id is not None:
        if not isinstance(resource_id, (str, int)):
            raise TypeError(
                f'pyslk.{inspect.stack()[0][3]}: "resource_id" has to be of type "str" or "int" but is '
                + f"{type(resource_id).__name__}"
            )
        slk_call.append("--resource-id")
        slk_call.append(str(resource_id))
    if search_id is not None:
        if not isinstance(search_id, (str, int)):
            raise TypeError(
                f'pyslk.{inspect.stack()[0][3]}: "search_id" has to be of type "str" or "int" but is '
                + f"{type(resource_id).__name__}"
            )
        slk_call.append("--search-id")
        slk_call.append(str(search_id))
    if recursive:
        slk_call.append("-R")
    if verbose:
        slk_call.append("-v")
    if double_verbose:
        slk_call.append("-vv")

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


def is_on_tape_raw(
    resource_path: Union[str, Path, None] = None,
    resource_id: Union[str, int, None] = None,
    search_id: Union[str, int, None] = None,
    recursive: bool = False,
    verbose: bool = False,
    double_verbose: bool = False,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """Get info whether file is stored on a tape or not (independent on whether it is stored in the cache)

    :param resource_path: resource (full path)
    :type resource_path: str or Path or None
    :param resource_id: a resource id
    :type resource_id: str or int or None
    :param search_id: id of a search
    :type search_id: int or str or None
    :param recursive: export metadata from all files in resource_path recursively
    :type recursive: bool
    :param verbose: single verbose mode, Default: False
    :type verbose: bool
    :param double_verbose: double verbose mode, Default: False
    :type double_verbose: bool
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    if resource_path is not None and not isinstance(resource_path, (str, Path)):
        raise TypeError(
            f'pyslk.{inspect.stack()[0][3]}: "resource_path" has to be of type "str" or path-like but is '
            + f"{type(resource_id).__name__}"
        )

    if resource_id is not None and not isinstance(resource_id, (str, int)):
        raise TypeError(
            f'pyslk.{inspect.stack()[0][3]}: "resource_id" has to be of type "str" or "int" but is '
            + f"{type(resource_id).__name__}"
        )

    if search_id is not None and not isinstance(search_id, (str, int)):
        raise TypeError(
            f'pyslk.{inspect.stack()[0][3]}: "search_id" has to be of type "str" or "int" but is '
            + f"{type(resource_id).__name__}"
        )

    slk_call = [SLK_HELPERS, "is_on_tape"]

    if resource_path is not None:
        slk_call.append(str(resource_path))
    if resource_id is not None:
        slk_call.append("--resource-id")
        slk_call.append(str(resource_id))
    if search_id is not None:
        slk_call.append("--search-id")
        slk_call.append(str(search_id))
    if recursive:
        slk_call.append("-R")
    if verbose:
        slk_call.append("-v")
    if double_verbose:
        slk_call.append("-vv")

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


def group_files_by_tape_raw(
    resource_paths: Union[str, list, set, Path, None] = None,
    resource_ids: Union[str, list, set, int, None] = None,
    search_id: Union[int, str, None] = None,
    search_query: Union[str, None] = None,
    destination: Union[Path, str, None] = None,
    recursive: bool = False,
    preserve_path: bool = True,
    print_tape_id: bool = False,
    print_tape_barcode: bool = False,
    print_tape_status: bool = False,
    print_resource_id: bool = False,
    count_files: bool = False,
    gen_search_query: bool = False,
    run_search_query: bool = False,
    set_max_tape_number_per_search: int = -1,
    json: bool = False,
    full: bool = False,
    details: bool = False,
    count_tapes: bool = False,
    evaluate_regex_in_input: bool = False,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess, subprocess.Popen]:
    """groups a list of files based on which tape they are stored on

    Receives a list of files or a search id as input. Looks up which files are stored in the HSM-Cache and which are
    not stored in the HSM-Cache but only on tape. Files on tape are grouped by tape: each line of the output contains
    all files which are on one tape. The user can directly create a search query for retrieving all files from one
    tape (--gen-search-query) or directly run this search (--run-search-query). In the latter case, the search id is
    printed per tape. If the user wants to know the tape id and the tape status, she/he might use --print-tape-id and
    --print-tape-status, respectively.

    :param resource_paths: list of resource paths to be searched for
    :type resource_paths: str or list or set or Path-like or None
    :param resource_ids: list of resource ids to be searched for
    :type resource_ids: str or list or set or Path-like or None
    :param search_id: id of a search
    :type search_id: int or str or None
    :param search_query: a search query
    :type search_query: str
    :param destination: destination directory to check whether some of the needed files are already available and
        don't need to be retrieved
    :type destination: str or Path
    :param recursive: do recursive search in the namespaces
    :type recursive: bool
    :param preserve_path: preserve original file path, Default: True
    :type preserve_path: bool
    :param print_tape_id: print the tape id on the far left followed by a ':', Default: False
    :type print_tape_id: bool
    :param print_tape_barcode: print the tape barcode on the far left followed by a ':', Default: False
    :type print_tape_barcode: bool
    :param print_tape_status:  print the status ('avail' or 'blocked') of the tape of each file group; if print_tape_id
        is set, this is printed: 'TAPE_ID, TAPE_STATUS: FILES'; if this is not set, this is printed: TAPE_STATUS: FILES,
        Default: False
    :type print_tape_status: bool
    :param print_resource_id: print the resource id for each file instead of its path. Is ignored when
        '--gen-search-query', '--run-search-query', '--full' or '--count-files' are set. Default: False.
    :type print_resource_id: bool
    :param count_files: count files instead of printing file list
    :type count_files: bool
    :param gen_search_query: generate and print (a) search query strings instead of the lists of files per tape,
        Default: False
    :type gen_search_query: bool
    :param run_search_query: generate and run (a) search query strings instead of the lists of files per tape and print
        the search i, Default: False
    :type run_search_query: bool
    :param set_max_tape_number_per_search: number of tapes per search; if '-1' => the parameter is not set
    :type set_max_tape_number_per_search: int
    :param json: return the output as JSON
    :type json: bool
    :param full: print useful information and run search query per tape; implies print_tape_barcode, print_tape_status
        and run_search_query
    :type full: bool
    :param details: print useful information; implies print_tape_barcode and print_tape_status
    :type details: bool
    :param count_tapes: only count the number of involved tapes and print the number incl. some text
    :type count_tapes: bool
    :param evaluate_regex_in_input: expect that a regular expression in part of the input (file names) and evalute it
    :type evaluate_regex_in_input: bool
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output), 3 (running subproc.)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess, subprocess.Popen]

    .. seealso::
        * :py:meth:`~pyslk.group_files_by_tape`

    """
    # TODO: make nice version
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    slk_call = SLK_HELPERS + " group_files_by_tape"

    if resource_paths is not None:
        if isinstance(resource_paths, str) and resource_paths != "":
            slk_call = slk_call + " " + resource_paths
        elif isinstance(resource_paths, (list, set)) and len(resource_paths) > 0:
            if not all([isinstance(r, (str, Path)) for r in resource_paths]):
                raise TypeError(
                    f"pyslk.{inspect.stack()[0][3]}: if argument 'resource_paths' is of type 'list' or 'set' its items "
                    + "need to be of type 'str' or Path-like but got type(s): "
                    + f"'{', '.join([type(r).__name__ for r in resource_paths if not isinstance(r, (str, Path))])}'."
                )
            slk_call = slk_call + " " + " ".join([str(res) for res in resource_paths])
        elif isinstance(resource_paths, Path):
            slk_call = slk_call + " " + str(resource_paths)
        else:
            raise TypeError(
                f'pyslk.{inspect.stack()[0][3]}: "resource_paths" has to be of type "str", path-like or "list" but is '
                + f"{type(resource_paths).__name__}"
            )
    if resource_ids is not None:
        if isinstance(resource_ids, str) and resource_ids != "":
            slk_call = slk_call + " --resource-ids " + resource_ids
        elif isinstance(resource_ids, int):
            slk_call = slk_call + " " + str(resource_ids)
        elif isinstance(resource_ids, (list, set)) and len(resource_ids) > 0:
            if not all([isinstance(r, (str, int)) for r in resource_ids]):
                raise TypeError(
                    f"pyslk.{inspect.stack()[0][3]}: if argument 'resource_ids' is of type 'list' or 'set' its items "
                    + "need to be of type 'str' or 'int' but got type(s): "
                    + f"'{', '.join([type(r).__name__ for r in resource_ids if not isinstance(r, (str, Path))])}'."
                )
            slk_call = slk_call + " " + " ".join([str(res) for res in resource_ids])
        else:
            raise TypeError(
                f'pyslk.{inspect.stack()[0][3]}: "resource_paths" has to be of type "str", path-like or "list" but is '
                + f"{type(resource_paths).__name__}"
            )
    if search_id is not None and not (isinstance(search_id, int) and search_id == -1):
        slk_call = slk_call + " --search-id " + str(search_id)
    if search_query is not None:
        if isinstance(search_query, str):
            slk_call = slk_call + " --search-query " + f"'{search_query}'"
        else:
            raise TypeError(
                f'pyslk.{inspect.stack()[0][3]}: "search_query" has to be of type "str" but is '
                + f"{type(search_query).__name__}"
            )

    if destination is not None:
        if isinstance(destination, (str, Path)):
            slk_call = slk_call + " -dst " + str(destination)
        else:
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: argument 'destination' needs to be 'str' or path-like but got "
                + f"'{type(destination).__name__}'"
            )
    if recursive:
        slk_call = slk_call + " --recursive"
    if preserve_path:
        slk_call = slk_call + " -ns"
    if print_tape_id:
        slk_call = slk_call + " --print-tape-id"
    if print_tape_barcode:
        slk_call = slk_call + " --print-tape-barcode"
    if print_tape_status:
        slk_call = slk_call + " --print-tape-status"
    if print_resource_id:
        slk_call = slk_call + " --print-resource-id"
    if count_files:
        slk_call = slk_call + " --count-files"
    if gen_search_query:
        slk_call = slk_call + " --gen-search-query"
    if run_search_query:
        slk_call = slk_call + " --run-search-query"
    if set_max_tape_number_per_search != -1:
        slk_call = (
            slk_call
            + " --set-max-tape-number-per-search "
            + str(set_max_tape_number_per_search)
        )
    if json:
        slk_call = slk_call + " --json"
    if full:
        slk_call = slk_call + " --full"
    if details:
        slk_call = slk_call + " --details"
    if count_tapes:
        slk_call = slk_call + " --count-tapes"
    if evaluate_regex_in_input:
        slk_call = slk_call + " --evaluate-regex-in-input"

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


def print_rcrs_raw(
    resource_path: Union[str, Path, None] = None,
    resource_id: Union[str, int, None] = None,
    json: bool = False,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """prints resource content record (rcr) information

    :param resource_path: resource (full path)
    :type resource_path: str or Path or None
    :param resource_id: a resource id
    :type resource_id: str or int or None
    :param json: print json
    :type json: ``bool``
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    slk_call = [SLK_HELPERS, "print_rcrs"]

    if resource_path is not None:
        if not isinstance(resource_path, (str, Path)):
            raise TypeError(
                f'pyslk.{inspect.stack()[0][3]}: "resource_path" has to be of type "str" or path-like but is '
                + f"{type(resource_id).__name__}"
            )
        slk_call.append(str(resource_path))
    if resource_id is not None:
        if not isinstance(resource_id, (str, int)):
            raise TypeError(
                f'pyslk.{inspect.stack()[0][3]}: "resource_id" has to be of type "str" or "int" but is '
                + f"{type(resource_id).__name__}"
            )
        if isinstance(resource_id, str):
            try:
                int(resource_id)
            except ValueError:
                raise TypeError(
                    f"pyslk.{inspect.stack()[0][3]}: 'resource_id' cannot be processed; need 'str', which holds an "
                    + f"integer number, or 'int' but got '{type(resource_id).__name__}' with value '{resource_id}'"
                )
        slk_call.append("--resource-id")
        slk_call.append(str(resource_id))

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
