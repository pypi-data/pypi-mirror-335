from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Union

from ..pyslk_exceptions import PySlkException
from ..raw import iscached_raw, job_status_raw
from .stati import StatusJob

__all__: list = ["FileGroup"]


class FileGroup:
    def __init__(self, group_dict: dict):
        # tape_id
        self.tape_ids: list[int] = list()
        tmp_tape_id = group_dict.get("tape_id", None)
        if tmp_tape_id is not None:
            self.tape_ids.append(tmp_tape_id)
        # tape_barcode
        self.tape_barcodes: list[str] = list()
        tmp_tape_barcode = group_dict.get("tape_barcode", None)
        if tmp_tape_barcode is not None:
            self.tape_barcodes.append(tmp_tape_barcode)
        # job_id
        self.job_ids: list[int] = list()
        tmp_job_id: Union[int, None] = group_dict.get("job_id", None)
        if tmp_job_id is not None:
            if isinstance(tmp_job_id, list):
                self.job_ids.extend(tmp_job_id)
            else:
                self.job_ids.append(tmp_job_id)
        # process_id
        self.process_ids: list[int] = list()
        tmp_process_id = group_dict.get("process_id", group_dict.get("pid", None))
        if tmp_process_id is not None:
            if isinstance(tmp_process_id, list):
                self.process_ids.extend(tmp_process_id)
            else:
                self.process_ids.append(tmp_process_id)
        # search_id
        self.search_id: int = group_dict.get("search_id", -1)
        # search_query
        self.search_query: str = group_dict.get("search_query", None)
        # files
        self.files: Union[list[str], list[Path]] = group_dict.get("files", list())
        # past caching status
        self.cached: bool = group_dict.get("location", "") == "cache"
        # initialize dict for job stati
        self.job_stati: dict = dict()
        # set error flag for failed recall jobs
        self.recall_error: bool = False

    def get_job_status(self) -> StatusJob:
        if len(self.job_ids) == 0:
            raise PySlkException(
                f"pyslk.{inspect.stack()[0][3]}: tried to get job status although no job id is set"
            )
        job_id: int = self.job_ids[-1]
        job_status: StatusJob = self.job_stati.get(job_id, None)
        # IF: no status exists for this job id or the job status indicates that an updated might be needed
        if job_status is None or job_status not in [
            StatusJob.COMPLETED,
            StatusJob.SUCCESSFUL,
            StatusJob.FAILED,
            StatusJob.ABORTED,
        ]:
            # run raw job_status function
            output = job_status_raw(job_id, return_type=2)
            if output.returncode in [0, 1]:
                # convert it to a proper status
                job_status = StatusJob(output.stdout.decode("utf-8")[:-1])
                self.job_stati[job_id] = job_status
            else:
                raise PySlkException(
                    f"pyslk.{inspect.stack()[0][3]}: "
                    + output.stdout.decode("utf-8")
                    + " "
                    + output.stderr.decode("utf-8")
                )

        return job_status

    def get_tape_ids(self) -> list[int]:
        return self.tape_ids

    def get_tape_barcodes(self) -> list[str]:
        return self.tape_barcodes

    def get_search_id(self) -> int:
        return self.search_id

    def get_search_query(self) -> str:
        return self.search_query

    def get_files(self) -> Union[list[str], list[Path]]:
        return self.files

    def is_cached(self) -> bool:
        return self.cached

    def updated_caching_info(self) -> bool:
        """
        Check is all files of this job are cached. Throws an error if this job is associated to no file.

        :return: info if all files of this job are cached
        :rtype: bool
        """
        if self.search_id != -1:
            self.cached = _cached_duplicate(search_id=self.search_id)
        elif self.files is not None and len(self.files) > 0:
            self.cached = all([_cached_duplicate(f) for f in self.files])
        else:
            raise PySlkException(
                f"pyslk.{inspect.stack()[0][3]}: neither search id ('search_id') nor file list ('files')"
            )
        return self.cached

    def get_job_id(self) -> int:
        """
        Returns the current job id of this job

        :return: job id
        :rtype: int
        """
        if len(self.job_ids) == 0:
            return -1
        return self.job_ids[-1]

    def get_job_ids(self) -> list[int]:
        """
        Prints the history of job IDs of this job. The first one is the oldest and the last one the newest.

        :return: all job ids which have been associated to this job
        :rtype: list[int]
        """
        return self.job_ids

    def put_job_id(self, job_id: int):
        if len(self.job_ids) == 0 or job_id != self.job_ids[-1]:
            self.job_ids.append(job_id)

    def get_process_id(self) -> int:
        """
        Returns the process id slk call which submitted the last recall job

        :return: process id
        :rtype: int
        """
        if len(self.process_ids) == 0:
            return -1
        return self.process_ids[-1]

    def get_pid(self) -> int:
        """
        Same as get_process_id(). Returns the process id slk call which submitted the last recall job

        :return: process id
        :rtype: int
        """
        return self.get_process_id()

    def get_process_ids(self) -> list[int]:
        """
        Returns the history of the process ids of the slk calls which submitted the recall jobs

        :return: all process ids which have been associated to this group
        :rtype: list[int]
        """
        return self.process_ids

    def get_pids(self) -> list[int]:
        """
        Same as get_process_ids(). Returns the history of the process ids of the slk calls which submitted the recalls

        :return: all process ids which have been associated to this group
        :rtype: list[int]
        """
        return self.get_process_ids()

    def put_process_id(self, process_id: int):
        """
        Set the current pid / process id of slk call which submitted the current recall job

        :param process_id: process id / pid to be set
        :type process_id: int
        """
        if len(self.process_ids) == 0 or process_id != self.process_ids[-1]:
            self.process_ids.append(process_id)

    def put_pid(self, process_id: int):
        """
        Same as put_process_id(). Set the current pid / process id of slk call which submitted the current recall job

        :param process_id: process id / pid to be set
        :type process_id: int
        """
        self.put_process_id(process_id)

    def is_recall_error(self) -> bool:
        return self.recall_error

    def set_recall_error(self, recall_error):
        self.recall_error = recall_error

    def has_tape_ids(self) -> bool:
        return len(self.tape_ids) > 0

    def has_tape_barcodes(self) -> bool:
        return len(self.tape_barcodes) > 0

    def has_job_id(self) -> bool:
        return len(self.job_ids) > 0

    def has_process_id(self) -> bool:
        return len(self.process_ids) > 0

    def has_pid(self) -> bool:
        return self.has_process_id()

    def has_search_id(self) -> bool:
        return self.search_id != -1

    def has_search_query(self) -> bool:
        return self.search_query is not None

    def has_files(self) -> bool:
        return len(self.files) > 0

    def put_tape_id(self, tape_id: int):
        if tape_id not in self.tape_ids:
            self.tape_ids.append(tape_id)

    def put_tape_barcode(self, tape_barcode: str):
        if tape_barcode not in self.tape_barcodes:
            self.tape_barcodes.append(tape_barcode)

    def put_files(self, files: Union[list[str], list[Path]]):
        for f in files:
            if f not in self.files:
                self.files.append(f)

    def merge_group(self, group: FileGroup):
        if self.has_search_id() and group.has_search_id():
            if self.search_id != group.get_search_id():
                raise PySlkException(
                    f"pyslk.{inspect.stack()[0][3]}: search ids do not agree. this search id: {self.search_id}. "
                    + f"other search id: {group.get_search_id()}"
                )
        for tape_id in group.get_tape_ids():
            self.put_tape_id(tape_id)
        for tape_barcode in group.get_tape_barcodes():
            self.put_tape_barcode(tape_barcode)
        self.put_files(group.get_files())

    def dump(self) -> dict:
        """
        Dump all details  of this job as a dictionary

        :return: a dictionary of all job details
        :rtype: dict
        """
        tmp_dict = dict()
        if self.has_job_id():
            tmp_dict["job_id"] = self.get_job_id()
            tmp_dict["job_ids"] = self.get_job_ids()
            tmp_dict["status"] = self.get_job_status()
        if self.has_tape_ids():
            tmp_dict["tape_ids"] = self.get_tape_ids()
        if self.has_tape_barcodes():
            tmp_dict["tape_barcodes"] = self.get_tape_barcodes()
        if self.has_search_id():
            tmp_dict["search_id"] = self.get_search_id()
        if self.has_search_query():
            tmp_dict["search_query"] = json.loads(self.get_search_query())
        if self.has_files():
            tmp_dict["files"] = self.get_files()
        tmp_dict["cached"] = self.is_cached()
        return tmp_dict

    def __str__(self) -> str:
        """
        print a JSON string of all details of this job

        :return: JSON strong of all details of this job
        :rtype: str
        """
        tmp_dict: dict = self.dump()
        if self.has_job_id():
            tmp_dict["status"] = self.get_job_status().__str__()
        return json.dumps(tmp_dict)

    def json(self) -> str:
        """
        print a JSON string of all details of this job

        :return: JSON string of all details of this job
        :rtype: str
        """
        return self.__str__()


def _cached_duplicate(
    resource: Union[str, Path, None] = None,
    search_id: Union[int, None] = None,
) -> Union[bool, dict[str, list[Path]]]:
    """Check if whether file(s) is/are in HSM cache or not; returns True/False or a dict with keys 'cached' and
        'not_cached', depending on 'details'

    :param resource: a resource path
    :type resource: str or path-like
    :param search_id: id of a search
    :type search_id: int
    :returns: True if file is in cache; False otherwise; if 'details': dictionary with an entry per file
    :rtype: bool or dict
    """
    output = iscached_raw(
        resource_path=resource, search_id=search_id, recursive=True, return_type=2
    )
    if output.returncode == 0:
        return True
    elif output.returncode == 1:
        return False
    else:
        # output.returncode is neither 0 nor 1
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + output.stdout.decode("utf-8")
            + " "
            + output.stderr.decode("utf-8")
        )
