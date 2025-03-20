import inspect
import subprocess
from pathlib import Path
from typing import Union

from ..constants import PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS, SLK, SLK_HELPERS
from ..pyslk_exceptions import PySlkException
from ..utils import run_slk, which

__all__ = [
    "resource_tape_raw",
    "exists_raw",
    "checksum_raw",
    "rename_raw",
    "move_raw",
    "delete_raw",
    "mkdir_raw",
    "size_raw",
    "resource_mtime_raw",
    "resource_path_raw",
    "resource_type_raw",
    "resource_permissions_raw",
    "has_no_flag_partial_raw",
    "owner_raw",
    "group_raw",
    "chmod_raw",
]


def resource_tape_raw(
    resource: str,
    json: bool = False,
    print_tape_barcode_only: bool = False,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """prints resource tape information

    :param resource: resource (full path)
    :type resource: `str`
    :param json: print json
    :type json: `bool`
    :param print_tape_barcode_only: print only barcode and no other information like tape id
    :type print_tape_barcode_only: `bool`
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    slk_call = [SLK_HELPERS, "resource_tape", resource]

    # --json
    if not isinstance(json, bool):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'json' has wrong type; need 'bool' but got "
            + f"'{type(json).__name__}'"
        )
    if json:
        slk_call.append("--json")

    # --print-tape-barcode-only
    if not isinstance(print_tape_barcode_only, bool):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'print_tape_barcode_only' has wrong type; need 'bool' but got "
            + f"'{type(print_tape_barcode_only).__name__}'"
        )
    if print_tape_barcode_only:
        slk_call.append("--print-tape-barcode-only")

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


def exists_raw(
    gns_path: Union[str, Path], return_type: int = 0
) -> Union[str, int, subprocess.CompletedProcess]:
    """Check if resource exists

    :param gns_path: namespace or resource
    :type gns_path: str
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    if not isinstance(gns_path, (str, Path)):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'gns_path' needs to be 'str' or Path-like but got "
            + f"'{type(gns_path).__name__}'."
        )

    slk_call = [SLK_HELPERS, "exists", str(gns_path)]

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


def checksum_raw(
    resource_path: Union[str, Path],
    checksum_type: Union[str, None] = None,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """Get a checksum of a resource

    :param resource_path: resource (full path)
    :type resource_path: str or Path
    :param checksum_type: checksum_type (possible values: None, "sha512",
                          "adler32"; None => print all)
    :type checksum_type: str
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    if not isinstance(resource_path, (str, Path)):
        raise TypeError(
            f'pyslk.{inspect.stack()[0][3]}: "resource_path" has to be of type "str" but is '
            + f"{type(resource_path).__name__}."
        )

    slk_call = [SLK_HELPERS, "checksum"]

    if checksum_type is not None:
        slk_call.append("-t")
        slk_call.append(checksum_type)
    slk_call.append(str(resource_path))

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


def rename_raw(
    old_name: Union[str, Path], new_name: Union[str, Path], return_type: int = 0
) -> Union[str, int, subprocess.CompletedProcess]:
    """Rename a folder or file; moving is not possible

    :param old_name: folder or file name (full GNS path)
    :type old_name: str or Path
    :param new_name: new name (only name; no full GNS path)
    :type new_name: str or Path
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK) is None:
        raise PySlkException(f"pyslk: {SLK}: command not found")

    slk_call = [SLK, "rename"]
    if isinstance(old_name, (str, Path)):
        slk_call.append(str(old_name))
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'old_name' has to be of type 'str' or 'Path' but is "
            + f"{type(old_name).__name__}"
        )
    if isinstance(new_name, (str, Path)):
        slk_call.append(str(new_name))
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'new_name' has to be of type 'str' or 'Path' but is "
            + f"{type(new_name).__name__}"
        )

    if return_type == 0:
        return run_slk(slk_call, inspect.stack()[0][3])
    elif return_type == 1:
        return run_slk(slk_call, inspect.stack()[0][3], handle_output=False).returncode
    elif return_type == 2:
        return run_slk(slk_call, inspect.stack()[0][3], handle_output=False)
    else:
        raise ValueError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'return_type' needs to be 0, 1 or 2."
        )


