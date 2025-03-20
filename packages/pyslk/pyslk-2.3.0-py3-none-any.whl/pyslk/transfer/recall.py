import inspect
import os
import socket
import subprocess
import time
import warnings
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

from ..base import GroupCollection, StatusJob, ls
from ..core import _check_input_gfbt, _gen_group_collection, is_namespace
from ..jobs import job_queue
from ..pyslk_exceptions import (
    PySlkBadProcessError,
    PySlkException,
    PySlkNothingToRecallError,
)
from ..raw import recall2_raw, recall_needed_raw, recall_raw
from ..utils import get_recall_job_id, get_slk_pid, is_search_id

__all__ = [
    "is_recall_needed",
    "recall_dev",
    "recall_single",
    "which_files_require_recall",
]


def recall_single(
    resources: Union[
        Path, str, int, list[Path], list[str], list[int], set[Path], set[str], set[int]
    ],
    destination: Union[Path, str, None] = None,
    resource_ids: bool = False,
    search_id: bool = False,
    recursive: bool = False,
    preserve_path: bool = True,
) -> int:
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
    """
    if destination is not None:
        destination = os.path.expandvars(os.path.expanduser(destination))
    output: subprocess.CompletedProcess = recall2_raw(
        resources=resources,
        destination=destination,
        resource_ids=resource_ids,
        search_id=search_id,
        recursive=recursive,
        preserve_path=preserve_path,
        verbose=False,
        double_verbose=False,
        return_type=2,
    )
    if output.returncode == 0:
        try:
            return int(output.stdout.decode("utf-8").rstrip())
        except ValueError:
            if (
                "no resources available for recall"
                in output.stdout.decode("utf-8").rstrip()
            ):
                raise PySlkNothingToRecallError(
                    f"pyslk.{inspect.stack()[0][3]}: No files need to be recalled because they are already cached "
                    + "or/and present in the destination"
                )
            else:
                raise PySlkException(
                    f"pyslk.{inspect.stack()[0][3]}: Expected 'recall job id' as output of successfully run "
                    + "'slk_helpers recall' but could not convert output to 'int'. Output was: "
                    + f"{output.stdout.decode('utf-8').rstrip()} {output.stderr.decode('utf-8').rstrip()}"
                )
    elif output.returncode == 1:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )
    else:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )


def which_files_require_recall(
    resources: Union[
        Path, str, int, list[Path], list[str], list[int], set[Path], set[str], set[int]
    ],
    destination: Union[Path, str, None] = None,
    resource_ids: bool = False,
    search_id: bool = False,
    recursive: bool = False,
    preserve_path: bool = True,
) -> Optional[set[str]]:
    """Run a slk_helpers recall --dry-run and evaluate which files need to be recalled

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
    """
    if destination is not None:
        destination = os.path.expandvars(os.path.expanduser(destination))
    output: subprocess.CompletedProcess = recall2_raw(
        resources=resources,
        destination=destination,
        resource_ids=resource_ids,
        search_id=search_id,
        recursive=recursive,
        preserve_path=preserve_path,
        verbose=False,
        double_verbose=True,
        dry_run=True,
        return_type=2,
    )
    if output.returncode == 0:
        file_set_raw: set[str] = set(output.stderr.decode("utf-8").rstrip().split("\n"))
        file_set_require_recall: set[str] = {
            f.split(" ")[0] for f in file_set_raw if "needs to be recalled" in f
        }
        if len(file_set_require_recall) > 0:
            return file_set_require_recall
        else:
            return None
    elif output.returncode == 1:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )
    else:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )


def is_recall_needed(
    resources: Union[
        Path, str, int, list[Path], list[str], list[int], set[Path], set[str], set[int]
    ],
    destination: Union[Path, str, None] = None,
    resource_ids: bool = False,
    search_id: bool = False,
    recursive: bool = False,
    preserve_path: bool = True,
) -> bool:
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
    """
    if destination is not None:
        destination = os.path.expandvars(os.path.expanduser(destination))
    output: subprocess.CompletedProcess = recall_needed_raw(
        resources=resources,
        destination=destination,
        resource_ids=resource_ids,
        search_id=search_id,
        recursive=recursive,
        preserve_path=preserve_path,
        verbose=False,
        double_verbose=False,
        return_type=2,
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


# TODO: test
def recall(
    resource: Union[str, int, Path, list[str], GroupCollection, None] = None,
    search_id: Union[str, int, None] = None,
    search_query: Union[str, None] = None,
    recursive: bool = False,
    n_parallel_recalls_soft_max: int = 5,
    proceed_on_error: bool = False,
    verbose: bool = False,
    **kwargs,
) -> GroupCollection:
    """

    kwargs:
    * n_parallel_recalls_hard_max
    * split_recalls
    * wait_time_check_running_jobs (in seconds)
    * max_tape_number_per_search
    * wait_until_finished

    :param resource: list of files or a namespaces with files that should be recalled.
    :type resource: ``str``, ``list``, ``Path``
    :param search_id: id of a search
    :type search_id: ``int``, ``str``
    :param search_query: a search query
    :type search_query: ``str``
    :param recursive: do recursive search in the namespaces
    :type recursive: ``bool``
    :param n_parallel_recalls_soft_max: number of parallel recalls to perform
    :type n_parallel_recalls_soft_max: ``int``
    :param proceed_on_error: do not throw an error if a recall job cannot be submitted
    :type proceed_on_error: ``bool``
    :param verbose: verbose mode
    :type verbose: ``bool``
    :param kwargs: keyword arguments
    :type verbose: ``dict``
    :return: a collection of all
    :rtype: ``GroupCollection``
    """
    raise NotImplementedError(
        f"pyslk.{inspect.stack()[0][3]}: this function is not finally implement yet. Please use 'pyslk.recall_raw' "
        + "or the development version of this function 'pyslk.recall_dev'. The latter function has to be considered"
        + "as unstable and subject to spontaneous changes."
    )


def recall_dev(
    resource: Union[str, int, Path, list[str], GroupCollection, None] = None,
    search_id: Union[str, int, None] = None,
    search_query: Union[str, None] = None,
    recursive: bool = False,
    n_parallel_recalls_soft_max: int = 5,
    proceed_on_error: bool = False,
    verbose: bool = False,
    **kwargs,
) -> GroupCollection:
    """

    kwargs:
    * n_parallel_recalls_hard_max
    * split_recalls
    * wait_time_check_running_jobs (in seconds)
    * max_tape_number_per_search
    * wait_until_finished

    :param resource: list of files or a namespaces with files that should be recalled.
    :type resource: ``str``, ``list``, ``Path``
    :param search_id: id of a search
    :type search_id: ``int``, ``str``
    :param search_query: a search query
    :type search_query: ``str``
    :param recursive: do recursive search in the namespaces
    :type recursive: ``bool``
    :param n_parallel_recalls_soft_max: number of parallel recalls to perform
    :type n_parallel_recalls_soft_max: ``int``
    :param proceed_on_error: do not throw an error if a recall job cannot be submitted
    :type proceed_on_error: ``bool``
    :param verbose: verbose mode
    :type verbose: ``bool``
    :param kwargs: keyword arguments
    :type verbose: ``dict``
    :return: a collection of all
    :rtype: ``GroupCollection``
    """
    # check if input values are OK
    if isinstance(resource, GroupCollection):
        _check_input_gfbt(
            inspect.stack()[0][3], None, search_id, search_query, recursive
        )
    else:
        _check_input_gfbt(
            inspect.stack()[0][3], resource, search_id, search_query, recursive
        )

    msg: str
    # some default values for keyword arguments
    default_n_parallel_recalls_hard_max = -1
    default_split_recalls = True
    default_wait_time_check_running_jobs = 60
    default_max_tape_number_per_search = -1
    default_wait_until_finished = False
    # 600 seconds; 10 minutes
    default_max_time_to_wait_for_running_jobs = 600
    default_max_time_to_wait_for_job_id = 20
    # get max wait time
    max_wait_time_total: int = kwargs.get(
        "max_time_to_wait_for_running_jobs",
        default_max_time_to_wait_for_running_jobs,
    )
    max_wait_time_job_id_total: int = kwargs.get(
        "max_time_to_wait_for_job_id",
        default_max_time_to_wait_for_job_id,
    )
    # get wait time
    wait_time_check_running_jobs: int = kwargs.get(
        "wait_time_check_running_jobs",
        default_wait_time_check_running_jobs,
    )
    # wait time of loops
    wait_time: int

    groups: GroupCollection()
    # get or generate file groups
    if isinstance(resource, GroupCollection):
        if verbose:
            print(
                "~~~ got an instance of GroupCollection as input. No need to generate need GroupCollection"
            )
        groups = resource
    else:
        if verbose:
            print(
                "~~~ no instance of GroupCollection as input. Generate new instance of GroupCollection from input"
            )
        groups = _gen_group_collection(
            resource,
            search_id,
            search_query,
            recursive,
            max_tape_number_per_search=kwargs.get(
                "max_tape_number_per_search", default_max_tape_number_per_search
            ),
            split_recalls=kwargs.get("split_recalls", default_split_recalls),
            verbose=verbose,
        )

    # dicts to store job ids in (contain JOB_IDs AND GROUPS)
    all_jobs = set()
    active_jobs = set()
    successful_jobs = set()
    failed_jobs = set()
    error_not_started_jobs = set()
    cached_groups = set()
    # we iterate over the search Ids
    for search_id in groups:
        if verbose:
            print(f"~~~ processing group with search id '{search_id}'")

        group = groups.get_group(search_id)
        # remove error flag in file group (if set from previous recalls
        group.set_recall_error(False)
        # job needs to be started:

        # update caching info of this 'group'
        group.updated_caching_info()
        # skip group if all files are cached or group has job id + non-aborted job
        if group.is_cached() or (
            group.has_job_id()
            and group.get_job_status() not in [StatusJob.ABORTED, StatusJob.COMPLETED]
        ):
            if verbose:
                print("      skip this group (every cached or still-running recall job")
            cached_groups.add(group)
        else:
            # check if a job is COMPLETE, although we are  here (then the job is completed but not all files are cached)
            if group.has_job_id() and group.get_job_status() == StatusJob.COMPLETED:
                # warn user
                warnings.warn(
                    f"pyslk.{inspect.stack()[0][3]}: file group with search id '{search_id}' has already been "
                    + f"successfully recalled by job with id '{group.get_job_id()}' but not all files are cached."
                )
            # We set this to -1 so that we run through the while loop at least once!
            n_parallel_recalls = -1
            wait_time = 0
            while (
                len(active_jobs) > n_parallel_recalls
                and wait_time < max_wait_time_total
            ):
                # re-calculate number of allow parallel jobs
                n_parallel_recalls = _n_parallel_recalls_max(
                    n_parallel_recalls_soft_max,
                    kwargs.get(
                        "n_parallel_recalls_hard_max",
                        default_n_parallel_recalls_hard_max,
                    ),
                )
                # check running jobs
                if verbose:
                    print("   ~~~ update status of running jobs")
                # FIRST: go through all active recalls and check which are finished
                for active_job in active_jobs:
                    status = active_job.get_job_status()
                    if status.is_finished():
                        # job has finished
                        # ... add to successful or failed jobs
                        if status.is_successful():
                            successful_jobs.add(active_job)
                        else:
                            failed_jobs.add(active_job)
                            # set error flag in file group
                            active_job.set_recall_error(True)
                        # ... remove from active jobs
                        active_jobs.remove(active_job)
                if verbose:
                    print("   ~3020~~ status of recall jobs (total numbers)")
                    print(
                        "      waiting (not submitted too StrongLink): "
                        + f"{len(groups) - len(all_jobs) - len(cached_groups)}"
                    )
                    print(f"      allowed: {n_parallel_recalls}")
                    print(f"      submitted (active/queued): {len(active_jobs)}")
                    print(f"      finished, successful: {len(successful_jobs)}")
                    print(f"      finished, failed: {len(failed_jobs)}")
                    print(
                        f"      failed to be submitted: {len(error_not_started_jobs)}"
                    )
                if len(active_jobs) > n_parallel_recalls:
                    # inform user
                    if verbose:
                        print(
                            f"   ~~~ cannot submit new jobs for now; sleep {wait_time_check_running_jobs} seconds "
                            + "until re-check jobs"
                        )
                    # sleep / wait
                    time.sleep(wait_time_check_running_jobs)
                    wait_time = wait_time + wait_time_check_running_jobs
            # SECOND: submit next job
            if verbose:
                print(f"   ~~~ submitting recall job for search id {search_id}")
            proc: subprocess.Popen = recall_raw(search_id, recursive, return_type=3)
            # count submitted job
            all_jobs.add(group)
            pid: int = -1
            try:
                # try to get pid
                pid = get_slk_pid(proc)
            except PySlkBadProcessError as e:
                # no pid available
                now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                msg = (
                    "slk recall did not start properly; could not grab process ID of recall with message "
                    + f"'{str(e)}'; please see slk-cli log for details (~/.slk/slk-cli.log) close to timestamp "
                    + f"'{now}' and with hostname '{socket.gethostname()}'"
                )
                if not proceed_on_error:
                    raise PySlkBadProcessError(f"pyslk.{inspect.stack()[0][3]}: {msg}")
                # set error flag in file group
                group.set_recall_error(True)
                # store problematic group:
                error_not_started_jobs.add(group)
                # warn user
                warnings.warn(f"pyslk.{inspect.stack()[0][3]}: {msg}")
                if verbose:
                    print(f"   ~~~ {msg}")
            # set pid if available (then we are here)
            if verbose:
                print(f"   ~~~ slk recall started with pid {pid}")
            group.put_process_id(pid)
            job_id: Union[int, None] = None
            wait_time = 0
            while job_id is None and wait_time < max_wait_time_job_id_total:
                job_id = get_recall_job_id(pid)
                time.sleep(2)
                wait_time = wait_time + 2
            if job_id is not None:
                if verbose:
                    print(
                        f"   ~~~ recall job submitted successfully with job id {job_id}"
                    )
                group.put_job_id(job_id)
                active_jobs.add(group)
            else:
                # no job_id available
                now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                msg = (
                    "recall did not start as expected; please see slk-cli log for details "
                    + f"(~/.slk/slk-cli.log); related log entries contain the pid '{pid}' in column four, the "
                    + f"hostname '{socket.gethostname()}' in column three and a time stamp similar to '{now}' "
                    + "in columns one and two"
                )
                if not proceed_on_error:
                    raise PySlkBadProcessError(f"pyslk.{inspect.stack()[0][3]}: {msg}")
                # set error flag in file group
                group.set_recall_error(True)
                # store problematic group:
                error_not_started_jobs.add(group)
                # raise warning
                warnings.warn(f"pyslk.{inspect.stack()[0][3]}: {msg}")
                # write verbose
                if verbose:
                    print(f"   ~~~ {msg}")

    if kwargs.get("wait_until_finished", default_wait_until_finished):
        job_status: StatusJob
        wait_time = 0
        while len(active_jobs) > 0 and wait_time < max_wait_time_total:
            # inform user
            if verbose:
                print(
                    f"   ~~~ wait for all jobs to be finished; {len(active_jobs)}/{len(all_jobs)} not finished yet; "
                    + f"waiting {wait_time_check_running_jobs} seconds before checking the status of running jobs the "
                    + "next time"
                )
            # sleep / wait
            time.sleep(wait_time_check_running_jobs)
            wait_time = wait_time + wait_time_check_running_jobs
            for group in active_jobs:
                job_status = group.get_job_status()
                if job_status.is_finished():
                    if job_status.is_successful():
                        successful_jobs.add(group)
                    else:
                        failed_jobs.add(group)
                    active_jobs.remove(group)

    if verbose:
        print("  ~~~ number of tape groups ~~~")
        print(f"      submitted as recall jobs: {len(all_jobs)} / {len(groups)}")
        print(f"      available in the cache: {len(cached_groups)} / {len(groups)}")
        print("  ~~~ number of recall jobs ~~~")
        print(f"      submitted (active/queued): {len(active_jobs)}")
        print(f"      finished, successful: {len(successful_jobs)}")
        print(f"      finished, failed: {len(failed_jobs)}")
        print(f"      failed to be submitted: {len(error_not_started_jobs)}")

    return groups


# TODO: test
def _n_parallel_recalls_max(
    n_parallel_recalls_soft_max: int, n_parallel_recalls_hard_max: int = -1
) -> int:
    if n_parallel_recalls_hard_max > 0:
        return n_parallel_recalls_hard_max
    job_queue_info = job_queue()
    sl_active_jobs = job_queue_info["raw"]["active"]
    sl_queued_jobs = job_queue_info["raw"]["queued"]
    basic_max: int = max(14 - sl_active_jobs, 0) + max(5 - sl_queued_jobs, 0)
    return max(basic_max, n_parallel_recalls_soft_max)


def construct_target_file_path_local(
    path_or_id: Union[Path, str, int],
    dest_dir: Union[str, Path],
    recursive: bool = False,
    preserve_path: bool = False,
) -> set:
    """Construct the target path of each file to be retrieved when the given parameters are set

    :param path_or_id: search id or gns path of resources to retrieve
    :type path_or_id: ``str`` or ``int``
    :param dest_dir: destination directory for retrieval
    :type dest_dir: ``str``
    :param recursive: use the -R flag to retrieve recursively, Default: False
    :type recursive: ``bool``
    :param preserve_path: preserve namespace in destination
    :type preserve_path: ``bool``
    :returns: set of target file paths
    :rtype: ``set``
    """
    if not is_search_id(path_or_id) and is_namespace(path_or_id) and not recursive:
        raise ValueError(
            f"pyslk.{inspect.stack()[0][3]}: 'path_or_id' considered as a namespace/directory, but recursive is not set"
        )
    if preserve_path:
        files = {Path(dest_dir, f[1:]) for f in ls(path_or_id)["filename"]}
    elif is_search_id(path_or_id):
        files = {
            Path(dest_dir, f[1:]) for f in ls(path_or_id, full_path=False)["filename"]
        }
    else:
        files = {
            Path(dest_dir, Path(f).relative_to(Path(path_or_id).parent))
            for f in ls(path_or_id, full_path=False)["filename"]
        }
    return files
