from os import path as op

import pytest

import pyslk as slk

from . import requires_slk, scratch

# once there is a test system ...
test_file = "test.txt"
arch_path = "/arch/ch0636/pyslk"


@pytest.fixture
def resource():
    with open(test_file, "w") as f:
        f.write("test content for pyslk")
    return test_file


@pytest.mark.new
@requires_slk
def test_with_slk(resource):
    # run slk commands once we have a test system
    out = slk.transfer.archive(resource=resource, dst_gns=arch_path)
    assert out == (["/arch/ch0636/pyslk/test.txt"], "Non-recursive Archive completed")

    path = op.join(arch_path, test_file)
    retr = slk.transfer.retrieve_improved(resources=path, destination=scratch)
    assert "SUCCESS" in retr
    assert "SUCCESS" in retr["SUCCESS"]
    assert path in retr["SUCCESS"]["SUCCESS"]
    assert "FILES" in retr
    assert path in retr["FILES"]


@requires_slk
def test_list():
    out = slk.list("/")
    assert "/arch" in out.filename.to_list()


@pytest.mark.new
@requires_slk
def test_retrieve():
    path = "/test/test3/ingest_01_1"
    # out = pyslk.transfer.retrieve.retrieve(path, scratch)
    out = slk.transfer.retrieve_improved(resources=path, destination=scratch)
    assert "SUCCESS" in out
    assert "SUCCESS" in out["SUCCESS"]
    assert path in out["SUCCESS"]["SUCCESS"]
    assert "FILES" in out
    assert path in out["FILES"]

    # retrieve
    path = ["/test/test3/ingest_01_1", "/test/test3/ingest_01_10"]
    # out = pyslk.transfer.retrieve.retrieve(path, scratch, group=False)
    out = slk.transfer.retrieve_improved(resources=path, destination=scratch)
    print(out)
    assert ("SUCCESS" in out) or ("SKIPPED" in out)
    assert ("SUCCESS" in out and "SUCCESS" in out["SUCCESS"]) or (
        "SKIPPED" in out and "SKIPPED_TARGET_EXISTS" in out["SKIPPED"]
    )
    assert ("SUCCESS" in out and path[0] in out["SUCCESS"]["SUCCESS"]) or (
        "SKIPPED" in out and path[0] in out["SKIPPED"]["SKIPPED_TARGET_EXISTS"]
    )
    # assert ('SUCCESS' in out and path[1] in out['SUCCESS']['SUCCESS']) or ('SKIPPED' in out and path[1] in out['SKIPPED']['SKIPPED_TARGET_EXISTS'])
    assert "FILES" in out
    assert path[0] in out["FILES"]
    # assert path[1] in out['FILES']

    # grouped retrieve
    # path = ["/test/test3/ingest_01_1", "/test/test3/ingest_01_10"]
    # out = slk.retrieve(path, scratch, group=True)
    # for o in out:
    #    assert o == ''
