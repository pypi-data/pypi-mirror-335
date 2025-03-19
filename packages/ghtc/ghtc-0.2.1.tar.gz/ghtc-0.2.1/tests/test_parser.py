from ghtc.parser import parse, ConventionalCommitType


MSG1 = """feat: allow provided config object to extend other configs

BREAKING CHANGE: `extends` key in config file is now used for extending other config files
"""

MSG2 = """refactor!: drop support for Node 6"""

MSG3 = """refactor!: drop support for Node 6

BREAKING CHANGE: refactor to use JavaScript features not available in Node 6.
"""

MSG4 = """docs: correct spelling of CHANGELOG"""

MSG5 = """feat(lang): add polish language"""

MSG6 = """fix: correct minor typos in code

see the issue for details

on typos fixed.

Reviewed-by: Z
Refs #133
"""


def test_valid_messages():
    msg = parse(MSG1)
    assert msg.type == ConventionalCommitType.FEAT
    assert msg.breaking
    assert msg.body is None
    assert msg.scope is None
    assert msg.description == \
        "allow provided config object to extend other configs"
    assert len(msg.footers) == 1
    assert msg.footers[0].key == "BREAKING CHANGE"
    assert msg.footers[0].value == (
        "`extends` key in config file is now used for extending other config files"
    )
    msg = parse(MSG2)
    assert msg.type == ConventionalCommitType.REFACTOR
    assert msg.breaking
    assert msg.body is None
    assert msg.scope is None
    assert msg.description == "drop support for Node 6"
    assert len(msg.footers) == 0
    msg = parse(MSG3)
    assert msg.type == ConventionalCommitType.REFACTOR
    assert msg.breaking
    assert msg.body is None
    assert msg.scope is None
    assert msg.description == "drop support for Node 6"
    assert len(msg.footers) == 1
    assert msg.footers[0].key == "BREAKING CHANGE"
    assert msg.footers[0].value == (
        "refactor to use JavaScript features not available in Node 6."
    )
    msg = parse(MSG4)
    assert msg.type == ConventionalCommitType.DOCS
    assert msg.breaking is False
    assert msg.body is None
    assert msg.scope is None
    assert msg.description == "correct spelling of CHANGELOG"
    assert len(msg.footers) == 0
    msg = parse(MSG5)
    assert msg.type == ConventionalCommitType.FEAT
    assert msg.breaking is False
    assert msg.body is None
    assert msg.scope == "lang"
    assert msg.description == "add polish language"
    assert len(msg.footers) == 0
    msg = parse(MSG6)
    assert msg.type == ConventionalCommitType.FIX
    assert msg.breaking is False
    assert msg.body == "see the issue for details\non typos fixed."
    assert msg.scope is None
    assert msg.description == "correct minor typos in code"
    assert len(msg.footers) == 2
    assert msg.footers[0].key == "Reviewed-by"
    assert msg.footers[0].value == "Z"
    assert msg.footers[1].key == "Refs"
    assert msg.footers[1].value == "133"