def move_raw(
    src_path: Union[str, Path],
    dst_gns: Union[str, Path],
    interactive: bool,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """Move namespaces/files from one parent folder to another; renaming is
    not possible

    :param src_path: namespace or file (full GNS path)
    :type src_path: str or Path
    :param dst_gns: new parent namespace
    :type dst_gns: str or Path
    :param interactive: prompt user before overwrite; none-interactive: don't overwrite
    :type interactive: bool
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK) is None:
        raise PySlkException(f"pyslk: {SLK}: command not found")

    slk_call = [SLK, "delete"]
    if isinstance(src_path, (str, Path)):
        slk_call.append(str(src_path))
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'src_path' has to be of type 'str' or 'Path' but is "
            + f"{type(src_path).__name__}"
        )
    if isinstance(dst_gns, (str, Path)):
        slk_call.append(str(dst_gns))
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'dst_gns' has to be of type 'str' or 'Path' but is "
            + f"{type(dst_gns).__name__}"
        )
    if interactive:
        slk_call.append("-i")

    if return_type == 0:
        return run_slk(slk_call, inspect.stack()[0][3])
    elif return_type == 1:
        return run_slk(slk_call, inspect.stack()[0][3], handle_output=False).returncode
    elif return_type == 2:
        return run_slk(slk_call, inspect.stack()[0][3], handle_output=False)
    else:
        raise ValueError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'return_type' needs to be 0, 1 or 2."
        )


def delete_raw(
    gns_path: Union[Path, str, list], recursive: bool = False, return_type: int = 0
) -> Union[str, int, subprocess.CompletedProcess]:
    """Soft delete a namespace (optionally all child objects of a non-empty
            namespace) or a specific file

    :param gns_path: namespace or file (full GNS path); can be file list
    :type gns_path: str or list or Path
    :param recursive: use the -R flag to delete recursively, Default: False
    :type recursive: bool
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK) is None:
        raise PySlkException(f"pyslk: {SLK}: command not found")

    slk_call = [SLK, "delete"]
    if recursive:
        slk_call.append("-R")
    if isinstance(gns_path, (str, Path)):
        slk_call.append(str(gns_path))
    elif isinstance(gns_path, list):
        if not all([isinstance(r, (str, Path)) for r in gns_path]):
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: if argument 'gns_path' is of type 'list' its items need to be"
                + "of type 'str' or Path-like but got type(s): "
                + f"'{', '.join([type(r).__name__ for r in gns_path if not isinstance(r, (str, Path))])}'."
            )
        slk_call.extend(gns_path)
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'gns_path' needs to be 'str' or 'Path' but got "
            + f"{type(gns_path).__name__}."
        )

    if return_type == 0:
        return run_slk(slk_call, inspect.stack()[0][3])
    elif return_type == 1:
        return run_slk(slk_call, inspect.stack()[0][3], handle_output=False).returncode
    elif return_type == 2:
        return run_slk(slk_call, inspect.stack()[0][3], handle_output=False)
    else:
        raise ValueError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'return_type' needs to be 0, 1 or 2."
        )


