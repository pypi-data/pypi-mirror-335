import inspect
import subprocess
import typing
from pathlib import Path
from typing import Union

from ..pyslk_exceptions import PySlkException
from ..raw import resource_path_raw

__all__ = ["get_resource_path"]


def get_resource_path(resource_id: Union[str, int]) -> typing.Optional[Path]:
    """Get path for a resource id

    :param resource_id: a resource_id
    :type resource_id: ``str`` or ``int``
    :returns: path of the resource; None if resource does not exist
    :rtype: ``Path`` or ``None``
    """
    if not isinstance(resource_id, (str, int)):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'resource_id' has wrong type; need 'str' or 'int' but "
            + f"got {type(resource_id).__name__}"
        )
    try:
        resource_id = int(resource_id)
    except ValueError:
        return None
    output: subprocess.CompletedProcess = resource_path_raw(resource_id, return_type=2)
    if output.returncode == 0:
        return Path(output.stdout.decode("utf-8").rstrip())
    elif output.returncode == 1:
        return None
    else:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )
