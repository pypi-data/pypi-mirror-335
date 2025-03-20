import inspect
import subprocess
import warnings
from pathlib import Path
from typing import Union

import pandas as pd

from ..constants import PYSLK_DEFAULT_LIST_CLONE_COLUMNS, PYSLK_DEFAULT_LIST_COLUMNS
from ..pyslk_exceptions import PySlkException
from ..raw import list_clone_file_raw, list_clone_search_raw, list_raw
from ..utils import _parse_list

__all__ = ["ls", "list_clone_search", "list_clone_file"]


def ls(
    path_or_id: Union[
        str, int, Path, list[str], list[int], list[Path], set[str], set[int], set[Path]
    ],
    show_hidden: bool = False,
    numeric_ids: bool = False,
    recursive: bool = False,
    column_names: list = PYSLK_DEFAULT_LIST_COLUMNS,
    parse_dates: bool = True,
    parse_sizes: bool = True,
    full_path: bool = True,
) -> pd.DataFrame:
    """Return pandas.DataFrame containing results from search id or GNS path

    Calls :py:meth:`~pyslk.list_raw` and parses the return string into a
    ``pandas.DataFrame``. All arguments are copied 1:1 except for 'column_widths'.
    Assumes six output columns of 'slk list' having
    the widths 12, 12, 12, 9, 4, 4, 5 and 999 (999 => as wide as necessary).

    Note: :py:meth:`~pyslk.list_raw` currently only print the modification date and no
    modification time. The output of this parser might be modified in
    future when modification times are printed as well.

    :param path_or_id: search id or gns path
    :type path_or_id: ``str`` or ``Path`` or ``int``
    :param show_hidden: show '.' files, default: False (don't show these files)
    :type show_hidden: ``bool``
    :param numeric_ids: show numeric values for user and group, default: False
        (show user and group names)
    :type numeric_ids: ``bool``
    :param recursive: use the -R flag to list recursively, default: False
    :type recursive: ``bool``
    :param column_names: names of the columns in the pandas.DataFrame
    :type column_names: ``list``
    :param parse_dates: parse day, month and year into a datetime column.
    :type parse_dates: ``bool``
    :param parse_sizes: parse 'filesize' column into bytes integer.
    :type parse_sizes: ``bool``
    :param full_path: add full filepath to filename column.
    :type full_path: ``bool``
    :returns: output of 'slk list' parsed into a pandas.DataFrame with eight
        columns (permissions, owner, group, size, day, month, year, filename)
    :rtype: ``pandas.DataFrame``

    .. seealso::
        * :py:meth:`~pyslk.list_raw`

    """
    # try:
    #     import pandas as pd
    # except ModuleNotFoundError:
    #     PySlkException(f"pyslk.{inspect.stack()[0][3]}: functions needs "
    #                    "'pandas' to be installed")

    # list_out = io.StringIO(list_raw(path_or_id, show_hidden=show_hidden, numeric_ids=numeric_ids, R=R, text=text)+"\n"
    #                       "-----------    user      group             0   28"
    #                       " Aug 1986  file")
    if isinstance(path_or_id, (list, set)):
        return pd.concat(
            [
                ls(
                    p,
                    show_hidden=show_hidden,
                    numeric_ids=numeric_ids,
                    recursive=recursive,
                    column_names=column_names,
                    parse_dates=parse_dates,
                )
                for p in set(path_or_id)
            ],
            ignore_index=True,
        )

    output: subprocess.CompletedProcess = list_raw(
        path_or_id,
        show_hidden=show_hidden,
        numeric_ids=numeric_ids,
        recursive=recursive,
        text=False,
        print_bytes=parse_sizes,
        return_type=2,
    )
    stdout = output.stdout.decode("utf-8").rstrip()
    stderr = output.stderr.decode("utf-8").rstrip()
    if output.returncode > 0:
        if "ERROR: No resources found for given search id:" in f"{stdout}  {stderr}":
            return pd.DataFrame(columns=column_names)
        else:
            raise PySlkException(f"pyslk.{inspect.stack()[0][3]}: {stdout} {stderr}")
    # df = pd.read_fwf(list_out, col_specs = 'infer',
    #                 width=column_widths, dtype=str, header=None,
    #                 names=column_names, infer_nrows=10000) #infer_nrows
    # df.drop(df.tail(2).index, inplace=True)

    df = _parse_list(
        stdout,
        path_or_id,
        column_names,
        parse_dates,
        parse_sizes,
        numeric_ids,
        full_path,
    )

    return df


def list_clone_search(
    search_id: Union[str, int, list[int], list[str], set[int], set[str]],
    only_files: bool = False,
    only_namespaces: bool = False,
    start: Union[int, None] = None,
    count: Union[int, None] = None,
    column_names=PYSLK_DEFAULT_LIST_CLONE_COLUMNS,
) -> pd.DataFrame:
    """Return pandas.DataFrame containing results from search id

    Calls :py:meth:`~pyslk.list_clone_search_raw` and parses the return string into
    a :py:meth:`pandas.DataFrame`. Assumes six output columns of 'slk_helpers list_clone_search'
    having the widths 12, 16, 999 (999 => as wide as necessary).

    :param search_id: search id of search which results should be printed
    :type search_id: ``str``, ``int``, ``list``, ``set``
    :param only_files: print only files (like default for `slk list`)
    :type only_files: ``bool``
    :param only_namespaces: print only namespaces
    :type only_namespaces: ``bool``
    :param start: collect search results starting with the result 'start'; if set to 1 then collect from the beginning
    :type start: int
    :param count: Collect as many search results as defined by this parameter. If set to 0 then collect until end.
    :type count: int
    :param column_names: names of the columns in the pandas.DataFrame
    :type column_names: ``list``
    :returns: output of 'slk_helpers list_search' parsed into a
        pandas.DataFrame with three columns (permissions, size, filename)
    :rtype: ``pandas.DataFrame``
    """
    # we got a list or set with search ids
    if isinstance(search_id, (list, set)):
        # check type of list/set elements
        if not all([isinstance(sid, (int, str)) for sid in search_id]):
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: argument 'search_id' has to be 'str', 'int' or 'list'/'set' these "
                + "but it is 'list'/'set' which contains at least elements of these other types: "
                + f"'{', '.join([type(sid).__name__ for sid in search_id if not isinstance(sid, str)])}'"
            )
        # call this function recursively
        return pd.concat(
            [
                list_clone_search(
                    sid,
                    only_files=only_files,
                    only_namespaces=only_namespaces,
                    start=start,
                    count=count,
                    column_names=column_names,
                )
                for sid in set(search_id)
            ],
            ignore_index=True,
        )
    elif isinstance(search_id, str):
        # we have a search id as string which needs to be converted to int
        try:
            search_id = int(search_id)
        except ValueError:
            raise ValueError(
                f"pyslk.{inspect.stack()[0][3]}: cannot convert 'search_id' to 'int' (== search id), got: {search_id}"
            )
    elif not isinstance(search_id, int):
        # we have something else which is neither 'int' nor something we caught before
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'search_id' has wrong type; need 'str', 'int' or 'list'/'set' of these "
            + f"but got {type(search_id).__name__}"
        )

    output: subprocess.CompletedProcess = list_clone_search_raw(
        search_id,
        only_files=only_files,
        only_namespaces=only_namespaces,
        start=start,
        count=count,
        return_type=2,
    )
    stdout = output.stdout.decode("utf-8").rstrip()
    stderr = output.stderr.decode("utf-8").rstrip()
    if output.returncode > 0:
        if "ERROR: No resources found for given search id:" in f"{stdout}  {stderr}":
            return pd.DataFrame(columns=column_names)
        else:
            raise PySlkException(f"pyslk.{inspect.stack()[0][3]}: {stdout} {stderr}")
    # df = pd.read_fwf(list_out, col_specs = 'infer',
    #                 width=column_widths, dtype=str, header=None,
    #                 names=column_names, infer_nrows=10000) #infer_nrows
    # df.drop(df.tail(2).index, inplace=True)

    df = _parse_list(
        stdout,
        search_id,
        column_names,
        True,
        True,
        True,
        True,
    )

    return df


