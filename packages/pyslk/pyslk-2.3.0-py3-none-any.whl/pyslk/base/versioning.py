import inspect
from typing import Union

from ..raw import version_slk_helpers_raw, version_slk_raw

__all__ = ["cli_versions", "version_slk", "version_slk_helpers"]


def cli_versions(cli: Union[list[str], tuple[str], str, None] = None) -> dict[str, str]:
    """Return the version of slk and/or slk_helpers

    Uses :py:meth:`~pyslk.version_slk_raw` and :py:meth:`~pyslk.version_slk_helpers_raw`

    Similar to `~pyslk.version_slk` and `~pyslk.version_slk_helpers`

    :param cli: names of the commands for which the version should be obtained
    :type cli: ``list[str]``, tuple[str], ``str``
    :return: dictionary containing the versions of clis slk and/or slk_helpers
    :rtype: ``dict``

    .. seealso::
        * :py:meth:`~pyslk.version_slk`
        * :py:meth:`~pyslk.version_slk_helpers`
        * :py:meth:`~pyslk.version_slk_helpers_raw`
        * :py:meth:`~pyslk.version_slk_raw`

    """
    # check type
    if cli is not None and not isinstance(cli, (list, tuple, str)):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'cli' has wrong type; need 'list[str]', 'tuple[str]', 'str' or 'None' but "
            + f"got '{type(cli).__name__}'"
        )
    # define output dict
    output = dict()
    if (
        cli is None
        or (isinstance(cli, (list, tuple)) and "slk" in cli)
        or (isinstance(cli, str) and "slk" == cli)
    ):
        output["slk"] = version_slk_raw()
    if (
        cli is None
        or (isinstance(cli, (list, tuple)) and "slk_helpers" in cli)
        or (isinstance(cli, str) and "slk_helpers" == cli)
    ):
        output["slk_helpers"] = version_slk_helpers_raw()
    return output


def version_slk() -> str:
    """List the version of slk

    Uses :py:meth:`~pyslk.version_slk_raw`

    :returns: stdout of the slk call
    :rtype: ``str``

    .. seealso::
        * :py:meth:`~pyslk.cli_versions`
        * :py:meth:`~pyslk.version_slk`
        * :py:meth:`~pyslk.version_slk_raw`
    """
    return version_slk_raw()


def version_slk_helpers() -> str:
    """List the version of slk_helpers

    Uses :py:meth:`~pyslk.version_slk_helpers_raw`

    :returns: stdout of the slk_helpers call
    :rtype: ``str``

    .. seealso::
        * :py:meth:`~pyslk.cli_versions`
        * :py:meth:`~pyslk.version_slk_helpers`
        * :py:meth:`~pyslk.version_slk_helpers_raw`
    """
    return version_slk_helpers_raw()
