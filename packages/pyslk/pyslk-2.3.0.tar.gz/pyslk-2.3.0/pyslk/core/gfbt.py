import inspect
import json
import time
import warnings
from pathlib import Path
from typing import Union

from ..base import FileGroup, GroupCollection, ls, search
from ..constants import PYSLK_SEARCH_DELAY, PYSLK_WILDCARDS
from ..pyslk_exceptions import PySlkEmptyInputError
from ..raw import group_files_by_tape_raw, retrieve_raw
from .gen_queries import gen_file_query
from .resource_extras import resource_exists
from .storage import is_cached

__all__ = [
    "_check_input_gfbt",
    "_gen_group_collection",
    "_group_retrieve",
    "count_tapes",
    "count_tapes_with_multi_tape_files",
    "count_tapes_with_single_tape_files",
    "group_files_by_tape",
]


def group_files_by_tape(
    resource_path: Union[Path, str, list, set, None] = None,
    resource_ids: Union[str, list, set, int, None] = None,
    search_id: Union[str, int, None] = None,
    search_query: Union[str, None] = None,
    recursive: bool = False,
    max_tape_number_per_search: int = -1,
    run_search_query: bool = False,
    evaluate_regex_in_input: bool = False,
) -> list[dict]:
    """Group files by tape id.

    Group a list of files by their tape id. Has not all arguments of the `slk_helpers group_files_by_tape` cli call.
    Please us :py:meth:`pyslk.count_tapes` to count the number of tapes onto which files are stored on.

    :param resource_path: list of files or a namespaces with files that should be grouped.
    :type resource_path: ``str``, ``list``, ``Path``, ``set``
    :param resource_ids: list of resource ids to be searched for
    :type resource_ids: ``str`` or ``list`` or Path-like or None or ``set``
    :param search_id: id of a search
    :type search_id: ``int``, ``str``
    :param search_query: a search query
    :type search_query: ``str``
    :param recursive: do recursive search in the namespaces
    :type recursive: ``bool``
    :param max_tape_number_per_search: number of tapes per search; if '-1' => the parameter is not set
    :type max_tape_number_per_search: ``int``
    :param run_search_query: generate and run (a) search query strings instead of the lists of files per tape and print
            the search i, Default: False
    :type run_search_query: ``bool``
    :param evaluate_regex_in_input: expect that a regular expression in part of the input (file names) and evalute it
    :type evaluate_regex_in_input: bool
    :return: A list of dictionaries containing group and tape info.
    :rtype: ``list[dict]``

    .. seealso::
        * :py:meth:`~pyslk.count_tapes`
        * :py:meth:`~pyslk.group_files_by_tape_raw`

    .. rubric:: Examples

    .. code-block:: python

        >>> import pyslk as slk
        >>> slk.group_files_by_tape(["/test/test3/ingest_01_102", "/test/test3/ingest_01_339"])
        [{'id': -1,
          'location': 'cache',
          'label': '',
          'status': '',
          'file_count': 2,
          'files': ['/test/test3/ingest_01_102', '/test/test3/ingest_01_339'],
          'search_query': '{"$and":[{"path":{"$gte":"/test/test3","$max_depth":1}},
                            {"resources.name":{"$regex":"ingest_01_102|ingest_01_339"}}]}',
          'search_id': 416837}]
    """
    # check if input values are OK
    _check_input_gfbt(
        calling_function=inspect.stack()[0][3],
        resource_path=resource_path,
        resource_ids=resource_ids,
        search_id=search_id,
        search_query=search_query,
        recursive=recursive,
    )
    # only grouping by tape id / barcode makes sense, otherwise we have duplicated keys.
    output = group_files_by_tape_raw(
        resource_paths=resource_path,
        resource_ids=resource_ids,
        search_id=search_id,
        search_query=search_query,
        print_tape_barcode=True,
        recursive=recursive,
        json=True,
        gen_search_query=True,
        set_max_tape_number_per_search=max_tape_number_per_search,
        run_search_query=run_search_query,
        evaluate_regex_in_input=evaluate_regex_in_input,
    )
    return json.loads(output)


def _group_retrieve(
    resource: Union[str, Path, int, list],
    dest_dir: Union[str, Path],
    recursive: bool,
    delayed: bool = False,
    **kwargs,
) -> list:
    """
    Grouped retrieve

    Helper function used by :py:meth:`pyslk.retrieve`. Uses :py:meth:`pyslk.group_files_by_tape`.

    :param resource: a resource (path to it or resource id)
    :type resource: ``str`` or ``Path`` or ``int`` or ``list``
    :param dest_dir: destination directory
    :type dest_dir: ``str`` or ``Path``
    :param recursive: do recursive retrieval
    :type recursive: ``bool``
    :param delayed: do delayed retrieval
    :type delayed: ``bool``
    :param `**kwargs`: keyword args of :py:meth:`pyslk.retrieve`
    :return: a list
    :rtype: ``list``

    .. seealso::
        * :py:meth:`~pyslk.retrieve`
        * :py:meth:`~pyslk.group_files_by_tape`
    """

    if delayed is True:
        from dask import delayed as delay
    else:

        def delay(x):
            return x

    # determine whether we have a search id or a resource
    #  whereas a resource might be
    #    * a list of resources,
    #    * an expression with wildcards or
    #    * an individual resource represented as str or Path-like obj
    search_id: Union[int, None] = None
    # str with wildcards
    if isinstance(resource, str) and PYSLK_WILDCARDS in resource:
        # create file list and group them
        resource = list(ls(resource).filename)
    elif isinstance(resource, Path):
        # resource is a path => do nothing except for checking whether it exists
        if not resource_exists(resource):
            warnings.warn(
                f"pyslk.{inspect.stack()[0][3]}: resource does not exist: {str(resource)}"
            )
    elif isinstance(resource, list):
        # resource is a list => all items need to be string or Path-like
        wrong_type: list = [
            type(res).__name__ for res in resource if not isinstance(res, (str, Path))
        ]
        if len(wrong_type) > 0:
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: if 'resource' is a list then the list's items have to be of type "
                + f"'str' or Path-like; {len(wrong_type)} items are affected having the types "
                + f"{', '.join(set(wrong_type))}"
            )
        # check if all items of list exist
        not_exist: list = [res for res in resource if not resource_exists(res)]
        if len(not_exist) > 0:
            warnings.warn(
                f"pyslk.{inspect.stack()[0][3]}: some resources does not exist: "
                + ", ".join(not_exist)
            )
    elif isinstance(resource, int):
        # resource is a search id
        search_id = resource
        resource = None
    elif isinstance(resource, str):
        # resource can either be a resource or a search id
        try:
            search_id = int(resource)
            resource = None
        except ValueError:
            pass
        if resource is not None:
            # resource is a path => do nothing except for checking whether it exists
            if not resource_exists(resource):
                warnings.warn(
                    f"pyslk.{inspect.stack()[0][3]}: resource does not exist: "
                    + resource
                )
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'resource' has wrong type; need 'str', 'int' or 'Path' but "
            + f"got {type(resource).__name__}"
        )

    groups = group_files_by_tape(
        resource_path=resource,
        search_id=search_id,
        recursive=recursive,
        run_search_query=True,
        evaluate_regex_in_input=True,
    )

    # HERE WE HAVE TO WAIT?! Otherwise, the search_ids from the grouped
    # search queries will not be valid for a retrieve.
    if delayed is False:
        time.sleep(PYSLK_SEARCH_DELAY)

    # return grouped retrieves
    return [
        delay(retrieve_raw)(g["search_id"], dest_dir, recursive=recursive, **kwargs)
        for g in groups
    ]


