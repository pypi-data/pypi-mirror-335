import inspect
import subprocess
from typing import Union

from pyslk.constants import PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS, SLK_HELPERS
from pyslk.pyslk_exceptions import PySlkException
from pyslk.utils import run_slk, which

__all__ = [
    "session_raw",
    "hostname_raw",
]


def session_raw(return_type: int = 0) -> Union[str, int, subprocess.CompletedProcess]:
    """Shows expiration date of your token

    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    slk_call = [SLK_HELPERS, "session"]

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


def hostname_raw(return_type: int = 0) -> Union[str, int, subprocess.CompletedProcess]:
    """Shows current hostname you are connected to

    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    slk_call = [SLK_HELPERS, "hostname"]

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
