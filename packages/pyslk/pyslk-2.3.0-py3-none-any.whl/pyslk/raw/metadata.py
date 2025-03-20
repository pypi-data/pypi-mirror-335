import inspect
import subprocess
from pathlib import Path
from typing import Union

from pyslk.constants import PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS, SLK, SLK_HELPERS
from pyslk.pyslk_exceptions import PySlkException
from pyslk.utils import run_slk, which

__all__ = [
    "json2hsm_raw",
    "hsm2json_raw",
    "metadata_raw",
    "tag_raw",
]


def json2hsm_raw(
    json_file: Union[str, Path, None] = None,
    restart_file: Union[str, Path, None] = None,
    schema: Union[str, list, None] = None,
    expect_json_lines: bool = False,
    verbose: bool = False,
    quiet: bool = False,
    ignore_non_existing_metadata_fields: bool = False,
    write_mode: Union[str, None] = None,
    instant_metadata_record_update: bool = False,
    use_res_id: bool = False,
    skip_bad_metadata_sets: bool = False,
    print_summary: bool = False,
    print_json_summary: bool = False,
    json_string: Union[str, None] = None,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """
    Read metadata from JSON file and write them to archived files into HSM. Use absolute paths from metadata records
    to identify target files.

    :param json_file: JSON input file containing metadata; incompatible with json_string [default: None]
    :type json_file: str or Path-like or None
    :param restart_file: set a restart file in which the processed metadata entries are listed [default: None]
    :type restart_file: str or Path-like or None,
    :param schema: import only metadata fields of listed schemata; if str: comma-separated list without spaces
    :type schema: str or list
    :param expect_json_lines: read JSON-lines from file instead of JSON
    :type expect_json_lines: bool
    :param verbose: verbose mode
    :type verbose: bool
    :param quiet: quiet mode
    :type quiet: bool
    :param ignore_non_existing_metadata_fields: throw no error if metadata field does not exist in StrongLink
    :type ignore_non_existing_metadata_fields: bool
    :param write_mode: select write mode for metadata: OVERWRITE, KEEP, ERROR, CLEAN
    :type write_mode: str
    :param use_res_id: use resource_id instead of path to identify file
    :type use_res_id: bool
    :param skip_bad_metadata_sets: skip damaged / incomplete metadata sets [default: throw error]
    :type skip_bad_metadata_sets: bool
    :param instant_metadata_record_update: False (default): read metadata records of all files and import into
                StrongLink afterwards; True: import each metadata record after it has been read
    :type instant_metadata_record_update: bool
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :param print_summary: print a summary
    :type print_summary: bool
    :param print_json_summary: print a summary as JSON
    :type print_json_summary: bool
    :param json_string: provide a json string instead of a json file; incompatible with json_file
    :type json_string: str
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    slk_call = [SLK_HELPERS, "json2hsm"]
    if json_file is not None:
        if not isinstance(json_file, (str, Path)):
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: argument 'json_file' needs to be 'str' or Path-like but got "
                + f"'{type(json_file).__name__}'."
            )
        slk_call.append(str(json_file))
    if restart_file is not None:
        if not isinstance(restart_file, (str, Path)):
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: argument 'restart_file' needs to be 'str' or Path-like but got "
                + f"'{type(restart_file).__name__}'."
            )
        if " " in str(restart_file):
            raise ValueError(
                f"pyslk.{inspect.stack()[0][3]}: 'restart_file' is not allowed to contain spaces"
            )
        slk_call.append("--restart-file")
        slk_call.append(str(restart_file))
    if expect_json_lines:
        slk_call.append("--expect-json-lines")
    if ignore_non_existing_metadata_fields:
        slk_call.append("--ignore-non-existing-metadata-fields")
    if verbose:
        slk_call.append("--verbose")
    if quiet:
        slk_call.append("-q")
    if use_res_id:
        slk_call.append("--use-res-id")
    if skip_bad_metadata_sets:
        slk_call.append("-k")
    if schema is not None:
        slk_call.append("--schema")
        if isinstance(schema, str):
            slk_call.append(schema)
        elif isinstance(schema, list):
            slk_call.append(",".join(schema))
        else:
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: 'schema' has wrong type; need 'str' or 'list' of 'str' but got "
                + f"{type(schema).__name__}"
            )
    if write_mode is not None:
        slk_call.append("--write-mode")
        slk_call.append(write_mode)
    if instant_metadata_record_update:
        slk_call.append("--instant-metadata-record-update")
    if print_summary:
        slk_call.append("--print-summary")
    if print_json_summary:
        slk_call.append("--print-json-summary")
    if json_string is not None:
        slk_call.append("--json-string")
        slk_call.append("'" + json_string + "'")

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


def hsm2json_raw(
    resources: Union[str, list, Path, None] = None,
    search_id: int = -1,
    recursive: bool = False,
    outfile: Union[str, Path, None] = None,
    restart_file: Union[str, Path, None] = None,
    schema: Union[str, list, None] = None,
    write_json_lines: bool = False,
    verbose: bool = False,
    quiet: bool = False,
    write_mode: Union[str, None] = None,
    print_summary: bool = False,
    print_json_summary: bool = False,
    write_compact_json: bool = False,
    instant_metadata_record_output: bool = False,
    print_hidden: bool = False,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """
    Extract metadata from HSM file(s) and return them in JSON structure

    :param resources: list of resources to be searched for [default: None]
    :type resources: str or list or Path-like or None
    :param search_id: id of a search
    :type search_id: int
    :param recursive: export metadata from all files in gns_path recursively
    :type recursive: bool
    :param outfile: Write the output into a file instead to the stdout [default: None]
    :type outfile: str or Path-like or None
    :param restart_file: set a restart file in which the processed metadata entries are listed [default: None]
    :type restart_file: str or Path-like or None
    :param schema: import only metadata fields of listed schemata; if str: comma-separated list without spaces
    :type schema: str, list or None
    :param write_json_lines: write JSON-lines instead of JSON
    :type write_json_lines: bool = False
    :param verbose: verbose mode
    :type verbose: bool = False
    :param quiet: quiet mode
    :type quiet: bool = False
    :param write_mode: applies when 'output' is set; possible values: OVERWRITE, ERROR
    :type write_mode: str = None
    :param print_summary: print summary on how many metadata records have been processed [default: False]
    :type print_summary: bool = False
    :param print_json_summary: print summary on how many metadata records have been processed as JSON [default: False]
    :type print_json_summary: bool = False
    :param write_compact_json: write JSON metadata in a compact form with less line breaks [default: False]
    :type write_compact_json: bool = False
    :param instant_metadata_record_output: False (default): read metadata of all files and write/print out afterwards;
                True: write/print each metadata record after it has been read (requires 'write_json_lines')
    :type instant_metadata_record_output: bool
    :param print_hidden: print read-only not-searchable metadata fields (sidecar file) [default: False]
    :type print_hidden: bool
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK_HELPERS) is None:
        raise PySlkException(f"pyslk: {SLK_HELPERS}: command not found")

    slk_call = [SLK_HELPERS, "hsm2json"]
    if resources is not None:
        if isinstance(resources, Path):
            slk_call.append(str(resources))
        elif isinstance(resources, str):
            if resources != "":
                slk_call.extend(resources.split(" "))
        elif isinstance(resources, list):
            if len(resources) > 0:
                if not all([isinstance(r, (str, Path)) for r in resources]):
                    raise TypeError(
                        f"pyslk.{inspect.stack()[0][3]}: if argument 'resources' is of type 'list' its items need to be"
                        + "of type 'str' or Path-like but got type(s): "
                        + f"'{', '.join([type(r).__name__ for r in resources if not isinstance(r, (str, Path))])}'."
                    )
                slk_call.extend(resources)
        else:
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: argument 'resources' needs to be 'str', 'list' (of 'str' or "
                + f"Path-like) or Path-like but got '{type(resources).__name__}'."
            )
    if search_id != -1:
        slk_call.append("--search-id")
        slk_call.append(str(search_id))
    if recursive:
        slk_call.append("-R")
    if outfile is not None:
        if not isinstance(outfile, (str, Path)):
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: argument 'outfile' needs to be 'str' or Path-like but got "
                + f"'{type(outfile).__name__}'."
            )
        if " " in str(outfile):
            raise ValueError(
                f"pyslk.{inspect.stack()[0][3]}: 'outfile' is not allowed to contain spaces"
            )
        slk_call.append("--outfile")
        slk_call.append(str(outfile))
    if restart_file is not None:
        if not isinstance(restart_file, (str, Path)):
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: argument 'restart_file' needs to be 'str' or Path-like but got "
                + f"'{type(restart_file).__name__}'."
            )
        if " " in str(restart_file):
            raise ValueError(
                f"pyslk.{inspect.stack()[0][3]}: 'restart_file' is not allowed to contain spaces"
            )
        slk_call.append("--restart-file")
        slk_call.append(str(restart_file))
    if write_json_lines:
        slk_call.append("--write-json-lines")
    if verbose:
        slk_call.append("--verbose")
    if quiet:
        slk_call.append("-q")
    if instant_metadata_record_output:
        slk_call.append("--instant-metadata-record-output")
    if print_summary:
        slk_call.append("--print-summary")
    if print_json_summary:
        slk_call.append("--print-json-summary")
    if write_compact_json:
        slk_call.append("--write-compact-json")
    if print_hidden:
        slk_call.append("--print-hidden")
    if schema is not None:
        slk_call.append("--schema")
        if isinstance(schema, str):
            slk_call.append(schema)
        elif isinstance(schema, list):
            slk_call.append(",".join(schema))
        else:
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: 'schema' has wrong type; need 'str' or 'list' of 'str' but got "
                + f"{type(schema).__name__}"
            )
    if write_mode is not None:
        slk_call.append("--write-mode")
        slk_call.append(write_mode)

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


