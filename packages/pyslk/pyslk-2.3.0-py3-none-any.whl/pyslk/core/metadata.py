import inspect
import json
import os
import subprocess
import tempfile
import typing
from pathlib import Path
from typing import Union

from ..base import searchid_exists
from ..pyslk_exceptions import PySlkException
from ..raw import hsm2json_raw, json2hsm_raw, metadata_raw, tag_raw
from .resource_extras import resource_exists

__all__ = [
    "json2hsm",
    "json_file2hsm",
    "json_str2hsm",
    "json_dict2hsm",
    "hsm2json",
    "hsm2json_file",
    "hsm2json_dict",
    "get_metadata",
    "get_tag",
    "set_tag",
]


def json2hsm(
    json_file: Union[str, None] = None,
    restart_file: Union[str, None] = None,
    schema: Union[str, list, None] = None,
    expect_json_lines: bool = False,
    verbose: bool = False,
    quiet: bool = False,
    ignore_non_existing_metadata_fields: bool = False,
    write_mode: Union[str, None] = None,
    instant_metadata_record_update: bool = False,
    use_res_id: bool = False,
    skip_bad_metadata_sets: bool = False,
    json_string: Union[str, None] = None,
) -> dict:
    """
    Read metadata from JSON file and write them to archived files into HSM. Use absolute paths from metadata records
    to identify target files.

    :param json_file: JSON input file containing metadata
    :type json_file: ``str``
    :param restart_file: set a restart file in which the processed metadata entries are listed
    :type restart_file: ``str`` = None,
    :param schema: import only metadata fields of listed schemata; if str: comma-separated list without spaces
    :type schema: ``str`` or ``list``
    :param expect_json_lines: read JSON-lines from file instead of JSON
    :type expect_json_lines: ``bool``
    :param verbose: verbose mode
    :type verbose: ``bool``
    :param quiet: quiet mode
    :type quiet: ``bool``
    :param ignore_non_existing_metadata_fields: do not throw an error if a metadata field is used, which does not exist
            in StrongLink
    :type ignore_non_existing_metadata_fields: ``bool``
    :param write_mode: select write mode for metadata: OVERWRITE, KEEP, ERROR, CLEAN
    :type write_mode: ``str``
    :param use_res_id: use resource_id instead of path to identify file
    :type use_res_id: ``bool``
    :param skip_bad_metadata_sets: skip damaged / incomplete metadata sets [default: throw error]
    :type skip_bad_metadata_sets: ``bool``
    :param instant_metadata_record_update: False (default): read metadata records of all files and import into
            StrongLink afterward; True: import each metadata record after it has been read
    :type instant_metadata_record_update: ``bool``
    :param json_string: provide a json string instead of a json file; incompatible with json_file
    :type json_string: ``str``
    :returns: metadata import summary (key 'header')
    :rtype: ``dict``

    .. seealso::
        * :py:meth:`~pyslk.json_dict2hsm`
        * :py:meth:`~pyslk.json_file2hsm`
        * :py:meth:`~pyslk.json_str2hsm`
        * :py:meth:`~pyslk.hsm2json`
        * :py:meth:`~pyslk.hsm2json_dict`
        * :py:meth:`~pyslk.hsm2json_file`
    """
    if json_file is None and json_string is None:
        raise ValueError(
            f"pyslk.{inspect.stack()[0][3]}: either 'json_file' xor 'json_string' have to be set but none of both is"
        )
    if json_file is not None and json_string is not None:
        raise ValueError(
            f"pyslk.{inspect.stack()[0][3]}: only 'json_file' xor 'json_string' must to be set but both are"
        )
    out = json2hsm_raw(
        json_file,
        restart_file,
        schema,
        expect_json_lines,
        verbose,
        quiet,
        ignore_non_existing_metadata_fields,
        write_mode,
        instant_metadata_record_update,
        use_res_id,
        skip_bad_metadata_sets,
        print_summary=False,
        print_json_summary=True,
    )
    return {"header": json.loads(out)["_summary"]}


