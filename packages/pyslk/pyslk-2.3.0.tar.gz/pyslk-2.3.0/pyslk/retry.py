from warnings import warn

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from .pyslk_exceptions import ArchiveError
from .raw import archive_raw

__all__ = ["try_archive", "log_attempt_number"]

archive_attempts = 3


def log_attempt_number(retry_state):
    """return the result of the last call attempt"""
    warn(f"{retry_state.outcome}, retrying: {retry_state.attempt_number}...")


@retry(
    stop=stop_after_attempt(archive_attempts),
    retry=retry_if_exception_type(ArchiveError),
    reraise=True,
    wait=wait_fixed(10),
    after=log_attempt_number,
)
def try_archive(resource, dst_gns, recursive=False, **kwargs):
    """Archive function wrapper for slk_archive

    If the archive fails due to HostNotReachableError, archiving will
    wait for 10 seconds and retry. Maximal 3 attempts are made.
    After that, HostNotReachableError will be raised after all.

    """
    return archive_raw(resource, dst_gns, recursive=recursive, **kwargs)
