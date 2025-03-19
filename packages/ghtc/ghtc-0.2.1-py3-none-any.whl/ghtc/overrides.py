from typing import Dict, Optional
import os
import re
from ghtc.models import ConventionalCommitMessage
from ghtc.parser import parse
import mflog

GIT_COMMIT_DELIMITER_REGEX = r"^\[([0-9a-f]{5,40})\]$"
GIT_COMMIT_DELIMITER_COMPILED_REGEX = re.compile(GIT_COMMIT_DELIMITER_REGEX)
LOGGER = mflog.get_logger("ghtc.overrides")


class Overrides:
    def __init__(self, path):
        self.path = path
        self.commits: Dict[str, Optional[ConventionalCommitMessage]] = {}

    def parse(self):
        if not os.path.isfile(self.path):
            return
        with open(self.path, "r") as f:
            commit: Optional[str] = None
            commit_message: Optional[str] = None
            for tmp in f.readlines():
                line = tmp.strip()
                if commit is None and len(line) == 0:
                    continue
                match = GIT_COMMIT_DELIMITER_COMPILED_REGEX.match(line)
                if match is None:
                    if commit is None:
                        LOGGER.warning("badly formatted overrides file => ignoring")
                        return False
                    if commit_message is None:
                        if len(line) > 0:
                            commit_message = line
                    else:
                        commit_message = commit_message + "\n" + line
                else:
                    if commit is not None:
                        self.commits[commit] = self._parse(commit, commit_message)
                    commit = match[1]
                    commit_message = None
            if commit is not None:
                self.commits[commit] = self._parse(commit, commit_message)
        return True

    def _parse(self, commit, commit_message) -> Optional[ConventionalCommitMessage]:
        res: Optional[ConventionalCommitMessage] = None
        if commit_message is not None:
            res = parse(commit_message)
            if res is None:
                LOGGER.warning(
                    f"can't parse overriden commit "
                    f"message for commit: {commit} => ignoring"
                )
        return res