def json_file2hsm(
    json_file: str,
    restart_file: Union[str, None] = None,
    schema: Union[str, list, None] = None,
    expect_json_lines: bool = False,
    verbose: bool = False,
    quiet: bool = False,
    ignore_non_existing_metadata_fields: bool = False,
    write_mode: Union[str, None] = None,
    instant_metadata_record_update: bool = False,
    use_res_id: bool = False,
    skip_bad_metadata_sets: bool = False,
) -> dict:
    """
    Read metadata from JSON file and write them to archived files into HSM. Use absolute paths from metadata records
    to identify target files.

    :param json_file: JSON input file containing metadata
    :type json_file: ``str``
    :param restart_file: set a restart file in which the processed metadata entries are listed
    :type restart_file: ``str`` = None,
    :param schema: import only metadata fields of listed schemata; if str: comma-separated list without spaces
    :type schema: ``str`` or ``list``
    :param expect_json_lines: read JSON-lines from file instead of JSON
    :type expect_json_lines: ``bool``
    :param verbose: verbose mode
    :type verbose: ``bool``
    :param quiet: quiet mode
    :type quiet: ``bool``
    :param ignore_non_existing_metadata_fields: do not throw an error if a metadata field is used, which does not exist
            in StrongLink
    :type ignore_non_existing_metadata_fields: ``bool``
    :param write_mode: select write mode for metadata: OVERWRITE, KEEP, ERROR, CLEAN
    :type write_mode: ``str``
    :param use_res_id: use resource_id instead of path to identify file
    :type use_res_id: ``bool``
    :param skip_bad_metadata_sets: skip damaged / incomplete metadata sets [default: throw error]
    :type skip_bad_metadata_sets: ``bool``
    :param instant_metadata_record_update: False (default): read metadata records of all files and import into
            StrongLink afterward; True: import each metadata record after it has been read
    :type instant_metadata_record_update: ``bool``
    :returns: metadata import summary (key 'header')
    :rtype: ``dict``

    .. seealso::
        * :py:meth:`~pyslk.json2hsm`
        * :py:meth:`~pyslk.json_dict2hsm`
        * :py:meth:`~pyslk.json_str2hsm`
        * :py:meth:`~pyslk.hsm2json`
        * :py:meth:`~pyslk.hsm2json_dict`
        * :py:meth:`~pyslk.hsm2json_file`
    """
    return json2hsm(
        json_file,
        restart_file,
        schema,
        expect_json_lines,
        verbose,
        quiet,
        ignore_non_existing_metadata_fields,
        write_mode,
        instant_metadata_record_update,
        use_res_id,
        skip_bad_metadata_sets,
        None,
    )


def json_str2hsm(
    json_string: str,
    restart_file: Union[str, None] = None,
    schema: Union[str, list, None] = None,
    expect_json_lines: bool = False,
    verbose: bool = False,
    quiet: bool = False,
    ignore_non_existing_metadata_fields: bool = False,
    write_mode: Union[str, None] = None,
    instant_metadata_record_update: bool = False,
    use_res_id: bool = False,
    skip_bad_metadata_sets: bool = False,
) -> dict:
    """
    Read metadata from JSON file and write them to archived files into HSM. Use absolute paths from metadata records
    to identify target files.

    :param json_string: JSON string containing metadata
    :type json_string: ``str``
    :param restart_file: set a restart file in which the processed metadata entries are listed
    :type restart_file: ``str`` = None,
    :param schema: import only metadata fields of listed schemata; if str: comma-separated list without spaces
    :type schema: ``str`` or ``list``
    :param expect_json_lines: read JSON-lines from file instead of JSON
    :type expect_json_lines: ``bool``
    :param verbose: verbose mode
    :type verbose: ``bool``
    :param quiet: quiet mode
    :type quiet: ``bool``
    :param ignore_non_existing_metadata_fields: do not throw an error if a metadata field is used, which does not exist
            in StrongLink
    :type ignore_non_existing_metadata_fields: ``bool``
    :param write_mode: select write mode for metadata: OVERWRITE, KEEP, ERROR, CLEAN
    :type write_mode: ``str``
    :param use_res_id: use resource_id instead of path to identify file
    :type use_res_id: ``bool``
    :param skip_bad_metadata_sets: skip damaged / incomplete metadata sets [default: throw error]
    :type skip_bad_metadata_sets: ``bool``
    :param instant_metadata_record_update: False (default): read metadata records of all files and import into
            StrongLink afterward; True: import each metadata record after it has been read
    :type instant_metadata_record_update: ``bool``
    :returns: metadata import summary (key 'header')
    :rtype: ``dict``

    .. seealso::
        * :py:meth:`~pyslk.json2hsm`
        * :py:meth:`~pyslk.json_dict2hsm`
        * :py:meth:`~pyslk.json_file2hsm`
        * :py:meth:`~pyslk.hsm2json`
        * :py:meth:`~pyslk.hsm2json_dict`
        * :py:meth:`~pyslk.hsm2json_file`
    """
    fd, tmp_json_file = tempfile.mkstemp(suffix=".json", prefix="metadata")
    with os.fdopen(fd, "w") as f:
        f.write(json_string)
    output = json_file2hsm(
        tmp_json_file,
        restart_file,
        schema,
        expect_json_lines,
        verbose,
        quiet,
        ignore_non_existing_metadata_fields,
        write_mode,
        instant_metadata_record_update,
        use_res_id,
        skip_bad_metadata_sets,
    )
    os.remove(tmp_json_file)
    return output


