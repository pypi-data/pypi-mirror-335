import inspect
import subprocess
from pathlib import Path
from typing import Union

from pyslk.constants import PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS, SLK_HELPERS
from pyslk.pyslk_exceptions import PySlkException
from pyslk.utils import run_slk, which

__all__ = [
    "job_status_raw",
    "job_exists_raw",
    "job_queue_raw",
    "job_report_raw",
]


def job_status_raw(
    job_id: int, return_type: int = 0
) -> Union[str, int, subprocess.CompletedProcess]:
    """Check the status of a tape read job with the given ID

    Possible status values are AVAILABLE, BLOCKED and ERRORSTATE

    :param job_id: id of a recall job in StrongLink
    :type job_id: int
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    if not isinstance(job_id, int):
        raise TypeError(
            f'pyslk.{inspect.stack()[0][3]}: argument "job_id" needs to be "int" but got "{type(job_id).__name__}".'
        )

    slk_call = [SLK_HELPERS, "job_status", str(job_id)]

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


def job_exists_raw(
    job_id: int, return_type: int = 0
) -> Union[str, int, subprocess.CompletedProcess]:
    """Check if tape read job exists

    :param job_id: id of a recall job in StrongLink
    :type job_id: int
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    if not isinstance(job_id, int):
        raise TypeError(
            f'pyslk.{inspect.stack()[0][3]}: argument "job_id" needs to be "int" but got "{type(job_id).__name__}".'
        )

    slk_call = [SLK_HELPERS, "job_exists", str(job_id)]

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


def job_queue_raw(
    interpret: Union[str, None] = None, return_type: int = 0
) -> Union[str, int, subprocess.CompletedProcess]:
    """Prints status of the queue of tape read jobs

    :param interpret: interpret the queue length; possible values: DETAILS, NUMBER, TEXT, RAW, JSON
    :type interpret: str or None
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    slk_call = [SLK_HELPERS, "job_queue"]

    if interpret is not None:
        slk_call.append("--interpret")
        slk_call.append(interpret)

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


def job_report_raw(
    job_id: Union[int, str],
    outfile: Union[Path, str, None] = None,
    overwrite: bool = False,
    return_incomplete_report: bool = False,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """
    return job report

    :param job_id: a job id
    :type job_id: `str` or `int`
    :param outfile: optional output file if job report should be written into a file
    :type outfile: `str` or `Path`
    :param overwrite: overwrite destination output file if it already exists
    :type overwrite: `bool`
    :param return_incomplete_report: try to write out job report even if job is not finished yet
    :type return_incomplete_report: `bool`
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: `int`
    :returns: stdout of the slk call
    :rtype: `Union[str, int, subprocess.CompletedProcess]`
    """
    if which(SLK_HELPERS) is None:
        raise RuntimeError(f"pyslk: {SLK_HELPERS}: command not found")

    slk_call = [SLK_HELPERS, "job_report"]

    # job_id
    if isinstance(job_id, int):
        slk_call.append(str(job_id))
    elif isinstance(job_id, str):
        try:
            slk_call.append(str(int(job_id)))
        except ValueError:
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: 'job_id' cannot be processed; need 'str', which holds an integer "
                + f"number, or 'int' but got '{type(job_id).__name__}' with value '{job_id}'"
            )
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'job_id' has wrong type; need 'str' or 'int' but got "
            + f"'{type(job_id).__name__}'"
        )

    # --outfile
    if outfile is not None:
        if isinstance(outfile, (str, Path)):
            slk_call.append("--outfile").append(str(outfile))
        else:
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: 'outfile' has wrong type; need 'str' or 'Path' but got "
                + f"'{type(outfile).__name__}'"
            )

    # --force-overwrite
    if not isinstance(overwrite, bool):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'overwrite' has wrong type; need 'bool' but got "
            + f"'{type(overwrite).__name__}'"
        )
    if overwrite:
        slk_call.append("--force-overwrite")

    # --return-incomplete-report
    if not isinstance(return_incomplete_report, bool):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'return_incomplete_report' has wrong type; need 'bool' but got "
            + f"'{type(return_incomplete_report).__name__}'"
        )
    if return_incomplete_report:
        slk_call.append("--return-incomplete-report")

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
    else:
        raise ValueError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'return_type' needs to be 0, 1, 2 or 3."
        )
