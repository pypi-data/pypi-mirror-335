from __future__ import annotations

__all__ = ["StatusJob"]

import inspect
from typing import Union


class StatusJob:
    PAUSED, QUEUED, PROCESSING, COMPLETED, SUCCESSFUL, FAILED, ABORTED = range(-4, 3)
    STATI = {}

    # PROCESSING includes COMPLETING
    # ABORTED includes ABORTING

    def __init__(self, status_str: str):
        """
        Converts a string representing the status of a recall job into a status_job object

        Possible values for status_str are:
            PAUSED, PAUSING, QUEUED, PROCESSING, COMPLETED, COMPLETING, ABORTED, ABORTING

        :param status_str: status of a recall job
        :type status_str: str
        """
        if not isinstance(status_str, str):
            raise TypeError(
                f"pyslk.StatusJob.{inspect.stack()[0][3]}: wrong type provided; need 'str'; "
                + f"got '{type(status_str).__name__}'"
            )

        self.status: int

        self.STATI[self.PAUSED] = "PAUSED"
        self.STATI[self.QUEUED] = "QUEUED"
        self.STATI[self.PROCESSING] = "PROCESSING"
        self.STATI[self.COMPLETED] = "COMPLETED"
        self.STATI[self.SUCCESSFUL] = "SUCCESSFUL"
        self.STATI[self.FAILED] = "FAILED"
        self.STATI[self.ABORTED] = "ABORTED"

        if status_str == "SUCCESSFUL":
            self.status = self.SUCCESSFUL
        elif status_str == "FAILED":
            self.status = self.FAILED
        elif status_str == "COMPLETED":
            self.status = self.COMPLETED
        elif status_str in ["PROCESSING", "COMPLETING"]:
            self.status = self.PROCESSING
        elif status_str[0:6] == "QUEUED":
            self.status = self.QUEUED
        elif status_str in ["PAUSED", "PAUSING"]:
            self.status = self.PAUSED
        elif status_str in ["ABORTED", "ABORTING"]:
            self.status = self.ABORTED
        else:
            raise ValueError(
                f"pyslk.StatusJob.{inspect.stack()[0][3]}: provided status cannot be processed: {status_str}; "
                + "please contact support@dkrz.de"
            )

    def get_status(self) -> int:
        """
        return the status as integer

        Meaning of the output
        * -4: PAUSED / PAUSING
        * -3: QUEUED
        * -2: PROCESSING / COMPLETING
        * -1: COMPLETED
        * 0: SUCCESSFUL
        * 1: FAILED
        * 2: ABORTED / ABORTING

        :return: status as integer value (-4 to 2)
        :rtype: int
        """
        return self.status

    def get_status_name(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return self.STATI[self.status]

    def get_possible_stati(self) -> dict:
        return self.STATI

    def is_paused(self) -> bool:
        return self.status == self.PAUSED

    def is_queued(self) -> bool:
        return self.status == self.QUEUED

    def is_processing(self) -> bool:
        return self.status == self.PROCESSING

    def is_finished(self) -> bool:
        return self.status in [
            self.COMPLETED,
            self.SUCCESSFUL,
            self.FAILED,
            self.ABORTED,
        ]

    def is_successful(self) -> bool:
        return self.status == self.SUCCESSFUL

    def is_completed(self) -> bool:
        return self.status == self.COMPLETED

    def has_failed(self) -> bool:
        return self.status in [self.FAILED, self.ABORTED]

    def __eq__(self, other: Union[StatusJob, int]) -> bool:
        if isinstance(other, StatusJob):
            return self.status == other.get_status()
        if isinstance(other, int):
            return self.status == other
        raise TypeError(
            f"pyslk.StatusJob.{inspect.stack()[0][3]}: wrong type provided; need 'int' or 'StatusJob'; "
            + f"got '{type(other).__name__}'"
        )

    def __ne__(self, other: StatusJob) -> bool:
        if isinstance(other, StatusJob):
            return self.status != other.get_status()
        if isinstance(other, int):
            return self.status != other
        raise TypeError(
            f"pyslk.StatusJob.{inspect.stack()[0][3]}: wrong type provided; need 'int' or 'StatusJob'; "
            + f"got '{type(other).__name__}'"
        )