def json_dict2hsm(
    json_dict: dict,
    restart_file: Union[str, None] = None,
    schema: Union[str, list, None] = None,
    expect_json_lines: bool = False,
    verbose: bool = False,
    quiet: bool = False,
    ignore_non_existing_metadata_fields: bool = False,
    write_mode: Union[str, None] = None,
    instant_metadata_record_update: bool = False,
    use_res_id: bool = False,
    skip_bad_metadata_sets: bool = False,
) -> dict:
    """
    Read metadata from JSON dictionary and write them to archived files into HSM. Use absolute paths from metadata
    records to identify target files.

    :param json_dict: a dictionary representing JSON
    :type json_dict: ``dict``
    :param restart_file: set a restart file in which the processed metadata entries are listed
    :type restart_file: ``str`` = None,
    :param schema: import only metadata fields of listed schemata; if str: comma-separated list without spaces
    :type schema: ``str`` or ``list``
    :param expect_json_lines: read JSON-lines from file instead of JSON
    :type expect_json_lines: ``bool``
    :param verbose: verbose mode
    :type verbose: ``bool``
    :param quiet: quiet mode
    :type quiet: ``bool``
    :param ignore_non_existing_metadata_fields: do not throw an error if a metadata field is used, which does not exist
            in StrongLink
    :type ignore_non_existing_metadata_fields: ``bool``
    :param write_mode: select write mode for metadata: OVERWRITE, KEEP, ERROR, CLEAN
    :type write_mode: ``str``
    :param use_res_id: use resource_id instead of path to identify file
    :type use_res_id: ``bool``
    :param skip_bad_metadata_sets: skip damaged / incomplete metadata sets [default: throw error]
    :type skip_bad_metadata_sets: ``bool``
    :param instant_metadata_record_update: False (default): read metadata records of all files and import into
            StrongLink afterward; True: import each metadata record after it has been read
    :type instant_metadata_record_update: ``bool``
    :returns: metadata import summary (key 'header')
    :rtype: ``dict``

    .. seealso::
        * :py:meth:`~pyslk.json2hsm`
        * :py:meth:`~pyslk.json_file2hsm`
        * :py:meth:`~pyslk.json_str2hsm`
        * :py:meth:`~pyslk.hsm2json`
        * :py:meth:`~pyslk.hsm2json_dict`
        * :py:meth:`~pyslk.hsm2json_file`
    """
    return json2hsm(
        None,
        restart_file,
        schema,
        expect_json_lines,
        verbose,
        quiet,
        ignore_non_existing_metadata_fields,
        write_mode,
        instant_metadata_record_update,
        use_res_id,
        skip_bad_metadata_sets,
        json.dumps(json_dict),
    )


