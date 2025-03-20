#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""\
pyslk.utils contains utilities needed by pyslk.pyslk.
"""

import calendar
import glob
import inspect
import json
import math
import os
import re
import shutil
import subprocess
import time
import warnings
from datetime import datetime
from grp import getgrgid
from pathlib import Path
from pwd import getpwuid
from stat import filemode
from typing import Optional, Union

import pandas as pd
import psutil
from dateutil.parser import parse

from .config import module_load
from .constants import (
    PYSLK_DEFAULT_LIST_CLONE_COLUMNS,
    PYSLK_DEFAULT_LIST_COLUMNS,
    PYSLK_FILE_SIZE_UNITS,
    PYSLK_LOGGER,
    PYSLK_WILDCARDS,
    SLK_USER_CONFIG,
    SLK_USER_LOG,
)
from .pyslk_exceptions import (
    PySlkBadProcessError,
    PySlkException,
    PySlkNoValidLoginTokenError,
    check_for_errors,
)

__all__ = [
    "construct_dst_from_src",
    "convert_expiration_date",
    "login_valid",
    "run_slk",
    "access_local",
    "is_search_id",
    "which",
    "get_recall_job_id",
    "get_slk_pid",
    "FakeProc",
    "_convert_size",
    "_parse_list",
    "_parse_list_to_rows",
    "_parse_size",
    "_rows_to_dataframe",
]


class FakeProc:
    i = 0

    def __init__(self):
        pass

    def next_i(self):
        if self.i < 6:
            self.i = self.i + 1
        else:
            self.i = 1
        return self.i


def which(command: str) -> str:
    """Get the path to a given command."""
    path = module_load().get("PATH")
    return shutil.which(command, path=path) or ""


def run_slk(
    slk_call: Union[list, str],
    fun: str,
    env: Optional[str] = None,
    retries_on_timeout: int = 0,
    handle_output: bool = True,
    wait_until_finished: bool = True,
) -> Union[str, subprocess.CompletedProcess, subprocess.Popen]:
    """Runs a provided slk_call via subprocess.run and returns stdout

    The argument 'slk_call' is used as argument in a call of
    'subprocess.run(...)'. If slk_call is a string then 'shell=True' is set in
    the run(...)-call. Otherwise, the argument 'shell' is omitted.

    If the command provided via 'slk_call' does not exist (e.g. 'slk' not
    available on this system) or if 'slk' returns an exit code '!= 0' then a
    PySlkException is raised.

    :param slk_call: slk call as input for subprocess.run
    :type slk_call: str or list of str
    :param fun: name of the calling pyslk function; printed when exception is
                raised
    :type fun: str
    :param env: environment string
    :type env: str
    :param retries_on_timeout: run slk_helpers calls repeatedly 'n' times when exit code 3 (timeout) is returned
    :type retries_on_timeout: int
    :param handle_output: whether to handle exceptions and parse outputs or just return outputs.
    :type handle_output: bool
    :param wait_until_finished: let this function run as long as the slk command is running
    :type wait_until_finished: bool
    :returns: stdout of the slk call
    :rtype: str
    """
    PYSLK_LOGGER.debug(f"slk call: {slk_call}")
    # set / get / update environment
    env = env or module_load()
    os_env = os.environ.copy()
    os_env.update(env)
    # convert slk_call to string list if it is a list
    if isinstance(slk_call, list):
        tmp_slk_call: list = [str(c) for c in slk_call]
        slk_call = tmp_slk_call
    # check if 'retries_on_timeout' is set to invalid value
    if retries_on_timeout < 0:
        raise ValueError("argument 'retries_on_timeout' has to be a positive integer")
    if retries_on_timeout > 10:
        warnings.warn(
            f"argument 'retries_on_timeout' is set to {retries_on_timeout} which might cause long waiting "
            + "times if the StrongLink system is actually not responding."
        )
    # count number of iterations
    i: int = 0
    # set 'True' if timeout error arises to remain in 'while' loop; needs to be initially 'True'; otherwise we do
    # not enter the while loop
    timeout_error: bool = True
    try:
        output = None
        while i <= retries_on_timeout and timeout_error:
            if isinstance(slk_call, list):
                if wait_until_finished:
                    output = subprocess.run(
                        slk_call,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        env=os_env,
                    )
                else:
                    output = subprocess.Popen(
                        slk_call,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        env=os_env,
                        text=True,
                    )
                    time.sleep(2)
            elif isinstance(slk_call, str):
                if wait_until_finished:
                    output = subprocess.run(
                        slk_call,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        shell=True,
                        env=os_env,
                    )
                else:
                    output = subprocess.Popen(
                        slk_call,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        shell=True,
                        env=os_env,
                        text=True,
                    )
                    time.sleep(2)
            else:
                raise TypeError(
                    f"pyslk.{fun}: 'slk_call' has to be of type 'list' or 'str' but is {type(slk_call).__name__}"
                )
            # if the return code is unequals 3 we leave the while loop by setting 'timeout_error' to False
            if output.returncode != 3:
                timeout_error = False
    except FileNotFoundError as e:
        raise PySlkException(
            f"pyslk.{fun}: {str(e).split(':')[-1][2:-1]}: command not found"
        )
    if handle_output and wait_until_finished:
        check_for_errors(output, fun)

        # get return value and ...
        tmp_return = output.stdout.decode("utf-8")

        # ... pimp a bit if necessary
        if len(tmp_return) > 0:
            if tmp_return[-1] == "\n":
                tmp_return = tmp_return[:-1]

        # return the return value
        return tmp_return
    return output


def get_slk_pid(process: Union[subprocess.Popen, FakeProc]) -> int:
    """
    Return the pid of a slk call

    :param process: a process as instance of subprocess.Popen in which slk is running as child process
    :type process: subprocess.Popen
    :return: pid of a slk call within the provided instance of subprocess.Popen
    :rtype:
    """
    if isinstance(process, FakeProc):
        return process.next_i()

    # child pid
    cpid: int = -1
    if process.poll() is None:
        try:
            parent = psutil.Process(process.pid)
        except psutil.NoSuchProcess:
            tmp_args = process.args
            if not isinstance(tmp_args, str) and tmp_args is not None:
                tmp_args = " ".join(tmp_args)
            raise PySlkBadProcessError(
                f"pyslk.{inspect.stack()[0][3]}: process with pid {str(process.pid)} and name {tmp_args} does not exist"
            )
        children = parent.children(recursive=True)
        for process in children:
            # if multiple processes with the name "java" exist, we take the last one
            if process.name()[0:4] == "java":
                cpid = process.pid
        if cpid == -1:
            tmp_args = process.args
            if not isinstance(tmp_args, str) and tmp_args is not None:
                tmp_args = " ".join(tmp_args)
            raise PySlkBadProcessError(
                f"pyslk.{inspect.stack()[0][3]}: process with pid {str(process.pid)} and name {tmp_args} has no child "
                + "process which looks like a running instance of slk/slk_helpers."
            )
    else:
        tmp_args = process.args
        if not isinstance(tmp_args, str) and tmp_args is not None:
            tmp_args = " ".join(tmp_args)
        raise PySlkBadProcessError(
            f"pyslk.{inspect.stack()[0][3]}: process with pid {str(process.pid)} and name {tmp_args} has already ended."
            + " Cannot get child processes."
        )
    # return child pid
    return cpid


def get_recall_job_id(
    pid: Union[int, str],
    return_last_match: bool = True,
    slk_log_file: Union[str, Path] = SLK_USER_LOG,
) -> Union[int, None]:
    """

    :param pid: pid of a slk call
    :type pid: int or str
    :param return_last_match: if multiple slk runs hat the same PID and returned a job id, take the last job id;
        else, take the first one
    :type return_last_match: bool
    :param slk_log_file: path of the slk-cli log file from which this command should read
    :type slk_log_file: str or path-like object
    :return: a valid job id; if no job id was printed to the slk-cli log, print None
    :rtype: int or None
    """
    text = str(pid) + r"\s*INFO\s*Created copy job with id:\s*'([0-9]*)' for"
    jid: int = -1
    with open(slk_log_file) as file:
        for line in file:
            if re.search(text, line):
                # if the pid existed  multiple times, we will get the most recent output
                jid = int(re.search(text, line).group(1))
                if not return_last_match:
                    return jid
    if jid == -1:
        return None
    else:
        return jid


def _parse_list_to_rows(
    output,
    path_or_id: Union[str, int, Path, None] = None,
    full_path: bool = True,
    is_resource_id: bool = False,
) -> list:
    """Parsed the output from a list command to a list of rows.

    The parsing is very much static and fixed. The parsing is done line by line
    to also catch recursive outputs. Filenames are concatenated with the path.
    If the string output originates from a recursive list or search,
    full_path should be True to distinguish between files of the same name.


    :param is_resource_id: the last column is a resource id - no resource path
    :type is_resource_id: bool
    TODO: add variable description
    """  # .format(slk_version_used_for_parser_syntax)
    rows = []
    concat_path = ""

    if full_path and isinstance(path_or_id, (str, Path)):
        concat_path = str(path_or_id)
        base = os.path.basename(concat_path)
        dirname = os.path.dirname(concat_path)
        if PYSLK_WILDCARDS in base:
            # only use dirname to concat in this case
            concat_path = os.path.dirname(concat_path)
        if PYSLK_WILDCARDS in dirname:
            # output slk list is ambiguous in this case, no concat_path
            concat_path = ""

    if path_or_id is None:
        warnings.warn(
            "When 'path_or_id' is not set (which is the case), 'full_path' will be ignored."
        )

    for line in output:
        # if this is from a recursive list
        if line.startswith("/") and line.endswith(":") and full_path is True:
            # we keep the path for later concatenation to filename
            concat_path = line[:-1]
        split = [entry for entry in line.split(" ") if entry]
        if len(split) == len(PYSLK_DEFAULT_LIST_COLUMNS):
            if not is_resource_id:
                # if we list a search result, then the path is printed automatically
                # thus, if we have a search_id, then we need to remove the path when full_path is False
                if isinstance(path_or_id, int) and not full_path:
                    split[-1] = os.path.basename(split[-1])
                # if path is a path and not a search id
                if isinstance(path_or_id, (str, Path)):
                    if len(output) == 3 and os.path.basename(concat_path) == split[-1]:
                        # in this case, we list only one item. there is no way to say
                        # if this is a directory containing only one file or simply a single file listed.
                        # we assume it's as single file listed. This only doesn't work if we actually
                        # have a single file in a directory named like the file. we assume this does not happen...
                        split[-1] = concat_path
                    else:
                        split[-1] = os.path.join(concat_path, split[-1])
            rows.append(split)
        if len(split) == len(PYSLK_DEFAULT_LIST_CLONE_COLUMNS):
            if not is_resource_id:
                # we need to remove the path when full_path is False
                if path_or_id is not None and not full_path:
                    split[-1] = os.path.basename(split[-1])
            rows.append(split)

    return rows


def _parse_list_to_rows_3_3_21(output, path_or_id="", full_path=True):
    """Parsed the output from a list command to a list of rows.

    The parsing is very much static and fixed. The parsing is done line by line
    to also catch recursive outputs. Filenames are concatenated with the path.
    If the string output originates from a recursive list or search,
    full_path should be True to distinguish between files of the same name.

    """  # .format(slk_version_used_for_parser_syntax)
    rows = []
    concat_path = ""
    if full_path is True:
        concat_path = path_or_id

    for line in output:
        # if this is from a recursive list
        if line.startswith("/") and line.endswith(":") and full_path is True:
            # we keep the path for later concatenation to filename
            concat_path = line[:-1]
        split = [entry for entry in line.split(" ") if entry]
        if len(split) == 7:
            split.insert(3, "")
        if len(split) == 8:
            # if path is a path and not a search id...
            # if type(path) is str:
            split[-1] = os.path.join(concat_path, split[-1])
            # _parse_date(split)
            rows.append(split)
            # rows.append(split)

    return rows


def _parse_size(size_str):
    """parse slk filesize format into integer bytes.

    Assumes slk format, e.g., 22.6G, 11M, 343K etc..

    If parsing fails, return NaN.

    """
    # import numpy as np
    units = PYSLK_FILE_SIZE_UNITS
    if size_str:
        if re.match("^[0-9]+$", size_str) is not None:
            return float(size_str)
        else:
            try:
                number, unit = size_str[0:-1], size_str[-1]
                return float(number) * units[unit]
            except Exception as e:
                warnings.warn(
                    f"pyslk.{inspect.stack()[0][3]}: parsing size failed with: {repr(e)}"
                )
                return math.nan
            # removed "int"-casting of the results
    warnings.warn(
        f"pyslk.{inspect.stack()[0][3]}: file size cannot be "
        f"converted: {size_str}; return NaN instead"
    )
    return math.nan


def _convert_size(size_byte: int, unit: str = "B") -> dict[str, Union[str, float, int]]:
    """
    Converts the size of a file from byte to chosen unit

    :param size_byte:
    :type size_byte:
    :param unit:
    :type unit:
    :return:
    :rtype: int
    """
    if unit == "h":
        if size_byte == 0:
            return {"value": 0, "unit": "B"}
        for best_unit in PYSLK_FILE_SIZE_UNITS.keys():
            best_size = size_byte / PYSLK_FILE_SIZE_UNITS[best_unit]
            if (best_size >= 1.0) & (best_size < 1000.0):
                return {"value": best_size, "unit": best_unit}
        warnings.warn(
            f"pyslk.{inspect.stack()[0][3]}: could not find "
            + f"out human-readable value using available units for value {str(size_byte)}"
        )
        return {"value": size_byte, "unit": "B"}
    if unit not in PYSLK_FILE_SIZE_UNITS.keys():
        raise ValueError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'return_format' has to be a string of value "
            + f"{', '.join(PYSLK_FILE_SIZE_UNITS.keys())} or 'h' (human-readable)."
        )
    # Return result in desired format
    new_size = size_byte / PYSLK_FILE_SIZE_UNITS[unit]
    return {"value": new_size, "unit": unit}


def _filename_list_2_search_query(directory, filename_list):
    """generates a RQL search query to find files with names "filename_list"
    located in "directory"

    We get a directory and a list of filenames and create a RQL search
    query.

    :param directory: a directory
    :type directory: str
    :param filename_list: list of filenames
    :type filename_list: list of str
    :returns: search query to find the files
    :rtype: str
    """

    if not isinstance(filename_list, list):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'filename_list' has to be a list of strings but has type "
            + f"{type(filename_list).__name__}"
        )

    if not isinstance(directory, str):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'directory' has to be a string but has type "
            + f"{type(directory).__name__}"
        )

    if len(filename_list) == 0:
        return '{{"path": {{"$gte": "{0}", "$max_depth": 1}}}}'.format(directory)

    tmp_resource_names: str = '"}, {"resources.name": "'.join(filename_list)
    return (
        f'{{"$and": [{{"path": {{"$gte": "{directory}", "$max_depth": 1}}}}, {{"$or": [{{"resources.name"'
        + f': "{tmp_resource_names}"}}]}}]}}'
    )


def file_list_2_search_query(file_list):
    """generates a RQL search query to find listed files

    We get a list of files (with absolute path) and create a RQL search
    query.

    :param file_list: list of files with absolute path
    :type file_list: list of str
    :returns: search query to find the files listed in file_list
    :rtype: str
    """

    if not isinstance(file_list, list):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'file_list' has to be a list of strings but has type "
            + f"{type(file_list).__name__}"
        )

    if len(file_list) == 0:
        return None

    # disassemble the file list;
    #   - split directory and filename
    #   - create dictionary with directories as keys and
    #       lists of filenames as values
    file_dict = dict()
    for iP in file_list:
        i_dir = os.path.dirname(iP)
        i_file = os.path.basename(iP)

        tmp_list = file_dict.get(i_dir, [])
        # append filename if it is not already in the list
        if i_file not in tmp_list:
            tmp_list.append(i_file)
            file_dict[i_dir] = tmp_list

    # construct search query
    #  Differentiate between a situation where all files are in one
    #  directory/namespace in StrongLink (if ...) or in more than
    #  one (else ...).
    if len(file_dict) == 1:
        tmp_dir = list(file_dict.keys())[0]
        return _filename_list_2_search_query(tmp_dir, file_dict[tmp_dir])
    else:
        tmp_query = '{"$or":['
        for tmp_dir, tmp_fn in file_dict.items():
            tmp_query = tmp_query + _filename_list_2_search_query(tmp_dir, tmp_fn)
            tmp_query = tmp_query + ","
        tmp_query = tmp_query[:-1] + "]}"
        return tmp_query


def _parse_year_month_day_2_date(df: pd.DataFrame) -> pd.DataFrame:
    """parse the year, month, day columns into datetime object column."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'df' has to be a 'pandas.DataFrame' but has type "
            + f"{type(df).__name__}"
        )
    if "day" in df.columns and "month" in df.columns and "year" in df.columns:
        df["month"] = df.apply(
            lambda x: list(calendar.month_abbr).index(x.month), axis=1
        )
        dates = pd.to_datetime(dict(year=df.year, month=df.month, day=df.day))
        # move date column to where day column was
        df.insert(loc=df.columns.get_loc("day"), column="date", value=dates)
        return df.drop(columns=["year", "day", "month"])
    else:
        return df


