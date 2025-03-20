import inspect
import math
import os
import subprocess
import typing
from pathlib import Path
from typing import Union

from ..base import get_resource_path, ls
from ..constants import PYSLK_FILE_SIZE_UNITS
from ..pyslk_exceptions import PySlkException
from ..raw import (
    checksum_raw,
    chmod_raw,
    delete_raw,
    exists_raw,
    group_raw,
    has_no_flag_partial_raw,
    list_raw,
    mkdir_raw,
    move_raw,
    owner_raw,
    rename_raw,
    resource_mtime_raw,
    resource_permissions_raw,
    resource_tape_raw,
    size_raw,
)
from ..utils import _convert_size, _parse_list_to_rows, _parse_size
from .resource_extras import (
    _check_resource_and_search_id,
    is_namespace,
    resource_exists,
)

__all__ = [
    "access_hsm",
    "arch_size",
    "chgrp",
    "chmod",
    "chown",
    "delete",
    "get_checksum",
    "get_resource_id",
    "get_resource_mtime",
    "get_resource_permissions",
    "get_resource_size",
    "get_resource_tape",
    "has_no_flag_partial",
    "has_no_flag_partial_details",
    "makedirs",
    "mkdir",
    "move",
    "rename",
]


def get_resource_tape(
    resource_path: Union[str, Path],
) -> typing.Optional[dict[int, str]]:
    """returns tape on which resource with given path is stored on

    :param resource_path: namespace or resource
    :type resource_path: ``str`` or ``path-like``
    :returns: tape(s) on which a file is/are stored on as dict; None otherwise
    :rtype: ``dict[int, str]`` or ``None``
    """
    if not isinstance(resource_path, (str, Path)):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'resource_path' has wrong type; need 'str' or 'Path' but "
            + f"got {type(resource_path).__name__}"
        )
    output: subprocess.CompletedProcess = resource_tape_raw(
        str(resource_path), return_type=2
    )

    if output.returncode == 0:
        tmp_output: list[str] = [
            i for i in output.stdout.decode("utf-8").rstrip().split("\n") if i != ""
        ]
        try:
            n_tapes = int(tmp_output[-1].split(": ")[1])
        except ValueError:
            raise PySlkException(
                f"pyslk.{inspect.stack()[0][3]}: unexpected output from 'slk_helpers resource_tape': "
                + f"{output.stdout.decode('utf-8').rstrip()} "
                + f"{output.stderr.decode('utf-8').rstrip()}"
            )
        # file stored on no tape
        if n_tapes == 0:
            return None
        if len(tmp_output) != n_tapes + 1:
            raise PySlkException(
                f"pyslk.{inspect.stack()[0][3]}: unexpected output from 'slk_helpers resource_tape': "
                + f"{output.stdout.decode('utf-8').rstrip()} "
                + f"{output.stderr.decode('utf-8').rstrip()}"
            )
        out_dict: dict = {}
        for t in tmp_output[:-1]:
            t = t.split(": ")[1].split("(")
            out_dict[int(t[0])] = t[1][:-1]
        return out_dict
    else:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )


def get_resource_id(resource_path: Union[str, Path]) -> typing.Optional[int]:
    """returns resource_id to a resource path

    :param resource_path: namespace or resource
    :type resource_path: ``str`` or ``path-like``
    :returns: resource_id if the file exists; None otherwise
    :rtype: ``int`` or ``None``
    """
    if not isinstance(resource_path, (str, Path)):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'resource_path' has wrong type; need 'str' or 'Path' but "
            + f"got {type(resource_path).__name__}"
        )
    output: subprocess.CompletedProcess = exists_raw(str(resource_path), return_type=2)
    if output.returncode == 0:
        return int(output.stdout.decode("utf-8").rstrip().split(":")[1])
    elif output.returncode == 1:
        return None
    else:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )


def get_resource_mtime(resource_path: Union[str, Path]) -> typing.Optional[int]:
    """returns mtime of a resource path

    :param resource_path: namespace or resource
    :type resource_path: ``str`` or ``path-like``
    :returns: mtime if the file exists; None otherwise
    :rtype: ``int`` or ``None``
    """
    if not isinstance(resource_path, (str, Path)):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'resource_path' has wrong type; need 'str' or 'Path' but "
            + f"got {type(resource_path).__name__}"
        )
    output: subprocess.CompletedProcess = resource_mtime_raw(
        str(resource_path), return_type=2
    )
    if output.returncode == 0:
        return int(output.stdout.decode("utf-8").rstrip())
    elif output.returncode == 1:
        return None
    else:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )


def get_resource_size(
    resource: Union[str, int, Path], recursive: bool = False
) -> typing.Optional[int]:
    """Returns file size in byte

    :param resource: a resource id or a resource path
    :type resource: ``str`` or ``int`` or ``path-like``
    :param recursive: use the -R to calculate size recursively
    :type recursive: `bool`
    :returns: size in byte; None if resource does not exist
    :rtype: ``int`` or ``None``
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
        raise FileNotFoundError(
            f"pyslk.{inspect.stack()[0][3]}: 'resource' was considered as resource path and does not exist: {resource}"
        )
    if resource_id is not None and not get_resource_path(resource_id):
        raise FileNotFoundError(
            f"pyslk.{inspect.stack()[0][3]}: 'resource' was considered as resource id and does not exist: {resource}"
        )
    # check type of 'recursive'
    if not isinstance(recursive, bool):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'recursive' needs to be 'bool' but got "
            + f"'{type(recursive).__name__}'"
        )
    return int(size_raw(resource_path, resource_id, recursive))


def get_resource_permissions(
    resource: Union[str, int, Path, None] = None,
    as_octal_number: bool = False,
) -> typing.Optional[Union[str, bool]]:
    """Get path for a resource id

    :param resource: a resource id or a resource path
    :type resource: ``str`` or ``int`` or ``path-like``
    :param as_octal_number: Do not return the permissions as combination of x/w/r/- but as three digit octal number
    :type as_octal_number: ``bool``
    :returns: permissions string; False if resource does not exist
    :rtype: ``str`` or ``bool`` or ``None``
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
    output: subprocess.CompletedProcess = resource_permissions_raw(
        resource_path, resource_id, as_octal_number, return_type=2
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


def access_hsm(
    resource: Union[list[str], list[Path], str, Path], mode: int
) -> Union[bool, list[bool]]:
    if isinstance(resource, str):
        return access_hsm(Path(resource), mode)
    elif isinstance(resource, list):
        return [access_hsm(i, mode) for i in resource]
    elif isinstance(resource, Path):
        if mode not in [os.F_OK, os.R_OK, os.W_OK, os.X_OK]:
            return [False]
        if not resource_exists(resource):
            return [False]
        if mode == os.F_OK:
            return [True]
        # TODO: can we use resource_permissions here?
        raise NotImplementedError(
            "Tests for 'os.W_OK', 'os.X_OK' and 'os.R_OK' are not implemented yet."
        )
    else:
        raise TypeError(
            "Need 'str', path-like object or list of one of both types as input. Got "
            + f"'{type(resource).__name__}'."
        )


def arch_size(
    path_or_id: Union[str, int], unit: str = "B"
) -> dict[str, Union[str, float, int]]:
    """Get archive size from search id or GNS path
    by recursively listing all files of archive and
    adding file sizes

    :param path_or_id: search id or gns path
    :type path_or_id: ``str``
    :param unit: Prefix of returned size must be
        one of B, K, M, G, T, P or h for Byte, Kilobyte, Megabyte
        Gigabyte, Terrabyte, Petabyte or "human-readable";
        default: B
    :type unit: ``str``
    :returns: archive size, in key "value" contains size without unit and key "unit" contains unit
    :rtype: ``dict``
    """
    if not isinstance(unit, str):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'return_format' has to be a string of value "
            + f"{', '.join(PYSLK_FILE_SIZE_UNITS.keys())} or h."
        )

    # Get archive files
    list_out = list_raw(path_or_id, recursive=True)
    # df = pd.read_fwf(list_out, col_specs = 'infer',
    #                 width=column_widths, dtype=str, header=None,
    #                 names=column_names, infer_nrows=10000) #infer_nrows
    # df.drop(df.tail(2).index, inplace=True)
    rows = _parse_list_to_rows(
        list_out.split("\n"), path_or_id=path_or_id, full_path=False
    )
    sizes = [_parse_size(r[3]) for r in rows]

    # sum sizes
    size_byte = sum([s for s in sizes if not math.isnan(s)])

    # check if return format is byte or 'best size'/human-readable
    return _convert_size(size_byte, unit)


