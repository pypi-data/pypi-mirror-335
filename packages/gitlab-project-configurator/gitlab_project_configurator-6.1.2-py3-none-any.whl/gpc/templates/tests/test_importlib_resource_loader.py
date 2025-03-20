# Third Party Libraries
from jinja2 import Environment
from jinja2 import select_autoescape

# Gitlab-Project-Configurator Modules
from gpc import version
from gpc.templates import ImportLibResourceLoader
from gpc.templates import load_template


# pylint: disable=duplicate-code


def test_list_templates():
    autoescape = select_autoescape(
        default_for_string=True,
        enabled_extensions=("html", "htm", "xml"),
    )
    env = Environment(  # nosec
        autoescape=autoescape, loader=ImportLibResourceLoader("gpc.templates")
    )
    lst = env.list_templates()
    assert lst
    assert "layout.html.j2" in lst


def test_load_with_importlib():
    tpl = load_template("report.html.j2")
    json_report = {
        "excluded": [],
        "projects_report": [
            {
                "project_name": "some/path/to/a/project",
                "status": "success",
                "rule": {"rule_name": "my_team_master_rule"},
                "updated": True,
                "diff": {
                    "members": {
                        "property_name": "members",
                        "differences": {
                            "some-other-user": {
                                "status": "added",
                                "before": None,
                                "after": {
                                    "name": "some-other-user",
                                    "role": "developers",
                                },
                            }
                        },
                    },
                    "protected_branches": {
                        "property_name": "protected_branches",
                        "differences": {
                            "toto*": {
                                "status": "updated",
                                "before": {
                                    "name": "toto*",
                                    "allowed_to_merge": [
                                        "maintainers",
                                        "gitlab-nestor-bot",
                                    ],
                                    "allowed_to_push": ["no one"],
                                },
                                "after": {
                                    "name": "toto*",
                                    "allowed_to_merge": [
                                        "maintainers",
                                        "some-other-user",
                                    ],
                                    "allowed_to_push": ["no one"],
                                },
                            }
                        },
                    },
                    "approvers": {
                        "property_name": "approvers",
                        "differences": {
                            "approvers": {
                                "status": "updated",
                                "before": {
                                    "name": "approvers",
                                    "approvals_before_merge": 1,
                                    "reset_approvals_on_push": False,
                                    "can_override_approvals_per_merge_request": True,
                                    "users": ["gitlab-nestor-bot", "some-user"],
                                },
                                "after": {
                                    "name": "approvers",
                                    "approvals_before_merge": 1,
                                    "reset_approvals_on_push": False,
                                    "can_override_approvals_per_merge_request": True,
                                    "users": ["some-user", "some-other-user"],
                                },
                            }
                        },
                    },
                    "jira": {
                        "property_name": "jira",
                        "differences": {
                            "jira": {
                                "before": {
                                    "name": "jira",
                                    "url": None,
                                    "username": None,
                                    "jira_issue_transition_id": None,
                                    "trigger_on_commit": "We can not get the value!",
                                    "password": "****",
                                },
                                "after": {
                                    "name": "jira",
                                    "url": "https://jira.server",
                                    "username": "dummy bot",
                                    "jira_issue_transition_id": 101,
                                    "trigger_on_commit": False,
                                    "warning": "/!\\ blabla.",
                                },
                                "action": "warning",
                            }
                        },
                    },
                    "project_badges": {
                        "property_name": "project_badges",
                        "differences": {
                            "unset-1": {
                                "status": "added",
                                "before": None,
                                "after": {
                                    "badge_id": "unset-1",
                                    "link_url": "http://fake.url/to/the/config/project",
                                    "image_url": "https://some.other/url",
                                },
                            }
                        },
                    },
                },
            }
        ],
        "groups_report": [
            {
                "status": "success",
                "rule": {
                    "rule_name": "group_config_variables",
                    "variables": [
                        {"name": "TEST_VAR1", "value": "test"},
                        {"name": "TEST_VAR2", "value": "test2"},
                        {"name": "TEST_VAR3", "value": "test3"},
                    ],
                    "variable_profiles": {
                        "COMMON_VARIABLES": [
                            {"name": "TEST_VAR", "value": "test", "protected": False}
                        ]
                    },
                },
                "updated": False,
                "changes": [
                    {
                        "property_name": "variables",
                        "differences": {
                            "TEST_VAR1": {
                                "status": "kept",
                                "before": {
                                    "name": "TEST_VAR1",
                                    "protected": False,
                                    "warning": "",
                                    "variable_type": "env_var",
                                    "masked": False,
                                    "value": "test",
                                },
                                "after": {
                                    "name": "TEST_VAR1",
                                    "protected": False,
                                    "warning": "",
                                    "variable_type": "env_var",
                                    "masked": False,
                                    "value": "test",
                                },
                            },
                            "TEST_VAR2": {
                                "status": "kept",
                                "before": {
                                    "name": "TEST_VAR2",
                                    "protected": False,
                                    "warning": "",
                                    "variable_type": "env_var",
                                    "masked": False,
                                    "value": "test2",
                                },
                                "after": {
                                    "name": "TEST_VAR2",
                                    "protected": False,
                                    "warning": "",
                                    "variable_type": "env_var",
                                    "masked": False,
                                    "value": "test2",
                                },
                            },
                            "TEST_VAR3": {
                                "status": "kept",
                                "before": {
                                    "name": "TEST_VAR3",
                                    "protected": False,
                                    "warning": "",
                                    "variable_type": "env_var",
                                    "masked": False,
                                    "value": "test3",
                                },
                                "after": {
                                    "name": "TEST_VAR3",
                                    "protected": False,
                                    "warning": "",
                                    "variable_type": "env_var",
                                    "masked": False,
                                    "value": "test3",
                                },
                            },
                        },
                    }
                ],
                "diff": {},
                "group_name": "swlabs/nestor/repo_test/gpc_tests",
            }
        ],
    }
    projects = [
        {
            "id": x["project_name"].replace("/", ""),
            "category": x["project_name"].rpartition("/")[0],
            "title": x["project_name"],
        }
        for x in json_report.get("projects_report", [])
    ]
    groups = [
        {
            "id": x["group_name"].replace("/", ""),
            "category": x["group_name"].rpartition("/")[0],
            "title": x["group_name"],
        }
        for x in json_report.get("groups_report", [])
    ]
    rendered = tpl.render(
        groups=groups, projects=projects, report=json_report, gpc_version=version()
    )
    print(rendered)
