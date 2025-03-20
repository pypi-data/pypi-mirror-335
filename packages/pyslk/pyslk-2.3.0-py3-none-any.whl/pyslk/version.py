import inspect

from .config import get as get_config
from .constants import SLK, SLK_HELPERS
from .pyslk_exceptions import PySlkException
from .utils import run_slk, which

__all__ = [
    "slk_helpers_version",
    "slk_version",
]

__slk_version__ = get_config("__slk_version__")
__slk_helpers_version__ = get_config("__slk_helpers_version__")

# this is the slk_version that we used to develop parsing of command line output
# if the command line output format changes in the future, the parser has to
# be adapted.
__slk_version_used_for_parser_syntax__ = "3.3.91"
__slk_helpers_version_used_for_parser_syntax__ = "1.13.3"


def slk_version() -> str:
    """List the version of slk

    :returns: stdout of the slk call
    :rtype: str
    """

    if which(SLK) is None:
        raise PySlkException("pyslk: " + SLK + ": command not found")

    slk_call = [SLK, "version"]

    return run_slk(slk_call, inspect.stack()[0][3])


def slk_helpers_version() -> str:
    """List the version of slk_helpers

    :returns: stdout of the slk_helpers call
    :rtype: str
    """

    if which(SLK_HELPERS) is None:
        raise PySlkException("pyslk: " + SLK_HELPERS + ": command not found")

    slk_call = [SLK_HELPERS, "version"]

    return run_slk(slk_call, inspect.stack()[0][3])
