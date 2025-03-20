import inspect
import json
import warnings
from pathlib import Path
from typing import Union

from ..base import StatusJob, get_resource_path
from ..constants import MAX_RETRIES_SUBMIT_JOBS_BASIC, MAX_RETRIES_SUBMIT_JOBS_SAVE_MODE
from ..pyslk_exceptions import PySlkException
from ..raw import result_verify_job_raw, submit_verify_job_raw
from .basic import _is_job_completed, get_job_status, is_job_finished, is_job_successful
from .submitted_jobs import SubmittedJobs

__all__ = [
    "submit_verify_job",
    "get_bad_files_verify_job",
    "get_checked_resources_verify_job",
    "get_result_verify_job",
]


def submit_verify_job(
    resources: Union[str, Path, list[str], list[Path], None] = None,
    resource_ids: Union[int, str, list[int], list[str], None] = None,
    search_id: Union[int, str, None] = None,
    search_query: Union[str, None] = None,
    json_input_file: Union[str, Path, None] = None,
    recursive: bool = False,
    resume_on_page: int = 1,
    end_on_page: int = -1,
    save_mode: bool = False,
) -> SubmittedJobs:
    """
    Submit a verify job

    :param resources: provide a list of resources over which the verify job should be run
    :type resources: `str` or `Path` or `list[str]` or `list[Path]` or `None`
    :param resource_ids: provide a list of ids of resources over which the verify job should be run
    :type resource_ids: `str` or `int` or `list[str]` or `list[int]` or `None`
    :param search_id: provide a search id pointing to files over which the verify job should be run
    :type search_id: `str` or `int` or `None`
    :param search_query: provide a search query to select files over which the verify job should be run
    :type search_query: `str` or `None`
    :param json_input_file: read a JSON file which contains payload of the verify job (admin users only)
    :type json_input_file: `str` or `Path`  or `None`
    :param recursive: iterate namespaces recursively
    :type recursive: `bool`
    :param resume_on_page: resume the command and start with search result page `resume_on_page`; internally, 1000
            search results are on one 'page' and fetched by one request; you do not necessarily have read permissions
            for all of these files
    :type resume_on_page: `int`
    :param end_on_page: end with search result page `end_on_page`; internally, 1000 search results
            are on one 'page' and fetched by one request; you do not necessarily have read permissions for all of
            these files
    :type end_on_page: `int`
    :param save_mode: save mode suggested to be used in times of many timeouts; please do not regularly use this
            parameter; start one verify job per page of search results instead of one verify job for 50 pages of
            search results
    :type save_mode: `bool`
    :return: submitted jobs and, if command failed due to timeout, restart information
    :rtype: `SubmittedJobs`
    """
    first_iteration: bool = True
    iteration: int = 0
    return_code: int = -1
    submitted_jobs: SubmittedJobs = SubmittedJobs()

    # TODO: remove things

    while (first_iteration or return_code) and (
        iteration < MAX_RETRIES_SUBMIT_JOBS_BASIC + MAX_RETRIES_SUBMIT_JOBS_SAVE_MODE
    ):
        # increment counter
        iteration = iteration + 1
        # submit verify job and get subprocess output
        if first_iteration:
            first_iteration = False
            output = submit_verify_job_raw(
                resources,
                resource_ids,
                search_id,
                search_query,
                json_input_file,
                recursive,
                resume_on_page,
                end_on_page,
                save_mode,
                json=True,
                return_type=2,
            )
        else:
            if iteration <= MAX_RETRIES_SUBMIT_JOBS_BASIC:
                warnings.warn(
                    f"pyslk.{inspect.stack()[0][3]}: 'submit_verify_job' had a timeout. Retrying ..."
                )
                output = submitted_jobs.resume_submission()
            else:
                warnings.warn(
                    f"pyslk.{inspect.stack()[0][3]}: 'submit_verify_job' had a timeout. Retrying in save mode (1000 "
                    + "files per verify job)"
                )
                output = submitted_jobs.resume_submission(save_mode=True)

        # get return code (needed for while loop)
        return_code = output.returncode

        # we have an error which is not a timeout
        if output.returncode != 0 or output.returncode != 3:
            raise PySlkException(
                f"pyslk.{inspect.stack()[0][3]}: received error code {output.returncode} on iteration {iteration}. "
                + "Error message: "
                + f"{output.stdout.decode('utf-8').rstrip()} "
                + f"{output.stderr.decode('utf-8').rstrip()}"
            )

        # generate submitted jobs object
        submitted_jobs = SubmittedJobs(
            submitted_jobs_raw_output=output.stdout.decode("utf-8").rstrip()
        )

        # warn if still timeout occurred
        if output.returncode == 3:
            warnings.warn(
                f"pyslk.{inspect.stack()[0][3]}: "
                + (MAX_RETRIES_SUBMIT_JOBS_BASIC + MAX_RETRIES_SUBMIT_JOBS_SAVE_MODE)
                + " timeouts occurred while submitting verify jobs. Please start the remaining verify jobs at "
                + "a later point of time. Restart information is given in the Object returned by this function."
            )

        # return submitted_jobs
        return submitted_jobs


