import tempfile
import os
from mfutil import get_unique_hexa_identifier
from ghtc.overrides import Overrides
from ghtc.models import ConventionalCommitType

PARSE1 = """
[123456]
feat: this is a test

Close: #456

[aaaaaa]
fix: this is another test

[bbbbbb]


"""


def make_tmp_filepath(content: str):
    path = os.path.join(tempfile.gettempdir(), get_unique_hexa_identifier())
    with open(path, "w") as f:
        f.write(content)
    return path


def test_not_found():
    x = Overrides("/foo/bar/not_found")
    x.parse()
    assert len(x.commits) == 0


def test_parse1():
    path = make_tmp_filepath(PARSE1)
    x = Overrides(path)
    x.parse()
    assert len(x.commits) == 3
    assert x.commits["123456"].type == ConventionalCommitType.FEAT
    assert x.commits["123456"].description == "this is a test"
    assert x.commits["123456"].footers[0].key == "Close"
    assert x.commits["123456"].footers[0].value == "#456"
    assert x.commits["aaaaaa"].type == ConventionalCommitType.FIX
    assert x.commits["aaaaaa"].description == "this is another test"
    assert x.commits["bbbbbb"] is None
    os.unlink(path)
