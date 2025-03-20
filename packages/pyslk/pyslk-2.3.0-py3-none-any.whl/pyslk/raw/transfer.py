import inspect
import os
import shutil
import subprocess
import typing
import warnings
from pathlib import Path
from typing import Union

from pyslk.constants import (
    PYSLK_DEFAULT_LIST_COLUMNS,
    PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
    SLK,
    SLK_HELPERS,
)
from pyslk.pyslk_exceptions import PySlkException
from pyslk.utils import FakeProc, _parse_list, run_slk, which

from .listing import list_raw

__all__ = [
    "recall_needed_raw",
    "recall_raw",
    "recall2_raw",
    "retrieve_raw",
    "retrieve2_raw",
    "archive_raw",
]


def recall_raw(
    path_or_id: Union[str, int, Path], recursive: bool = False, return_type: int = 0
) -> Union[str, int, subprocess.CompletedProcess, subprocess.Popen, FakeProc]:
    """Recall files from tape to cache via search id or GNS path

    :param path_or_id: search id or gns path of resources to recall
    :type path_or_id: str or int or Path
    :param recursive: use the -R flag to recall recursively, Default: False
    :type recursive: bool
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output), 3 (running subproc.)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess, subprocess.Popen, FakeProc]
    """
    if which(SLK) is None:
        raise PySlkException(f"pyslk: {SLK}: command not found")

    slk_call = [SLK, "recall"]
    if recursive:
        slk_call.append("-R")
    if isinstance(path_or_id, (str, Path)):
        slk_call.append(str(path_or_id))
    elif isinstance(path_or_id, int):
        slk_call.append(str(path_or_id))
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'path_or_id' needs to be 'str', 'int' or Path-like but got "
            + f"'{type(path_or_id).__name__}'."
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
    elif return_type == -1:
        return FakeProc()
    else:
        raise ValueError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'return_type' needs to be 0, 1 or 2."
        )