def mkdir_raw(
    gns_path: Union[str, Path],
    recursive: bool = False,
    parents: bool = False,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """Create a directory

    :param gns_path: gns path to create
    :type gns_path: str or Path
    :param recursive: use the -R create folders recursively; throw error if folder already exists
    :type recursive: bool
    :param parents: create parent folders recursively; throw no error if folder already exists (like 'mkdir -p')
    :type parents: bool
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    if not isinstance(gns_path, (str, Path)):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'gns_path' needs to be 'str' or 'Path' but got "
            + f"{type(gns_path).__name__}."
        )

    slk_call = [SLK_HELPERS, "mkdir"]

    if recursive:
        slk_call.append("-R")
    if parents:
        slk_call.append("-p")
    slk_call.append(str(gns_path))

    if return_type == 0:
        return run_slk(slk_call, inspect.stack()[0][3])
    elif return_type == 1:
        return run_slk(slk_call, inspect.stack()[0][3], handle_output=False).returncode
    elif return_type == 2:
        return run_slk(slk_call, inspect.stack()[0][3], handle_output=False)
    else:
        raise ValueError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'return_type' needs to be 0, 1 or 2."
        )


def size_raw(
    resource_path: Union[str, Path, None] = None,
    resource_id: Union[str, int, None] = None,
    recursive: bool = False,
    pad_spaces_left: int = -1,
    verbose: bool = False,
    double_verbose: bool = False,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """Returns file size in byte

    :param resource_path: namespace or resource
    :type resource_path: `str` or `Path` or `None`
    :param resource_id: a resource id
    :type resource_id: `str` or `int`
    :param recursive: use the -R to calculate size recursively
    :type recursive: `bool`
    :param pad_spaces_left: pad spaces left
    :type pad_spaces_left: `int`
    :param verbose: single verbose mode, Default: False
    :type verbose: `bool`
    :param double_verbose: double verbose mode, Default: False
    :type double_verbose: `bool`
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: `int`
    :returns: stdout of the slk call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    if resource_id is not None and not isinstance(resource_id, (str, int)):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'resource_id' has to be of type 'str' or 'int' but is "
            + f"{type(resource_id).__name__}"
        )

    if resource_path is not None and not isinstance(resource_path, (str, Path)):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'resource_path' has to be of type 'str' or path-like but is "
            + f"{type(resource_path).__name__}"
        )

    slk_call = [SLK_HELPERS, "size"]

    if resource_path is not None:
        slk_call.append(str(resource_path))
    if resource_id is not None:
        slk_call.append("--resource-id")
        slk_call.append(str(resource_id))
    # -R / --recursive
    if recursive:
        slk_call.append("-R")
    # --pad-spaces-left
    if not isinstance(pad_spaces_left, int):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'pad_spaces_left' has to be of type 'int' but is "
            + f"{type(pad_spaces_left).__name__}"
        )
    if pad_spaces_left != -1:
        slk_call.append("--pad-spaces-left")
        slk_call.append(str(pad_spaces_left))
    # -vv (double verbose)
    if double_verbose:
        slk_call.append("-vv")
    elif verbose:
        # -v (verbose)
        slk_call.append("-v")

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


def resource_path_raw(
    resource_id: Union[str, int], return_type: int = 0
) -> Union[str, int, subprocess.CompletedProcess]:
    """Get path for a resource id

    :param resource_id: a resource_id
    :type resource_id: str or int
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    if not isinstance(resource_id, (str, int)):
        raise TypeError(
            f'pyslk.{inspect.stack()[0][3]}: "resource_id" has to be of type "str" or "int" but is '
            + f"{type(resource_id).__name__}"
        )

    slk_call = [SLK_HELPERS, "resource_path", str(resource_id)]

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


def resource_type_raw(
    resource_path: Union[str, Path, None] = None,
    resource_id: Union[str, int, None] = None,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """Get type of resource provided via resource id or a resource path

    :param resource_path: resource path (either resource_id or resource_path have to be provided; not both)
    :type resource_path: str or path-like or None
    :param resource_id: a resource id
    :type resource_id: str or int
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    if resource_id is not None and not isinstance(resource_id, (str, int)):
        raise TypeError(
            f'pyslk.{inspect.stack()[0][3]}: "resource_id" has to be of type "str" or "int" but is '
            + f"{type(resource_id).__name__}"
        )

    if resource_path is not None and not isinstance(resource_path, (str, Path)):
        raise TypeError(
            f'pyslk.{inspect.stack()[0][3]}: "resource_path" has to be of type "str" or path-like but is '
            + f"{type(resource_path).__name__}"
        )

    slk_call = [SLK_HELPERS, "resource_type"]

    if resource_path is not None:
        slk_call.append(str(resource_path))
    if resource_id is not None:
        slk_call.append("--resource-id")
        slk_call.append(str(resource_id))

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


