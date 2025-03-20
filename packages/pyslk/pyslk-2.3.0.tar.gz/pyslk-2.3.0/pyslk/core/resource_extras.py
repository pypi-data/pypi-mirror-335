import inspect
import subprocess
import typing
from pathlib import Path
from typing import Union

from ..base import get_resource_path, searchid_exists
from ..pyslk_exceptions import PySlkException
from ..raw import exists_raw, resource_path_raw, resource_type_raw

__all__ = [
    "get_resource_type",
    "is_file",
    "is_namespace",
    "resource_exists",
    "_check_resource",
    "_check_resource_and_search_id",
]


def resource_exists(resource: Union[str, Path, int]) -> bool:
    """Check if resource exists and return True/False

    :param resource: namespace or resource
    :type resource: ``str`` or ``path-like``
    :returns: True if file exists; False otherwise
    :rtype: ``bool``
    """
    # determine whether we have resource id or resource path
    resource_id: Union[int, None] = None
    resource_path: Union[Path, None] = None
    if isinstance(resource, int):
        resource_id = resource
    elif isinstance(resource, Path):
        resource_path = resource
    elif isinstance(resource, str):
        # resource can either be a resource id or a resource path
        try:
            resource_id = int(resource)
        except ValueError:
            try:
                resource_path = Path(resource)
            except ValueError:
                raise TypeError(
                    f"pyslk.{inspect.stack()[0][3]}: cannot convert 'resource' to 'int' (== resource id) "
                    + "or 'path-like' (== resource path)"
                )
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'resource' has wrong type; need 'str', 'int' or 'Path' but "
            + f"got {type(resource).__name__}"
        )
    # run slk_helpers command
    if resource_path is not None:
        output: subprocess.CompletedProcess = exists_raw(
            str(resource_path), return_type=2
        )
    else:
        # resource_id is not None
        output: subprocess.CompletedProcess = resource_path_raw(
            resource_id, return_type=2
        )
    # evaluate output
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


def _check_resource_and_search_id(
    calling_function: str,
    resource: Union[str, int, Path, list, None] = None,
    search_id: Union[str, int, None] = None,
) -> typing.Optional[tuple[Union[Path, list[Path]], int, int]]:
    """Checks whether the input arguments 'resource' and 'search_id' are properly set

    Thrown errors

    * ``PySlkException``
    * ``TypeError``
    * ``ValueError``

    :param calling_function: name of the functions which calls this function
    :type calling_function: ``str``
    :param resource: a resource id or a resource path
    :type resource: ``str`` or ``int`` or ``path-like``
    :param search_id: id of a search
    :type search_id: ``int`` or ``str``
    :returns: True if one or more files are flagged; False otherwise; if 'details': dictionary with two keys
        'flag_partial' and 'no_flag_partial' which each have a list of files as value
    :rtype: ``bool`` or ``dict`` or ``None``
    """
    # check if one of resource and search_id is set
    if resource is None and search_id is None:
        raise ValueError(
            f"pyslk.{calling_function}: either 'resource' xor 'search_id' have to be non-None values"
        )
    if resource is not None and search_id is not None:
        raise ValueError(
            f"pyslk.{calling_function}: either 'resource' xor 'search_id' have to be non-None values, not both"
        )
    # ~~~~~~~~~ check resource ~~~~~~~~~
    if resource is not None:
        # basic type checking
        if not isinstance(resource, (str, int, Path, list)):
            raise TypeError(
                f"pyslk.{calling_function}: 'resource' has wrong type; need 'str', 'int', 'Path' or 'list' but "
                + f"got {type(resource).__name__}"
            )
        if isinstance(resource, list):
            if len(resource) == 0:
                # check if resource exists and if empty list
                return None
            elif isinstance(resource, list) and len(resource) == 1:
                # make list to non-list if list has length of 1
                resource = resource[0]
            else:
                # here, we only have lists with length > 1
                if any([isinstance(i, int) for i in resource]):
                    # check if we have multiple resources and at least one is an int
                    raise TypeError(
                        f"pyslk.{calling_function}: 'resource' is a list with more than one item; at least one item "
                        + "is of type 'int' (== resource id); however, only one resource id is allowed"
                    )
                if any([not isinstance(i, (str, Path)) for i in resource]):
                    raise TypeError(
                        f"pyslk.{calling_function}: 'resource' is a list; the elements in the list have to be 'str' or "
                        + f"path-like but got: {', '.join([type(res).__name__ for res in resource])}"
                    )
        elif not resource_exists(resource):
            # we arrive here if we are not a list;
            # check if resource exists
            return None
    # ~~~~~~~~~ check search ~~~~~~~~~
    # check if search_id exists if non-None
    if search_id is not None and not searchid_exists(search_id):
        return None
    # ~~~~~~~~~ convert values ~~~~~~~~~
    resource_id: Union[int, None] = None
    resource_path: Union[Path, list, None] = None
    if isinstance(resource, int):
        resource_id = resource
    elif isinstance(resource, Path):
        resource_path = resource
    elif isinstance(resource, list):
        # note: we checked already above whether all elements of the list are 'str' or path-like
        resource_path = resource
    elif isinstance(resource, str):
        # resource can either be a resource id or a resource path
        try:
            resource_id = int(resource)
        except ValueError:
            try:
                resource_path = Path(resource)
            except ValueError:
                raise TypeError(
                    f"pyslk.{calling_function}: cannot convert 'resource' to 'int' (== resource id) "
                    + "or 'path-like' (== resource path)"
                )
    if isinstance(search_id, str):
        # resource can either be a resource id or a resource path
        try:
            search_id = int(search_id)
        except ValueError:
            raise TypeError(
                f"pyslk.{calling_function}: cannot convert 'search_id' from 'str' to 'int'"
            )
    # return proper values
    return resource_path, resource_id, search_id


