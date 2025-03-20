import os

import pytest

from pyslk.utils import (
    _parse_dates,
    _parse_list_to_rows,
    _parse_sizes,
    _rows_to_dataframe,
)

test_dir = os.path.dirname((os.path.abspath(__file__)))


@pytest.fixture
def test_output():
    filename = os.path.join(test_dir, "test_dir_output.txt")
    with open(filename) as f:
        test_str = f.read()
    return test_str


@pytest.fixture
def test_output_recursive():
    filename = os.path.join(test_dir, "test_recursive_output.txt")
    with open(filename) as f:
        test_str = f.read()
    return test_str


@pytest.fixture
def test_output_wildcard():
    filename = os.path.join(test_dir, "wildcard_output.txt")
    with open(filename) as f:
        test_str = f.read()
    return test_str


def test_wildcard_output(test_output_wildcard):
    rows = _parse_list_to_rows(
        test_output_wildcard.splitlines(),
        "/arch/ch0636/remo-runs/065002/1960/e065002t*.tar",
    )
    print(rows)
    df = _rows_to_dataframe(rows)
    files = list(df.filename)
    expect = [
        "/arch/ch0636/remo-runs/065002/1960/e065002t196001.tar",
        "/arch/ch0636/remo-runs/065002/1960/e065002t196002.tar",
        "/arch/ch0636/remo-runs/065002/1960/e065002t196003.tar",
        "/arch/ch0636/remo-runs/065002/1960/e065002t196004.tar",
        "/arch/ch0636/remo-runs/065002/1960/e065002t196005.tar",
        "/arch/ch0636/remo-runs/065002/1960/e065002t196006.tar",
        "/arch/ch0636/remo-runs/065002/1960/e065002t196007.tar",
        "/arch/ch0636/remo-runs/065002/1960/e065002t196008.tar",
        "/arch/ch0636/remo-runs/065002/1960/e065002t196009.tar",
        "/arch/ch0636/remo-runs/065002/1960/e065002t196010.tar",
        "/arch/ch0636/remo-runs/065002/1960/e065002t196011.tar",
        "/arch/ch0636/remo-runs/065002/1960/e065002t196012.tar",
    ]
    assert files == expect

    # test single
    raw = "-rw-r--r--- stronglink  0               1.0G   21 Jan 2022 18:57 ingest_01_1\nFiles: 1\n\x1b[?25h"
    result = _parse_list_to_rows(raw.splitlines(), "/test/test3/ingest_01_1")
    expect = [
        [
            "-rw-r--r---",
            "stronglink",
            "0",
            "1.0G",
            "21",
            "Jan",
            "2022",
            "18:57",
            "/test/test3/ingest_01_1",
        ]
    ]
    assert result == expect


def test_parse_to_dataframe(test_output):
    rows = _parse_list_to_rows(test_output.split("\n"))
    df = _rows_to_dataframe(rows)
    assert df.loc[273].filename == "uu0808"


def test_parse_to_dataframe_recursive(test_output_recursive):
    rows = _parse_list_to_rows(test_output_recursive.split("\n"))
    df = _rows_to_dataframe(rows)
    df = _parse_sizes(df)
    df = _parse_dates(df)
    assert df.filesize.sum() == 92119300000000.0