def _parse_iso_str_timestamp_2_datetime(df: pd.DataFrame) -> pd.DataFrame:
    """parse the str ISO timestamps to datetime"""
    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'df' has to be a 'pandas.DataFrame' but has type "
            + f"{type(df).__name__}"
        )
    for col in df:
        if col.startswith("timestamp"):
            df[col] = pd.to_datetime(df[col])
    return df


def _parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """parse the year, month, day columns into datetime object column."""
    # try:
    #     import pandas as pd
    # except ModuleNotFoundError:
    #     PySlkException(f"pyslk.{inspect.stack()[0][3]}: functions needs "
    #                    "'pandas' to be installed")
    # map month abbreviations to integers
    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'df' has to be a 'pandas.DataFrame' but has type "
            + f"{type(df).__name__}"
        )
    return _parse_iso_str_timestamp_2_datetime(_parse_year_month_day_2_date(df))


def _rows_to_dataframe(
    rows: list, cols: list = PYSLK_DEFAULT_LIST_COLUMNS
) -> pd.DataFrame:
    """convert list of rows to dataframe"""
    return pd.DataFrame(rows, columns=cols)


def _parse_sizes(df: pd.DataFrame) -> pd.DataFrame:
    """parses the filesize column into integer bytes"""
    df["filesize"] = df["filesize"].map(_parse_size)
    return df


