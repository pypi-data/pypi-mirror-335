from typing import Any, Dict, List, Optional
from typer import Typer, Argument, Option
from git import Repo
from ghtc.utils import (
    get_tags,
    get_commits_between,
    render_template,
    get_reverted_commit,
)
from ghtc.models import (
    ChangelogLine,
    ChangelogEntryForATag,
    ConventionalCommitMessage,
    ConventionalCommitType,
    UNRELEASED_TAG_TIMESTAMP,
)
from ghtc.parser import parse
from ghtc.overrides import Overrides

app = Typer(add_completion=False)
ALL_TYPES = ", ".join([x.name.lower() for x in ConventionalCommitType])


@app.command()
def cli(
    repo_root: str = Argument(..., help="the fullpath to the git repository"),
    tags_regex: str = Option(
        "^v[0-9]", help="regex to select tags to show on changelog"
    ),
    starting_rev: str = Option(
        None,
        help="starting revision (if not set latest tag starting with "
        "ghtc_changelog_start if exists, else first git commit)",
    ),
    remove_duplicates_entries: bool = Option(
        True, help="if True, remove duplicate entries"
    ),
    unreleased: bool = Option(
        True, help="if True, add a section about unreleased changes"
    ),
    override_file: str = Option(
        ".ghtc_overrides.ini", help="the path/name of the 'commit overrides' file"
    ),
    include_type: List[str] = Option(
        [],
        help="include (only) given conventional types in changelog (can be used "
        "multiple times, all types by default), available types: %s" % ALL_TYPES,
    ),
    title: str = "CHANGELOG",
    unreleased_title: str = "[Unreleased]",
    debug: bool = Option(False, help="add debug values for each changelog entry"),
):
    overrides = Overrides(override_file)
    overrides.parse()
    repo = Repo(repo_root)
    previous_tag = starting_rev
    context: Dict[str, Any] = {
        "TITLE": title,
        "UNRELEASED_TAG_TIMESTAMP": UNRELEASED_TAG_TIMESTAMP,
        "TAGS": [],
    }
    tags = get_tags(repo, tags_regex)
    if len(include_type) == 0:
        # if include_type is empty, we consider we want all types
        included_cats = [x.name.lower() for x in list(ConventionalCommitType)]
    else:
        included_cats = [x.strip().lower() for x in include_type]
    if unreleased:
        tags.append(None)
    for tag in tags:
        if tag is None:
            tag_name = unreleased_title
            tag_date = UNRELEASED_TAG_TIMESTAMP
            rev = ""
        else:
            tag_name = tag.name
            tag_date = tag.object.authored_date
            rev = tag_name
        reverted_commits = []
        for commit in get_commits_between(repo, previous_tag, rev):
            reverted_commit = get_reverted_commit(commit)
            if reverted_commit is not None:
                reverted_commits.append(reverted_commit)
        lines: Dict[ConventionalCommitType, List[ChangelogLine]] = {}
        for commit in get_commits_between(repo, previous_tag, rev):
            if commit.hexsha in reverted_commits:
                continue
            msg: Optional[ConventionalCommitMessage] = None
            if commit.hexsha in overrides.commits:
                msg = overrides.commits[commit.hexsha]
                if msg is None:
                    # ignored message
                    continue
            else:
                msg = parse(commit.message)
            if msg is None:
                continue
            cat = msg.type
            if cat.name.lower() not in included_cats:
                continue
            cline = ChangelogLine(msg, commit.hexsha, commit.committed_date)
            if cat not in lines:
                lines[cat] = []
            if remove_duplicates_entries and cline in lines[cat]:
                continue
            lines[cat].insert(0, cline)
        entry = ChangelogEntryForATag(tag_name, tag_date, lines)
        if tag is not None or len(lines) > 0:
            context["TAGS"].append(entry)
        context["DEBUG"] = debug
        previous_tag = tag
    print(render_template(context))


def main():
    app()


if __name__ == "__main__":
    main()
