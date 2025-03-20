import inspect
import json
import subprocess
import typing

from ..base import StatusJob
from ..pyslk_exceptions import PySlkException
from ..raw import job_exists_raw, job_queue_raw, job_status_raw

__all__ = [
    "_is_job_completed",
    "job_exists",
    "get_job_status",
    "is_job_finished",
    "is_job_queued",
    "is_job_processing",
    "is_job_successful",
    "job_queue",
]


def _is_job_completed(job_id: int) -> typing.Optional[bool]:
    """Check the status of a tape

    :param job_id: id of a recall job in StrongLink
    :type job_id: ``int``
    :returns: True if job with job_id is finished and has status 'COMPLETED'; else False
    :rtype: ``bool`` or ``None``
    """
    job_status: StatusJob = get_job_status(job_id)
    if job_status is None:
        return None
    return job_status.is_completed()


def job_exists(job_id: int) -> bool:
    """Check if job exists

    :param job_id: id of a recall job in StrongLink
    :type job_id: ``int``
    :returns: True if job exists; False otherwise
    :rtype: ``bool``
    """
    if not isinstance(job_id, int):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: wrong input type; need 'int'; got '{type(job_id).__name__}'"
        )
    output: subprocess.CompletedProcess = job_exists_raw(job_id, return_type=2)
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


def get_job_status(job_id: int) -> typing.Optional[StatusJob]:
    """Check the status of a job

    :param job_id: id of a recall job in StrongLink
    :type job_id: ``int``
    :returns: job status; None, if job_id does not exist
    :rtype: ``pyslk.StatusJob`` or ``None``
    """
    if not isinstance(job_id, int):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: wrong input type; need 'int'; got '{type(job_id).__name__}'"
        )
    if not job_exists(job_id):
        return None
    output: subprocess.CompletedProcess = job_status_raw(job_id, return_type=2)
    if output.returncode in [0, 1]:
        return StatusJob(output.stdout.decode("utf-8").rstrip())
    else:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )


def is_job_successful(job_id: int) -> typing.Optional[bool]:
    """Check the status of a tape

    :param job_id: id of a recall job in StrongLink
    :type job_id: ``int``
    :returns: True if job with job_id is finished and was successful; else False
    :rtype: ``bool`` or ``None``
    """
    job_status: StatusJob = get_job_status(job_id)
    if job_status is None:
        return None
    return job_status.is_successful()


def is_job_finished(job_id: int) -> typing.Optional[bool]:
    """Check the status of a tape

    :param job_id: id of a recall job in StrongLink
    :type job_id: ``int``
    :returns: True if job with job_id is finished; else False
    :rtype: ``bool`` or ``None``
    """
    job_status: StatusJob = get_job_status(job_id)
    if job_status is None:
        return None
    return job_status.is_finished()


def is_job_processing(job_id: int) -> typing.Optional[bool]:
    """Check the status of a tape

    :param job_id: id of a recall job in StrongLink
    :type job_id: ``int``
    :returns: True if job with job_id is currently being processed; else False
    :rtype: ``bool`` or ``None``
    """
    job_status: StatusJob = get_job_status(job_id)
    if job_status is None:
        return None
    return job_status.is_processing()


def is_job_queued(job_id: int) -> typing.Optional[bool]:
    """Check the status of a tape

    :param job_id: id of a recall job in StrongLink
    :type job_id: ``int``
    :returns: True if job with job_id is queued; else False
    :rtype: ``bool`` or ``None``
    """
    job_status: StatusJob = get_job_status(job_id)
    if job_status is None:
        return None
    return job_status.is_queued()


def job_queue() -> dict:
    """Prints status of the queue of tape read jobs

    :returns: information on the recall job queue (number of queued and processing jobs and some more information)
    :rtype: ``dict``
    """
    return json.loads(job_queue_raw(interpret="JSON"))