def mkdir(gns_path: Union[str, Path]) -> int:
    """Create a directory

    If the directory already exists, ``FileExistsError`` is raised. If a parent directory in the path does not exist,
    ``FileNotFoundError`` is raised.

    :param gns_path: gns path to create
    :type gns_path: ``str`` or ``Path``
    :returns: namespace/resource id of the created namespace
    :rtype: ``int``

    .. seealso::
        * :py:meth:`~pyslk.makedirs`
        * :py:meth:`~pyslk.mkdir_raw`
    """
    # throw FileExistsError if resource already exists
    if resource_exists(gns_path):
        raise FileExistsError(f"pyslk.{inspect.stack()[0][3]}: file exists: {gns_path}")
    # check if parent directory does not exist
    if not resource_exists(os.path.dirname(gns_path)):
        raise FileNotFoundError(
            f"pyslk.{inspect.stack()[0][3]}: no such file or directory: {os.path.dirname(gns_path)}"
        )
    output: subprocess.CompletedProcess = mkdir_raw(
        gns_path, recursive=False, parents=False, return_type=2
    )
    # if problems during creation of folder / namespace
    if output.returncode > 0:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )
    return get_resource_id(gns_path)


def makedirs(gns_path: Union[str, Path], exist_ok: bool = False) -> int:
    """Create a directory like 'mkdir()' but create parent directories recursively, if they do not exist

    If exist_ok is False (the default), a FileExistsError is raised if the target directory already exists.

    :param gns_path: gns path to create
    :type gns_path: ``str`` or ``Path``
    :param exist_ok: throw no error if folder already exists (like 'mkdir -p')
    :type exist_ok: ``bool``
    :returns: namespace/resource id of the created namespace
    :rtype: ``int``

    .. seealso::
        * :py:meth:`~pyslk.mkdir`
        * :py:meth:`~pyslk.mkdir_raw`
    """
    # throw FileExistsError if resource already exists and [it is not a namespace or exist_ok is not set]
    if resource_exists(gns_path) and (not is_namespace(gns_path) or not exist_ok):
        raise FileExistsError(f"pyslk.{inspect.stack()[0][3]}: file exists: {gns_path}")
    # following if-clause is actually not needed because we catch the different cases already in the lines above
    if exist_ok:
        # create recursively and do nothing if namespace exists
        output: subprocess.CompletedProcess = mkdir_raw(
            gns_path, recursive=False, parents=True, return_type=2
        )
    else:
        # create recursively and throw error if namespace exists
        output: subprocess.CompletedProcess = mkdir_raw(
            gns_path, recursive=True, parents=False, return_type=2
        )
    # if problems during creation of folder / namespace
    if output.returncode > 0:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )
    return get_resource_id(gns_path)


def rename(old_name: str, new_name: str) -> int:
    """Rename a folder or file; moving is not possible

    :param old_name: folder or file name (full GNS path)
    :type old_name: ``str``
    :param new_name: new name (only name; no full GNS path)
    :type new_name: ``str``
    :returns: return resource id of the renamed resource
    :rtype: ``int``
    """
    # get res id and throw error if source file does not exist
    resource_id: Union[int, None] = get_resource_id(old_name)
    if resource_id is None:
        raise FileNotFoundError(
            f"pyslk.{inspect.stack()[0][3]}: resource does not exist: {old_name}"
        )
    # run command
    output: subprocess.CompletedProcess = rename_raw(old_name, new_name, return_type=2)
    # if problems during creation of folder / namespace
    if output.returncode > 0:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )
    # resource id
    return resource_id