def _check_resource(
    calling_function: str,
    resource: Union[str, int, Path, list],
) -> typing.Optional[tuple[Union[Path, list[Path]], int]]:
    """Checks whether the input argument 'resource' is properly set

    Thrown errors

    * ``PySlkException``
    * ``TypeError``
    * ``ValueError``

    :param calling_function: name of the functions which calls this function
    :type calling_function: ``str``
    :param resource: a resource id or a resource path
    :type resource: ``str`` or ``int`` or ``path-like``
    :returns: True if one or more files are flagged; False otherwise; if 'details': dictionary with two keys
        'flag_partial' and 'no_flag_partial' which each have a list of files as value
    :rtype: ``bool`` or ``dict`` or ``None``
    """
    # ~~~~~~~~~ check resource ~~~~~~~~~
    if resource is not None:
        # basic type checking
        if not isinstance(resource, (str, int, Path, list)):
            raise TypeError(
                f"pyslk.{calling_function}: 'resource' has wrong type; need 'str', 'int', 'Path' or 'list' but "
                + f"got {type(resource).__name__}"
            )
        if isinstance(resource, list):
            if len(resource) == 0:
                # check if resource exists and if empty list
                return None
            elif isinstance(resource, list) and len(resource) == 1:
                # make list to non-list if list has length of 1
                resource = resource[0]
            else:
                # here, we only have lists with length > 1
                if any([isinstance(i, int) for i in resource]):
                    # check if we have multiple resources and at least one is an int
                    raise TypeError(
                        f"pyslk.{calling_function}: 'resource' is a list with more than one item; at least one item "
                        + "is of type 'int' (== resource id); however, only one resource id is allowed"
                    )
                if any([not isinstance(i, (str, Path)) for i in resource]):
                    raise TypeError(
                        f"pyslk.{calling_function}: 'resource' is a list; the elements in the list have to be 'str' or "
                        + f"path-like but got: {', '.join([type(res).__name__ for res in resource])}"
                    )
        elif not resource_exists(resource):
            # we arrive here if we are not a list;
            # check if resource exists
            return None
    # ~~~~~~~~~ convert values ~~~~~~~~~
    resource_id: Union[int, None] = None
    resource_path: Union[Path, list, None] = None
    if isinstance(resource, int):
        resource_id = resource
    elif isinstance(resource, Path):
        resource_path = resource
    elif isinstance(resource, list):
        # note: we checked already above whether all elements of the list are 'str' or path-like
        resource_path = resource
    elif isinstance(resource, str):
        # resource can either be a resource id or a resource path
        try:
            resource_id = int(resource)
        except ValueError:
            try:
                resource_path = Path(resource)
            except ValueError:
                raise TypeError(
                    f"pyslk.{calling_function}: cannot convert 'resource' to 'int' (== resource id) "
                    + "or 'path-like' (== resource path)"
                )
    # return proper values
    return resource_path, resource_id


def get_resource_type(resource: Union[str, int, Path]) -> typing.Optional[str]:
    """Get type of resource

    :param resource: a resource id or a resource path
    :type resource: ``str`` or ``int`` or ``path-like``
    :returns: type of the resource; None if resource does not exist
    :rtype: ``str`` or ``None``
    """
    if not resource_exists(resource):
        return None
    resource_id: Union[int, None] = None
    resource_path: Union[Path, None] = None
    if isinstance(resource, int):
        resource_id = resource
    elif isinstance(resource, Path):
        resource_path = resource
    elif isinstance(resource, str):
        # resource can either be a resource id or a resource path
        try:
            resource_id = int(resource)
        except ValueError:
            try:
                resource_path = Path(resource)
            except ValueError:
                raise TypeError(
                    f"pyslk.{inspect.stack()[0][3]}: cannot convert 'resource' to 'int' (== resource id) "
                    + "or 'path-like' (== resource path)"
                )
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'resource' has wrong type; need 'str', 'int' or 'Path' but "
            + f"got {type(resource).__name__}"
        )
    if resource_path is not None and not resource_exists(resource_path):
        raise ValueError(
            f"pyslk.{inspect.stack()[0][3]}: 'resource' was considered as resource path and does not exist: {resource}"
        )
    if resource_id is not None and not get_resource_path(resource_id):
        raise ValueError(
            f"pyslk.{inspect.stack()[0][3]}: 'resource' was considered as resource id and does not exist: {resource}"
        )
    output: subprocess.CompletedProcess = resource_type_raw(
        resource_path, resource_id, return_type=2
    )
    if output.returncode == 0:
        return output.stdout.decode("utf-8").rstrip()
    elif output.returncode == 1:
        return None
    else:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )


def is_namespace(resource: Union[str, int, Path, None] = None) -> typing.Optional[bool]:
    """Returns True if resource is a namespace

    :param resource: a resource id or a resource path
    :type resource: ``str`` or ``int`` or ``path-like``
    :returns: True if resource is a namespace; else False
    :rtype: ``str`` or ``None``
    """
    # run get_resource_type
    output = get_resource_type(resource)
    if output is None:
        return None
    # check the type
    if output.lower() == "namespace":
        return True
    return False


def is_file(resource: Union[str, int, Path, None] = None) -> typing.Optional[bool]:
    """Returns True if resource is a file

    :param resource: a resource id or a resource path
    :type resource: ``str`` or ``int`` or ``path-like``
    :returns: True if resource is a file; else False
    :rtype: ``str`` or ``None``
    """
    # run get_resource_type
    output = get_resource_type(resource)
    if output is None:
        return None
    # check the type
    if output.lower() == "file":
        return True
    return False