def _parse_list(
    list_out: str,
    path_or_id: Union[str, int, Path],
    column_names: list = PYSLK_DEFAULT_LIST_COLUMNS,
    parse_dates: bool = True,
    parse_sizes: bool = True,
    numeric_ids: bool = False,
    full_path: bool = True,
    is_resource_id: bool = False,
) -> pd.DataFrame:
    """Return pandas.DataFrame containing results from search id or GNS path

    Calls 'pyslk.pyslk.slk_list(...)' and parses the return string into a
    pandas.DataFrame. All arguments are copied 1:1 into the 'slk_list' call
    except for 'column_widths'. Assumes six output columns of 'slk list' having
    the widths 12, 12, 12, 9, 4, 4, 5 and 999 (999 => as wide as necessary).

    Note: 'slk list' currently only print the modification date and no
    modification time. The output of this parser might be modified in
    future when modification times are printed as well.

    :param list_out: output of slk list
    :type list_out: str
    :param path_or_id: search id or gns path
    :type path_or_id: str or int or Path
    :param column_names: names of the columns in the pandas.DataFrame
    :type column_names: list
    :param parse_dates: parse day, month and year into a datetime column.
    :type parse_dates: bool
    :param parse_sizes: parse filesize column into bytes integer.
    :type parse_sizes: bool
    :param numeric_ids: show numeric values for user and group, default: False
        (show user and group names)
    :type numeric_ids: bool
    :param full_path: add full filepath to filename column.
    :type full_path: bool
    :param is_resource_id: the last column is a resource id - no resource path
    :type is_resource_id: bool
    :returns: output of 'slk list' parsed into a pandas.DataFrame with eight
        columns (permissions, owner, group, size, day, month, year, filename)
    :rtype: pandas.DataFrame
    """
    n_columns_expected = len(column_names)
    n_columns_reality = len(
        [entry for entry in list_out.split("\n")[0].split(" ") if entry]
    )
    if n_columns_reality != n_columns_expected:
        warnings.warn(
            f"pyslk.{inspect.stack()[0][3]}: based on value of 'column_names' expected {n_columns_expected} columns in "
            + f"raw output but got {n_columns_reality} columns"
        )

    rows = _parse_list_to_rows(
        list_out.split("\n"),
        path_or_id=path_or_id,
        full_path=full_path,
        is_resource_id=is_resource_id,
    )
    # split each row into individual columns
    df = _rows_to_dataframe(rows, cols=column_names)

    if parse_dates:
        try:
            df = _parse_dates(df)
        except Exception as e:
            warnings.warn(
                f"pyslk.{inspect.stack()[0][3]}: date parsing failed with: {repr(e)}"
            )

    if parse_sizes:
        try:
            df = _parse_sizes(df)
        except Exception as e:
            warnings.warn(
                f"pyslk.{inspect.stack()[0][3]}: filesize parsing failed with: {repr(e)}"
            )

    if numeric_ids:
        df.group = df.group.astype(int)
        df.owner = df.owner.astype(int)

    if is_resource_id:
        df.filename = df.filename.astype(int)

    return df