def retrieve_raw(
    path_or_id: Union[str, int, Path],
    dest_dir: Union[str, Path],
    partsize: int = -1,
    streams: int = -1,
    stats: bool = False,
    writeblocksize: int = -1,
    recursive: bool = False,
    duplicate: bool = False,
    preserve_path: bool = True,
    skip_if_exists: bool = False,
    return_type: int = 0,
) -> typing.Optional[Union[str, int, subprocess.CompletedProcess, subprocess.Popen]]:
    """Retrieve files via search id or GNS path.

    Overwrite files if they already exists. Prevent this by 'duplicate'
    or 'skip_if_exists'.

    :param path_or_id: search id or gns path of resources to retrieve
    :type path_or_id: str or int or Path
    :param dest_dir: destination directory for retrieval
    :type dest_dir: str or Path
    :param partsize: size of each file to download per stream, Default: 500 (default is used if not >0)
    :type partsize: int
    :param streams: number of file part streams to use per node, Default: 4 (default is used if not >0)
    :type streams: int
    :param stats: Display part and I/O stats for each node
    :type stats: bool
    :param writeblocksize: I/O block size for file writes (KB), Default: 4096 (default is used if not >0)
    :type writeblocksize: int
    :param recursive: use the -R flag to retrieve recursively, Default: False
    :type recursive: bool
    :param duplicate: create a duplicate file if file exists
    :type duplicate: bool
    :param preserve_path: preserve namespace in destination [default: True]
    :type preserve_path: bool
    :param skip_if_exists: Skip if file exists
    :type skip_if_exists: bool
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output), 3 (running subproc.)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess, subprocess.Popen] or None

    .. seealso::
        * :py:meth:`~pyslk.retrieve`

    """
    if which(SLK) is None:
        raise PySlkException(f"pyslk: {SLK}: command not found")

    # check if a search id should be retrieved and if preserve_path is not set
    is_search: bool = False
    mv_files: bool = False
    src_paths: list = list()
    if isinstance(path_or_id, (str, int)):
        try:
            int(path_or_id)
            is_search = True
        except ValueError:
            pass
    if is_search and not preserve_path:
        warnings.warn(
            "Retrieving via search id without preserving namespace is not implemented in slk. "
            + "Instead slk will silently preserve the namespace. Pyslk will move the data after "
            + "successful download for you. However, this behaviour is not consistent with using "
            + "slk from the command line, hence, it will raise an error in the future or force "
            + "preserve_path=True. See https://gitlab.dkrz.de/hsm-tools/pyslk/-/issues/54."
        )
        mv_files = True
        # check for old slk version
        column_names = PYSLK_DEFAULT_LIST_COLUMNS
        try:
            list_out = list_raw(path_or_id)
        except PySlkException as e:
            if "ERROR: No resources found for given search id:" in str(e):
                warnings.warn("No resources found for given search id")
                return None
            else:
                raise e
        df = _parse_list(list_out, path_or_id, column_names, full_path=True)
        src_paths = df["filename"].tolist()
        # check for duplicate filenames
        tmp_files = [os.path.basename(src_path) for src_path in src_paths]
        duplicate_files = set()
        checked_file = set()
        for tmp_file in tmp_files:
            if tmp_file in checked_file:
                duplicate_files.add(tmp_file)
            else:
                checked_file.add(tmp_file)
        if len(duplicate_files) > 0:
            raise PySlkException(
                "You want to retrieve search results into one target directory without reconstructing the source path "
                + "('preserve_path' set to 'False' or not set at all). However, one or more search results have the "
                + "same name and would overwrite each other. Please run this command again with "
                + f"'preserve_path = True'. Affected filenames are: {', '.join(duplicate_files)}."
            )

    slk_call = [SLK, "retrieve"]
    if recursive:
        slk_call.append("-R")
    if isinstance(partsize, int):
        if partsize > 0:
            slk_call.append("--partsize")
            slk_call.append(str(partsize))
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'partsize' needs to be 'int' but got '{type(partsize).__name__}'."
        )
    if isinstance(streams, int):
        if streams > 0:
            slk_call.append("--streams")
            slk_call.append(str(streams))
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'streams' needs to be 'int' but got '{type(streams).__name__}'."
        )
    if stats:
        slk_call.append("--stats")
    if isinstance(writeblocksize, int):
        if writeblocksize > 0:
            slk_call.append("--writeblocksize")
            slk_call.append(str(writeblocksize))
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'writeblocksize' need to be 'int' but got "
            + f"'{type(writeblocksize).__name__}'."
        )
    if duplicate:
        slk_call.append("-d")
    if preserve_path:
        slk_call.append("-ns")
    if skip_if_exists:
        slk_call.append("-s")
    if isinstance(path_or_id, (str, int, Path)):
        slk_call.append(str(path_or_id))
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'path_or_id' need to be 'str', 'int' or path-like but got "
            + f"'{type(path_or_id).__name__}'."
        )
    if isinstance(dest_dir, (str, Path)):
        slk_call.append(str(dest_dir))
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'dest_dir' need to be 'str' or path-like but got "
            + f"'{type(dest_dir).__name__}'."
        )

    if return_type == 0:
        output = run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
        )
    elif return_type == 1:
        output = run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
            handle_output=False,
        ).returncode
    elif return_type == 2:
        output = run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS,
            handle_output=False,
        )
    else:
        raise ValueError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'return_type' needs to be 0, 1 or 2."
        )

    if mv_files:
        for src_path in src_paths:
            shutil.move(
                os.path.join(dest_dir, src_path[1:]),
                os.path.join(dest_dir, os.path.basename(src_path)),
            )

    return output