def get_result_verify_job(
    job_id: int,
    return_no_source: bool = False,
) -> dict[str, dict]:
    """
    Get results of one or more verify jobs

    :param job_id: job id
    :type job_id: `int`
    :param return_no_source: return the result of the verify job but do not contain a list of checked files
    :type return_no_source: `bool`
    :return: results of the verify job and its header
    :rtype: `dict[str, dict]`
    """

    # type check: job
    if not isinstance(job_id, int):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'job_id' has wrong type; need 'int' but got "
            + f"'{type(job_id).__name__}'"
        )

    # type check: --json-no-source
    if not isinstance(return_no_source, bool):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'return_no_source' has wrong type; need 'bool' but got "
            + f"'{type(return_no_source).__name__}'"
        )

    return json.loads(
        result_verify_job_raw(job_id, json=True, json_no_source=return_no_source)
    )


def get_bad_files_verify_job(
    jobs: Union[int, list[int], set[int], SubmittedJobs],
) -> dict[str, list[Path]]:
    """Get results of one or more verify jobs

    :param jobs: submitted jobs (job id, list of job ids or SubmittedJobs object)
    :type jobs: `int` or `list[int]` or `set[int]` or `SubmittedJobs`
    :return: results of the verify job
    :rtype: `dict[str, list[Path]]`
    """
    # init job list
    job_ids: list[int] = []
    # tmp raw job results and paths
    tmp_results: dict[str, list[Path]] = {}
    tmp_paths: list[Path]
    # init return value
    output: dict[str, list[Path]] = {}

    # if jobs is an int, convert to list
    if isinstance(jobs, int):
        job_ids.append(jobs)
    elif isinstance(jobs, list):
        job_ids = jobs
    elif isinstance(jobs, set):
        job_ids = list(jobs)
    elif isinstance(jobs, SubmittedJobs):
        job_ids = jobs.get_job_ids()
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'jobs' has to be of type 'int', 'list[int]' or 'SubmittedJobs' but is "
            + f"{type(jobs).__name__}"
        )

    """
    Structure of output of get_result_verify_job:
    {
    "header": {
      "job_id": "187988",
      "job_status": "COMPLETED",
      "job_start": "Tue Jan 16 22:35:17 UTC 2024",
      "job_end": "Tue Jan 16 22:36:52 UTC 2024",
      "scanned_files": "10",
      "io_verify_size_failed": 2,
      "source_resources":[76311882010,76311802010,76613132010]
    },
    "erroneous_files": {
      "size_mismatch": [
        "/dkrz_test/netcdf/20240116b/file_500mb_b.nc",
        "/dkrz_test/netcdf/20240116b/file_500mb_h.nc"
      ],
      "missing": [],
      "other": []
    }
    """
    finished_job_ids: list[bool] = [is_job_finished(job_id) for job_id in job_ids]
    status_job_ids: list[StatusJob] = [get_job_status(job_id) for job_id in job_ids]
    # check if all jobs are finished; if not => exception
    if not all(finished_job_ids):
        states: list[str] = [
            f"{job_id} with status {status}"
            for job_id, finished, status in zip(
                job_ids, finished_job_ids, status_job_ids
            )
            if not finished
        ]
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: failed: some jobs are not finished: {', '.join(states)}. Please contact "
            + "support@dkrz.de if one or more stati are not QUEUED or PROCESSING."
        )
    # check if all jobs are successful or completed; if not => exception
    successful_job_ids: list[bool] = [is_job_successful(job_id) for job_id in job_ids]
    if not all(successful_job_ids):
        completed_job_ids: list[bool] = [
            _is_job_completed(job_id) for job_id in job_ids
        ]
        if not all([s or c for s, c in zip(successful_job_ids, completed_job_ids)]):
            states: list[str] = [
                f"{job_id} with status {status}"
                for job_id, successful, status in zip(
                    job_ids, successful_job_ids, status_job_ids
                )
                if not successful
            ]
            raise PySlkException(
                f"pyslk.{inspect.stack()[0][3]}: failed: some jobs are not successful: {', '.join(states)}. Please "
                + "contact support@dkrz.de if one or more stati are not SUCCESSFUL."
            )
        # else:
        #     job_list: list[int] = [
        #         job_id
        #         for job_id, successful in zip(job_ids, successful_job_ids)
        #         if not successful
        #     ]
        #     if len(job_list) > 0:  # job_list
        #         warnings.warn(
        #             f"pyslk.{inspect.stack()[0][3]}: these jobs have the status COMPLETED but not SUCCESSFUL: "
        #             + f"{', '.join([str(job_id) for job_id in job_list])}. Please be careful when working with "
        #             + "these jobs and contact support@dkrz.de."
        #         )

    # get results of jobs
    for job_id in job_ids:
        try:
            tmp_results = get_result_verify_job(job_id, return_no_source=True)
        except PySlkException as e:
            PySlkException(
                f"pyslk.{inspect.stack()[0][3]}: 'get_result_verify_job' failed on job {job_id}, please re-run this "
                + f"function without this job id; error details: {str(e)}"
            )

        for key in tmp_results["erroneous_files"].keys():
            tmp_paths = [
                Path(res_path) for res_path in tmp_results["erroneous_files"][key]
            ]
            if key in output:
                output[key].extend(tmp_paths)
            else:
                output[key] = tmp_paths

    # return output
    return output