def login_valid(quiet: bool = False, rise_error_on_invalid: bool = False) -> bool:
    """
    Check if a valid login token exists.

    Raises 'PySlkNoValidLoginTokenError' when 'rise_error_on_invalid' is True.

    Code calling this function might raise PySlkNoValidLoginTokenError if this functions returns False.

    :param quiet: print no warnings when the slk config file cannot be properly interpreted
    :type quiet: bool
    :param rise_error_on_invalid: raise a 'PySlkNoValidLoginTokenError' when no valid token is present
    :type rise_error_on_invalid: bool
    :return:
    """
    if not os.path.isfile(SLK_USER_CONFIG):
        message = (
            f"slk user config file with login token does not exist ({SLK_USER_CONFIG}). "
            + "Please run 'slk login' to login and to generate this file."
        )
        if rise_error_on_invalid:
            raise PySlkNoValidLoginTokenError(message)
        if not quiet:
            warnings.warn(message)
        return False
    try:
        with open(SLK_USER_CONFIG) as f:
            config_json = json.load(f)
        if not ("expireDate" in config_json and "sessionKey" in config_json):
            message = (
                f"slk user config file seems to be incomplete ({SLK_USER_CONFIG}). Please run 'slk login' "
                + "to login and to generate this file."
            )
            if rise_error_on_invalid:
                raise PySlkNoValidLoginTokenError(message)
            if not quiet:
                warnings.warn(message)
            return False

        exp_date = convert_expiration_date(config_json["expireDate"])
        if exp_date > datetime.now(exp_date.tzinfo):
            return True
        else:
            if rise_error_on_invalid:
                raise PySlkNoValidLoginTokenError(
                    "slk login token is expired. Please run 'slk login' to login to get a fresh token"
                )
            return False
    except json.decoder.JSONDecodeError:
        message = (
            f"slk user config file with login token could not be interpreted ({SLK_USER_CONFIG}). "
            + "Please run 'slk login' to login and to re-generate file."
        )
        if rise_error_on_invalid:
            raise PySlkNoValidLoginTokenError(message)
        if not quiet:
            warnings.warn(message)
        return False