def archive_raw(
    src_path: Union[str, list, Path],
    dst_gns: Union[str, Path],
    partsize: Union[int, None] = None,
    streams: Union[int, None] = None,
    stats: bool = False,
    recursive: bool = False,
    preserve_permissions: bool = False,
    exclude_hidden: bool = False,
    verbose: bool = False,
    double_verbose: bool = False,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """Upload files in a directory and optionally tag resources
            using directory path and GNS path

    :param src_path: search id or gns path of resources to retrieve
    :type src_path: str or list or Path
    :param dst_gns: destination directory for retrieval
    :type dst_gns: str or Path
    :param partsize: size of each file to download per stream, Default: 500
    :type partsize: int
    :param streams: number of file part streams to use per node, Default: 4
    :type streams: int
    :param stats: Display part & I/O stats for each node; Default: False
    :type stats: bool
    :param recursive: use the -R flag to archive recursively, Default: False
    :type recursive: bool
    :param preserve_permissions: preserve original file permission, Default: False
    :type preserve_permissions: bool
    :param exclude_hidden: exclude . (hidden) files, Default: False
    :type exclude_hidden: bool
    :param verbose: single verbose mode, Default: False
    :type verbose: bool
    :param double_verbose: double verbose mode, Default: False
    :type double_verbose: bool
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK) is None:
        raise PySlkException(f"pyslk: {SLK}: command not found")

    slk_call = [SLK, "archive"]
    if recursive:
        slk_call.append("-R")
    if preserve_permissions:
        slk_call.append("-p")
    if verbose:
        slk_call.append("-v")
    if double_verbose:
        slk_call.append("-vv")
    if exclude_hidden:
        slk_call.append("-x")
    if partsize is not None:
        if isinstance(partsize, int):
            slk_call.append("--partsize")
            slk_call.append(str(partsize))
        else:
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: argument 'partsize' needs to be 'int' but got "
                + f"'{type(partsize).__name__}'"
            )
    if streams is not None:
        if isinstance(streams, int):
            slk_call.append("--streams")
            slk_call.append(str(streams))
        else:
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: argument 'streams' needs to be 'int' but got "
                + f"'{type(streams).__name__}'"
            )
    if stats:
        slk_call.append("--stats")
    if isinstance(src_path, (str, Path)):
        slk_call.append(str(src_path))
    elif isinstance(src_path, list):
        if not all([isinstance(r, (str, Path)) for r in src_path]):
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: if argument 'src_path' is of type 'list' its items need to be"
                + "of type 'str' or Path-like but got type(s): "
                + f"'{', '.join([type(r).__name__ for r in src_path if not isinstance(r, (str, Path))])}'."
            )
        slk_call.extend(src_path)
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'src_path' needs to be 'str', 'list' or path-like but got "
            + f"'{type(src_path).__name__}'"
        )
    if isinstance(dst_gns, (str, Path)):
        slk_call.append(str(dst_gns))
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'dst_gns' needs to be 'str' or path-like but got "
            + f"'{type(dst_gns).__name__}'"
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


def recall2_raw(
    resources: Union[
        Path, str, int, list[Path], list[str], list[int], set[Path], set[str], set[int]
    ],
    destination: Union[Path, str, None] = None,
    resource_ids: bool = False,
    search_id: bool = False,
    recursive: bool = False,
    preserve_path: bool = True,
    verbose: bool = False,
    double_verbose: bool = False,
    dry_run: bool = False,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """Run a slk_helpers recall

    :param resources: multiple resource ids (set resource_ids=True) or paths OR one search id (set search_id=True)
    :type resources: str or Path or int or list[str] or list[Path] or list[int] or set[str] or set[Path] or set[int]
    :param destination: destination directory to check whether some of the needed files are already available and
        don't need to be recalled
    :type destination: str or Path
    :param resource_ids: consider input as 'resource' as resource id or resource ids
    :type resource_ids: bool
    :param search_id: consider input as 'resource' as search id
    :type search_id: bool
    :param recursive: use the -R flag to recall recursively, Default: False
    :type recursive: bool
    :param preserve_path: preserve original file path, Default: True
    :type preserve_path: bool
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

    if resources:
        if isinstance(resources, (str, Path, int)):
            slk_call = [SLK_HELPERS, "recall", str(resources)]
        elif isinstance(resources, (list, set)):
            slk_call = [SLK_HELPERS, "recall"]
            slk_call.extend([str(r) for r in resources])
        else:
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: argument 'resources' needs to be 'str', path-like, int or list/set "
                + f" containing variables of one of these types but got '{type(destination).__name__}'"
            )
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'resources' has to be set but got 'None'"
        )
    if destination:
        if isinstance(destination, (str, Path)):
            slk_call.append("-d")
            slk_call.append(str(destination))
        else:
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: argument 'destination' needs to be 'str' or path-like but got "
                + f"'{type(destination).__name__}'"
            )
    if resource_ids:
        slk_call.append("--resource-ids")
    if search_id:
        slk_call.append("--search-id")
    if recursive:
        slk_call.append("-R")
    if preserve_path:
        slk_call.append("-ns")
    if verbose:
        slk_call.append("-v")
    if double_verbose:
        slk_call.append("-vv")
    if dry_run:
        slk_call.append("--dry-run")

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


