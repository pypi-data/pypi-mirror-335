import inspect
import subprocess
from pathlib import Path
from typing import Union

from ..constants import PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS, SLK, SLK_HELPERS
from ..pyslk_exceptions import PySlkException
from ..utils import run_slk, which

__all__ = [
    "list_raw",
    "list_clone_file_raw",
    "list_clone_search_raw",
]


def list_raw(
    path_or_id: Union[str, int, Path],
    show_hidden: bool = False,
    numeric_ids: bool = False,
    recursive: bool = False,
    text: bool = False,
    print_bytes: bool = False,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """List results from search id or GNS path

    :param path_or_id: search id or gns path
    :type path_or_id: str or int or Path
    :param show_hidden: show '.' files, default: False (don't show these files)
    :type show_hidden: bool
    :param numeric_ids: show numeric values for user and group, default: False
        (show user and group names)
    :type numeric_ids: bool
    :param recursive: use the -R flag to list recursively, default: False
    :type recursive: bool
    :param text: print result to file 'slk_${USER}_list.txt', default: False
        (print to command line / print non-empty return string)
    :type text: bool
    :param print_bytes: use the -b to show sizes in bytes, default: False
    :type print_bytes: bool
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK) is None:
        raise PySlkException(f"pyslk: {SLK}: command not found")

    slk_call = [SLK, "list"]
    if show_hidden:
        slk_call.append("-a")
    if numeric_ids:
        slk_call.append("-n")
    if recursive:
        slk_call.append("-R")
    if text:
        slk_call.append("--text")
    if print_bytes:
        slk_call.append("-b")
    if isinstance(path_or_id, (str, Path)):
        slk_call.append(str(path_or_id))
    elif isinstance(path_or_id, int):
        slk_call.append(str(path_or_id))
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'path_or_id' need to be 'str', 'int' or Path-like but got "
            + f"'{type(path_or_id).__name__}'"
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


def list_clone_file_raw(
    resource_paths: Union[str, Path, list[str], list[Path], set[str], set[Path]],
    print_resource_ids: bool = False,
    print_timestamps_as_seconds_since_1970: bool = False,
    proceed_on_error: bool = False,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """List file information

    :param resource_paths: namespace or resource
    :type resource_paths: `str` or `Path`
    :param print_resource_ids: print resource ids instead of file paths
    :type print_resource_ids: `bool`
    :param print_timestamps_as_seconds_since_1970: print timestamps in seconds since 1970
    :type print_timestamps_as_seconds_since_1970: `bool`
    :param proceed_on_error: Proceed listing files even if an error arose
    :type proceed_on_error: `bool`
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]

    """
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    slk_call = [SLK_HELPERS, "list_clone_file"]

    if isinstance(resource_paths, str) and resource_paths != "":
        slk_call.append(resource_paths)
    elif isinstance(resource_paths, (list, set)) and len(resource_paths) > 0:
        if not all([isinstance(r, (str, Path)) for r in resource_paths]):
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: if argument 'resource_paths' is of type 'list' its items need to be"
                + "of type 'str' or Path-like but got type(s): "
                + f"'{', '.join([type(r).__name__ for r in resource_paths if not isinstance(r, (str, Path))])}'."
            )
        slk_call.extend([str(res) for res in resource_paths])
    elif isinstance(resource_paths, Path):
        slk_call.append(str(resource_paths))
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'resource_paths' has to be of type 'str', path-like or 'list'/'set' "
            + f"of these but is {type(resource_paths).__name__}"
        )

    if print_resource_ids:
        slk_call.append("--print-resource-ids")
    if print_timestamps_as_seconds_since_1970:
        slk_call.append("--print-timestamps-as-seconds-since-1970")
    if proceed_on_error:
        slk_call.append("--proceed-on-error")

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


def list_clone_search_raw(
    search_id: Union[int, str],
    only_files: bool = False,
    only_namespaces: bool = False,
    start: Union[int, None] = None,
    count: Union[int, None] = None,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """List results from search id and important time stamps

    :param search_id: search id of search which results should be printed
    :type search_id: int or str
    :param only_files: print only files (like default for `slk list`)
    :type only_files: bool
    :param only_namespaces: print only namespaces
    :type only_namespaces: bool
    :param start: collect search results starting with the result 'start'; if set to 1 then collect from the beginning
    :type start: int
    :param count: Collect as many search results as defined by this parameter. If set to 0 then collect until end.
    :type count: int
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]

    """
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    slk_call = [SLK_HELPERS, "list_clone_search"]
    if only_files:
        slk_call.append("-f")
    if only_namespaces:
        slk_call.append("-d")
    if start is not None:
        slk_call.append("--start")
        slk_call.append(str(start))
    if count is not None:
        slk_call.append("--count")
        slk_call.append(str(count))
    if isinstance(search_id, (str, int)):
        slk_call.append(str(search_id))
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'search_id' has to be of type 'str' or 'int' but is "
            + f"{type(search_id).__name__}"
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