def convert_expiration_date(exp_date: str) -> datetime:
    """
    interprets a date in a string and converts it into a datetime object

    :param exp_date: expiration date of the format '%a %b %d %H:%M:%S %Z %Y'
    :type exp_date: str
    :return: expiration date converted into a datetime object
    :rtype: datetime
    """
    # new approach after issue in KIX ticket 142464
    out_date = parse(exp_date)
    # this is an approach which will cause issues if no 'locale' is set:
    # if locale.getlocale()[0] == "en_US":
    #     out_date = datetime.strptime(exp_date, "%a %b %d %H:%M:%S %Z %Y")
    # else:
    #     curr_locale = locale.getlocale(locale.LC_TIME)
    #    locale.setlocale(locale.LC_TIME, "en_US.utf-8")
    #    out_date = datetime.strptime(exp_date, "%a %b %d %H:%M:%S %Z %Y")
    #    locale.setlocale(locale.LC_TIME, f"{curr_locale[0]}.{curr_locale[1]}")
    return out_date


def access_local(
    resources: Union[list[str], list[Path], str, Path], mode: int
) -> Union[list[bool], bool]:
    if isinstance(resources, str):
        return access_local(Path(resources), mode)
    elif isinstance(resources, list):
        return [access_local(i, mode) for i in resources]
    elif isinstance(resources, Path):
        return os.access(resources, mode)
    else:
        raise TypeError(
            "Need 'str', path-like object or list of one of both types as input. Got "
            + f"'{type(resources).__name__}'."
        )


