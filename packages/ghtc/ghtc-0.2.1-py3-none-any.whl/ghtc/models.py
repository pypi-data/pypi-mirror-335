from typing import Optional, List, Dict
import enum
import time
from dataclasses import dataclass, field

UNRELEASED_TAG_TIMESTAMP = 9999999999


class ConventionalCommitType(enum.Enum):
    OTHER = 0
    BUILD = 1
    CHORE = 2
    STYLE = 3
    CI = 4
    REFACTOR = 5
    TEST = 6
    DOCS = 7
    PERF = 8
    FIX = 9
    FEAT = 10


@dataclass(frozen=True)
class ConventionalCommitFooter:
    key: str
    value: str


@dataclass(frozen=True, unsafe_hash=True)
class ConventionalCommitMessage:
    type: ConventionalCommitType
    description: str
    breaking: bool
    scope: Optional[str]
    body: Optional[str]
    footers: List[ConventionalCommitFooter]


@dataclass(frozen=True)
class ChangelogLine:
    commit_message: ConventionalCommitMessage
    commit_sha: str
    commit_timestamp: int
    commit_date: str = field(init=False)

    def __post_init__(self):
        object.__setattr__(
            self,
            "commit_date",
            time.strftime("%Y-%m-%d", time.gmtime(self.commit_timestamp)),
        )  # because frozen=True, we have to use this ugly __setattr__


@dataclass(frozen=True)
class ChangelogEntryForATag:
    tag_name: str
    tag_timestamp: int
    lines_by_type: Dict[ConventionalCommitType, List[ChangelogLine]]
    tag_date: str = field(init=False)

    def __post_init__(self):
        object.__setattr__(
            self, "tag_date", time.strftime("%Y-%m-%d", time.gmtime(self.tag_timestamp))
        )  # because frozen=True, we have to use this ugly __setattr__
