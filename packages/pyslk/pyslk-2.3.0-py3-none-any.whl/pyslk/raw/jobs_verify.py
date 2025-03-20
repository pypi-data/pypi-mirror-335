import inspect
import subprocess
from pathlib import Path
from typing import Union

from pyslk.constants import PYSLK_DEFAULT_NUMBER_RETRIES_NONMOD_CMDS, SLK_HELPERS
from pyslk.utils import run_slk, which

__all__ = [
    "result_verify_job_raw",
    "submit_verify_job_raw",
]


def submit_verify_job_raw(
    resources: Union[str, Path, list[str], list[Path], None] = None,
    resource_ids: Union[int, str, list[int], list[str], None] = None,
    search_id: Union[int, str, None] = None,
    search_query: Union[str, None] = None,
    json_input_file: Union[str, Path, None] = None,
    recursive: bool = False,
    resume_on_page: int = 1,
    results_per_page: int = -1,
    end_on_page: int = -1,
    save_mode: bool = False,
    verbose: bool = False,
    json: bool = False,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess, subprocess.Popen]:
    """
    submit a verify job

    :param resources: provide a list of resources over which the verify job should be run
    :type resources: `str` or `Path` or `list[str]` or `list[Path]` or `None`
    :param resource_ids: provide a list of ids of resources over which the verify job should be run
    :type resource_ids: `str` or `int` or `list[str]` or `list[int]` or `None`
    :param search_id: provide a search id pointing to files over which the verify job should be run
    :type search_id: `str` or `int` or `None`
    :param search_query: provide a search query to select files over which the verify job should be run
    :type search_query: `str` or `None`
    :param json_input_file: read a JSON file which contains payload of the verify job (admin users only)
    :type json_input_file: `str` or `Path`  or `None`
    :param recursive: iterate namespaces recursively
    :type recursive: `bool`
    :param resume_on_page: resume the command and start with search result page `resume_on_page`; internally, 1000
            search results are on one 'page' and fetched by one request; you do not necessarily have read permissions
            for all of these files
    :type resume_on_page: `int`
    :param results_per_page: number of search results requested per page
    :type results_per_page: `int`
    :param end_on_page: end with search result page `end_on_page`; internally, 1000 search results
            are on one 'page' and fetched by one request; you do not necessarily have read permissions for all of
            these files
    :type end_on_page: `int`
    :param save_mode: save mode suggested to be used in times of many timeouts; please do not regularly use this
            parameter; start one verify job per page of search results instead of one verify job for 50 pages of
            search results
    :type save_mode: `bool`
    :param verbose: verbose output
    :type verbose: `bool`
    :param json: print output as JSON
    :type json: `bool`
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :return: stdout of the slk call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK_HELPERS) is None:
        raise RuntimeError(f"pyslk: {SLK_HELPERS}: command not found")

    slk_call = SLK_HELPERS + " submit_verify_job"

    if resources is not None:
        if isinstance(resources, str) and resources != "":
            slk_call = slk_call + " " + resources
        elif isinstance(resources, list) and len(resources) > 0:
            if not all([isinstance(r, (str, Path)) for r in resources]):
                raise TypeError(
                    f"pyslk.{inspect.stack()[0][3]}: if argument 'resources' is of type 'list' its items need to be"
                    + "of type 'str' or Path-like but got type(s): "
                    + f"'{', '.join([type(r).__name__ for r in resources if not isinstance(r, (str, Path))])}'."
                )
            slk_call = slk_call + " " + " ".join([str(res) for res in resources])
        elif isinstance(resources, Path):
            slk_call = slk_call + " " + str(resources)
        else:
            raise TypeError(
                f'pyslk.{inspect.stack()[0][3]}: "resources" has to be of type "str", path-like or "list" but is '
                + f"{type(resources).__name__}"
            )
    if resource_ids is not None:
        if isinstance(resource_ids, str) and resource_ids != "":
            slk_call = slk_call + " --resource-ids " + resource_ids
        elif isinstance(resource_ids, int):
            slk_call = slk_call + " --resource-ids " + str(resource_ids)
        elif isinstance(resource_ids, list) and len(resources) > 0:
            if not all([isinstance(r, (str, int)) for r in resources]):
                raise TypeError(
                    f"pyslk.{inspect.stack()[0][3]}: if argument 'resource_ids' is of type 'list' its items need to be"
                    + "of type 'str' or 'int' but got type(s): "
                    + f"'{', '.join([type(r).__name__ for r in resources if not isinstance(r, (str, int))])}'."
                )
            slk_call = (
                slk_call
                + " --resource-ids "
                + " ".join([str(res) for res in resources])
            )
        else:
            raise TypeError(
                f'pyslk.{inspect.stack()[0][3]}: "resources" has to be of type "str", path-like or "list" but is '
                + f"{type(resources).__name__}"
            )

    # --search-id
    if search_id is not None:
        if isinstance(search_id, int):
            if search_id > 0:
                # correct search id provided
                slk_call = slk_call + " --search-id " + str(search_id)
            elif search_id < -2:
                # wrong search id provided
                raise ValueError(
                    f"pyslk.{inspect.stack()[0][3]}: argument 'search_id' needs to be > -2 but is {search_id} ('> 0': "
                    + "considered as normal search id; '0' and '-1': considered as None)."
                )
            # case search_id == 0 or -1: assume that it means the same as None
        elif isinstance(search_id, str):
            slk_call = slk_call + " --search-id " + search_id
        else:
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: 'search_id' has to be of type 'str' or 'int' but is "
                + f"{type(search_id).__name__}"
            )

    # --search-query
    if search_query is not None:
        if isinstance(search_query, str):
            slk_call = slk_call + " --search-query " + f"'{search_query}'"
        else:
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: 'search_query' has wrong type; need 'str' but got "
                + f"'{type(search_query).__name__}'"
            )

    # --infile
    if json_input_file is not None:
        if isinstance(json_input_file, (str, Path)):
            slk_call = slk_call + " --infile " + str(json_input_file)
        else:
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: 'json_input_file' has wrong type; need 'str' or 'Path' but got "
                + f"'{type(json_input_file).__name__}'"
            )

    # --resume-on-page
    if not isinstance(resume_on_page, int):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'resume_on_page' has wrong type; need 'int' but got "
            + f"'{type(resume_on_page).__name__}'"
        )
    if resume_on_page != 1:
        slk_call = slk_call + " --resume-on-page " + str(resume_on_page)

    # --results-per-page
    if not isinstance(results_per_page, int):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'results_per_page' has wrong type; need 'int' but got "
            + f"'{type(results_per_page).__name__}'"
        )
    if results_per_page not in [-1, 0, 1000]:
        slk_call = slk_call + " --results-per-page " + str(results_per_page)

    # --end-on-page
    if not isinstance(end_on_page, int):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'end_on_page' has wrong type; need 'int' but got "
            + f"'{type(end_on_page).__name__}'"
        )
    if end_on_page != -1:
        slk_call = slk_call + " --end-on-page " + str(end_on_page)

    # --save-mode
    if not isinstance(save_mode, bool):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'save_mode' has wrong type; need 'bool' but got "
            + f"'{type(save_mode).__name__}'"
        )
    if save_mode:
        slk_call = slk_call + " --save-mode"

    # --verbose
    if not isinstance(verbose, bool):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'verbose' has wrong type; need 'bool' but got "
            + f"'{type(verbose).__name__}'"
        )
    if verbose:
        slk_call = slk_call + " --verbose"

    # --json
    if not isinstance(json, bool):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'json' has wrong type; need 'bool' but got "
            + f"'{type(json).__name__}'"
        )
    if json:
        slk_call = slk_call + " --json"

    # --recursive
    if not isinstance(recursive, bool):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'recursive' has wrong type; need 'bool' but got "
            + f"'{type(recursive).__name__}'"
        )
    if recursive:
        slk_call = slk_call + " --recursive"

    if return_type == 0:
        return run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=0,
        )
    elif return_type == 1:
        return run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=0,
            handle_output=False,
        ).returncode
    elif return_type == 2:
        return run_slk(
            slk_call,
            inspect.stack()[0][3],
            retries_on_timeout=0,
            handle_output=False,
        )
    else:
        raise ValueError(
            f"pyslk.{inspect.stack()[0][3]}: argument 'return_type' needs to be 0, 1 or 2."
        )


# TODO: nice wrapper
def result_verify_job_raw(
    job_id: Union[int, str],
    header: bool = False,
    json: bool = False,
    json_no_source: bool = False,
    number_errors: bool = False,
    number_sources: bool = False,
    sources: bool = False,
    return_type: int = 0,
) -> Union[str, int, subprocess.CompletedProcess]:
    """prints result verification job information

    :param job_id: job id
    :type job_id: ``int`` or ``str``
    :param header: print header
    :type header: ``bool``
    :param json: print json
    :type json: ``bool``
    :param json_no_source: print json without source
    :type json_no_source: ``bool``
    :param number_errors: print number of errors
    :type number_errors: ``bool``
    :param number_sources: print number of sources
    :type number_sources: ``bool``
    :param sources: print sources
    :type sources: ``bool``
    :param return_type: select between 0 (== str output), 1 (== exit code), 2 (subprocess output)
    :type return_type: int
    :returns: stdout of the slk_helpers call
    :rtype: Union[str, int, subprocess.CompletedProcess]
    """
    if which(SLK_HELPERS) is None:
        raise RuntimeError(f"pyslk: {SLK_HELPERS}: command not found")

    slk_call = [SLK_HELPERS, "result_verify_job"]

    # job_id
    if isinstance(job_id, int):
        slk_call.append(str(job_id))
    elif isinstance(job_id, str):
        try:
            slk_call.append(str(int(job_id)))
        except ValueError:
            raise TypeError(
                f"pyslk.{inspect.stack()[0][3]}: 'job_id' cannot be processed; need 'str', which holds an integer "
                + f"number, or 'int' but got '{type(job_id).__name__}' with value '{job_id}'"
            )
    else:
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'job_id' has wrong type; need 'str' or 'int' but got "
            + f"'{type(job_id).__name__}'"
        )

    # --header
    if not isinstance(header, bool):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'header' has wrong type; need 'bool' but got "
            + f"'{type(header).__name__}'"
        )
    if header:
        slk_call.append("--header")

    # --json
    if not isinstance(json, bool):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'json' has wrong type; need 'bool' but got "
            + f"'{type(json).__name__}'"
        )
    if json:
        slk_call.append("--json")

    # --json-no-source
    if not isinstance(json_no_source, bool):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'json_no_source' has wrong type; need 'bool' but got "
            + f"'{type(json_no_source).__name__}'"
        )
    if json_no_source:
        slk_call.append("--json-no-source")

    # --number-errors
    if not isinstance(number_errors, bool):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'number_errors' has wrong type; need 'bool' but got "
            + f"'{type(number_errors).__name__}'"
        )
    if number_errors:
        slk_call.append("--number-errors")

    # --number-sources
    if not isinstance(number_sources, bool):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'number_sources' has wrong type; need 'bool' but got "
            + f"'{type(number_sources).__name__}'"
        )
    if number_sources:
        slk_call.append("--number-sources")

    # --sources
    if not isinstance(sources, bool):
        raise TypeError(
            f"pyslk.{inspect.stack()[0][3]}: 'sources' has wrong type; need 'bool' but got "
            + f"'{type(sources).__name__}'"
        )
    if sources:
        slk_call.append("--sources")

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