def recall_needed_raw(
    resources: Union[
        Path, str, int, list[Path], list[str], list[int], set[Path], set[str], set[int]
    ],
    destination: Union[Path, str, None] = None,
    resource_ids: bool = False,
    search_id: bool = False,
    recursive: bool = False,
    preserve_path: bool = True,
    verbose: bool = False,
    double_verbose: bool = False,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """Run a slk_helpers recall_needed

    :param resources: multiple resource ids (set resource_ids=True) or paths OR one search id (set search_id=True)
    :type resources: str or Path or int or list[str] or list[Path] or list[int] or set[str] or set[Path] or set[int]
    :param destination: destination directory to check whether some of the needed files are already available and
        don't need to be recalled
    :type destination: str or Path
    :param resource_ids: consider input as 'resource' as resource id or resource ids
    :type resource_ids: bool
    :param search_id: consider input as 'resource' as search id
    :type search_id: bool
    :param recursive: use the -R flag to recall recursively, Default: False
    :type recursive: bool
    :param preserve_path: preserve original file path, Default: True
    :type preserve_path: bool
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

    if resources:
        if isinstance(resources, (str, Path, int)):
            slk_call = [SLK_HELPERS, "recall_needed", str(resources)]
        elif isinstance(resources, (list, set)):
            slk_call = [SLK_HELPERS, "recall_needed"]
            slk_call.extend([str(r) for r in resources])
        else:
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: argument 'resources' needs to be 'str', path-like, int or list/set "
                + f" containing variables of one of these types but got '{type(destination).__name__}'"
            )
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'resources' has to be set but got 'None'"
        )
    if destination:
        if isinstance(destination, (str, Path)):
            slk_call.append("-d")
            slk_call.append(str(destination))
        else:
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: argument 'destination' needs to be 'str' or path-like but got "
                + f"'{type(destination).__name__}'"
            )
    if resource_ids:
        slk_call.append("--resource-ids")
    if search_id:
        slk_call.append("--search-id")
    if recursive:
        slk_call.append("-R")
    if preserve_path:
        slk_call.append("-ns")
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


def retrieve2_raw(
    resources: Union[
        Path, str, int, list[Path], list[str], list[int], set[Path], set[str], set[int]
    ],
    destination: Union[Path, str],
    dry_run: bool = False,
    force_overwrite: bool = False,
    ignore_existing: bool = False,
    json_to_file: Union[Path, str, None] = None,
    json_batch: bool = True,
    print_progress: bool = False,
    resource_ids: bool = False,
    search_id: bool = False,
    recursive: bool = False,
    stop_on_failed_retrieval: bool = False,
    write_envisaged_to_file: Union[Path, str, None] = None,
    write_missing_to_file: Union[Path, str, None] = None,
    preserve_path: bool = True,
    verbose: bool = False,
    double_verbose: bool = False,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """Run a slk_helpers retrieve

    :param resources: multiple resource ids (set resource_ids=True) or paths OR one search id (set search_id=True)
    :type resources: str or Path or int or list[str] or list[Path] or list[int] or set[str] or set[Path] or set[int]
    :param destination: destination directory to check whether some of the needed files are already available and
        don't need to be retrieved
    :type destination: str or Path
    :param dry_run: list which file would be transferred but do not actually transfer data
    :type dry_run: bool
    :param force_overwrite: force overwrite of all existing files
    :type force_overwrite: bool
    :param ignore_existing: ignore-existing
    :type ignore_existing: bool
    :param json_to_file: prints a JSON summary to a file (if you do not want to capture it together with verbose
        information)
    :type json_to_file: str or Path
    :param json_batch: prints a JSON summary to the terminal/stdout; all other output is suppressed or printed to stderr
    :type json_batch: bool
    :param print_progress: prints the progress of this command to stderr (if you do not want to capture it together with
        JSON or verbose information)
    :type print_progress: bool
    :param resource_ids: consider input as 'resource' as resource id or resource ids
    :type resource_ids: bool
    :param search_id: consider input as 'resource' as search id
    :type search_id: bool
    :param recursive: use the -R flag to recall recursively, Default: False
    :type recursive: bool
    :param stop_on_failed_retrieval: stop immediately when one file cannot be retrieved
    :type stop_on_failed_retrieval: bool
    :param write_envisaged_to_file:  write files, which could be retrieved, to provided file (failed files, which should
        be retrieved, are ignored)
    :type write_envisaged_to_file: str or Path
    :param write_missing_to_file: write files, which currently cannot / could not be retrieve, to provided file
    :type write_missing_to_file: str or Path
    :param preserve_path: preserve original file path, Default: True
    :type preserve_path: bool
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

    if resources:
        if isinstance(resources, (str, Path, int)):
            slk_call = [SLK_HELPERS, "retrieve", str(resources)]
        elif isinstance(resources, (list, set)):
            slk_call = [SLK_HELPERS, "retrieve"]
            slk_call.extend([str(r) for r in resources])
        else:
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: argument 'resources' needs to be 'str', path-like, int or list/set "
                + f" containing variables of one of these types but got '{type(destination).__name__}'"
            )
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'resources' has to be set but got 'None'"
        )

    if destination:
        if isinstance(destination, (str, Path)):
            slk_call.append("-d")
            slk_call.append(str(destination))
        else:
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: argument 'destination' needs to be 'str' or path-like but got "
                + f"'{type(destination).__name__}'"
            )
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'destination' has to be set but got 'None'"
        )

    if dry_run:
        slk_call.append("--dry-run")
    if force_overwrite:
        slk_call.append("--force-overwrite")
    if ignore_existing:
        slk_call.append("--ignore-existing")
    if json_to_file:
        if isinstance(json_to_file, (str, Path)):
            slk_call.append("--json-to-file")
            slk_call.append(str(json_to_file))
        else:
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: argument 'json_to_file' needs to be 'str' or path-like but got "
                + f"'{type(json_to_file).__name__}'"
            )
    if json_batch:
        slk_call.append("--json-batch")
    if print_progress:
        slk_call.append("--print-progress")
    if resource_ids:
        slk_call.append("--resource-ids")
    if search_id:
        slk_call.append("--search-id")
    if recursive:
        slk_call.append("-R")
    if stop_on_failed_retrieval:
        slk_call.append("--stop-on-failed-retrieval")
    if write_envisaged_to_file:
        if isinstance(write_envisaged_to_file, (str, Path)):
            slk_call.append("--write-envisaged-to-file")
            slk_call.append(str(write_envisaged_to_file))
        else:
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: argument 'write_envisaged_to_file' needs to be 'str' or path-like "
                + f"but got '{type(write_envisaged_to_file).__name__}'"
            )
    if write_missing_to_file:
        if isinstance(write_missing_to_file, (str, Path)):
            slk_call.append("--write-missing-to-file")
            slk_call.append(str(write_missing_to_file))
        else:
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: argument 'write_missing_to_file' needs to be 'str' or path-like "
                + f"but got '{type(write_missing_to_file).__name__}'"
            )
    if preserve_path:
        slk_call.append("-ns")
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