def is_search_id(path_or_id: Union[Path, str, int]) -> bool:
    if isinstance(path_or_id, int):
        return True
    if isinstance(path_or_id, Path):
        return False
    if isinstance(path_or_id, str):
        try:
            int(path_or_id)
            return True
        except ValueError:
            return False
    raise TypeError(
        f"'path_or_id' has to be 'str', 'int' or path-like but is of type '{type(path_or_id).__name__}'"
    )


def list_local(
    path: Union[str, int],
    show_hidden: bool = False,
    numeric_ids: bool = False,
    recursive: bool = False,
    parse_dates: bool = True,
    parse_sizes: bool = True,
    full_path: bool = True,
) -> pd.DataFrame:
    """Return pandas.DataFrame containing results from search id or GNS path

    Calls 'pyslk.pyslk.slk_list(...)' and parses the return string into a
    pandas.DataFrame. All arguments are copied 1:1 into the 'slk_list' call
    except for 'column_widths'. Assumes six output columns of 'slk list' having
    the widths 12, 12, 12, 9, 4, 4, 5 and 999 (999 => as wide as necessary).

    Note: 'slk list' currently only print the modification date and no
    modification time. The output of this parser might be modified in
    future when modification times are printed as well.

    :param path: search id or gns path
    :type path: str
    :param show_hidden: show '.' files, default: False (don't show these files)
    :type show_hidden: bool
    :param numeric_ids: show numeric values for user and group, default: False
        (show user and group names)
    :type numeric_ids: bool
    :param recursive: use the -R flag to list recursively, default: False
    :type recursive: bool
    :param parse_dates: parse day, month and year into a datetime column.
    :type parse_dates: bool
    :param parse_sizes: parse filesize column into bytes integer.
    :type parse_sizes: bool
    :param full_path: add full filepath to filename column.
    :type full_path: bool
    :returns: output of 'slk list' parsed into a pandas.DataFrame with eight
        columns (permissions, owner, group, size, day, month, year, filename)
    :rtype: pandas.DataFrame
    """
    # get file list and file stats
    files = [
        Path(root, f)
        for root, dirs, files in os.walk(path)
        for f in files
        if not show_hidden or f[0] != "."
    ]
    stats = [os.stat(f) for f in files]
    # permissions
    modes = {s.st_mode: filemode(s.st_mode) for s in stats}
    df = pd.DataFrame([modes[s.st_mode] for s in stats], columns=["permissions"])
    # owner
    if numeric_ids:
        df["owner"] = [s.st_uid for s in stats]
    else:
        uids = {s.st_uid: getpwuid(s.st_uid).pw_name for s in stats}
        df["owner"] = [uids[s.st_uid] for s in stats]
    # groups
    # owner
    if numeric_ids:
        df["group"] = [s.st_gid for s in stats]
    else:
        gids = {s.st_gid: getgrgid(s.st_gid).gr_name for s in stats}
        df["group"] = [gids[s.st_gid] for s in stats]
    # sizes
    if parse_sizes:
        df["filesize"] = [s.st_size for s in stats]
    else:
        df["filesize"] = [_convert_size(s.st_size, "h")["value"] for s in stats]
    # dates
    mtimes = [datetime.utcfromtimestamp(s.st_mtime) for s in stats]
    df["day"] = [t.strftime("%d") for t in mtimes]
    df["month"] = [t.strftime("%b") for t in mtimes]
    df["year"] = [t.strftime("%Y") for t in mtimes]
    df["time"] = [t.strftime("%H:%M") for t in mtimes]
    if parse_dates:
        df = _parse_dates(df)
    # filename
    if full_path:
        df["filename"] = files
    else:
        df["filename"] = [os.path.basename(f) for f in files]
    # return dataframe
    return df