def _gen_group_collection(
    resource_path: Union[
        str, Path, list[str], list[Path], set[str], set[Path], None
    ] = None,
    resource_ids: Union[str, list, set, int, None] = None,
    search_id: Union[str, int, None] = None,
    search_query: Union[str, None] = None,
    recursive: bool = False,
    max_tape_number_per_search: int = -1,
    split_recalls: bool = True,
    verbose: bool = False,
    evaluate_regex_in_input: bool = False,
) -> GroupCollection:
    """

    output if not details:
        {int: int}

        key: job_id
        value: job_status: -1 => running/queued; 0 => finished; >0 => error

    :param resource_path: list of files or a namespaces with files that should be recalled.
    :type resource_path: ``str``, ``list``, ``Path``, ``set``
    :param resource_ids: list of resource ids to be searched for
    :type resource_ids: ``str`` or ``list`` or Path-like or None or ``set``
    :param search_id: id of a search
    :type search_id: ``int``, ``str``
    :param search_query: a search query
    :type search_query: ``str``
    :param recursive: do recursive search in the namespaces
    :type recursive: ``bool``
    :param max_tape_number_per_search: number of tapes per search; if '-1' => the parameter is not set
    :type max_tape_number_per_search: ``int``
    :param split_recalls: run one recall per tape ...
    :type split_recalls: ``bool``
    :param verbose: verbose mode
    :type verbose: ``bool``
    :param evaluate_regex_in_input: expect that a regular expression in part of the input (file names) and evalute it
    :type evaluate_regex_in_input: bool
    :return:
    """
    # check if input values are OK
    _check_input_gfbt(
        calling_function=inspect.stack()[0][3],
        resource_path=resource_path,
        resource_ids=resource_ids,
        search_id=search_id,
        search_query=search_query,
        recursive=recursive,
    )

    # TODO: further implement 'verbose'

    if not isinstance(verbose, bool):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'verbose' has wrong type; need 'bool' but "
            + f"got {type(verbose).__name__}"
        )

    output: GroupCollection = GroupCollection()
    tape_group: dict

    if split_recalls:
        if verbose:
            print(f"pyslk.{inspect.stack()[0][3]}: split recalls")
        # ~~~~~~~~~~~~~~~~ SPLIT RECALL AND ... ~~~~~~~~~~~~~~~~
        tape_groups = group_files_by_tape(
            resource_path=resource_path,
            resource_ids=resource_ids,
            search_id=search_id,
            search_query=search_query,
            recursive=recursive,
            run_search_query=True,
            max_tape_number_per_search=max_tape_number_per_search,
            evaluate_regex_in_input=evaluate_regex_in_input,
        )
        if verbose:
            print(f"pyslk.{inspect.stack()[0][3]}: splitting recalls successful")
        if len(tape_groups) == 0:
            # ~~~~~~~~~~~~~~~~ ... NO GROUP ~~~~~~~~~~~~~~~~
            raise PySlkEmptyInputError(
                f"pyslk.{inspect.stack()[0][3]}: No content to recall"
            )
            # => error
        # consider each tape group as a job and add it to the JobCollection
        if verbose:
            print(
                f"pyslk.{inspect.stack()[0][3]}: request split into {len(tape_groups)} recalls"
            )
        for tape_group in tape_groups:
            output.add_group(FileGroup(tape_group))
    else:
        if verbose:
            print(f"pyslk.{inspect.stack()[0][3]}: not split recalls")
        tape_group = dict()
        # we need the search_id
        # * if search_query or resource_path are not None, search_id will be None
        # * if search_query and resource_path are None, search_id will not be None
        if search_query is not None:
            if verbose:
                print(
                    f"pyslk.{inspect.stack()[0][3]}: run search for provided search query"
                )
            search_id = search(search_query)
        elif resource_path is not None:
            if verbose:
                print(
                    f"pyslk.{inspect.stack()[0][3]}: run search for provided resource path"
                )
            # => run search ...
            search_query = gen_file_query(resource_path, recursive)
            search_id = search(search_query)
        if verbose:
            print(
                f"pyslk.{inspect.stack()[0][3]}: collect files from search id {search_id}"
            )
        # get file list
        files: list[str] = list(ls(search_id).filename)
        if verbose:
            print(f"pyslk.{inspect.stack()[0][3]}: files collected: {files}")
        # set values in group dict
        tape_group["search_query"] = search_query
        tape_group["search_id"] = search_id
        tape_group["files"] = files
        tape_group["file_count"] = len(files)
        if is_cached(search_id=search_id):
            tape_group["location"] = "cache"
        else:
            tape_group["location"] = "tape"
        # generate a FileGroup from this
        output.add_group(FileGroup(tape_group))
    # return GroupCollection
    return output


