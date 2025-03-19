# {{ TITLE|default("CHANGELOG") }}
{%
    set TYPE_MAPPINGS = {
        "OTHER": "Other",
        "BUILD": "Dev stuff",
        "CHORE": "Dev stuff",
        "STYLE": "Code style",
        "CI": "Continuous Integration",
        "REFACTOR": "Refactoring",
        "TEST": "Tests",
        "DOCS": "Documentation",
        "PERF": "Performances",
        "FIX": "Bug Fixes",
        "FEAT": "New Features"
    }
%}
{% for ENTRY_FOR_A_TAG in TAGS|sort(attribute="tag_timestamp", reverse=True) -%}
## {{ ENTRY_FOR_A_TAG.tag_name }}{% if ENTRY_FOR_A_TAG.tag_timestamp != UNRELEASED_TAG_TIMESTAMP %} ({{ ENTRY_FOR_A_TAG.tag_date }}){% endif %}

{% if ENTRY_FOR_A_TAG.lines_by_type|length == 0 -%}
- No interesting change

{% endif -%}
{% for CAT, LINES in ENTRY_FOR_A_TAG.lines_by_type.items()|sort(attribute='0.value', reverse=True) -%}
{% if LINES|length > 0 -%}
### {{ TYPE_MAPPINGS.get(CAT.name, CAT.name) }}

{% for LINE in LINES|sort(attribute='commit_timestamp', reverse=False) -%}
- {{ LINE.commit_message.description }}{% if DEBUG %} { commit_hash: {{LINE.commit_sha}}, commit_date: {{LINE.commit_date}} }{% endif %}
{% endfor %}
{% endif -%}
{% endfor -%}
{% endfor -%}