def move(src_path: str, dst_gns: str, no_overwrite: bool) -> int:
    """Move namespaces/files from one parent folder to another; renaming is
    not possible

    :param src_path: namespace or file (full GNS path)
    :type src_path: ``str``
    :param dst_gns: new parent namespace
    :type dst_gns: ``str``
    :param no_overwrite: do not overwrite target file if it exists
    :type no_overwrite: ``bool``
    :returns: return resource id of the moved resource
    :rtype: ``int``
    """
    # get res id and throw error if source file does not exist
    resource_id: Union[int, None] = get_resource_id(src_path)
    if resource_id is None:
        raise FileNotFoundError(
            f"pyslk.{inspect.stack()[0][3]}: resource does not exist: {src_path}"
        )
    # run command
    output: subprocess.CompletedProcess = move_raw(
        src_path, dst_gns, no_overwrite, return_type=2
    )
    # if problems during creation of folder / namespace
    if output.returncode > 0:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )
    # return resource id
    return resource_id


def delete(gns_path: Union[str, Path, list], recursive: bool = False) -> None:
    """Soft delete a namespace (optionally all child objects of a non-empty
            namespace) or a specific file

    :param gns_path: namespace or file (full GNS path); can be file list
    :type gns_path: ``str`` or list or ``Path``
    :param recursive: use the -R flag to delete recursively, Default: False
    :type recursive: ``bool``
    :returns: nothing is returned (void function)
    :rtype: ``None``
    """
    # TODO: What to do when some files of LIST exist but not all?
    # throw error if source file does not exist
    if isinstance(gns_path, (str, Path)) and not resource_exists(gns_path):
        raise FileNotFoundError(
            f"pyslk.{inspect.stack()[0][3]}: resource does not exist: {gns_path}"
        )
    # check type of 'recursive'
    if not isinstance(recursive, bool):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'recursive' needs to be 'bool' but got "
            + f"'{type(recursive).__name__}'"
        )
    # run command
    delete_raw(gns_path, recursive)


def get_checksum(
    resource: Union[str, Path],
    checksum_type: Union[str, None] = None,
) -> typing.Optional[dict[str, str]]:
    """Get a checksum of a resource

    :param resource: resource (full path)
    :type resource: ``str`` or ``Path``
    :param checksum_type: checksum_type (possible values: None, "sha512", "adler32"; None => print all)
    :type checksum_type: ``str``
    :returns: dictionary with checksum type as key(s) and checksum(s) as value(s); empty keys if no checksum; 'None' if
        resource does not exist
    :rtype: ``dict`` or ``None``
    """
    # throw error if source file does not exist
    if not resource_exists(resource):
        return None
    # run command
    output: subprocess.CompletedProcess = checksum_raw(
        resource, checksum_type, return_type=2
    )
    if output.returncode == 0:
        if checksum_type is None:
            return {
                o.split(": ")[0]: o.split(": ")[1]
                for o in output.stdout.decode("utf-8").split("\n")
                if o != ""
            }
        else:
            return {checksum_type: output.stdout.decode("utf-8").rstrip()}
    elif output.returncode == 1:
        return None
    else:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )


def _has_no_flag_partial(
    resource: Union[str, int, Path, list, None] = None,
    search_id: Union[str, int, None] = None,
    details: bool = False,
) -> typing.Optional[Union[bool, dict[str, list[Path]]]]:
    """Check if whether file(s) is/are flagged as partial; return True/False or a dict with keys 'flag_partial' and
        'no_flag_partial', depending on 'details'

    :param resource: a resource id or a resource path
    :type resource: ``str`` or ``int`` or ``path-like``
    :param search_id: id of a search
    :type search_id: ``int`` or ``str``
    :param details: print flagging status of each file; if not set, output is False if no file in flagged and else True
    :type details: ``bool``
    :returns: True if one or more files are flagged; False otherwise; if 'details': dictionary with two keys
        'flag_partial' and 'no_flag_partial' which each have a list of files as value
    :rtype: ``bool`` or ``dict`` or ``None``
    """
    # check a parse the input values
    check_result = _check_resource_and_search_id(
        inspect.stack()[0][3], resource, search_id
    )
    # if we received None=> return None
    if check_result is None:
        return None
    # extract values from resource path, resource id and search id
    resource_path, resource_id, search_id = check_result
    # run raw function
    output: subprocess.CompletedProcess = has_no_flag_partial_raw(
        resource_path,
        resource_id,
        search_id,
        recursive=True,
        verbose=False,
        double_verbose=details,
        return_type=2,
    )
    if output.returncode in [0, 1]:
        if not details:
            if output.returncode == 0:
                return True
            elif output.returncode == 1:
                return False
        else:
            # [:-1] because we drop the last row
            return {
                "no_flag_partial": [
                    Path(o.split(" ")[0])
                    for o in output.stdout.decode("utf-8").split("\n")[:-2]
                    if len(o) > 0 and "has no partial flag" in o
                ],
                "flag_partial": [
                    Path(o.split(" ")[0])
                    for o in output.stdout.decode("utf-8").split("\n")[:-2]
                    if len(o) > 0 and "has partial flag" in o
                ],
            }
    else:
        # output.returncode is neither 0 nor 1
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )


def has_no_flag_partial(
    resource: Union[str, int, Path, list, None] = None,
    search_id: Union[str, int, None] = None,
) -> bool:
    """Check if whether file(s) is/are flagged as partial; return True/False

    :param resource: a resource id or a resource path
    :type resource: ``str`` or ``int`` or ``path-like``
    :param search_id: id of a search
    :type search_id: ``int`` or ``str``
    :returns: True if no files is flagged; False otherwise
    :rtype: ``bool``
    """
    return _has_no_flag_partial(resource, search_id, details=False)


def has_no_flag_partial_details(
    resource: Union[str, int, Path, list, None] = None,
    search_id: Union[str, int, None] = None,
) -> dict[str, list[Path]]:
    """Check if whether file(s) is/are flagged as partial; returns dict with keys 'flag_partial' and 'no_flag_partial'

    :param resource: a resource id or a resource path
    :type resource: ``str`` or ``int`` or ``path-like``
    :param search_id: id of a search
    :type search_id: ``int`` or ``str``
    :returns: dictionary with two keys 'flag_partial' and 'no_flag_partial' which each have a list of files as value
    :rtype: ``dict[str, list[Path]]``
    """
    return _has_no_flag_partial(resource, search_id, details=True)


def chown(
    gns_path: [str, Path], owner: Union[str, int], recursive: bool = False
) -> typing.Optional[dict]:
    """Change the owner of a resource or namespace

    :param gns_path: namespace or file (full GNS path)
    :type gns_path: ``str`` or ``Path``
    :param owner: new owner of a file (username or uid)
    :type owner: ``str`` or ``int``
    :param recursive: use the -R flag to delete recursively, Default: False
    :type recursive: ``bool``
    :returns: dict of Paths of the modified files 'PATH: TRUE-IF-OWNER-CORRECT'; None if gns_path does not exist
    :rtype: ``dict`` or ``None``
    """
    # check input types
    if not isinstance(owner, (str, int)):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'owner' needs to be 'str' or 'int' but got "
            + f"'{type(owner).__name__}'"
        )
    try:
        owner = int(owner)
    except ValueError:
        pass
    if isinstance(gns_path, (str, Path)):
        # if path_or_id is a str or Path check whether the resource exists
        if not resource_exists(gns_path):
            return None
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'gns_path' needs to be 'str' or Path-like but got "
            + f"'{type(gns_path).__name__}'"
        )
    # check type of 'recursive'
    if not isinstance(recursive, bool):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'recursive' needs to be 'bool' but got "
            + f"'{type(recursive).__name__}'"
        )
    # run tag_raw
    output_raw: subprocess.CompletedProcess = owner_raw(
        gns_path, owner, recursive, return_type=2
    )
    # create actual output
    output: dict[str, Union[bool, str, list]] = dict()
    # copy exit code and stdout/stderr
    output["error"] = output_raw.returncode != 0
    output["stdout"] = output_raw.stdout.decode("utf-8").rstrip()
    output["stderr"] = output_raw.stderr.decode("utf-8").rstrip()
    # collect modified / not-modified files
    if isinstance(owner, int):
        files = ls(gns_path, recursive=recursive, numeric_ids=True)
    else:
        files = ls(gns_path, recursive=recursive, numeric_ids=False)
    output["files_correct"] = list(files.loc[files["owner"] == owner, "filename"])
    output["files_incorrect"] = list(files.loc[files["owner"] != owner, "filename"])
    # return output
    return output


