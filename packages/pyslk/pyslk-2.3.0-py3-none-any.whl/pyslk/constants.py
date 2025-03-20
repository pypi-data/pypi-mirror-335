#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os

"""
pyslk.constants provides constants for the pyslk package
"""

__all__ = [
    "MAX_RETRIES_RETRIEVAL_ON_TIMEOUT",
    "MAX_RETRIES_SUBMIT_JOBS_BASIC",
    "MAX_RETRIES_SUBMIT_JOBS_SAVE_MODE",
    "MIN_VERSION_SLK",
    "MIN_VERSION_SLK_HELPERS",
    "PYSLK_DEFAULT_LIST_CLONE_COLUMNS",
    "PYSLK_DEFAULT_LIST_COLUMNS",
    "PYSLK_DEFAULT_LIST_COLUMNS_3_3_21",
    "PYSLK_DEFAULT_LIST_COLUMN_TYPES",
    "PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS",
    "PYSLK_FILE_SIZE_UNITS",
    "PYSLK_LOGGER",
    "PYSLK_SEARCH_DELAY",
    "PYSLK_WILDCARDS",
    "SEARCH_QUERY_OPERATORS",
    "SLK",
    "SLK_HELPERS",
    "SLK_SYSTEM_CONFIG",
    "SLK_USER_CONFIG",
    "SLK_USER_LOG",
]

PYSLK_LOGGER = logging.getLogger("pyslk")
PYSLK_LOGGER.setLevel(logging.WARNING)
SLK_USER_CONFIG = os.path.expanduser("~/.slk/config.json")
SLK_SYSTEM_CONFIG = "/etc/stronglink.conf"
SLK_USER_LOG = os.path.expanduser("~/.slk/slk-cli.log")
MAX_RETRIES_SUBMIT_JOBS_BASIC = 5
MAX_RETRIES_SUBMIT_JOBS_SAVE_MODE = 5
MAX_RETRIES_RETRIEVAL_ON_TIMEOUT = 3

# wildcard will trigger a slk.list in core functions
# since slk can not handle wildcards in archive and retrieve calls
PYSLK_WILDCARDS = "*"

# if we want to retrieve several search ids from tape id groups,
# we should wait a little between grouping and retrieving because
# otherwise search ids will not be valid!
PYSLK_SEARCH_DELAY = 5

PYSLK_FILE_SIZE_UNITS = {"B": 1, "K": 10**3, "M": 10**6, "G": 10**9, "T": 10**12}
# PYSLK_FILE_SIZE_UNITS = {"B": 1, "K": 2**10, "M": 2**20, "G": 2**30, "T": 2**40}

# operators for gen_search_query
SEARCH_QUERY_OPERATORS: list[str] = ["=", "<", ">", "<=", ">="]

PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS = 3

PYSLK_DEFAULT_LIST_COLUMNS = [
    "permissions",
    "owner",
    "group",
    "filesize",
    "day",
    "month",
    "year",
    "time",
    "filename",
]
PYSLK_DEFAULT_LIST_COLUMNS_3_3_21 = [
    "permissions",
    "owner",
    "group",
    "filesize",
    "day",
    "month",
    "year",
    "filename",
]
PYSLK_DEFAULT_LIST_CLONE_COLUMNS = [
    "permissions",
    "owner",
    "group",
    "filesize",
    "timestamp_mtime",
    "timestamp_created",
    "timestamp_modified",
    "timestamp_storage",
    "tape_id",
    "filename",
]
PYSLK_DEFAULT_LIST_COLUMN_TYPES = {
    "owner": int,
    "group": int,
    "filesize": int,
    "tape_id": int,
}

SLK = "slk"
SLK_HELPERS = "slk_helpers"

MIN_VERSION_SLK = {
    "help": "3.3.21",
    "version": "3.3.0",
    "login": "3.0.0",
    "search": "3.3.0",
    "list": "3.3.56",
    "retrieve": "3.3.56",
    "recall": "3.1.0",
    "archive": "3.3.56",
    "tag": "3.3.56",
    "owner": "3.1.0",
    "group": "3.1.0",
    "chmod": "3.1.0",
    "move": "3.3.56",
    "rename": "3.0.0",
    "delete": "3.1.53",
}

MIN_VERSION_SLK_HELPERS = {
    "checksum": "1.0.0",
    "exists": "1.0.0",
    "gen_file_query": "1.8.4",
    "gen_search_query": "1.9.2",
    "gfbt": "1.13.3",
    "group_files_by_tape": "1.13.3",
    "has_no_flag_partial": "1.9.0",
    "help": "1.0.0",
    "hostname": "1.0.0",
    "hsm2json": "1.7.5",
    "is_admin_session": "1.9.9",
    "is_on_tape": "1.9.1",
    "iscached": "1.9.0",
    "job_exists": "1.7.0",
    "job_queue": "1.8.9",
    "job_report": "1.9.9",
    "job_status": "1.7.0",
    "json2hsm": "1.7.5",
    "list_clone_file": "1.13.0",
    "list_clone_search": "1.12.8",
    "list_search": "1.2.0",
    "metadata": "1.7.5",
    "mkdir": "1.0.0",
    "print_rcrs": "1.12.0",
    "recall": "1.13.0",
    "recall_needed": "1.13.0",
    "resource_id": "1.13.0",
    "resource_path": "1.8.0",
    "resource_permissions": "1.8.4",
    "resource_tape": "1.13.0",
    "resource_type": "1.8.4",
    "resourcepath": "1.0.0",
    "result_verify_job": "1.12.0",
    "retrieve": "1.13.0",
    "search_immediately": "1.9.9",
    "search_incomplete": "1.9.9",
    "search_limited": "1.1.0",
    "search_successful": "1.9.9",
    "search_status": "1.12.0",
    "searchid_exists": "1.8.8",
    "session": "1.0.0",
    "size": "1.10.0",
    "submit_verify_job": "1.12.3",
    "tape_barcode": "1.8.0",
    "tape_exists": "1.8.0",
    "tape_id": "1.8.0",
    "tape_library": "1.12.7",
    "tape_status": "1.8.0",
    "tnsr": "1.12.4",
    "total_number_search_results": "1.5.6",
    "version": "1.1.0",
}
