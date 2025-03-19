from typing import List, Optional
import os
import jinja2
from git import Repo, Tag, Commit
import re

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


class TagNotFound(Exception):
    pass


def get_tags(repo: Repo, tag_regex: str) -> List[Tag]:
    compiled_pattern = re.compile(tag_regex)
    res = []
    for tag in repo.tags:
        if re.match(compiled_pattern, tag.name):
            res.append(tag)
    return sorted(res, key=lambda x: x.object.authored_date)


def get_first_commit(repo: Repo) -> Commit:
    return list(repo.iter_commits(max_parents=0))[0]


def get_commits_between(repo: Repo, rev1: str = "", rev2: str = "") -> List[Commit]:
    kwargs = {}
    first_commit = None
    if rev1 is None or rev1 == "":
        tmp_tags = get_tags(repo, "^ghtc_changelog_start")
        if len(tmp_tags) >= 1:
            tag1_name = tmp_tags[-1]
        else:
            first_commit = get_first_commit(repo)
            tag1_name = first_commit.hexsha
    else:
        tag1_name = rev1
    tag2_name = "HEAD" if rev2 is None or rev2 == "" else rev2
    kwargs["rev"] = f"{tag1_name}..{tag2_name}"
    tmp = list(repo.iter_commits(**kwargs))
    if first_commit is None:
        return tmp
    # we also include first commit in list
    return [first_commit] + tmp


def render_template(context, template_file: str = "") -> str:
    if template_file is not None and template_file != "":
        template_to_read = template_file
    else:
        template_to_read = f"{CURRENT_DIR}/CHANGELOG.md"
    with open(template_to_read, "r") as f:
        content = f.read()
    template = jinja2.Template(content)
    return template.render(context)


def get_reverted_commit(commit: Commit) -> Optional[str]:
    for tmp in commit.message.splitlines():
        line = tmp.strip()
        if line.startswith("This reverts commit "):
            sha = line.replace("This reverts commit ", "").split(".")[0]
            if len(sha) >= 40:
                return sha
    return None
