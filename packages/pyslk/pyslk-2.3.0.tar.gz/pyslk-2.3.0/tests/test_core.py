import datetime
import re
from pathlib import Path

import pytest

from pyslk import (
    StatusJob,
    is_job_finished,
    is_job_successful,
)
from pyslk import list as ls
from pyslk.base.login import (
    expiration_date,
    hostname,
    session,
    valid_session,
    valid_token,
)
from pyslk.base.resource_path import get_resource_path
from pyslk.base.searching import search, total_number_search_results
from pyslk.base.versioning import cli_versions, version_slk, version_slk_helpers
from pyslk.core.gfbt import count_tapes, group_files_by_tape
from pyslk.core.resource import (
    get_resource_id,
    get_resource_permissions,
    get_resource_size,
    has_no_flag_partial,
    has_no_flag_partial_details,
)
from pyslk.core.resource_extras import (
    get_resource_type,
    is_file,
    is_namespace,
    resource_exists,
)
from pyslk.core.storage import (
    get_tape_barcode,
    get_tape_id,
    is_cached,
    is_cached_details,
    tape_exists,
    tape_status,
)
from pyslk.jobs import (
    get_job_status,
    is_job_processing,
    is_job_queued,
    job_exists,
    job_queue,
)
from pyslk.pyslk_exceptions import PySlkException


class TestBasics:
    def test_valid_session(self):
        assert valid_session()

    def test_valid_token(self):
        assert valid_token()

    def test_hostname(self):
        output = hostname()
        assert isinstance(output, str)
        assert len(output) > 0

    def test_expiration_date(self):
        output = expiration_date()
        now = datetime.datetime.now(tz=output.tzinfo)
        in_one_year = datetime.datetime.now(tz=output.tzinfo)
        in_one_year = in_one_year.replace(year=in_one_year.year + 1)
        assert isinstance(output, datetime.datetime)
        assert output > now
        assert output < in_one_year

    def test_session(self):
        output = session()
        now = datetime.datetime.now(tz=output.tzinfo)
        in_one_year = datetime.datetime.now(tz=output.tzinfo)
        in_one_year = in_one_year.replace(year=in_one_year.year + 1)
        assert isinstance(output, datetime.datetime)
        assert output > now
        assert output < in_one_year


class TestBasicOperations:
    def test_mkdir_rename_move_delete(self):
        pass

    def test_mkdir_archive_rename_move_detele(self):
        pass


class TestVersionFunctions:
    def test_version_slk_helpers(self):
        slk_helpers_version = re.findall(
            "[0-9]+[.][0-9]+[.][0-9]+", version_slk_helpers()
        )
        assert len(slk_helpers_version) == 1

    def test_version_slk(self):
        slk_version = re.findall("[0-9]+[.][0-9]+[.][0-9]+", version_slk())
        assert len(slk_version) == 1

    @pytest.mark.parametrize(
        "test_input,in_output,not_output",
        [
            (None, ["slk", "slk_helpers"], list()),
            ("slk", ["slk"], ["slk_helpers"]),
            ("slk_helpers", ["slk_helpers"], ["slk"]),
            ("slk", ["slk"], ["slk_helpers"]),
            (["slk"], ["slk"], ["slk_helpers"]),
            (["slk", "slk_helpers"], ["slk", "slk_helpers"], list()),
            (("slk", "slk_helpers"), ["slk", "slk_helpers"], list()),
        ],
    )
    def test_cli_versions(self, test_input, in_output, not_output):
        slk_versions = cli_versions(test_input)
        for i in in_output:
            assert i in slk_versions
            slk_version = re.findall("[0-9]+[.][0-9]+[.][0-9]+", version_slk())
            assert len(slk_version) == 1
        for i in not_output:
            assert i not in slk_versions


class TestListFunctions:
    def test_ls_basic(self):
        # path for test
        resource_path = "/arch/bm0146/k204221/iow"
        # things to compare
        columns = [
            "permissions",
            "owner",
            "group",
            "filesize",
            "date",
            "time",
            "filename",
        ]
        n_rows = 23
        files = [
            "/arch/bm0146/k204221/iow/INDEX.txt",
            "/arch/bm0146/k204221/iow/iow_data2_001.tar",
            "/arch/bm0146/k204221/iow/iow_data2_002.tar",
            "/arch/bm0146/k204221/iow/iow_data2_003.tar",
            "/arch/bm0146/k204221/iow/iow_data2_004.tar",
            "/arch/bm0146/k204221/iow/iow_data2_005.tar",
            "/arch/bm0146/k204221/iow/iow_data2_006.tar",
            "/arch/bm0146/k204221/iow/iow_data3_001.tar",
            "/arch/bm0146/k204221/iow/iow_data3_002.tar",
            "/arch/bm0146/k204221/iow/iow_data4_001.tar",
            "/arch/bm0146/k204221/iow/iow_data4_002.tar",
            "/arch/bm0146/k204221/iow/iow_data5_001.tar",
            "/arch/bm0146/k204221/iow/iow_data5_002.tar",
            "/arch/bm0146/k204221/iow/iow_data5_003.tar",
            "/arch/bm0146/k204221/iow/iow_data5_004.tar",
            "/arch/bm0146/k204221/iow/iow_data5_005.tar",
            "/arch/bm0146/k204221/iow/iow_data5_006.tar",
            "/arch/bm0146/k204221/iow/iow_data_001.tar",
            "/arch/bm0146/k204221/iow/iow_data_002.tar",
            "/arch/bm0146/k204221/iow/iow_data_003.tar",
            "/arch/bm0146/k204221/iow/iow_data_004.tar",
            "/arch/bm0146/k204221/iow/iow_data_005.tar",
            "/arch/bm0146/k204221/iow/iow_data_006.tar",
        ]

        # call function
        output = ls(resource_path)

        # compare output
        assert list(output.columns) == columns
        assert len(output) == n_rows
        for f in files:
            assert f in list(output["filename"])
        for f in list(output["filename"]):
            assert f in files