def hsm2json(
    resources: Union[str, Path, list, None] = None,
    search_id: int = -1,
    recursive: bool = False,
    outfile: Union[str, Path, None] = None,
    restart_file: Union[str, Path, None] = None,
    schema: Union[str, list, None] = None,
    write_json_lines: bool = False,
    write_mode: Union[str, None] = None,
    instant_metadata_record_output: bool = False,
    print_hidden: bool = False,
) -> dict[str, Union[dict, list, None]]:
    """
    Extract metadata from HSM file(s) and return them in JSON structure

    :param resources: list of resources to be searched for
    :type resources: ``str`` or ``Path`` or ``list``
    :param search_id: id of a search
    :type search_id: ``int``
    :param recursive: export metadata from all files in gns_path recursively
    :type recursive: ``bool``
    :param outfile: Write the output into a file instead to the stdout
    :type outfile: ``str`` or ``Path`` or ``None``
    :param restart_file: set a restart file in which the processed metadata entries are listed
    :type restart_file: ``str`` or ``Path`` or ``None``
    :param schema: import only metadata fields of listed schemata; if str: comma-separated list without spaces
    :type schema: ``str`` or ``list`` or ``None``
    :param write_json_lines: write JSON-lines instead of JSON
    :type write_json_lines: ``bool`` = False
    :param write_mode: applies when 'output' is set; possible values: OVERWRITE, ERROR
    :type write_mode: ``str`` = None
    :param instant_metadata_record_output: False (default): read metadata of all files and write/print out
            afterward; True: write/print each metadata record after it has been read (requires 'write_json_lines')
    :type instant_metadata_record_output: ``bool``
    :param print_hidden: print read-only not-searchable metadata fields (sidecar file) [default: False]
    :type print_hidden: ``bool``
    :returns: dictionary with keys 'header' (summary report), 'metadata' (actual metadata) and 'file' (JSON file);
        either 'metadata' or 'file' is none depending on the value of input argument 'outfile'
    :rtype: ``dict``

    .. seealso::
        * :py:meth:`~pyslk.hsm2json_dict`
        * :py:meth:`~pyslk.hsm2json_file`
        * :py:meth:`~pyslk.json2hsm`
        * :py:meth:`~pyslk.json_dict2hsm`
        * :py:meth:`~pyslk.json_file2hsm`
        * :py:meth:`~pyslk.json_str2hsm`
    """
    if resources is None and search_id == -1:
        raise ValueError(
            f"pyslk.{inspect.stack()[0][3]}: either 'resources' xor 'search_id' have to be set but none of both is"
        )
    if resources is not None and search_id != -1:
        raise ValueError(
            f"pyslk.{inspect.stack()[0][3]}: only 'resources' xor 'search_id' must to be set but both are"
        )
    if outfile is None and (instant_metadata_record_output or write_json_lines):
        raise ValueError(
            f"pyslk.{inspect.stack()[0][3]}: if 'outfile' is not set, 'instant_metadata_record_output' and "
            + "'write_json_lines' cannot be set"
        )
    if instant_metadata_record_output and not write_json_lines:
        raise ValueError(
            f"pyslk.{inspect.stack()[0][3]}: 'instant_metadata_record_output' does only work, if 'write_json_lines' is "
            + "set"
        )
    if restart_file is not None and not instant_metadata_record_output:
        raise ValueError(
            f"pyslk.{inspect.stack()[0][3]}: 'restart_file' can only be used when 'instant_metadata_record_output' is "
            + "set"
        )

    # check types
    if resources is not None:
        if isinstance(resources, list):
            if not all([isinstance(r, (str, Path)) for r in resources]):
                raise TypeError(
                    f"pyslk.{inspect.stack()[0][3]}: argument 'resources' has to be 'str' or path-like or 'list' of "
                    + "'str' or path-like but is a list which contains at least elements of these other types: "
                    + f"'{', '.join([type(r).__name__ for r in resources if not isinstance(r, (str, Path))])}'"
                )
        elif not isinstance(resources, (str, Path)):
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: 'resources' has wrong type; need 'str' or path-like or 'list' but "
                + f"got {type(outfile).__name__}"
            )
    if outfile is not None:
        if not isinstance(outfile, (str, Path)):
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: 'outfile' has wrong type; need 'str' or 'Path' but "
                + f"got {type(outfile).__name__}"
            )
        # check if output file exists
        if os.path.exists(outfile):
            raise FileExistsError(
                f"pyslk.{inspect.stack()[0][3]}: 'outfile' does already exist; please remove it or set 'outfile' to "
                + f"another value; current value of 'outfile': {str(outfile)}"
            )

    # check types
    if restart_file is not None:
        if not isinstance(restart_file, (str, Path)):
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: 'restart_file' has wrong type; need 'str' or 'Path' but "
                + f"got {type(restart_file).__name__}"
            )
    output = hsm2json_raw(
        resources,
        search_id,
        recursive,
        outfile,
        restart_file,
        schema,
        write_json_lines,
        False,
        False,
        write_mode,
        False,
        True,
        True,
        instant_metadata_record_output,
        print_hidden,
    )
    if outfile is None:
        split_output = output.split("\n")
        json_string = json.loads(split_output[0])
        summary = json.loads(split_output[1])["_summary"]
    else:
        json_string = None
        summary = json.loads(output)["_summary"]

    return {"header": summary, "metadata": json_string, "file": outfile}


