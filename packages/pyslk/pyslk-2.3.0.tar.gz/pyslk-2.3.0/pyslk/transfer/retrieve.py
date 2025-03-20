import inspect
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Optional, Union

from pyslk.pyslk_exceptions import PySlkException

from ..base import ls
from ..constants import MAX_RETRIES_RETRIEVAL_ON_TIMEOUT, PYSLK_LOGGER, PYSLK_WILDCARDS
from ..core import _group_retrieve
from ..raw import retrieve2_raw, retrieve_raw

__all__ = [
    "retrieve",
    "retrieve_improved",
]


def retrieve_improved(
    resources: Union[
        Path, str, int, list[Path], list[str], list[int], set[Path], set[str], set[int]
    ],
    destination: Union[Path, str],
    dry_run: bool = False,
    force_overwrite: bool = False,
    ignore_existing: bool = False,
    resource_ids: bool = False,
    search_id: bool = False,
    recursive: bool = False,
    stop_on_failed_retrieval: bool = False,
    preserve_path: bool = True,
    verbose: bool = False,
) -> Optional[dict]:
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
    :param resource_ids: consider input as 'resource' as resource id or resource ids
    :type resource_ids: bool
    :param search_id: consider input as 'resource' as search id
    :type search_id: bool
    :param recursive: use the -R flag to recall recursively, Default: False
    :type recursive: bool
    :param stop_on_failed_retrieval: stop immediately when one file cannot be retrieved
    :type stop_on_failed_retrieval: bool
    :param preserve_path: preserve original file path, Default: True
    :type preserve_path: bool
    :returns: dict of file paths which were or were not retrieved
    :rtype: Optional[dict]
    """
    destination = os.path.expandvars(os.path.expanduser(destination))
    # get json output of retrieval dry run; `slk_helpers retrieve -R --json-batch /arch/bm0146/k204221/iow -d .`
    output: subprocess.CompletedProcess = retrieve2_raw(
        resources=resources,
        destination=destination,
        dry_run=True,
        force_overwrite=force_overwrite,
        ignore_existing=ignore_existing,
        json_to_file=False,
        json_batch=True,
        print_progress=False,
        resource_ids=resource_ids,
        search_id=search_id,
        recursive=recursive,
        stop_on_failed_retrieval=stop_on_failed_retrieval,
        write_envisaged_to_file=False,
        write_missing_to_file=False,
        preserve_path=preserve_path,
        verbose=False,
        double_verbose=False,
        return_type=2,
    )
    """
    example json output:
    {
      "ENVISAGED": {
        "ENVISAGED": [
          "/arch/bm0146/k204221/iow/iow_data4_001.tar",
          "/arch/bm0146/k204221/iow/INDEX.txt"
        ]
      },
      "FAILED": {
        "FAILED_NOT_CACHED": [
          "/arch/bm0146/k204221/iow/iow_data_006.tar",
          "/arch/bm0146/k204221/iow/iow_data_005.tar",
          "/arch/bm0146/k204221/iow/iow_data_004.tar",
          "/arch/bm0146/k204221/iow/iow_data_003.tar",
          "/arch/bm0146/k204221/iow/iow_data_002.tar",
          "/arch/bm0146/k204221/iow/iow_data_001.tar"
        ]
      },
      "FILES": {
        "/arch/bm0146/k204221/iow/iow_data_006.tar": "/home/k204221/Documents/99_disk2tape/48_OperationalPhase/30_lost_files/42_accidental_cache_deletion_20240808/from_sl_db/./iow_data_006.tar",
        "/arch/bm0146/k204221/iow/iow_data_005.tar": "/home/k204221/Documents/99_disk2tape/48_OperationalPhase/30_lost_files/42_accidental_cache_deletion_20240808/from_sl_db/./iow_data_005.tar",
        "/arch/bm0146/k204221/iow/iow_data_004.tar": "/home/k204221/Documents/99_disk2tape/48_OperationalPhase/30_lost_files/42_accidental_cache_deletion_20240808/from_sl_db/./iow_data_004.tar",
        "/arch/bm0146/k204221/iow/iow_data_003.tar": "/home/k204221/Documents/99_disk2tape/48_OperationalPhase/30_lost_files/42_accidental_cache_deletion_20240808/from_sl_db/./iow_data_003.tar",
        "/arch/bm0146/k204221/iow/iow_data_002.tar": "/home/k204221/Documents/99_disk2tape/48_OperationalPhase/30_lost_files/42_accidental_cache_deletion_20240808/from_sl_db/./iow_data_002.tar",
        "/arch/bm0146/k204221/iow/iow_data_001.tar": "/home/k204221/Documents/99_disk2tape/48_OperationalPhase/30_lost_files/42_accidental_cache_deletion_20240808/from_sl_db/./iow_data_001.tar",
        "/arch/bm0146/k204221/iow/INDEX.txt": "/home/k204221/Documents/99_disk2tape/48_OperationalPhase/30_lost_files/42_accidental_cache_deletion_20240808/from_sl_db/./INDEX.txt"
      }
    }
    """
    # check if exit code larger than 2: directly throw error
    if output.returncode > 2:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )
    # check if we received proper JSON output
    try:
        output_json: dict = json.loads(output.stdout.decode("utf-8").rstrip())
    except json.decoder.JSONDecodeError:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + "parsing json output failed and slk_helpers yielded this error before: "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )
    # return JSON now, if dry_run was requested
    if dry_run:
        return output_json
    # if no envisaged files are present
    if (
        "ENVISAGED" not in output_json
        or "ENVISAGED" not in output_json["ENVISAGED"]
        or len(output_json["ENVISAGED"]["ENVISAGED"]) == 0
    ):
        return output_json
    # if there are any envisaged files
    retries: int
    for src_file_path in output_json["ENVISAGED"]["ENVISAGED"]:
        dst_file_path = os.path.expandvars(
            os.path.expanduser(output_json["FILES"][src_file_path])
        )
        print(f"attempting to retrieve {src_file_path} to {dst_file_path}")
        # initial exit code; should be 3 so that we enter the loop the first time
        retries = 0
        exit_code = 3
        accumulated_wait_time = 0
        while retries < MAX_RETRIES_RETRIEVAL_ON_TIMEOUT and exit_code == 3:
            # run retrieval
            output2: subprocess.CompletedProcess = retrieve2_raw(
                resources=src_file_path,
                destination=os.path.dirname(dst_file_path),
                dry_run=dry_run,
                force_overwrite=force_overwrite,
                ignore_existing=ignore_existing,
                json_to_file=False,
                json_batch=True,
                print_progress=False,
                resource_ids=False,
                search_id=False,
                recursive=False,
                stop_on_failed_retrieval=stop_on_failed_retrieval,
                write_envisaged_to_file=False,
                write_missing_to_file=False,
                preserve_path=False,
                verbose=False,
                double_verbose=False,
                return_type=2,
            )
            exit_code = output.returncode
            # if we have reached MAX_RETRIES_RETRIEVAL_ON_TIMEOUT, we will exit anyway => no need to wait further
            if exit_code == 3 and retries + 1 < MAX_RETRIES_RETRIEVAL_ON_TIMEOUT:
                retries += 1
                accumulated_wait_time += 10 * retries
                time.sleep(10 * retries)
        # check if exit code larger than 2: directly throw error
        if output.returncode == 3:
            raise PySlkException(
                f"pyslk.{inspect.stack()[0][3]}: retrieval of {src_file_path} failed due to repeated timeouts after "
                + f"{MAX_RETRIES_RETRIEVAL_ON_TIMEOUT} retries and a total wait time of {accumulated_wait_time} seconds"
            )
        # check if we received proper JSON output
        try:
            output2_json: dict = json.loads(output2.stdout.decode("utf-8").rstrip())
        except json.decoder.JSONDecodeError:
            raise PySlkException(
                f"pyslk.{inspect.stack()[0][3]}: "
                + f"parsing json output failed and 'slk_helpers retrieve {src_file_path}' yielded this error before: "
                + f"{output.stderr.decode('utf-8').rstrip()}"
            )
        # generally, remove path from envisaged section of output_json
        output_json["ENVISAGED"]["ENVISAGED"].remove(src_file_path)
        # add the path to the respective error or success section (there should be only one section!)
        key_lvl_1 = next(iter(output2_json))
        key_lvl_2 = next(iter(output2_json[key_lvl_1]))
        if key_lvl_1 not in output_json:
            output_json[key_lvl_1] = {}
        if key_lvl_2 not in output_json[key_lvl_1]:
            output_json[key_lvl_1][key_lvl_2] = []
        output_json[key_lvl_1][key_lvl_2].append(src_file_path)

    # all retrievals done return JSON
    return output_json


def retrieve(
    resource: Union[str, list, int],
    dest_dir: Union[str, None] = None,
    recursive: bool = False,
    group: Union[bool, None] = None,
    delayed: bool = False,
    **kwargs,
) -> Union[str, list]:
    """Retrieve data from tape archive using slk retrieve

    If group is True or resource is a list of files, the retrieve calls will
    be grouped by tape id to optimize retrieve calls.
    This functions aims at implementing the recommendations of DKRZ for
    `speeding up retrievals <https://docs.dkrz.de/doc/datastorage/hsm/retrievals.html#speed-up-your-retrievals>`_.

    :param resource:
        Path, pattern, SearchID, file or list of files that should be retrieved.
    :type resource: ``str``, ``list`` or ``int``
    :param dest_dir:
        Destination directory for retrieval. Retrieves to current directory by default.
    :type dest_dir: ``str``
    :param recursive:
        Retrieve recursively.
    :type recursive: ``bool``
    :param group:
        Group files by tape id and make one retrieve call per group. If group is None,
        retrieve calls will only be grouped if resource is a list of files.
        To totally avoid grouping, set group to False.
    :type group: ``bool``
    :param delayed:
        Delay retrieve calls using dask delayed.
    :type delayed: ``bool``
    :return: StdOut from slk calls. If delayed is True, a list of ``dask.delayed.Delayed``
        objects per tape_id is returned for later (maybe parallel) execution.
    :rtype: ``str`` or ``list``

    .. seealso::
        * :py:meth:`~pyslk.retrieve_raw`

    """

    if dest_dir is None:
        dest_dir = ""

    if group is True or (isinstance(resource, (list, int)) and group is None):
        return _group_retrieve(resource, dest_dir, recursive, delayed, **kwargs)

    if delayed is True:
        from dask import delayed as delay
    else:

        def delay(x):
            return x

    if isinstance(resource, str) and PYSLK_WILDCARDS in resource:
        # create file list, slk retrieve does not support this
        resource = list(ls(resource).filename)

    PYSLK_LOGGER.debug(f"resource: {resource}")

    if isinstance(resource, list):
        return [
            delay(retrieve_raw)(r, dest_dir, recursive=recursive, **kwargs)
            for r in resource
        ]

    return delay(retrieve_raw)(resource, dest_dir, recursive=recursive, **kwargs)


# def check_retrieve_permissions_dst(
#     path_or_id: Union[Path, str, int],
#     dest_dir: Union[str, Path],
#     recursive: bool = False,
#     duplicate: bool = False,
#     preserve_path: bool = False,
#     skip_if_exists: bool = False,
# ) -> set:
#     """Retrieve files via search id or GNS path.
#
#     Overwrite files if they already exists. Prevent this by 'duplicate'
#     or 'skip_if_exists'.
#
#     :param path_or_id: search id or gns path of resources to retrieve
#     :type path_or_id: ``str`` or ``int``
#     :param dest_dir: destination directory for retrieval
#     :type dest_dir: ``str``
#     :param recursive: use the -R flag to retrieve recursively, Default: False
#     :type recursive: ``bool``
#     :param duplicate: create a duplicate file if file exists
#     :type duplicate: ``bool``
#     :param preserve_path: preserve namespace in destination
#     :type preserve_path: ``bool``
#     :param skip_if_exists: Skip if file exists
#     :type skip_if_exists: ``bool``
#     :returns: stdout of the slk call
#     :rtype: ``str``
#     """
#     output = {"allowed": dict(), "not_allowed": dict(), "root_problem": dict()}
#     files = construct_target_file_path_local(path_or_id, dest_dir, recursive, preserve_path)