def list_clone_file(
    resource_paths: Union[str, Path, list[str], list[Path], set[str], set[Path]],
    print_resource_ids: bool = False,
    print_timestamps_as_seconds_since_1970: bool = False,
    proceed_on_error: bool = True,
    column_names=PYSLK_DEFAULT_LIST_CLONE_COLUMNS,
) -> pd.DataFrame:
    """Return pandas.DataFrame containing results from search id

    Calls :py:meth:`~pyslk.list_clone_file_raw` and parses the return string into
    a :py:meth:`pandas.DataFrame`. Assumes six output columns of 'slk_helpers list_clone_file'
    having the widths 12, 16, 999 (999 => as wide as necessary).


    :param resource_paths: namespace or resource
    :type resource_paths: ``str`` or ``path-like`` or ``list[str]`` or ``list[Path]`` or ``set[str]`` or ``set[Path]``
    :param print_resource_ids: print resource ids instead of file paths
    :type print_resource_ids: `bool`
    :param print_timestamps_as_seconds_since_1970: print timestamps in seconds since 1970
    :type print_timestamps_as_seconds_since_1970: `bool`
    :param proceed_on_error: Proceed listing files even if an error arose
    :type proceed_on_error: `bool`
    :param column_names: names of the columns in the pandas.DataFrame
    :type column_names: ``list``
    :returns: output of 'slk_helpers list_search' parsed into a
        pandas.DataFrame with three columns (permissions, size, filename)
    :rtype: ``pandas.DataFrame``
    """
    # we got a list or set with search ids
    if isinstance(resource_paths, (list, set)):
        # check type of list/set elements
        if not all([isinstance(res, (Path, str)) for res in resource_paths]):
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: argument 'resource_path' has to be 'str', 'Path' or 'list'/'set' of "
                + "these but it is 'list'/'set' which contains at least elements of these other types: "
                + f"'{', '.join([type(res).__name__ for res in resource_paths if not isinstance(res, str)])}'"
            )
    elif not isinstance(resource_paths, (str, Path)):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'resource_path' has to be 'str', 'Path' or 'list'/'set' of "
            + f"these but got {type(resource_paths).__name__}"
        )

    output: subprocess.CompletedProcess = list_clone_file_raw(
        resource_paths,
        print_resource_ids,
        print_timestamps_as_seconds_since_1970,
        proceed_on_error,
        return_type=2,
    )
    stdout = output.stdout.decode("utf-8").rstrip()
    stderr = output.stderr.decode("utf-8").rstrip()
    if output.returncode == 1:
        if proceed_on_error:
            # print warning on what was not found
            warnings.warn("resources were not found:\n" + stderr)
        else:
            raise PySlkException(
                f"pyslk.{inspect.stack()[0][3]}: resources were not found:\n{stderr}"
            )
    if output.returncode == 2:
        raise PySlkException(f"pyslk.{inspect.stack()[0][3]}: {stdout} {stderr}")
    # df = pd.read_fwf(list_out, col_specs = 'infer',
    #                 width=column_widths, dtype=str, header=None,
    #                 names=column_names, infer_nrows=10000) #infer_nrows
    # df.drop(df.tail(2).index, inplace=True)

    # when print_resource_ids is set, where should be no processing of the
    # resouce (path) be done
    df = _parse_list(
        stdout,
        "/",
        column_names,
        not print_timestamps_as_seconds_since_1970,
        True,
        True,
        True,
        print_resource_ids,
    )

    return df