def hsm2json_file(
    outfile: str,
    resources: Union[str, Path, list] = "",
    search_id: int = -1,
    recursive: bool = False,
    restart_file: Union[str, None] = None,
    schema: Union[str, list, None] = None,
    write_json_lines: bool = False,
    write_mode: Union[str, None] = None,
    instant_metadata_record_output: bool = False,
    print_hidden: bool = False,
) -> None:
    """
    Extract metadata from HSM file(s) and return them in JSON structure

    :param outfile: Write the output into a file instead to the stdout
    :type outfile: ``str`` or ``Path``
    :param resources: list of resources to be searched for
    :type resources: ``str`` or ``Path`` or ``list``
    :param search_id: id of a search
    :type search_id: ``int``
    :param recursive: export metadata from all files in gns_path recursively
    :type recursive: ``bool``
    :param restart_file: set a restart file in which the processed metadata entries are listed
    :type restart_file: ``str`` = None,
    :param schema: import only metadata fields of listed schemata; if str: comma-separated list without spaces
    :type schema: ``str``, list or None
    :param write_json_lines: write JSON-lines instead of JSON
    :type write_json_lines: ``bool`` = False
    :param write_mode: applies when 'output' is set; possible values: OVERWRITE, ERROR
    :type write_mode: ``str`` = None
    :param instant_metadata_record_output: False (default): read metadata of all files and write/print out afterward;
            True: write/print each metadata record after it has been read (requires 'write_json_lines')
    :type instant_metadata_record_output: ``bool``
    :param print_hidden: print read-only not-searchable metadata fields (sidecar file) [default: False]
    :type print_hidden: ``bool``
    :returns: nothing; throws an error if writing failed
    :rtype: None

    .. seealso::
        * :py:meth:`~pyslk.hsm2json`
        * :py:meth:`~pyslk.hsm2json_dict`
        * :py:meth:`~pyslk.json2hsm`
        * :py:meth:`~pyslk.json_dict2hsm`
        * :py:meth:`~pyslk.json_file2hsm`
        * :py:meth:`~pyslk.json_str2hsm`
    """
    # check types
    hsm2json(
        resources,
        search_id,
        recursive,
        outfile,
        restart_file,
        schema,
        write_json_lines,
        write_mode,
        instant_metadata_record_output,
        print_hidden,
    )
    # return path of the output file
    return None


def hsm2json_dict(
    resources: Union[str, list] = "",
    search_id: int = -1,
    recursive: bool = False,
    restart_file: Union[str, None] = None,
    schema: Union[str, list, None] = None,
    print_hidden: bool = False,
) -> dict[str, Union[dict, list, None]]:
    """
    Extract metadata from HSM file(s) and return them in JSON structure

    :param resources: list of resources to be searched for
    :type resources: ``str`` or ``list``
    :param search_id: id of a search
    :type search_id: ``int``
    :param recursive: export metadata from all files in gns_path recursively
    :type recursive: ``bool``
    :param restart_file: set a restart file in which the processed metadata entries are listed
    :type restart_file: ``str`` = None,
    :param schema: import only metadata fields of listed schemata; if str: comma-separated list without spaces
    :type schema: ``str``, list or None
    :param print_hidden: print read-only not-searchable metadata fields (sidecar file) [default: False]
    :type print_hidden: ``bool``
    :returns: dictionary with keys 'header' (summary report), 'metadata' (actual metadata) and 'file' (None)
    :rtype: ``dict``

    .. seealso::
        * :py:meth:`~pyslk.hsm2json`
        * :py:meth:`~pyslk.hsm2json_file`
        * :py:meth:`~pyslk.json2hsm`
        * :py:meth:`~pyslk.json_dict2hsm`
        * :py:meth:`~pyslk.json_file2hsm`
        * :py:meth:`~pyslk.json_str2hsm`
    """
    return hsm2json(
        resources,
        search_id,
        recursive,
        None,
        restart_file,
        schema,
        False,
        None,
        False,
        print_hidden,
    )