def _check_input_gfbt(
    calling_function: str,
    resource_path: Union[str, list, set, Path, None] = None,
    resource_ids: Union[str, list, set, int, None] = None,
    search_id: Union[str, int, None] = None,
    search_query: Union[str, None] = None,
    recursive: bool = False,
):
    """
    Check if input values are correct; if not, throw errors

    Thrown errors

    * PySlkException
    * TypeError
    * ValueError

    :param calling_function: name of the functions which calls this function
    :type calling_function: ``str``
    :param resource_path: a resource path (str or Path) or multiple resource paths (in a list)
    :type resource_path: ``str`` or ``path-like`` or ``list`` or ``set``
    :param resource_ids: list of resource ids to be searched for
    :type resource_ids: ``str`` or ``list`` or Path-like or None or ``set``
    :param search_id: id of a search
    :type search_id: ``int``, ``str``
    :param search_query: a search query
    :type search_query: ``str``
    :param recursive: set whether resource should be evaluated recursively or not
    :type recursive: ``bool``
    """
    # check consistency of input
    if (
        (resource_path is not None and search_id is not None)
        or (resource_path is not None and search_query is not None)
        or (search_id is not None and search_query is not None)
        or (resource_path is not None and resource_ids is not None)
        or (search_id is not None and resource_ids is not None)
        or (search_query is not None and resource_ids is not None)
    ):
        raise ValueError(
            f"pyslk.{calling_function}: only resource_path xor search_id xor search_query can be set (== only one)"
        )
    if (
        resource_path is None
        and search_id is None
        and search_query is None
        and resource_ids is None
    ):
        raise ValueError(
            f"pyslk.{calling_function}: either resource_path or search_id or search_query have to be set"
        )
    # make type checks: resource_path
    if resource_path is not None:
        if not isinstance(resource_path, (str, Path, list, set)):
            raise TypeError(
                f"pyslk.{calling_function}: wrong input type; need 'str', 'Path', 'list' or 'set'; got "
                + f"'{type(resource_path).__name__}'"
            )
        if isinstance(resource_path, (str, Path)):
            if not resource_exists(resource_path):
                raise FileNotFoundError(
                    f"pyslk.{calling_function}: resource does not exist {resource_path}"
                )
        else:
            # resource_path is a list
            non_exist: list = [
                rp for rp in set(resource_path) if not resource_exists(rp)
            ]
            if len(non_exist) > 0:
                raise FileNotFoundError(
                    f"pyslk.{calling_function}: one or more resources do not exist {', '.join(non_exist)}"
                )
    if search_id is not None:
        if not isinstance(search_id, (str, int)):
            raise TypeError(
                f"pyslk.{calling_function}: wrong input type; need 'int' or 'str'; got '{type(search_id).__name__}'"
            )
        if isinstance(search_id, str):
            try:
                search_id = int(search_id)
            except ValueError:
                raise ValueError(
                    f"pyslk.{calling_function}: got 'str' as input for 'search_id' but cannot convert it to "
                    + f"'int'; value is '{search_id}'"
                )
    if search_query is not None:
        if not isinstance(search_query, str):
            raise TypeError(
                f"pyslk.{calling_function}: wrong input type; need 'str'; got '{type(search_query).__name__}'"
            )
    if not isinstance(recursive, bool):
        raise TypeError(
            f"pyslk.{calling_function}: wrong input type; need 'bool'; got '{type(recursive).__name__}'"
        )
    # make type checks: resource_ids
    if resource_ids is not None:
        if not isinstance(resource_ids, (str, int, list)):
            raise TypeError(
                f"pyslk.{calling_function}: wrong input type; need 'str', 'int', 'list' or 'set'; got "
                + f"'{type(resource_ids).__name__}'"
            )
        if isinstance(resource_ids, (str, int)):
            if not resource_exists(resource_ids):
                raise FileNotFoundError(
                    f"pyslk.{calling_function}: resource does not exist {resource_ids}"
                )
        else:
            # resource_ids are a list
            non_exist: list = [
                rp for rp in set(resource_ids) if not resource_exists(rp)
            ]
            if len(non_exist) > 0:
                raise FileNotFoundError(
                    f"pyslk.{calling_function}: one or more resources do not exist {', '.join(non_exist)}"
                )


