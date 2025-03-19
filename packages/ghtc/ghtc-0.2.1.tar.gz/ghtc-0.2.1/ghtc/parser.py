from typing import Optional, List, Dict
import re
from ghtc.models import (
    ConventionalCommitType,
    ConventionalCommitFooter,
    ConventionalCommitMessage,
)


TYPE_MAPPINGS: Dict[str, ConventionalCommitType] = {
    "feat": ConventionalCommitType.FEAT,
    "fix": ConventionalCommitType.FIX,
    "build": ConventionalCommitType.BUILD,
    "chore": ConventionalCommitType.CHORE,
    "ci": ConventionalCommitType.CI,
    "docs": ConventionalCommitType.DOCS,
    "doc": ConventionalCommitType.DOCS,
    "style": ConventionalCommitType.STYLE,
    "refactor": ConventionalCommitType.REFACTOR,
    "perf": ConventionalCommitType.PERF,
    "perfs": ConventionalCommitType.PERF,
    "test": ConventionalCommitType.TEST,
    "tests": ConventionalCommitType.TEST,
}
TITLE_REGEX = r"^([a-zA-Z0-9_-]+)(!{0,1})(\([a-zA-Z0-9_-]*\)){0,1}(!{0,1}): (.*)$"
TITLE_COMPILED_REGEX = re.compile(TITLE_REGEX)
FOOTER_REGEX1 = r"^([a-zA-Z0-9_-]+): (.*)$"
FOOTER_COMPILED_REGEX1 = re.compile(FOOTER_REGEX1)
FOOTER_REGEX2 = r"^([a-zA-Z0-9_-]+) #(.*)$"
FOOTER_COMPILED_REGEX2 = re.compile(FOOTER_REGEX2)
BREAKING_CHANGE_FOOTER_REGEX = r"^BREAKING[- ]CHANGE: (.*)$"
BREAKING_CHANGE_FOOTER_COMPILED_REGEX = re.compile(BREAKING_CHANGE_FOOTER_REGEX)


def type_string_to_commit_type(type_str: str) -> ConventionalCommitType:
    if type_str not in TYPE_MAPPINGS:
        return ConventionalCommitType.OTHER
    return TYPE_MAPPINGS[type_str]


def parse(commit_message: str) -> Optional[ConventionalCommitMessage]:
    if not commit_message:
        return None
    lines = commit_message.splitlines()
    first_line = lines[0]
    match = TITLE_COMPILED_REGEX.match(first_line)
    if match is None:
        return None
    type_str = match[1].lower()
    breaking = False
    if match[2] or match[4]:
        breaking = True
    scope = None
    if match[3]:
        scope = match[3].lower()[1:-1]
    description = match[5]
    body = None
    footers: List[ConventionalCommitFooter] = []
    if len(lines) > 1 and lines[1] == "":
        for line in lines[1:]:
            if not line:
                continue
            tmp1 = FOOTER_COMPILED_REGEX1.match(line)
            tmp2 = FOOTER_COMPILED_REGEX2.match(line)
            tmp3 = BREAKING_CHANGE_FOOTER_COMPILED_REGEX.match(line)
            if len(footers) == 0 and tmp1 is None and tmp2 is None and tmp3 is None:
                if body is None:
                    body = f"{line}"
                else:
                    body += f"\n{line}"
            else:
                if tmp3 is not None:
                    breaking = True
                    footers.append(ConventionalCommitFooter("BREAKING CHANGE", tmp3[1]))
                elif tmp1 is not None:
                    footers.append(ConventionalCommitFooter(tmp1[1], tmp1[2]))
                elif tmp2 is not None:
                    footers.append(ConventionalCommitFooter(tmp2[1], tmp2[2]))
    return ConventionalCommitMessage(
        type=type_string_to_commit_type(type_str),
        scope=scope,
        body=body,
        footers=footers,
        description=description,
        breaking=breaking,
    )