def get_metadata(
    resource: Union[str, Path],
    print_hidden: bool = False,
    print_raw_values: bool = False,
) -> typing.Optional[dict[str, Union[str, int, float, dict]]]:
    """Get metadata

    :param resource: resource (full path)
    :type resource: ``str`` or ``Path``
    :param print_hidden: print read-only not-searchable metadata fields (sidecar file) [default: False]
    :type print_hidden: ``bool``
    :param print_raw_values: print metadata values without trying to convert them to int/float/dict [default: False]
    :type print_raw_values: ``bool``
    :returns: dictionary with the metadata
    :rtype: ``dict`` or ``None``

    .. seealso::
        * :py:meth:`~pyslk.get_tag`
        * :py:meth:`~pyslk.set_tag`
    """
    if not resource_exists(resource):
        return None
    output = metadata_raw(resource, True, print_hidden)
    out_dict = {
        o.split(": ")[0]: o.split(": ")[1] for o in output.split("\n") if o != ""
    }
    if not print_raw_values:
        # do some interpretations
        for k, v in out_dict.items():
            # decode JSON
            if v[0] == "{":
                # if we can decode the string as JSON expression, then we do this
                try:
                    out_dict[k] = json.loads(v)
                    continue
                except json.decoder.JSONDecodeError:
                    pass
            # try to convert string to int
            try:
                out_dict[k] = int(v)
                continue
            except ValueError:
                pass
            # try to convert string to float
            try:
                out_dict[k] = float(v)
                continue
            except ValueError:
                pass
    return out_dict


def get_tag(
    path_or_id: Union[str, int],
    recursive: bool = False,
) -> typing.Optional[dict]:
    """Apply metadata to the namespace and child resources

    :param path_or_id: search id or gns path of resources to retrieve
    :type path_or_id: ``str`` or ``int``
    :param recursive: use the -R flag to tag recursively, Default: False
    :type recursive: ``bool``
    :returns: metadata of the target files
    :rtype: ``dict`` or ``None``
    """
    # convert String search_id to int, if needed
    if isinstance(path_or_id, str):
        try:
            path_or_id = int(path_or_id)
        except ValueError:
            pass
    if isinstance(path_or_id, int):
        # if path_or_id is a search_id check whether the search ID exists
        if not searchid_exists(path_or_id):
            return None
    elif isinstance(path_or_id, (str, Path)):
        # if path_or_id is a str or Path check whether the resource exists
        if not resource_exists(path_or_id):
            return None
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'path_or_id' needs to be 'str', 'int' or Path-like but got "
            + f"'{type(path_or_id).__name__}'"
        )
    # run tag_raw
    output: subprocess.CompletedProcess = tag_raw(
        path_or_id, recursive=recursive, display=True, return_type=2
    )
    # check if error occurred
    if output.returncode == 0:
        # print new metadata
        return json.loads(output.stdout.decode("utf-8").rstrip())
    else:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )


def set_tag(
    path_or_id: Union[str, int],
    metadata: dict,
    recursive: bool = False,
) -> typing.Optional[dict]:
    """Apply metadata to the namespace and child resources

    :param path_or_id: search id or gns path of resources to retrieve
    :type path_or_id: ``str`` or ``int``
    :param metadata: dict that holds as keys "[metadata schema].[field]" and
                     as values the metadata values
    :type metadata: ``dict``
    :param recursive: use the -R flag to tag recursively, Default: False
    :type recursive: ``bool``
    :returns: new metadata of the target files
    :rtype: ``dict`` or ``None``
    """
    # convert String search_id to int, if needed
    if isinstance(path_or_id, str):
        try:
            path_or_id = int(path_or_id)
        except ValueError:
            pass
    if isinstance(path_or_id, int):
        # if path_or_id is a search_id check whether the search ID exists
        if not searchid_exists(path_or_id):
            return None
    elif isinstance(path_or_id, (str, Path)):
        # if path_or_id is a str or Path check whether the resource exists
        if not resource_exists(path_or_id):
            return None
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'path_or_id' needs to be 'str', 'int' or Path-like but got "
            + f"'{type(path_or_id).__name__}'"
        )
    if isinstance(metadata, dict):
        if len(metadata) == 0:
            raise ValueError(
                f"slk.{inspect.stack()[0][3]}: argument 'metadata' is an empty dictionary; needs to have at "
                + "least one key-value pair"
            )
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'metadata' needs to be 'dict' but got "
            + f"'{type(metadata).__name__}'"
        )
    # run tag_raw
    output: subprocess.CompletedProcess = tag_raw(
        path_or_id, metadata, recursive, False, return_type=2
    )
    # check if error occurred
    if output.returncode == 0:
        # print new metadata
        return get_tag(path_or_id, recursive)
    else:
        raise PySlkException(
            f"pyslk.{inspect.stack()[0][3]}: "
            + f"{output.stdout.decode('utf-8').rstrip()} "
            + f"{output.stderr.decode('utf-8').rstrip()}"
        )