def count_tapes(
    resource_path: Union[str, list, set, Path, None] = None,
    resource_ids: Union[str, list, set, int, None] = None,
    search_id: Union[str, int, None] = None,
    search_query: Union[str, None] = None,
    recursive: bool = False,
    evaluate_regex_in_input: bool = False,
) -> dict[str, int]:
    """
    Count number of tapes onto which provided files are stored; distinguishes between multi-tape and single-tape files

    :param resource_path: a resource path (str or Path) or multiple resource paths (in a list)
    :type resource_path: ``str`` or ``path-like`` or ``list`` or ``set``
    :param resource_ids: list of resource ids to be searched for
    :type resource_ids: ``str`` or ``list`` or Path-like or None or ``set``
    :param search_id: id of a search
    :type search_id: ``int``, ``str``
    :param search_query: a search query
    :type search_query: ``str``
    :param recursive: set whether resource should be evaluated recursively or not
    :type recursive: ``bool``
    :param evaluate_regex_in_input: expect that a regular expression in part of the input (file names) and evalute it
    :type evaluate_regex_in_input: bool
    :return: dictionary containing the two tape counts
    :rtype: ``dict``

    .. seealso::
        * :py:meth:`~pyslk.group_files_by_tape`
        * :py:meth:`~pyslk.group_files_by_tape_raw`
    """
    # check if input values are OK
    _check_input_gfbt(
        calling_function=inspect.stack()[0][3],
        resource_path=resource_path,
        resource_ids=resource_ids,
        search_id=search_id,
        search_query=search_query,
        recursive=recursive,
    )
    output: dict = dict()
    # run group_files_by_tape
    raw_output = group_files_by_tape_raw(
        resource_paths=resource_path,
        resource_ids=resource_ids,
        search_id=search_id,
        search_query=search_query,
        recursive=recursive,
        count_tapes=True,
        evaluate_regex_in_input=evaluate_regex_in_input,
    ).split("\n")
    # look for output line with single-tape-files
    for i in raw_output:
        if "single-tape" in i:
            output["n_tapes__single_tape_files"] = int(i.split(" ")[0])
            break
    # look for output line with multi-tape-files
    for i in raw_output:
        if "multi-tape" in i:
            output["n_tapes__multi_tape_files"] = int(i.split(" ")[0])
            break
    # return dict
    return output


def count_tapes_with_single_tape_files(
    resource_path: Union[str, int, Path, None] = None,
    resource_ids: Union[str, list, int, None] = None,
    search_id: Union[str, int, None] = None,
    search_query: Union[str, None] = None,
) -> int:
    """
    Count number of tapes onto which provided files are stored which are not split onto multiple tapes per file

    Internally calls :py:meth:`pyslk.count_tapes`

    :param resource_path: a resource path
    :type resource_path: ``str`` or ``int`` or ``path-like``
    :param resource_ids: list of resource ids to be searched for
    :type resource_ids: str or list or Path-like or None
    :param search_id: id of a search
    :type search_id: ``int`` or ``str``
    :param search_query: a search query
    :type search_query: ``str``
    :return: number of tapes
    :rtype: ``int``

    .. seealso::
        * :py:meth:`~pyslk.count_tapes`
        * :py:meth:`~pyslk.count_tapes_with_multi_tape_files`
    """
    return count_tapes(
        resource_path=resource_path,
        resource_ids=resource_ids,
        search_id=search_id,
        search_query=search_query,
    )["n_tapes__single_tape_files"]


def count_tapes_with_multi_tape_files(
    resource_path: Union[str, int, Path, None] = None,
    resource_ids: Union[str, list, int, None] = None,
    search_id: Union[str, int, None] = None,
    search_query: Union[str, None] = None,
) -> int:
    """
    Count number of tapes onto which provided files are stored which are split onto multiple tapes per file

    Internally calls :py:meth:`pyslk.count_tapes`

    :param resource_path: a resource path
    :type resource_path: ``str`` or ``int`` or ``path-like``
    :param resource_ids: list of resource ids to be searched for
    :type resource_ids: str or list or Path-like or None
    :param search_id: id of a search
    :type search_id: ``int`` or ``str``
    :param search_query: a search query
    :type search_query: ``str``
    :return: number of tapes
    :rtype: ``int``

    .. seealso::
        * :py:meth:`~pyslk.count_tapes`
        * :py:meth:`~pyslk.count_tapes_with_single_tape_files`
    """
    return count_tapes(
        resource_path=resource_path,
        resource_ids=resource_ids,
        search_id=search_id,
        search_query=search_query,
    )["n_tapes__multi_tape_files"]