def get_checked_resources_verify_job(
    jobs: Union[int, list[int], SubmittedJobs],
    force_resource_path: bool = False,
) -> list[Union[int, Path]]:
    """Get results of one or more verify jobs

    TODO: doc update

    :param jobs: submitted jobs (job id, list of job ids or SubmittedJobs object)
    :type jobs: `int` or `list[int]` or `SubmittedJobs`
    :param force_resource_path: force resource path to be returned; otherwise, resource ids will be returned
        (except if a namespace was the target of the verify job which is limited to admins)
    :type force_resource_path: `bool`
    :return: results of the verify job
    :rtype: `list[Union[int, Path]]`
    """
    # init job list
    job_ids: list[int] = []
    # tmp raw job results and paths
    tmp_resource_ids: list[int] = []
    tmp_resource_paths: list[Path] = []
    # init return value
    # TODO: int or path
    output: list[Union[int, Path]] = []

    # if jobs is an int, convert to list
    if isinstance(jobs, int):
        job_ids.append(jobs)
    elif isinstance(jobs, list):
        job_ids = jobs
    elif isinstance(jobs, SubmittedJobs):
        job_ids = jobs.get_job_ids()
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'jobs' has to be of type 'int', 'list[int]' or 'SubmittedJobs' but is "
            + f"{type(jobs).__name__}"
        )

    """
    Structure of output of get_result_verify_job:
    {
    "header": {
      "job_id": "187988",
      "job_status": "COMPLETED",
      "job_start": "Tue Jan 16 22:35:17 UTC 2024",
      "job_end": "Tue Jan 16 22:36:52 UTC 2024",
      "scanned_files": "10",
      "io_verify_size_failed": 2,
      "source_resources":[76311882010,76311802010,76613132010]
    },
    "erroneous_files": {
      "size_mismatch": [
        "/dkrz_test/netcdf/20240116b/file_500mb_b.nc",
        "/dkrz_test/netcdf/20240116b/file_500mb_h.nc"
      ],
      "missing": [],
      "other": []
    }

    OR

    {
    "header": {
      "job_id": "187988",
      "job_status": "COMPLETED",
      "job_start": "Tue Jan 16 22:35:17 UTC 2024",
      "job_end": "Tue Jan 16 22:36:52 UTC 2024",
      "scanned_files": "10",
      "io_verify_size_failed": 2,
      "source_namespace": "/arch/bb1170/b381219/DELIVERABLE_WP12-D1/output"
    },
    "erroneous_files": {
      "size_mismatch": [
        "/dkrz_test/netcdf/20240116b/file_500mb_b.nc",
        "/dkrz_test/netcdf/20240116b/file_500mb_h.nc"
      ],
      "missing": [],
      "other": []
    }
    """
    finished_job_ids: list[bool] = [is_job_finished(job_id) for job_id in job_ids]
    status_job_ids: list[StatusJob] = [get_job_status(job_id) for job_id in job_ids]
    if not all(finished_job_ids):
        states: list[str] = [
            f"{job_id} with status {status}"
            for job_id, finished, status in zip(
                job_ids, finished_job_ids, status_job_ids
            )
            if not finished
        ]
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: failed: some jobs are not finished: {', '.join(states)}. Please contact "
            + "support@dkrz.de if one or more stati are not QUEUED or PROCESSING."
        )
    # TODO: COMPLETED + SUCCESSFUL are OK; no warning when COMPLETED
    successful_job_ids: list[bool] = [is_job_successful(job_id) for job_id in job_ids]
    if not all(successful_job_ids):
        completed_job_ids: list[bool] = [
            _is_job_completed(job_id) for job_id in job_ids
        ]
        if not all([s or c for s, c in zip(successful_job_ids, completed_job_ids)]):
            states: list[str] = [
                f"{job_id} with status {status}"
                for job_id, successful, status in zip(
                    job_ids, successful_job_ids, status_job_ids
                )
                if not successful
            ]
            raise PySlkException(
                f"pyslk.{inspect.stack()[0][3]}: failed: some jobs are not successful: {', '.join(states)}. Please "
                + "contact support@dkrz.de if one or more stati are not SUCCESSFUL."
            )
        # else:
        #     job_list: list[int] = [
        #         job_id
        #         for job_id, successful in zip(job_ids, successful_job_ids)
        #         if not successful
        #     ]
        #     if len(job_list) > 0:  # job_list
        #         warnings.warn(
        #             f"pyslk.{inspect.stack()[0][3]}: these jobs have the status COMPLETED but not SUCCESSFUL: "
        #             + f"{', '.join(job_list)}. Please be careful when working with these jobs and contact "
        #             + f"support@dkrz.de."
        #         )

    # get results of jobs
    for job_id in job_ids:
        try:
            tmp_results = get_result_verify_job(job_id, return_no_source=False)
        except PySlkException as e:
            PySlkException(
                f"pyslk.{inspect.stack()[0][3]}: 'get_result_verify_job' failed on job {job_id}, please re-run this "
                + f"function without this job id; error details: {str(e)}"
            )
        if "source_namespace" in tmp_results["header"]:
            tmp_resource_paths.append(Path(tmp_results["header"]["source_namespace"]))
        elif "source_resources" in tmp_results["header"]:
            tmp_resource_ids.extend(tmp_results["header"]["source_resources"])

    # add namespace paths anyway
    output.extend(tmp_resource_paths)
    # if lists of resource ids were returned, we need to check whether the user accepts ids or wants paths
    if not force_resource_path:
        output.extend(tmp_resource_ids)
    else:
        output.extend(
            [get_resource_path(resource_id) for resource_id in tmp_resource_ids]
        )

    # return output
    return output