def construct_dst_from_src(
    src: Union[str, Path, list], dst_gns: Union[str, Path], recursion_depth: int = 0
) -> Optional[Union[str, Path, list]]:
    """Construct destination paths for source resources when they were archived to given destination

    :param src:
        Path, pattern or list of files that should be archived.
    :type src: ``str`` or ``list``
    :param dst_gns:
        Destination directory for archiving.
    :type dst_gns: ``str``
    :param recursion_depth:
        count on how often this function has called itself (stop after 50 recursive calls)
    :type recursion_depth: ``int``
    :returns:
        target resource paths if ``src`` resource(s) are archived to ``dst_gns``
    :rtype: ``str`` or ``list`` or ``Path``

    .. seealso::
        * :py:meth:`~pyslk.archive_raw`
        * :py:meth:`~pyslk.archive`

    """
    if recursion_depth > 9:
        raise RuntimeError(
            "construct_dst_from_src: this function called itself recursively more than 10 times; input was: "
            + f"src = {src}; dst_gns = {dst_gns}"
        )
    if isinstance(src, (str, Path)):
        # here we get a list
        src = glob.glob(os.path.expanduser(os.path.expandvars(src)))
        if len(src) == 1:
            # original src matched one resource => proceed
            src = src[0]
            # next: src is a file
            if os.path.isfile(src):
                return os.path.join(dst_gns, os.path.basename(src))
            # when we arrive here, src is a folder
            dst_gns_full = list()
            for root, subdirs, files in os.walk(src):
                if len(files) > 0:
                    # construct destination paths
                    dst_gns_full.extend([str(dst_gns) + "/" + f for f in files])
                if len(subdirs) > 0:
                    # run this function again for all subdirs
                    dst_gns_full.extend(
                        construct_dst_from_src(
                            [root + "/" + s for s in subdirs],
                            dst_gns,
                            recursion_depth=recursion_depth + 1,
                        )
                    )
            return dst_gns_full
        elif len(src) == 0:
            # no match => does not exist
            warnings.warn(
                "construct_dst_from_src: resource does not exist or bash glob yielded no match; input was: "
                + f"src = {src}; dst_gns = {dst_gns}"
            )
            return None
        else:
            # multiple matches: call this command recursively and return output
            return construct_dst_from_src(
                src, dst_gns, recursion_depth=recursion_depth + 1
            )
    if isinstance(src, list):
        dst_gns_full = list()
        for src in src:
            dst_gns_tmp = construct_dst_from_src(
                src, dst_gns, recursion_depth=recursion_depth + 1
            )
            if isinstance(dst_gns_tmp, list):
                dst_gns_full.extend(dst_gns_tmp)
            elif isinstance(dst_gns_tmp, (str, Path)):
                dst_gns_full.append(dst_gns_tmp)
            elif dst_gns_tmp is None:
                pass
            else:
                raise TypeError(
                    "construct_dst_from_src: wrong return type of function call; expected 'str', 'list' or "
                    f"Path-like but got {type(dst_gns_tmp).__name__}"
                )
                pass
        return dst_gns_full
    raise TypeError(
        "construct_dst_from_src: wrong input type for 'src'; expected 'str', 'list' or Path-like but got "
        f"{type(src).__name__}"
    )
