from __future__ import annotations

import inspect
import json
import typing
import warnings
from pathlib import Path
from typing import Union

from pyslk.pyslk_exceptions import PySlkException
from pyslk.raw.jobs_verify import submit_verify_job_raw

from .basic import _is_job_completed, is_job_finished, is_job_successful

__all__ = [
    "SubmittedJobs",
]

from ..constants import MAX_RETRIES_SUBMIT_JOBS_BASIC, MAX_RETRIES_SUBMIT_JOBS_SAVE_MODE


class SubmittedJobs:

    required_keys = [
        "jobs",
        "search_id",
        "source",
        "submitted_all_jobs",
        "timeout",
    ]
    optional_keys = [
        "search_query",
        "n_max_search_results",
        "n_max_verify_jobs",
        "n_verify_jobs",
        "restart_information",
    ]
    required_restart_keys = ["search_id", "start_page", "save_mode", "verbose"]

    def __init__(
        self,
        *,
        submitted_jobs_raw_output: Union[str, None] = None,
        resources: Union[str, Path, list[str], list[Path], None] = None,
        resource_ids: Union[int, str, list[int], list[str], None] = None,
        search_id: Union[int, str, None] = None,
        search_query: Union[str, None] = None,
        json_input_file: Union[str, Path, None] = None,
        recursive: bool = False,
        resume_on_page: int = 1,
        results_per_page: int = -1,
        end_on_page: int = -1,
        save_mode: bool = False,
    ):
        """
        Constructor which submits a verify job

        Expected structure of:

        .. code-block:: json

            {'source': 'resources',
            'search_id': 659962,
            'n_max_search_results': 1342935,
            'n_max_verify_jobs': 27,
            'jobs': [{'job_id': 206839, 'offset': 0, 'limit': 50000},
                {'job_id': 206843, 'offset': 50000, 'limit': 50000},
                {'job_id': 206848, 'offset': 100000, 'limit': 50000},
                {'job_id': 206854, 'offset': 150000, 'limit': 50000},
                {'job_id': 206864, 'offset': 200000, 'limit': 50000},
                {'job_id': 206876, 'offset': 250000, 'limit': 50000},
                {'job_id': 206884, 'offset': 300000, 'limit': 50000},
                {'job_id': 206892, 'offset': 350000, 'limit': 50000},
                {'job_id': 206896, 'offset': 400000, 'limit': 50000},
                {'job_id': 206898, 'offset': 450000, 'limit': 50000},
                {'job_id': 206908, 'offset': 500000, 'limit': 50000},
                {'job_id': 206911, 'offset': 550000, 'limit': 50000},
                {'job_id': 206916, 'offset': 600000, 'limit': 50000},
                {'job_id': 206920, 'offset': 650000, 'limit': 50000},
                {'job_id': 206925, 'offset': 700000, 'limit': 50000},
                {'job_id': 206933, 'offset': 750000, 'limit': 50000},
                {'job_id': 206942, 'offset': 800000, 'limit': 50000},
                {'job_id': 206950, 'offset': 850000, 'limit': 50000},
                {'job_id': 206957, 'offset': 900000, 'limit': 50000},
                {'job_id': 206963, 'offset': 950000, 'limit': 50000},
                {'job_id': 206965, 'offset': 1000000, 'limit': 50000},
                {'job_id': 206978, 'offset': 1050000, 'limit': 50000},
                {'job_id': 206983, 'offset': 1100000, 'limit': 50000},
                {'job_id': 206988, 'offset': 1150000, 'limit': 50000},
                {'job_id': 206993, 'offset': 1200000, 'limit': 50000},
                {'job_id': 206999, 'offset': 1250000, 'limit': 50000},
                {'job_id': 207006, 'offset': 1300000, 'limit': 43000}],
            'n_verify_jobs': 27,
            'submitted_all_jobs': True,
            'timeout': False}

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
                search results are on one 'page' and fetched by one request; you do not necessarily have read
                permissions for all of these files
        :type resume_on_page: `int`
        :param results_per_page: number of search results requested per page
        :type results_per_page: `int`
        :param end_on_page: end with search result page `end_on_page`; internally, 1000 search results
                are on one 'page' and fetched by one request; you do not necessarily have read permissions for all of
                these files
        :type end_on_page: `int`
        :param save_mode: save mode suggested to be used in times of many timeouts; please do not regularly use this
                parameter; start one verify job per page of search results instead of one verify job for 50 pages of
                search results
        :type save_mode: `bool`
        """

        # ~~~ set class variables ~~~
        # variables for job output
        self.__jobs__: list[dict] = list()
        self.__n_max_search_results__: int = -1
        self.__n_max_verify_jobs__: int = -1
        self.__search_id__: Union[int, str, None] = search_id
        self.__source__: Union[str, None] = None
        self.__submitted_all_jobs__: bool = False
        self.__timeout__: bool = False
        self.__search_query__: Union[str, None] = search_query
        self.__n_verify_jobs__: int = 0
        self.__restart_information__: Union[dict, None] = None
        # some variables for internal processes
        self.__submitted_any_jobs__: bool = False
        # variables for original job specification
        self.__resources__: Union[str, Path, list[str], list[Path], None] = resources
        self.__resource_ids__: Union[int, str, list[int], list[str], None] = (
            resource_ids
        )
        self.__json_input_file__: Union[str, Path, None] = json_input_file
        self.__search_query__: Union[str, None] = search_query
        self.__recursive__: bool = recursive
        self.__resume_on_page__: int = resume_on_page
        self.__results_per_page__: int = results_per_page
        self.__end_on_page__: int = end_on_page
        self.__save_mode__: bool = save_mode

        # we have four cases:
        # 1. submitted_jobs_raw_output is set
        #      This means that someone ran submit_verify_job_raw() and we just extract the results of the str output
        # 2. submitted_jobs_raw_output is None BUT either resources, resource_ids, search_id or json_input_file is set
        #      This means that we store the input values and return; the user then can run 'submit()' when he/she wants
        # 3. more than one of the above-mentioned arguments is set:
        #      error
        # 4. none of the above-mentioned arguments is set:
        #      error
        number_of_set_arguments: int = (
            (submitted_jobs_raw_output is not None)
            + (resources is not None)
            + (resource_ids is not None)
            + (search_id is not None and ())
        )
        if number_of_set_arguments > 1:
            # case 3
            raise PySlkException(
                f"pyslk.{inspect.stack()[0][3]}: more than one of the following arguments is set but only one is "
                + "allowed: 'submitted_jobs_raw_output', 'resources', 'resource_ids', 'search_id', 'json_input_file'."
            )
        if number_of_set_arguments == 0:
            # case 4
            raise PySlkException(
                f"pyslk.{inspect.stack()[0][3]}: none of the following arguments is set but exactly one is required: "
                + "'submitted_jobs_raw_output', 'resources', 'resource_ids', 'search_id', 'json_input_file'."
            )
        if submitted_jobs_raw_output is not None:
            # case 1
            submitted_jobs_dict: dict = json.loads(submitted_jobs_raw_output)
            missing_keys = [
                key for key in self.required_keys if key not in submitted_jobs_dict
            ]
            if len(missing_keys) > 0:
                raise PySlkException(
                    f"pyslk.{inspect.stack()[0][3]}: a few keys were missing in the input 'submitted_jobs_dict': "
                    + f"{missing_keys}. If you just used the output of 'pyslk.submit_verify_jobs_raw', please contact "
                    + "support@dkrz.de"
                )
            # basic job output
            self.__jobs__ = submitted_jobs_dict["jobs"]
            self.__n_max_search_results__ = submitted_jobs_dict["n_max_search_results"]
            self.__n_max_verify_jobs__ = submitted_jobs_dict["n_max_verify_jobs"]
            self.__search_id__ = submitted_jobs_dict["search_id"]
            self.__source__ = submitted_jobs_dict["source"]
            self.__submitted_all_jobs__ = submitted_jobs_dict["submitted_all_jobs"]
            self.__timeout__ = submitted_jobs_dict["timeout"]
            if "search_query" in submitted_jobs_dict:
                self.__search_query__ = submitted_jobs_dict["search_query"]
            else:
                self.__search_query__ = None
            if "n_verify_jobs" in submitted_jobs_dict:
                self.__n_verify_jobs__ = submitted_jobs_dict["n_verify_jobs"]
            else:
                self.__n_verify_jobs__ = 0
            if "restart_information" in submitted_jobs_dict:
                self.__restart_information__ = submitted_jobs_dict[
                    "restart_information"
                ]
            else:
                self.__restart_information__ = None
            # jobs have been submitted at least once
            self.__submitted_any_jobs__ = True
        else:
            # case 2: nothing to be done
            pass
            # just in case we change the default above: no jobs have been submitted
            self.__submitted_any_jobs__ = False

    def __submit_jobs__(
        self,
        resources: Union[str, Path, list[str], list[Path], None] = None,
        resource_ids: Union[int, str, list[int], list[str], None] = None,
        search_id: Union[int, str, None] = None,
        search_query: Union[str, None] = None,
        json_input_file: Union[str, Path, None] = None,
        recursive: bool = False,
        resume_on_page: int = 1,
        results_per_page: int = -1,
        end_on_page: int = -1,
        save_mode: bool = False,
    ) -> bool:
        """
        internal function: submit verify jobs and store the output internally

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
                search results are on one 'page' and fetched by one request; you do not necessarily have read
                permissions for all of these files
        :type resume_on_page: `int`
        :param results_per_page: number of search results requested per page
        :type results_per_page: `int`
        :param end_on_page: end with search result page `end_on_page`; internally, 1000 search results
                are on one 'page' and fetched by one request; you do not necessarily have read permissions for all of
                these files
        :type end_on_page: `int`
        :param save_mode: save mode suggested to be used in times of many timeouts; please do not regularly use this
                parameter; start one verify job per page of search results instead of one verify job for 50 pages of
                search results
        :type save_mode: `bool`
        :return: `True` if all jobs were submitted successfully
        :rtype: `bool`
        """

        output = submit_verify_job_raw(
            resources,
            resource_ids,
            search_id,
            search_query,
            json_input_file,
            recursive,
            resume_on_page,
            results_per_page,
            end_on_page,
            save_mode,
            json=True,
            return_type=2,
        )

        # jobs have been submitted at least once
        self.__submitted_any_jobs__ = True

        # we have an error which is not a timeout
        if output.returncode not in [0, 3]:
            raise PySlkException(
                f"pyslk.{inspect.stack()[0][3]}: received error code {output.returncode}. "
                + "Error message: "
                + f"{output.stdout.decode('utf-8').rstrip()} "
                + f"{output.stderr.decode('utf-8').rstrip()}"
            )

        # warn if timeout occurred; no error => some jobs might have been submitted
        if output.returncode == 3:
            warnings.warn(
                f"pyslk.{inspect.stack()[0][3]}: "
                + (MAX_RETRIES_SUBMIT_JOBS_BASIC + MAX_RETRIES_SUBMIT_JOBS_SAVE_MODE)
                + " timeouts occurred while submitting verify jobs. Please start the remaining verify jobs at "
                + "a later point of time. Restart information is given in the Object returned by this function."
            )

        # extract command output
        submitted_jobs_dict: dict = json.loads(output.stdout.decode("utf-8").rstrip())

        # catch some issues
        if (
            self.__search_id__ is not None
            and self.__search_id__ != submitted_jobs_dict["search_id"]
        ):
            raise PySlkException(
                f"pyslk.{inspect.stack()[0][3]}: both there is a mismatch  " + "don't"
            )
        intersection = set(self.get_job_ids()).intersection(
            set(self.extract_job_ids(submitted_jobs_dict["jobs"]))
        )
        if len(intersection) > 0:
            raise PySlkException(
                f"pyslk.{inspect.stack()[0][3]}: the submitted jobs must have different job ids what they do not have; "
                + "same job ids: {', '.join(intersection)}"
            )

        # these fields are not modified if not None:
        #  * self.__search_id__
        #  * self.__search_query__
        #  * self.__resources__
        #  * self.__resource_ids__
        #  * self.__source__
        #  * self.__n_max_search_results__
        #  * self.__n_max_verify_jobs__
        if self.__search_id__ is None:
            self.__search_id__ = submitted_jobs_dict["search_id"]
        if self.__search_query__ is None and "search_query" in submitted_jobs_dict:
            self.__search_query__ = submitted_jobs_dict["search_query"]
        if self.__resources__ is None and "resources" in submitted_jobs_dict:
            self.__resources__ = submitted_jobs_dict["resources"]
        if self.__resource_ids__ is None and "resource_ids" in submitted_jobs_dict:
            self.__resource_ids__ = submitted_jobs_dict["resource_ids"]
        if self.__source__ is None and "source" in submitted_jobs_dict:
            self.__source__ = submitted_jobs_dict["source"]
        if (
            self.__n_max_search_results__ is None
            or (
                isinstance(self.__n_max_search_results__, int)
                and self.__n_max_search_results__ == -1
            )
        ) and "n_max_search_results" in submitted_jobs_dict:
            self.__n_max_search_results__ = submitted_jobs_dict["n_max_search_results"]
        if (
            self.__n_max_verify_jobs__ == -1
            and "n_max_verify_jobs" in submitted_jobs_dict
        ):
            self.__n_max_verify_jobs__ = submitted_jobs_dict["n_max_verify_jobs"]

        # these fields are overwritten because we assume that 'other' contains more up-to-date information:
        self.__submitted_all_jobs__ = submitted_jobs_dict["submitted_all_jobs"]
        self.__timeout__ = submitted_jobs_dict["timeout"]
        if "restart_information" in submitted_jobs_dict:
            self.__restart_information__ = submitted_jobs_dict["restart_information"]
        # are merged
        if "n_verify_jobs" in submitted_jobs_dict:
            self.__n_verify_jobs__ = (
                self.__n_verify_jobs__ + submitted_jobs_dict["n_verify_jobs"]
            )
        self.__jobs__ = self.__jobs__ + submitted_jobs_dict["jobs"]

        # return value
        return self.__submitted_all_jobs__

    def submit(self, force_save_mode: bool = False):
        """
        submit jobs; fresh start of all jobs and resume interrupted submission

        :param force_save_mode: force to submit jobs in save mode; forcing non-save mode is not possible by this switch
        :type force_save_mode: `bool`
        :return: `True` if all jobs were submitted successfully
        :rtype: `bool`
        """
        # check input parameter
        if not isinstance(force_save_mode, bool):
            raise PySlkException(
                f"pyslk.{inspect.stack()[0][3]}: 'force_save_mode' must be a boolean."
            )

        # all jobs submitted => nothing to do
        if self.__submitted_all_jobs__:
            warnings.warn(
                f"pyslk.{inspect.stack()[0][3]}: all jobs have already been submitted"
            )
            return True
        # else: no or some but not all jobs have been submitted

        # no jobs have yet been submitted
        if not self.__submitted_any_jobs__:
            return self.__submit_jobs__(
                self.__resources__,
                self.__resource_ids__,
                self.__search_id__,
                self.__search_query__,
                self.__json_input_file__,
                self.__recursive__,
                self.__resume_on_page__,
                self.__results_per_page__,
                self.__end_on_page__,
                self.__save_mode__ or force_save_mode,
            )
        # else: some but not all jobs have been submitted

        # no restart information available but necessary
        if not self.has_restart_information():
            raise PySlkException(
                f"pyslk.{inspect.stack()[0][3]}: restart information is not available. Some but not all jobs have "
                + "been submitted. Need restart information to submit more."
            )
        # else: some but not all jobs have been submitted; restart information is available to submit more

        # submit more jobs based on restart information
        return self.__submit_jobs__(
            search_id=self.__restart_information__["search_id"],
            resume_on_page=self.__restart_information__["resume_on_page"],
            results_per_page=self.__restart_information__["results_per_page"],
            end_on_page=self.__restart_information__["end_on_page"],
            save_mode=self.__restart_information__["save_mode"] or force_save_mode,
        )

    def needs_restart(self) -> bool:
        return self.__restart_information__ is not None

    def has_restart_information(self) -> bool:
        return self.__restart_information__ is not None

    def missing_restart_information(self) -> list[str]:
        """
        check whether fields are missing in the available restart information

        this json should have been returned by 'pyslk.submit_verify_jobs_raw'

        .. code-block:: json

            {
                "restart_information": {
                    "search_id": 613746,
                    "start_page": 1,
                    "save_mode": false,
                    "verbose": false
                }
            }
        """
        if not self.has_restart_information():
            raise PySlkException(
                f"pyslk.{inspect.stack()[0][3]}: restart information is not available."
            )
        return [
            key
            for key in self.required_restart_keys
            if key not in self.__restart_information__
        ]

    def get_restart_information(self) -> dict:
        if not self.has_restart_information():
            raise PySlkException(
                f"pyslk.{inspect.stack()[0][3]}: restart information is not available."
            )
        return self.__restart_information__

    def get_job_ids(self) -> list[int]:
        return [job["job_id"] for job in self.__jobs__]

    @staticmethod
    def extract_job_ids(jobs: list[dict]) -> list[int]:
        return [job["job_id"] for job in jobs]

    def get_job_information(self, job_id: int) -> typing.Optional[dict]:
        for job in self.__jobs__:
            if job["job_id"] == job_id:
                return job
        return None

    def get_search_id(self) -> int:
        return self.__search_id__

    def get_source(self) -> typing.Optional[str, Path, list[int]]:
        if self.__source__ is None:
            return None
        return self.__source__

    def get_search_query(self) -> typing.Optional[str]:
        if self.__search_query__ is None:
            return None
        return self.__search_query__

    def finished_successfully(self) -> bool:
        return self.__submitted_all_jobs__

    def had_timeout(self) -> bool:
        return self.__timeout__

    def are_finished_short(self) -> bool:
        for job_id in self.get_job_ids():
            if not is_job_finished(job_id):
                return False
        return True

    def are_finished_details(self) -> dict[int, bool]:
        output = {}
        for job_id in self.get_job_ids():
            output[job_id] = is_job_finished(job_id)
        return output

    def are_successful_short(self) -> bool:
        for job_id in self.get_job_ids():
            if not is_job_successful(job_id):
                return False
        return True

    def are_successful_details(self) -> dict[int, bool]:
        output = {}
        for job_id in self.get_job_ids():
            output[job_id] = is_job_successful(job_id)
        return output

    def are_completed_short(self) -> bool:
        for job_id in self.get_job_ids():
            if not _is_job_completed(job_id):
                return False
        return True

    def are_completed_details(self) -> dict[int, bool]:
        output = {}
        for job_id in self.get_job_ids():
            output[job_id] = _is_job_completed(job_id)
        return output

    def merge(self, other: SubmittedJobs):
        if self.__search_id__ != other.__search_id__:
            raise PySlkException(
                f"pyslk.{inspect.stack()[0][3]}: both SubmittedJobs need to be based on the same search id what they "
                + "don't"
            )
        intersection = set(self.get_job_ids()).intersection(set(other.get_job_ids()))
        if len(intersection) > 0:
            raise PySlkException(
                f"pyslk.{inspect.stack()[0][3]}: the SubmittedJobs must have different job ids what they do not have; "
                + "same job ids: {', '.join(intersection)}"
            )

        # these fields are not modified:
        #  * self.__search_query__
        #  * self.__source__
        # these files are set to -1 because it is hard to guess their values
        #  * self.__n_max_search_results__
        #  * self.__n_max_verify_jobs__
        self.__n_max_search_results__ = -1
        self.__n_max_verify_jobs__ = -1
        # these fields are overwritten because we assume that 'other' contains more up-to-date information:
        self.__submitted_all_jobs__ = other.__submitted_all_jobs__
        self.__timeout__ = other.__timeout__
        self.__restart_information__ = other.__restart_information__
        # are merged
        self.__n_verify_jobs__ = self.__n_verify_jobs__ + other.__n_verify_jobs__
        self.__jobs__ = self.__jobs__ + other.__jobs__