class TestResourceFunctions:
    @pytest.mark.parametrize(
        "test_input,expected_output,expected_error",
        [
            ("/arch/bm0146/k204221/iow", True, None),
            (Path("/arch/bm0146/k204221/iow"), True, None),
            ("/arch/bm0146/k204221/not_exists", False, None),
            ("/arch/bm0146/k204221/iow/INDEX.txt", True, None),
            ("/arch/bm0146/k204221/iow/not_exists.txt", False, None),
            (49058658013, True, None),
            ("49058658013", True, None),
            (49058705497, True, None),
            (999999999999999, False, None),
            (3.2, None, TypeError),
            (["/arch/bm0146/k204221/iow"], None, TypeError),
        ],
    )
    def test_resource_exists(self, test_input, expected_output, expected_error):
        if expected_error is None:
            # expect no error
            assert resource_exists(test_input) == expected_output
        else:
            # expect error
            with pytest.raises(expected_error):
                resource_exists(test_input)

    @pytest.mark.parametrize(
        "test_input,expected_output,expected_error",
        [
            ("/arch/bm0146/k204221/iow", None, None),
            (Path("/arch/bm0146/k204221/iow"), None, TypeError),
            ("/arch/bm0146/k204221/not_exists", None, None),
            ("/arch/bm0146/k204221/iow/INDEX.txt", None, None),
            ("/arch/bm0146/k204221/iow/not_exists.txt", None, None),
            (49058658013, Path("/arch/bm0146/k204221/iow"), None),
            ("49058658013", Path("/arch/bm0146/k204221/iow"), None),
            (49058705497, Path("/arch/bm0146/k204221/iow/INDEX.txt"), None),
            (999999999999999, None, None),
            (3.2, None, TypeError),
            (["/arch/bm0146/k204221/iow"], None, TypeError),
        ],
    )
    def test_get_resource_path(self, test_input, expected_output, expected_error):
        if expected_error is None:
            # expect no error
            assert get_resource_path(test_input) == expected_output
        else:
            # expect error
            with pytest.raises(expected_error):
                get_resource_path(test_input)

    @pytest.mark.parametrize(
        "test_input,expected_output,expected_error",
        [
            ("/arch/bm0146/k204221/iow", 49058658013, None),
            (Path("/arch/bm0146/k204221/iow"), 49058658013, None),
            ("/arch/bm0146/k204221/not_exists", None, None),
            ("/arch/bm0146/k204221/iow/INDEX.txt", 49058705497, None),
            ("/arch/bm0146/k204221/iow/not_exists.txt", None, None),
            (49058658013, None, TypeError),
            ("49058658013", None, None),
            (49058705497, None, TypeError),
            (999999999999999, None, TypeError),
            (3.2, None, TypeError),
            (["/arch/bm0146/k204221/iow"], None, TypeError),
        ],
    )
    def test_get_resource_id(self, test_input, expected_output, expected_error):
        if expected_error is None:
            # expect no error
            assert get_resource_id(test_input) == expected_output
        else:
            # expect error
            with pytest.raises(expected_error):
                get_resource_id(test_input)

    @pytest.mark.parametrize(
        "test_input,expected_output,expected_error",
        [
            ("/arch/bm0146/k204221/iow", "NAMESPACE", None),
            (Path("/arch/bm0146/k204221/iow"), "NAMESPACE", None),
            ("/arch/bm0146/k204221/not_exists", None, None),
            ("/arch/bm0146/k204221/iow/INDEX.txt", "FILE", None),
            ("/arch/bm0146/k204221/iow/not_exists.txt", None, None),
            (49058658013, "NAMESPACE", None),
            ("49058658013", "NAMESPACE", None),
            (49058705497, "FILE", None),
            (999999999999999, None, None),
            (3.2, None, TypeError),
            (["/arch/bm0146/k204221/iow"], None, TypeError),
        ],
    )
    def test_get_resource_type(self, test_input, expected_output, expected_error):
        if expected_error is None:
            # expect no error
            assert get_resource_type(test_input) == expected_output
        else:
            # expect error
            with pytest.raises(expected_error):
                get_resource_type(test_input)

    @pytest.mark.parametrize(
        "test_input,expected_output,expected_error",
        [
            ("/arch/bm0146/k204221/iow", 0, None),
            (Path("/arch/bm0146/k204221/iow"), 0, None),
            ("/arch/bm0146/k204221/not_exists", None, None),
            ("/arch/bm0146/k204221/iow/INDEX.txt", 1268945, None),
            ("/arch/bm0146/k204221/iow/not_exists.txt", None, None),
            (49058658013, 0, None),
            ("49058658013", 0, None),
            (49058705497, 1268945, None),
            (999999999999999, None, None),
            (3.2, None, TypeError),
            (["/arch/bm0146/k204221/iow"], None, TypeError),
        ],
    )
    def test_get_resource_size(self, test_input, expected_output, expected_error):
        if expected_error is None:
            # expect no error
            assert get_resource_size(test_input) == expected_output
        else:
            # expect error
            with pytest.raises(expected_error):
                get_resource_size(test_input)

    @pytest.mark.parametrize(
        "test_input,expected_output,expected_error",
        [
            ("/arch/bm0146/k204221/iow", False, None),
            (Path("/arch/bm0146/k204221/iow"), False, None),
            ("/arch/bm0146/k204221/not_exists", None, None),
            ("/arch/bm0146/k204221/iow/INDEX.txt", True, None),
            ("/arch/bm0146/k204221/iow/not_exists.txt", None, None),
            (49058658013, False, None),
            ("49058658013", False, None),
            (49058705497, True, None),
            (999999999999999, None, None),
            (3.2, None, TypeError),
            (["/arch/bm0146/k204221/iow"], None, TypeError),
        ],
    )
    def test_is_file(self, test_input, expected_output, expected_error):
        if expected_error is None:
            # expect no error
            assert is_file(test_input) == expected_output
        else:
            # expect error
            with pytest.raises(expected_error):
                is_file(test_input)

    @pytest.mark.parametrize(
        "test_input,expected_output,expected_error",
        [
            ("/arch/bm0146/k204221/iow", True, None),
            (Path("/arch/bm0146/k204221/iow"), True, None),
            ("/arch/bm0146/k204221/not_exists", None, None),
            ("/arch/bm0146/k204221/iow/INDEX.txt", False, None),
            ("/arch/bm0146/k204221/iow/not_exists.txt", None, None),
            (49058658013, True, None),
            ("49058658013", True, None),
            (49058705497, False, None),
            (999999999999999, None, None),
            (3.2, None, TypeError),
            (["/arch/bm0146/k204221/iow"], None, TypeError),
        ],
    )
    def test_is_namespace(self, test_input, expected_output, expected_error):
        if expected_error is None:
            # expect no error
            assert is_namespace(test_input) == expected_output
        else:
            # expect error
            with pytest.raises(expected_error):
                is_namespace(test_input)

    @pytest.mark.parametrize(
        "test_input,expected_output,expected_error",
        [
            (
                "/arch/bm0146/k204221/iow",
                "^[r-][w-][x-][r-][w-][x-][r-][w-][x-]$",
                None,
            ),
            (
                Path("/arch/bm0146/k204221/iow"),
                "^[r-][w-][x-][r-][w-][x-][r-][w-][x-]$",
                None,
            ),
            ("/arch/bm0146/k204221/not_exists", None, None),
            (
                "/arch/bm0146/k204221/iow/INDEX.txt",
                "^[r-][w-][x-][r-][w-][x-][r-][w-][x-]$",
                None,
            ),
            ("/arch/bm0146/k204221/iow/not_exists.txt", None, None),
            (49058658013, "^[r-][w-][x-][r-][w-][x-][r-][w-][x-]$", None),
            ("49058658013", "^[r-][w-][x-][r-][w-][x-][r-][w-][x-]$", None),
            (49058705497, "^[r-][w-][x-][r-][w-][x-][r-][w-][x-]$", None),
            (999999999999999, None, None),
            (3.2, None, TypeError),
            (["/arch/bm0146/k204221/iow"], None, TypeError),
        ],
    )
    def test_get_resource_permissions_text(
        self, test_input, expected_output, expected_error
    ):
        if expected_error is None:
            # expect no error
            output = get_resource_permissions(test_input)
            if expected_output is None:
                assert output == expected_output
            else:
                assert len(re.findall(expected_output, output)) == 1
        else:
            # expect error
            with pytest.raises(expected_error):
                get_resource_permissions(test_input)

    @pytest.mark.parametrize(
        "test_input,expected_output,expected_error",
        [
            ("/arch/bm0146/k204221/iow", "^[01234567]{3}$", None),
            (Path("/arch/bm0146/k204221/iow"), "^[01234567]{3}$", None),
            ("/arch/bm0146/k204221/not_exists", None, None),
            ("/arch/bm0146/k204221/iow/INDEX.txt", "^[01234567]{3}$", None),
            ("/arch/bm0146/k204221/iow/not_exists.txt", None, None),
            (49058658013, "^[01234567]{3}$", None),
            ("49058658013", "^[01234567]{3}$", None),
            (49058705497, "^[01234567]{3}$", None),
            (999999999999999, None, None),
            (3.2, None, TypeError),
            (["/arch/bm0146/k204221/iow"], None, TypeError),
        ],
    )
    def test_get_resource_permissions_octal(
        self, test_input, expected_output, expected_error
    ):
        if expected_error is None:
            # expect no error
            output = get_resource_permissions(test_input, as_octal_number=True)
            if expected_output is None:
                assert output == expected_output
            else:
                assert isinstance(output, str)
                assert len(re.findall(expected_output, output)) == 1
        else:
            # expect error
            with pytest.raises(expected_error):
                get_resource_permissions(test_input)