def chgrp(
    gns_path: str, group: Union[str, int], recursive: bool = False
) -> typing.Optional[dict]:
    """Change the group of a resource or namespace

    :param gns_path: namespace or file (full GNS path)
    :type gns_path: ``str``
    :param group: new group of a file (group name or gid)
    :type group: ``str`` or ``int``
    :param recursive: use the -R flag to delete recursively, Default: False
    :type recursive: ``bool``
    :returns: dict with stdout/stderr, exit code and lists of files with correct and incorrect group;
                None if gns_path does not exist
    :rtype: ``dict`` or ``None``
    """
    # check input types
    if not isinstance(group, (str, int)):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'group' needs to be 'str' or 'int' but got "
            + f"'{type(group).__name__}'"
        )
    try:
        group = int(group)
    except ValueError:
        pass
    if isinstance(gns_path, (str, Path)):
        # if path_or_id is a str or Path check whether the resource exists
        if not resource_exists(gns_path):
            return None
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'gns_path' needs to be 'str' or Path-like but got "
            + f"'{type(gns_path).__name__}'"
        )
    # check type of 'recursive'
    if not isinstance(recursive, bool):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'recursive' needs to be 'bool' but got "
            + f"'{type(recursive).__name__}'"
        )
    # run tag_raw
    output_raw: subprocess.CompletedProcess = group_raw(
        gns_path, group, recursive, return_type=2
    )
    # create actual output
    output: dict[str, Union[bool, str, list]] = dict()
    # copy exit code and stdout/stderr
    output["error"] = output_raw.returncode != 0
    output["stdout"] = output_raw.stdout.decode("utf-8").rstrip()
    output["stderr"] = output_raw.stderr.decode("utf-8").rstrip()
    # collect modified / not-modified files
    if isinstance(group, int):
        files = ls(gns_path, recursive=recursive, numeric_ids=True)
    else:
        files = ls(gns_path, recursive=recursive, numeric_ids=False)
    output["files_correct"] = list(files.loc[files["group"] == group, "filename"])
    output["files_incorrect"] = list(files.loc[files["group"] != group, "filename"])
    # return output
    return output


def chmod(
    gns_path: Union[str, list], mode: Union[str, int], recursive: bool = False
) -> typing.Optional[bool]:
    """Change the access mode of a resource or namespace

    :param gns_path: namespace or file (full GNS path); can be file list
    :type gns_path: ``str`` or ``list``
    :param mode: new mode/permissions of a file (as known from bash's chmod)
    :type mode: ``str`` or ``int``
    :param recursive: use the -R flag to delete recursively, Default: False
    :type recursive: ``bool``
    :returns: True if successful, None if target does not exist, PySlkException if fails
    :rtype: ``bool`` or ``None``
    """
    # check input types
    if not isinstance(mode, (str, int)):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'mode' needs to be 'str' or 'int' but got "
            + f"'{type(mode).__name__}'"
        )
    try:
        mode = int(mode)
    except ValueError:
        pass
    if isinstance(gns_path, (str, Path)):
        # if path_or_id is a str or Path check whether the resource exists
        if not resource_exists(gns_path):
            return None
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'gns_path' needs to be 'str' or Path-like but got "
            + f"'{type(gns_path).__name__}'"
        )
    # check type of 'recursive'
    if not isinstance(recursive, bool):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'recursive' needs to be 'bool' but got "
            + f"'{type(recursive).__name__}'"
        )
    # run tag_raw
    output: subprocess.CompletedProcess = chmod_raw(
        gns_path, mode, recursive, return_type=2
    )
    # check if error occurred
    if output.returncode == 0:
        return True
    else:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )
