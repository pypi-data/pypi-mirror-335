"""
test_update protected branch/tag
----------------------------------
"""

# Gitlab-Project-Configurator Modules
# Gitlab-Project-Configurator Modules# Gitlab-Project-Configurator Modules
from gpc.changes_converter import FieldBean
from gpc.changes_converter import PropertyBean
from gpc.general_executor import generate_event


# pylint: disable=redefined-outer-name, unused-argument, protected-access, no-member, duplicate-code
# pylint: disable=too-many-locals


def test_converter_factory(mocker):
    diffs = {
        "ci_git_shallow_clone": {
            "property_name": "ci_git_shallow_clone",
            "differences": {"before": 30, "after": 20},
        },
        "permissions": {
            "property_name": "permissions",
            "differences": {
                "before": {
                    "visibility": "private",
                    "request_access_enabled": False,
                    "wiki_access_level": "disabled",
                    "issues_access_level": "disabled",
                    "snippets_access_level": "disabled",
                    "lfs_enabled": False,
                    "builds_access_level": "disabled",
                },
                "after": {
                    "visibility": "internal",
                    "request_access_enabled": True,
                    "wiki_access_level": "disabled",
                    "issues_access_level": "disabled",
                    "snippets_access_level": "disabled",
                    "lfs_enabled": False,
                    "builds_access_level": "disabled",
                },
                "action": "updated",
            },
        },
        "mergerequests": {
            "property_name": "mergerequests",
            "differences": {
                "before": {
                    "only_allow_merge_if_all_discussions_are_resolved": True,
                    "only_allow_merge_if_pipeline_succeeds": True,
                    "resolve_outdated_diff_discussions": False,
                    "printing_merge_request_link_enabled": True,
                    "merge_method": "ff",
                },
                "after": {
                    "only_allow_merge_if_all_discussions_are_resolved": True,
                    "only_allow_merge_if_pipeline_succeeds": False,
                    "resolve_outdated_diff_discussions": False,
                    "printing_merge_request_link_enabled": True,
                    "merge_method": "ff",
                },
                "action": "updated",
            },
        },
        "protected_branches": {
            "property_name": "protected_branches",
            "differences": {
                "toto": {
                    "status": "removed",
                    "before": {
                        "name": "toto",
                        "allowed_to_merge": [
                            "maintainers",
                            "gitlab-nestor-integ-useless",
                        ],
                        "allowed_to_push": ["no one"],
                    },
                    "after": None,
                },
                "tototi*": {
                    "status": "added",
                    "before": None,
                    "after": {
                        "name": "tototi*",
                        "allowed_to_merge": [
                            "maintainers",
                            "gitlab-nestor-integ-useless",
                        ],
                        "allowed_to_push": ["no one"],
                    },
                },
            },
        },
        "protected_tags": {
            "property_name": "protected_tags",
            "differences": {
                "tag2": {
                    "status": "removed",
                    "before": {"name": "tag2", "allowed_to_create": ["maintainers"]},
                    "after": None,
                },
                "tag266": {
                    "status": "added",
                    "before": None,
                    "after": {"name": "tag266", "allowed_to_create": ["maintainers"]},
                },
                "tag666": {
                    "status": "added",
                    "before": None,
                    "after": {"name": "tag666", "allowed_to_create": ["maintainers"]},
                },
            },
        },
        "variables": {
            "property_name": "variables",
            "differences": {
                "OTHER_VARIABLE": {
                    "status": "updated",
                    "before": {
                        "name": "OTHER_VARIABLE",
                        "protected": False,
                        "warning": None,
                        "value": "other value",
                    },
                    "after": {
                        "name": "OTHER_VARIABLE",
                        "protected": False,
                        "warning": None,
                        "value": "other value2",
                    },
                }
            },
        },
        "approvers": {
            "property_name": "approvers",
            "action": "updated",
            "differences": {
                "before": {
                    "name": "approvers",
                    "approvals_before_merge": 1,
                    "reset_approvals_on_push": False,
                    "can_override_approvals_per_merge_request": True,
                    "users": ["gitlab-nestor-integ", "gitlab-nestor-integ-useless"],
                },
                "after": {
                    "name": "approvers",
                    "approvals_before_merge": 1,
                    "reset_approvals_on_push": False,
                    "can_override_approvals_per_merge_request": False,
                    "users": ["gitlab-nestor-integ-useless", "gitlab-nestor-integ"],
                },
            },
        },
        "push_rules": {
            "property_name": "push_rules",
            "differences": {
                "before": {
                    "name": "push_rules",
                    "dont_allow_users_to_remove_tags": None,
                    "member_check": False,
                    "prevent_secrets": False,
                    "commit_message": None,
                    "commit_message_negative": None,
                    "branch_name_regex": None,
                    "author_mail_regex": None,
                    "prohibited_file_name_regex": None,
                    "max_file_size": 0,
                    "reject_unsigned_commits": None,
                },
                "after": {
                    "name": "push_rules",
                    "dont_allow_users_to_remove_tags": None,
                    "member_check": None,
                    "prevent_secrets": None,
                    "commit_message": None,
                    "commit_message_negative": None,
                    "branch_name_regex": None,
                    "author_mail_regex": None,
                    "prohibited_file_name_regex": None,
                    "max_file_size": 0,
                    "reject_unsigned_commits": None,
                },
                "action": "removed",
            },
        },
        "jira": {
            "property_name": "jira",
            "differences": {
                "jira": {
                    "before": {
                        "name": "jira",
                        "url": "https://jira.server",
                        "username": "toto",
                        "jira_issue_transition_id": "123",
                        "trigger_on_commit": "We can not get the value!",
                        "password": "****",
                    },
                    "after": {
                        "name": "jira",
                        "url": "https://jira.server.v2",
                        "username": "toto",
                        "jira_issue_transition_id": "123",
                        "trigger_on_commit": False,
                        "password": "F***D",
                    },
                    "action": "updated",
                }
            },
        },
        "schedulers": {
            "property_name": "schedulers",
            "differences": {
                "schedule_toto": {
                    "status": "updated",
                    "before": {
                        "name": "schedule_toto",
                        "branch": "master",
                        "cron": "0 4 1 * *",
                        "tz": "UTC",
                        "enabled": True,
                        "variables": {
                            "OTHER_VARIABLE": {
                                "name": "OTHER_VARIABLE",
                                "protected": False,
                                "warning": None,
                                "value": "other value2",
                            }
                        },
                        "api_id": 4948,
                    },
                    "after": {
                        "name": "schedule_toto",
                        "branch": "master",
                        "cron": "0 4 1 * *",
                        "tz": "UTC",
                        "enabled": False,
                        "variables": {
                            "OTHER_VARIABLE": {
                                "name": "OTHER_VARIABLE",
                                "protected": False,
                                "warning": None,
                                "value": "other value3",
                            }
                        },
                        "api_id": None,
                    },
                }
            },
        },
    }
    all_changes, changes_event = generate_event({"test/path": diffs})
    ci_git_shallow_clone = PropertyBean("ci_git_shallow_clone")
    ci_git_shallow_clone.before = [30]
    ci_git_shallow_clone.after = [20]
    permissions = PropertyBean("permissions")
    permissions.before.add(FieldBean("request_access_enabled", value=False))
    permissions.before.add(FieldBean("visibility", value="private"))
    permissions.after.add(FieldBean("request_access_enabled", value=True))
    permissions.after.add(FieldBean("visibility", value="internal"))

    mergerequests = PropertyBean("mergerequests")
    mergerequests.before.add(FieldBean("only_allow_merge_if_pipeline_succeeds", value=True))
    mergerequests.after.add(FieldBean("only_allow_merge_if_pipeline_succeeds", value=False))

    protected_branches = PropertyBean("protected_branches")
    protected_branches.before.add(PropertyBean("toto"))
    protected_branches.after.add(PropertyBean("tototi*"))

    protected_tags = PropertyBean("protected_tags")
    protected_tags.before.add(PropertyBean("tag2"))
    protected_tags.after.add(PropertyBean("tag266"))
    protected_tags.after.add(PropertyBean("tag666"))

    variables = PropertyBean("variables")
    variables.before.add(PropertyBean("OTHER_VARIABLE"))
    variables.after.add(PropertyBean("OTHER_VARIABLE"))

    approvers = PropertyBean("approvers")
    approvers.before.add(FieldBean("can_override_approvals_per_merge_request", value=True))
    approvers.after.add(FieldBean("can_override_approvals_per_merge_request", value=False))

    push_rules = PropertyBean("push_rules")
    push_rules.before.add(FieldBean("member_check", value=False))
    push_rules.before.add(FieldBean("prevent_secrets", value=False))
    push_rules.after.add(FieldBean("member_check", value=None))
    push_rules.after.add(FieldBean("prevent_secrets", value=None))

    jira = PropertyBean("jira")
    jira.before.add(FieldBean(name="url", value="https://jira.server"))
    jira.before.add(FieldBean(name="username", value="toto"))
    jira.before.add(FieldBean(name="jira_issue_transition_id", value="123"))
    jira.before.add(FieldBean(name="password", value="****"))
    jira.before.add(FieldBean(name="trigger_on_commit", value="We can not get the value!"))

    jira.after.add(FieldBean(name="url", value="https://jira.server.v2"))
    jira.after.add(FieldBean(name="username", value="toto"))
    jira.after.add(FieldBean(name="jira_issue_transition_id", value="123"))
    jira.after.add(FieldBean(name="password", value="F***D"))
    jira.after.add(FieldBean(name="trigger_on_commit", value=False))

    schedulers = PropertyBean("schedulers")
    schedulers.before.add(PropertyBean("schedule_toto"))
    schedulers.after.add(PropertyBean("schedule_toto"))
    expected_changes = [
        ci_git_shallow_clone,
        permissions,
        mergerequests,
        protected_branches,
        protected_tags,
        variables,
        approvers,
        push_rules,
        jira,
        schedulers,
    ]
    assert all_changes
    assert changes_event["test/path"] == expected_changes