class TestTapeFunctions:
    @pytest.mark.parametrize(
        "test_input,expected_output,expected_error",
        [
            ("M24361M8", 136343, None),
            ("M24361M1", None, None),
            (12345, None, TypeError),
        ],
    )
    def test_get_tape_id(self, test_input, expected_output, expected_error):
        if expected_error is None:
            # expect no error
            assert get_tape_id(test_input) == expected_output
        else:
            # expect error
            with pytest.raises(expected_error):
                get_tape_id(test_input)

    @pytest.mark.parametrize(
        "test_input,expected_output,expected_error",
        [
            (136343, "M24361M8", None),
            (99999999, None, None),
            ("M24361M8", None, TypeError),
        ],
    )
    def test_get_tape_barcode(self, test_input, expected_output, expected_error):
        if expected_error is None:
            # expect no error
            assert get_tape_barcode(test_input) == expected_output
        else:
            # expect error
            with pytest.raises(expected_error):
                get_tape_barcode(test_input)

    @pytest.mark.parametrize(
        "test_input,expected_output,expected_error",
        [
            ("M24361M8", True, None),
            ("M24361M1", False, None),
            (136343, True, None),
            (99999999, False, None),
            (list("M24361M8"), None, TypeError),
        ],
    )
    def test_tape_exists(self, test_input, expected_output, expected_error):
        if expected_error is None:
            # expect no error
            assert tape_exists(test_input) == expected_output
        else:
            # expect error
            with pytest.raises(expected_error):
                tape_exists(test_input)

    @pytest.mark.parametrize(
        "test_input,expected_output,expected_error",
        [
            ("M24361M8", "AVAILABLE", None),
            ("M24361M1", None, None),
            (136343, "AVAILABLE", None),
            (99999999, None, None),
            (list("M24361M8"), None, TypeError),
        ],
    )
    def test_tape_status(self, test_input, expected_output, expected_error):
        if expected_error is None:
            # expect no error
            assert tape_status(test_input) == expected_output
        else:
            # expect error
            with pytest.raises(expected_error):
                tape_status(test_input)


class TestJobFunctions:
    @pytest.mark.parametrize(
        "test_input,expected_output,expected_error",
        [
            (133874, True, None),
            (133873, True, None),
            (99999999, False, None),
            ("abc", None, TypeError),
        ],
    )
    def test_job_exists(self, test_input, expected_output, expected_error):
        if expected_error is None:
            # expect no error
            assert job_exists(test_input) == expected_output
        else:
            # expect error
            with pytest.raises(expected_error):
                job_exists(test_input)

    @pytest.mark.parametrize(
        "test_input,expected_output,expected_error",
        [
            (133874, StatusJob("FAILED"), None),
            (133873, StatusJob("SUCCESSFUL"), None),
            (99999999, None, None),
            ("abc", None, TypeError),
        ],
    )
    def test_job_status(self, test_input, expected_output, expected_error):
        if expected_error is None:
            # expect no error
            assert get_job_status(test_input) == expected_output
        else:
            # expect error
            with pytest.raises(expected_error):
                get_job_status(test_input)

    @pytest.mark.parametrize(
        "test_input,expected_output,expected_error",
        [
            (133874, False, None),
            (133873, False, None),
            (99999999, None, None),
            ("abc", None, TypeError),
        ],
    )
    def test_is_job_queued(self, test_input, expected_output, expected_error):
        if expected_error is None:
            # expect no error
            assert is_job_queued(test_input) == expected_output
        else:
            # expect error
            with pytest.raises(expected_error):
                is_job_queued(test_input)

    @pytest.mark.parametrize(
        "test_input,expected_output,expected_error",
        [
            (133874, False, None),
            (133873, False, None),
            (99999999, None, None),
            ("abc", None, TypeError),
        ],
    )
    def test_is_job_processing(self, test_input, expected_output, expected_error):
        if expected_error is None:
            # expect no error
            assert is_job_processing(test_input) == expected_output
        else:
            # expect error
            with pytest.raises(expected_error):
                is_job_processing(test_input)

    @pytest.mark.parametrize(
        "test_input,expected_output,expected_error",
        [
            (133874, True, None),
            (133873, True, None),
            (99999999, None, None),
            ("abc", None, TypeError),
        ],
    )
    def test_is_job_finished(self, test_input, expected_output, expected_error):
        if expected_error is None:
            # expect no error
            assert is_job_finished(test_input) == expected_output
        else:
            # expect error
            with pytest.raises(expected_error):
                is_job_finished(test_input)

    @pytest.mark.parametrize(
        "test_input,expected_output,expected_error",
        [
            (133874, False, None),
            (133873, True, None),
            (99999999, None, None),
            ("abc", None, TypeError),
        ],
    )
    def test_is_job_successful(self, test_input, expected_output, expected_error):
        if expected_error is None:
            # expect no error
            assert is_job_successful(test_input) == expected_output
        else:
            # expect error
            with pytest.raises(expected_error):
                is_job_successful(test_input)

    def test_job_queue(self):
        assert job_queue() is not None


class TestGFBT:
    # @pytest.mark.new
    @pytest.mark.parametrize(
        "test_input,expected_error",
        [
            (("/arch/bm0146/k204221/iow", None, None), None),
            ((None, None, None), ValueError),
            (("/arch/bm0146/k204221/iow", 3, None), ValueError),
            (
                (
                    "/arch/bm0146/k204221/iow",
                    None,
                    '{"path":{"$gte":"/arch/bm0146/k204221/iow"}}',
                ),
                ValueError,
            ),
            ((None, 3, '{"path":{"$gte":"/arch/bm0146/k204221/iow"}}'), ValueError),
            ((1, None, None), TypeError),
            ((None, "abc", None), ValueError),
            ((None, None, 3), TypeError),
            (("abc", None, None), FileNotFoundError),
        ],
    )
    # comment on test: ((None, "abc", None), ValueError),
    #   We throw ValueError and no TypeError because we accept strings for this
    #   argument and try to convert them to int. If the argument was "4", the
    #   would be not error.
    def test_count_tapes_0(self, test_input, expected_error):
        if expected_error is None:
            # expect no error; test whether it works at all
            count_tapes(
                resource_path=test_input[0],
                search_id=test_input[1],
                search_query=test_input[2],
                recursive=True,
            )
            assert True
        else:
            # expect error
            with pytest.raises(expected_error):
                count_tapes(
                    resource_path=test_input[0],
                    search_id=test_input[1],
                    search_query=test_input[2],
                    recursive=True,
                )

    @pytest.mark.parametrize(
        "test_input,expected_output,expected_error",
        [
            ("/arch/bm0146/k204221/iow", (12, 0), None),
            ("/arch/bm0146/k204221/iow/iow_data2_001.tar", (1, 0), None),
            (Path("/arch/bm0146/k204221/iow"), (12, 0), None),
            ("/arch/bm0146/k204221/iow/INDEX.txt", (0, 0), None),
            (
                [
                    "/arch/bm0146/k204221/iow/iow_data_001.tar",
                    "/arch/bm0146/k204221/iow/iow_data2_002.tar",
                    "/arch/bm0146/k204221/iow/iow_data5_002.tar",
                ],
                (2, 0),
                None,
            ),
            (
                [
                    "/arch/bm0146/k204221/iow/iow_data_006.tar",
                    "/arch/bm0146/k204221/iow/iow_data5_006.tar",
                    "/arch/bm0146/k204221/iow/iow_data5_002.tar",
                ],
                (2, 0),
                None,
            ),
            ({"abc": 4}, None, TypeError),
        ],
    )
    def test_count_tapes_1(self, test_input, expected_output, expected_error):
        if expected_error is None:
            # expect no error
            output_dict = count_tapes(resource_path=test_input, recursive=True)
            if expected_output[0] == 12:
                # in case that some files were recalled for other tests
                assert (
                    output_dict.get("n_tapes__single_tape_files", None)
                    <= expected_output[0]
                ) and (
                    output_dict.get("n_tapes__single_tape_files", None)
                    >= (expected_output[0] - 2)
                )
            else:
                assert (
                    output_dict.get("n_tapes__single_tape_files", None)
                    == expected_output[0]
                )
            assert (
                output_dict.get("n_tapes__multi_tape_files", None) == expected_output[1]
            )
        else:
            # expect error
            with pytest.raises(expected_error):
                count_tapes(test_input, recursive=True)

    @pytest.mark.parametrize(
        "test_input,expected_output,expected_error",
        [
            ('{"path":{"$gte":"/arch/bm0146/k204221/iow"}}', (12, 0), None),
            (
                '{"$and":[{"path":{"$gte":"/arch/bm0146/k204221/iow"}},'
                + '{"resources.name":{"$regex":"iow_data2_001.tar"}}]}',
                (1, 0),
                None,
            ),
            (
                '{"$and":[{"path":{"$gte":"/arch/bm0146/k204221/iow"}},'
                + '{"resources.name":{"$regex":"INDEX.txt"}}]}',
                (0, 0),
                None,
            ),
            (
                '{"$and":[{"path":{"$gte":"/arch/bm0146/k204221/iow"}},'
                + '{"resources.name":'
                + '{"$regex":"iow_data2_001.tar|iow_data2_002.tar|iow_data5_002.tar"}}]}',
                (3, 0),
                None,
            ),
            (
                '{"$and":[{"path":{"$gte":"/arch/bm0146/k204221/iow"}},'
                + '{"resources.name":'
                + '{"$regex":"iow_data_006.tar|iow_data5_006.tar|iow_data5_002.tar"}}]}',
                (2, 0),
                None,
            ),
            ((1), None, TypeError),
        ],
    )
    def test_count_tapes_2(self, test_input, expected_output, expected_error):
        if expected_error is None:
            # expect no error
            # run with search query
            output_dict = count_tapes(search_query=test_input, recursive=True)
            if expected_output[0] == 12:
                # in case that some files were recalled for other tests
                assert (
                    output_dict.get("n_tapes__single_tape_files", None)
                    <= expected_output[0]
                ) and (
                    output_dict.get("n_tapes__single_tape_files", None)
                    >= (expected_output[0] - 2)
                )
            else:
                assert (
                    output_dict.get("n_tapes__single_tape_files", None)
                    == expected_output[0]
                )
            assert (
                output_dict.get("n_tapes__multi_tape_files", None) == expected_output[1]
            )
            # perform search and run with search id
            search_id = search(test_input)
            output_dict = count_tapes(search_id=search_id, recursive=True)
            if expected_output[0] == 12:
                # in case that some files were recalled for other tests
                assert (
                    output_dict.get("n_tapes__single_tape_files", None)
                    <= expected_output[0]
                ) and (
                    output_dict.get("n_tapes__single_tape_files", None)
                    >= (expected_output[0] - 2)
                )
            else:
                assert (
                    output_dict.get("n_tapes__single_tape_files", None)
                    == expected_output[0]
                )
            assert (
                output_dict.get("n_tapes__multi_tape_files", None) == expected_output[1]
            )
        else:
            # expect error
            with pytest.raises(expected_error):
                count_tapes(resource_path=test_input, recursive=True)

    # @pytest.mark.new
    @pytest.mark.parametrize(
        "test_input,expected_output,expected_error",
        [
            (("/arch/bm0146/k204221/iow3", None, None), (3, 0), None),
            ((Path("/arch/bm0146/k204221/iow3"), None, None), (3, 0), None),
            (("/arch/bm0146/k204221/not_exists", None, None), None, FileNotFoundError),
            (
                (
                    "/arch/bm0146/k204221/iow3/ocean_day3d_phoswam_v04_ist_2006.nc",
                    None,
                    None,
                ),
                (1, 0),
                None,
            ),
            (("/arch/bm0146/k204221/iow/INDEX.txt", None, None), (0, 0), None),
            (
                ("/arch/bm0146/k204221/iow3/not_exists.txt", None, None),
                None,
                FileNotFoundError,
            ),
            (
                (None, None, '{"path": {"$gte": "/arch/bm0146/k204221/iow3"}}'),
                (3, 0),
                None,
            ),
            ((None, 923792, None), (3, 0), None),
            ((None, "923792", None), (3, 0), None),
            (
                (
                    None,
                    None,
                    '{"$and": [{"path": {"$gte": "/arch/bd1022/b309073/Res"}}, '
                    + '{"resources.name": {"$regex": "[12][09][09]._(tracer_gp|vaxtra)"}}]}',
                ),
                (82, 13),
                None,
            ),
            ((None, 1.1, None), None, TypeError),
            ((None, None, 123456), None, TypeError),
            ((None, 451086, None), None, PySlkException),
            ((["/arch/bm0146/k204221/iow3"], None, None), (3, 0), None),
            ((12345, None, None), None, TypeError),
        ],
    )
    def test_group_files_by_tape_count(
        self, test_input, expected_output, expected_error
    ):
        if expected_error is None:
            # expect no error
            output = count_tapes(
                resource_path=test_input[0],
                search_id=test_input[1],
                search_query=test_input[2],
                recursive=True,
            )
            assert "n_tapes__single_tape_files" in output
            assert "n_tapes__multi_tape_files" in output
            assert output["n_tapes__single_tape_files"] == expected_output[0]
            assert output["n_tapes__multi_tape_files"] == expected_output[1]
        else:
            # expect error
            with pytest.raises(expected_error):
                count_tapes(
                    resource_path=test_input[0],
                    search_id=test_input[1],
                    search_query=test_input[2],
                    recursive=True,
                )

    # @pytest.mark.new
    @pytest.mark.parametrize(
        "test_input,expected_output,expected_error",
        [
            (("/arch/bm0146/k204221/iow3", None, None), (3, "B09384L5"), None),
            ((Path("/arch/bm0146/k204221/iow3"), None, None), (3, "B09384L5"), None),
            (("/arch/bm0146/k204221/not_exists", None, None), None, FileNotFoundError),
            (
                (
                    "/arch/bm0146/k204221/iow3/ocean_day3d_phoswam_v04_ist_2006.nc",
                    None,
                    None,
                ),
                (1, "B09398L5"),
                None,
            ),
            (
                ("/arch/bm0146/k204221/iow3/not_exists.txt", None, None),
                None,
                FileNotFoundError,
            ),
            (
                (None, None, '{"path": {"$gte": "/arch/bm0146/k204221/iow3"}}'),
                (3, "B09384L5"),
                None,
            ),
            ((None, 923792, None), (3, "B09384L5"), None),
            ((None, "923792", None), (3, "B09384L5"), None),
            (
                (
                    None,
                    None,
                    '{"$and": [{"path": {"$gte": "/arch/bd1022/b309073/Res"}}, '
                    + '{"resources.name": {"$regex": "[12][09][09]._(tracer_gp|vaxtra)"}}]}',
                ),
                (83, "M10397M8"),
                None,
            ),
            ((None, 1.1, None), None, TypeError),
            ((None, None, 123456), None, TypeError),
            ((None, 451086, None), None, PySlkException),
            ((["/arch/bm0146/k204221/iow3"], None, None), (3, "B09384L5"), None),
            ((12345, None, None), None, TypeError),
        ],
    )
    def test_group_files_by_tape_details(
        self, test_input, expected_output, expected_error
    ):
        expected_keys = [
            "barcode",
            "description",
            "file_count",
            "files",
            "id",
            "location",
            "search_query",
            "status",
        ]
        if expected_error is None:
            # expect no error
            output = group_files_by_tape(
                resource_path=test_input[0],
                search_id=test_input[1],
                search_query=test_input[2],
                recursive=True,
            )
            assert len(output) == expected_output[0]
            assert all([key in tape for key in expected_keys for tape in output])
            assert any(
                [tape.get("barcode", None) == expected_output[1] for tape in output]
            )
        else:
            # expect error
            with pytest.raises(expected_error):
                group_files_by_tape(
                    resource_path=test_input[0],
                    search_id=test_input[1],
                    search_query=test_input[2],
                    recursive=True,
                )


# {"path":{"$gte":"/arch/bm0146/k204221/iow"}}


class TestStorageInfoFunctions:
    @pytest.mark.parametrize(
        "test_input,expected_output,expected_error",
        [
            ("/arch/bm0146/k204221/iow", True, None),
            (Path("/arch/bm0146/k204221/iow"), True, None),
            ("/arch/bm0146/k204221/not_exists", None, None),
            ("/arch/bm0146/k204221/iow/INDEX.txt", True, None),
            ("/arch/bm0146/k204221/iow/not_exists.txt", None, None),
            (49058658013, True, None),
            ("49058658013", True, None),
            (49058705497, True, None),
            (999999999999999, None, None),
            (3.2, None, TypeError),
            (["/arch/bm0146/k204221/iow"], True, None),
        ],
    )
    def test_has_no_flag_partial(self, test_input, expected_output, expected_error):
        if expected_error is None:
            # expect no error
            assert has_no_flag_partial(test_input) == expected_output
        else:
            # expect error
            with pytest.raises(expected_error):
                has_no_flag_partial(test_input)

    @pytest.mark.parametrize(
        "test_input,expected_output,expected_error",
        [
            ("/arch/bm0146/k204221/iow", True, None),
            (Path("/arch/bm0146/k204221/iow"), True, None),
            ("/arch/bm0146/k204221/not_exists", None, None),
            ("/arch/bm0146/k204221/iow/INDEX.txt", True, None),
            ("/arch/bm0146/k204221/iow/not_exists.txt", None, None),
            (49058658013, True, None),
            ("49058658013", True, None),
            (49058705497, True, None),
            (999999999999999, None, None),
            (3.2, None, TypeError),
            (["/arch/bm0146/k204221/iow"], True, None),
        ],
    )
    def test_has_no_flag_partial_details(
        self, test_input, expected_output, expected_error
    ):
        if expected_error is None:
            # expect no error
            output = has_no_flag_partial_details(test_input)
            if expected_output is None:
                assert output == expected_output
            else:
                assert isinstance(output, dict)
                assert "no_flag_partial" in output
                assert "flag_partial" in output
                assert (
                    Path("/arch/bm0146/k204221/iow/INDEX.txt")
                    in output["no_flag_partial"]
                )
        else:
            # expect error
            with pytest.raises(expected_error):
                has_no_flag_partial_details(test_input)

    @pytest.mark.parametrize(
        "test_input,expected_output,expected_error",
        [
            ("/arch/bm0146/k204221/iow", False, None),
            (Path("/arch/bm0146/k204221/iow"), False, None),
            ("/arch/bm0146/k204221/not_exists", None, None),
            ("/arch/bm0146/k204221/iow/INDEX.txt", True, None),
            ("/arch/bm0146/k204221/iow/iow_data_006.tar", False, None),
            ("/arch/bm0146/k204221/iow/not_exists.txt", None, None),
            (49058658013, False, None),
            ("49058658013", False, None),
            (49058705497, True, None),
            (999999999999999, None, None),
            (3.2, None, TypeError),
            (["/arch/bm0146/k204221/iow"], False, None),
        ],
    )
    def test_is_cached(self, test_input, expected_output, expected_error):
        if expected_error is None:
            # expect no error
            assert is_cached(test_input) == expected_output
        else:
            # expect error
            with pytest.raises(expected_error):
                is_cached(test_input)

    # will fail due to issue #40 in the slk_helpers
    @pytest.mark.xfail
    @pytest.mark.parametrize(
        "test_input,expected_output,expected_error",
        [(49058658013, False, None), ("49058658013", False, None)],
    )
    def test_is_cached_fail(self, test_input, expected_output, expected_error):
        if expected_error is None:
            # expect no error
            assert is_cached(test_input) == expected_output
        else:
            # expect error
            with pytest.raises(expected_error):
                is_cached(test_input)

    @pytest.mark.parametrize(
        "test_input,expected_output,check_files,expected_error",
        [
            ("/arch/bm0146/k204221/iow", True, (True, True), None),
            (Path("/arch/bm0146/k204221/iow"), True, (True, True), None),
            ("/arch/bm0146/k204221/not_exists", None, (False, False), None),
            ("/arch/bm0146/k204221/iow/INDEX.txt", True, (True, False), None),
            ("/arch/bm0146/k204221/iow/iow_data_006.tar", False, (False, True), None),
            ("/arch/bm0146/k204221/iow/not_exists.txt", None, (False, False), None),
            (49058658013, True, (True, True), None),
            ("49058658013", True, (True, True), None),
            (49058705497, True, (True, False), None),
            (999999999999999, None, (False, False), None),
            (3.2, None, (False, False), TypeError),
            (["/arch/bm0146/k204221/iow"], True, (True, True), None),
        ],
    )
    def test_is_cached_details(
        self, test_input, expected_output, check_files, expected_error
    ):
        if expected_error is None:
            # expect no error
            output = is_cached_details(test_input)
            if expected_output is None:
                assert output == expected_output
            else:
                print(output)
                assert isinstance(output, dict)
                assert "cached" in output
                assert "not_cached" in output
                if check_files[0]:
                    assert (
                        Path("/arch/bm0146/k204221/iow/INDEX.txt") in output["cached"]
                    )
                if check_files[1]:
                    assert (
                        Path("/arch/bm0146/k204221/iow/iow_data_006.tar")
                        in output["not_cached"]
                    )
                # assert "/arch/bm0146/k204221/iow/INDEX.txt" in [str(out) for out in output["cached"]]
                # assert "/arch/bm0146/k204221/iow/iow_data_006.tar" in [str(out) for out in output["not_cached"]]
        else:
            # expect error
            with pytest.raises(expected_error):
                is_cached_details(test_input)


class TestSearch:
    @pytest.mark.parametrize(
        "test_input,expected_output,expected_error",
        [
            ('{"path": {"$gte": "/arch/bm0146/k204221"}}}', True, None),
            (123456, False, TypeError),
            ('{"$gte": "/arch/bm0146/k204221/cera_test"}}', False, PySlkException),
            (
                '{"path": {"$gte": "/arch/bm0146/k204221/abcdefgh"}}}',
                False,
                PySlkException,
            ),
        ],
    )
    def test_search_basic(self, test_input, expected_output, expected_error):
        if expected_error is None:
            # expect no error
            search_id_matches = re.findall("^[0-9]{1,7}$", str(search(test_input)))
            assert len(search_id_matches) == 1
        else:
            # expect error
            with pytest.raises(expected_error):
                search(test_input)

    @pytest.mark.parametrize(
        "test_input,expected_output,expected_error",
        [
            ("451901", 3, None),
            (451901, 3, None),
            (451900, 4, None),
            ("abc", None, ValueError),
            (1.2, None, TypeError),
            (99999999, None, None),
        ],
    )
    def test_total_number_search_results(
        self, test_input, expected_output, expected_error
    ):
        if expected_error is None:
            # expect no error
            assert total_number_search_results(test_input) == expected_output
        else:
            # expect error
            with pytest.raises(expected_error):
                total_number_search_results(test_input)


class TestChModGGrpOwn:
    def test_chgrp(self):
        # import pyslk
        # pyslk.chgrp("/arch/bm0146/k204221/iow", recursive=True, group="ka1209")
        # pyslk.chgrp("/arch/bm0146/k204221/iow", recursive=True, group="bm0146")
        # pyslk.chgrp("/arch/bm0146/k204221/iow", recursive=True, group="ka1209")
        # pyslk.chgrp("/arch/bm0146/k204221/iow", recursive=True, group=1076)
        pass

    def test_chown(self):
        # import pyslk
        # pyslk.chown("/arch/bm0146/k204221/iow", recursive=True, owner="k202147")
        # pyslk.chown("/arch/bm0146/k204221/iow", recursive=True, owner="k204221")
        # pyslk.chown("/arch/bm0146/k204221/iow", recursive=True, owner=200533)
        # pyslk.chown("/arch/bm0146/k204221/iow", recursive=True, owner=25301)
        pass