def metadata_raw(
    resource_path: Union[str, Path],
    alternative_output_format: bool = False,
    print_hidden: bool = False,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """Get metadata

    :param resource_path: resource (full path)
    :type resource_path: str or Path
    :param alternative_output_format: print the name of the metadata schema in front of each field name [default: False]
    :type alternative_output_format: bool
    :param print_hidden: print read-only not-searchable metadata fields (sidecar file) [default: False]
    :type print_hidden: bool
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

    slk_call = [SLK_HELPERS, "metadata", str(resource_path)]

    if alternative_output_format:
        slk_call.append("--alternative-output-format")
    if print_hidden:
        slk_call.append("--print-hidden")

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


def tag_raw(
    path_or_id: Union[str, int, Path],
    metadata: Union[dict, None] = None,
    recursive: bool = False,
    display: bool = False,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """Apply metadata to the namespace and child resources

    :param path_or_id: search id or gns path of resources to retrieve
    :type path_or_id: str or int or Path
    :param metadata: dict that holds as keys "[metadata schema].[field]" and
                     as values the metadata values
    :type metadata: dict
    :param recursive: use the -R flag to tag recursively, Default: False
    :type recursive: bool
    :param display: print metadata as JSON (ignore "metadata" if this is True), Default: False
    :type display: bool
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK) is None:
        raise PySlkException(f"pyslk: {SLK}: command not found")

    if metadata is None and not display:
        raise ValueError(
            f"slk.{inspect.stack()[0][3]}: neither 'metadata' is set nor 'display' is 'true'; however, either argument "
            + "'metadata' has to be set (== set metadata) or 'display' has to be 'true' (== print metadata)"
        )
    if metadata is not None and display:
        raise ValueError(
            f"slk.{inspect.stack()[0][3]}: 'metadata' is set and 'display' is 'true'; however, argument 'metadata' has "
            + "to be set (== set metadata) XOR 'display' has to be 'true' (== print metadata); not both"
        )

    slk_call = [SLK, "tag"]
    if recursive:
        slk_call.append("-R")
    if isinstance(path_or_id, (str, Path, int)):
        slk_call.append(str(path_or_id))
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'path_or_id' needs to be 'str', 'int' or path-like but got "
            + f"'{type(path_or_id).__name__}'"
        )
    if display:
        slk_call.append("-display")
    else:
        if isinstance(metadata, dict):
            if len(metadata) == 0:
                raise ValueError(
                    f"slk.{inspect.stack()[0][3]}: argument 'metadata' is an empty dictionary; needs to have at "
                    + "least one key-value pair"
                )
            for k, v in metadata.items():
                slk_call.append(k + "=" + v)
        else:
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: argument 'metadata' needs to be 'dict' but got "
                + f"'{type(metadata).__name__}'"
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