def resource_mtime_raw(
    resource_path: Union[str, Path, None] = None,
    resource_id: Union[str, int, None] = None,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """Get mtime of resource provided via resource id or a resource path

    :param resource_path: resource path (either resource_id or resource_path have to be provided; not both)
    :type resource_path: str or path-like or None
    :param resource_id: a resource id
    :type resource_id: str or int
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    if resource_id is not None and not isinstance(resource_id, (str, int)):
        raise TypeError(
            f'pyslk.{inspect.stack()[0][3]}: "resource_id" has to be of type "str" or "int" but is '
            + f"{type(resource_id).__name__}"
        )

    if resource_path is not None and not isinstance(resource_path, (str, Path)):
        raise TypeError(
            f'pyslk.{inspect.stack()[0][3]}: "resource_path" has to be of type "str" or path-like but is '
            + f"{type(resource_path).__name__}"
        )

    slk_call = [SLK_HELPERS, "resource_mtime"]

    if resource_path is not None:
        slk_call.append(str(resource_path))
    if resource_id is not None:
        slk_call.append("--resource-id")
        slk_call.append(str(resource_id))

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


def resource_permissions_raw(
    resource_path: Union[str, Path, None] = None,
    resource_id: Union[str, int, None] = None,
    as_octal_number: bool = False,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """Get permissions of a resource provided via resource id or a resource path

    :param resource_path: resource path (either resource_id or resource_path have to be provided; not both)
    :type resource_path: str or path-like
    :param resource_id: a resource id
    :type resource_id: str or int
    :param as_octal_number: Do not return the permissions as combination of x/w/r/- but as three digit octal number
    :type as_octal_number: bool
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    if resource_id is not None and not isinstance(resource_id, (str, int)):
        raise TypeError(
            f'pyslk.{inspect.stack()[0][3]}: "resource_id" has to be of type "str" or "int" but is '
            + f"{type(resource_id).__name__}"
        )

    if resource_path is not None and not isinstance(resource_path, (str, Path)):
        raise TypeError(
            f'pyslk.{inspect.stack()[0][3]}: "resource_path" has to be of type "str" or path-like but is '
            + f"{type(resource_path).__name__}"
        )

    slk_call = [SLK_HELPERS, "resource_permissions"]

    if resource_path is not None:
        slk_call.append(str(resource_path))
    if resource_id is not None:
        slk_call.append("--resource-id")
        slk_call.append(str(resource_id))
    if as_octal_number is True:
        slk_call.append("--as-octal-number")

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


def has_no_flag_partial_raw(
    resource_path: Union[str, Path, list, None] = None,
    resource_id: Union[str, int, None] = None,
    search_id: Union[str, int, None] = None,
    recursive: bool = False,
    verbose: bool = False,
    double_verbose: bool = False,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """Get info whether file is flagged as partial file

    :param resource_path: resource (full path)
    :type resource_path: str or Path or list or None
    :param resource_id: a resource id
    :type resource_id: str or int
    :param search_id: id of a search
    :type search_id: int or str
    :param recursive: go through all files in resource_path recursively
    :type recursive: bool
    :param verbose: single verbose mode, Default: False
    :type verbose: bool
    :param double_verbose: double verbose mode, Default: False
    :type double_verbose: bool
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    if resource_id is not None and not isinstance(resource_id, (str, int)):
        raise TypeError(
            f'pyslk.{inspect.stack()[0][3]}: "resource_id" has to be of type "str" or "int" but is '
            + f"{type(resource_id).__name__}"
        )

    if search_id is not None and not isinstance(search_id, (str, int)):
        raise TypeError(
            f'pyslk.{inspect.stack()[0][3]}: "search_id" has to be of type "str" or "int" but is '
            + f"{type(resource_id).__name__}"
        )

    slk_call = [SLK_HELPERS, "has_no_flag_partial"]

    if resource_path is not None:
        if isinstance(resource_path, (str, Path)):
            slk_call.append(str(resource_path))
        elif isinstance(resource_path, list):
            if not all([isinstance(r, (str, Path)) for r in resource_path]):
                raise TypeError(
                    f"pyslk.{inspect.stack()[0][3]}: if argument 'resource_path' is of type 'list' its items need to be"
                    + "of type 'str' or Path-like but got type(s): "
                    + f"'{', '.join([type(r).__name__ for r in resource_path if not isinstance(r, (str, Path))])}'."
                )
            slk_call.extend(resource_path)
        else:
            raise TypeError(
                f'pyslk.{inspect.stack()[0][3]}: "resource_path" has to be of type "str", path-like or "list" but is '
                + f"{type(resource_path).__name__}"
            )
    if resource_id is not None:
        slk_call.append("--resource-id")
        slk_call.append(str(resource_id))
    if search_id is not None:
        slk_call.append("--search-id")
        slk_call.append(str(search_id))
    if recursive:
        slk_call.append("-R")
    if double_verbose:
        slk_call.append("-vv")
    elif verbose:
        slk_call.append("-v")

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


def owner_raw(
    gns_path: Union[str, Path],
    owner: Union[str, int],
    recursive: bool = False,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """Change the owner of a resource or namespace

    :param gns_path: namespace or file (full GNS path)
    :type gns_path: str or Path
    :param owner: new owner of a file (username or uid)
    :type owner: str or int
    :param recursive: use the -R flag to delete recursively, Default: False
    :type recursive: bool
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK) is None:
        raise PySlkException(f"pyslk: {SLK}: command not found")

    # basic call
    slk_call = [SLK, "owner"]

    # check input types
    if isinstance(owner, (str, int)):
        slk_call.append(str(owner))
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'owner' needs to be 'str' or 'int' but got "
            + f"'{type(owner).__name__}'"
        )
    # add further arguments
    if recursive:
        slk_call.append("-R")
    if isinstance(gns_path, (str, Path)):
        slk_call.append(str(gns_path))
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'gns_path' needs to be 'str' or path-like but got "
            + f"'{type(gns_path).__name__}'"
        )

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


