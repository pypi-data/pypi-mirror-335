import math
import os

import pytest

from pyslk.utils import _parse_list_to_rows, _parse_size

test_dir = os.path.dirname((os.path.abspath(__file__)))


@pytest.fixture
def test_output():
    filename = os.path.join(test_dir, "test_dir_output.txt")
    with open(filename) as f:
        test_str = f.read()
    return test_str


def test_parse_list_to_rows(test_output):
    rows = _parse_list_to_rows(test_output.split("\n"))
    assert rows[273][8] == "uu0808"


def test_parse_size():
    assert _parse_size("22B") == 22.0
    assert _parse_size("22M") == 22 * 1.0e6
    assert _parse_size("22.3M") == 22.3 * 1.0e6
    assert _parse_size("22.3G") == 22.3 * 1.0e9
    assert math.isnan(_parse_size("22.3X"))
    assert math.isnan(_parse_size(""))