def group_raw(
    gns_path: Union[str, Path],
    group: Union[str, int],
    recursive: bool = False,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """Change the group of a resource or namespace

    :param gns_path: namespace or file (full GNS path)
    :type gns_path: str or Path
    :param group: new group of a file (group name or gid)
    :type group: str or int
    :param recursive: use the -R flag to delete recursively, Default: False
    :type recursive: bool
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK) is None:
        raise PySlkException(f"pyslk: {SLK}: command not found")

    # basic call
    slk_call = [SLK, "group"]

    # check input types
    if isinstance(group, (str, int)):
        slk_call.append(str(group))
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'group' needs to be 'str' or 'int' but got "
            + f"'{type(group).__name__}'"
        )
    # add further arguments
    if recursive:
        slk_call.append("-R")
    if isinstance(gns_path, (str, Path)):
        slk_call.append(str(gns_path))
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'gns_path' needs to be 'str' or path-like but got "
            + f"'{type(gns_path).__name__}'"
        )

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


def chmod_raw(
    gns_path: Union[str, list, Path],
    mode: Union[str, int],
    recursive: bool = False,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """Change the access mode of a resource or namespace

    :param gns_path: namespace or file (full GNS path); can be file list
    :type gns_path: str or list or Path
    :param mode: new mode/permissions of a file (as known from bash's chmod)
    :type mode: str or int
    :param recursive: use the -R flag to delete recursively, Default: False
    :type recursive: bool
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK) is None:
        raise PySlkException(f"pyslk: {SLK}: command not found")

    # basic call
    slk_call = [SLK, "chmod"]

    # check input types
    if isinstance(mode, (str, int)):
        slk_call.append(str(mode))
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'mode' needs to be 'str' or 'int' but got "
            + f"'{type(mode).__name__}'"
        )
    # add further arguments
    if recursive:
        slk_call.append("-R")
    if isinstance(gns_path, (str, Path)):
        slk_call.append(str(gns_path))
    elif isinstance(gns_path, list):
        if not all([isinstance(r, (str, Path)) for r in gns_path]):
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: if argument 'gns_path' is of type 'list' its items need to be"
                + "of type 'str' or Path-like but got type(s): "
                + f"'{', '.join([type(r).__name__ for r in gns_path if not isinstance(r, (str, Path))])}'."
            )
        slk_call.extend(gns_path)
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'gns_path' needs to be 'str', 'list' or path-like but got "
            + f"'{type(gns_path).__name__}'"
        )

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
