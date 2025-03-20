"""
test_update jira settings
----------------------------------
"""

# Third Party Libraries
import pytest

from dictns import Namespace
from gitlab.v4.objects import Project  # pylint: disable=unused-import

# Gitlab-Project-Configurator Modules
from gpc.parameters import GpcParameters
from gpc.parameters import RunMode
from gpc.project_rule_executor import ProjectRuleExecutor
from gpc.tests.test_helpers import get_change_value


# pylint: disable=redefined-outer-name, unused-argument, protected-access, duplicate-code

# flake8: noqa


@pytest.mark.parametrize(
    "project_rules, service_properties, expected_changes, has_diff, query",
    [
        # Execution 1
        (
            # project_rules
            Namespace(
                {
                    "push_rules": {
                        "dont_allow_users_to_remove_tags": False,
                        "member_check": True,
                        "prevent_secrets": True,
                        "commit_message": "^(.+)$",
                        "commit_message_negative": "truc",
                        "branch_name_regex": "^(.+)$",
                        "author_mail_regex": "^(.+)$",
                        "prohibited_file_name_regex": "^(.+)$",
                        "max_file_size": 500,
                        "reject_unsigned_commits": False,
                    }
                }
            ),
            # service_properties
            {},
            # expected_changes
            [
                {
                    "property_name": "push_rules",
                    "differences": {
                        "before": {
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
                            "reject_unsigned_commits": False,
                        },
                        "after": {
                            "member_check": True,
                            "dont_allow_users_to_remove_tags": False,
                            "name": "push_rules",
                            "prevent_secrets": True,
                            "commit_message": "^(.+)$",
                            "commit_message_negative": "truc",
                            "branch_name_regex": "^(.+)$",
                            "author_mail_regex": "^(.+)$",
                            "prohibited_file_name_regex": "^(.+)$",
                            "max_file_size": 500,
                            "reject_unsigned_commits": False,
                        },
                        "action": "updated",
                    },
                }
            ],
            # has_dif
            True,
            # query
            {
                "member_check": True,
                "deny_delete_tag": False,
                "prevent_secrets": True,
                "commit_message_regex": "^(.+)$",
                "commit_message_negative_regex": "truc",
                "branch_name_regex": "^(.+)$",
                "author_email_regex": "^(.+)$",
                "file_name_regex": "^(.+)$",
                "max_file_size": 500,
                "reject_unsigned_commits": False,
            },
        ),
        # Execution 2
        (
            # project_rules
            Namespace(
                {
                    "push_rules": {
                        "dont_allow_users_to_remove_tags": False,
                        "member_check": None,
                        "prevent_secrets": True,
                        "commit_message": "^(.+)$",
                        "commit_message_negative": "truc",
                        "branch_name_regex": "^(.+)$",
                        "author_mail_regex": "^(.+)$",
                        "prohibited_file_name_regex": "^(.+)$",
                        "max_file_size": 500,
                        "reject_unsigned_commits": None,
                    }
                }
            ),
            # service_properties
            None,
            # expected_changes
            [
                {
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
                            "member_check": False,
                            "dont_allow_users_to_remove_tags": False,
                            "name": "push_rules",
                            "prevent_secrets": True,
                            "commit_message": "^(.+)$",
                            "commit_message_negative": "truc",
                            "branch_name_regex": "^(.+)$",
                            "author_mail_regex": "^(.+)$",
                            "prohibited_file_name_regex": "^(.+)$",
                            "max_file_size": 500,
                            "reject_unsigned_commits": False,
                        },
                        "action": "updated",
                    },
                }
            ],
            # has_diff
            True,
            # query
            {
                "prevent_secrets": True,
                "deny_delete_tag": False,
                "member_check": False,
                "commit_message_regex": "^(.+)$",
                "commit_message_negative_regex": "truc",
                "branch_name_regex": "^(.+)$",
                "author_email_regex": "^(.+)$",
                "file_name_regex": "^(.+)$",
                "max_file_size": 500,
                "reject_unsigned_commits": False,
            },
        ),
        # Execution 3
        (
            # project_rules
            Namespace(
                {
                    "push_rules": {
                        "dont_allow_users_to_remove_tags": False,
                        "member_check": True,
                        "prevent_secrets": True,
                        "commit_message": "^(.+)$",
                        "commit_message_negative": "truc",
                        "branch_name_regex": "^(.+)$",
                        "author_mail_regex": "^(.+)$",
                        "prohibited_file_name_regex": "^(.+)$",
                        "max_file_size": 500,
                        "reject_unsigned_commits": False,
                    }
                }
            ),
            # service_properties
            {
                "deny_delete_tag": False,
                "member_check": True,
                "prevent_secrets": False,
                "commit_message_regex": None,
                "commit_message_negative_regex": "truc",
                "branch_name_regex": "toto",
                "author_email_regex": "^.*@server.com$",
                "file_name_regex": None,
                "max_file_size": 200,
                "reject_unsigned_commits": False,
            },
            # expected_changes
            [
                {
                    "property_name": "push_rules",
                    "differences": {
                        "before": {
                            "name": "push_rules",
                            "dont_allow_users_to_remove_tags": False,
                            "member_check": True,
                            "prevent_secrets": False,
                            "commit_message": None,
                            "commit_message_negative": "truc",
                            "branch_name_regex": "toto",
                            "author_mail_regex": "^.*@server.com$",
                            "prohibited_file_name_regex": None,
                            "max_file_size": 200,
                            "reject_unsigned_commits": False,
                        },
                        "after": {
                            "member_check": True,
                            "dont_allow_users_to_remove_tags": False,
                            "name": "push_rules",
                            "prevent_secrets": True,
                            "commit_message": "^(.+)$",
                            "commit_message_negative": "truc",
                            "branch_name_regex": "^(.+)$",
                            "author_mail_regex": "^(.+)$",
                            "prohibited_file_name_regex": "^(.+)$",
                            "max_file_size": 500,
                            "reject_unsigned_commits": False,
                        },
                        "action": "updated",
                    },
                }
            ],
            # has_diff
            True,
            # query
            {
                "member_check": True,
                "deny_delete_tag": False,
                "prevent_secrets": True,
                "commit_message_regex": "^(.+)$",
                "commit_message_negative_regex": "truc",
                "branch_name_regex": "^(.+)$",
                "author_email_regex": "^(.+)$",
                "file_name_regex": "^(.+)$",
                "max_file_size": 500,
                "reject_unsigned_commits": False,
            },
        ),
        # Execution 4
        (
            # project_rules
            Namespace(
                {
                    "push_rules": {
                        "dont_allow_users_to_remove_tags": False,
                        "member_check": True,
                        "prevent_secrets": True,
                        "commit_message": "^(.+)$",
                        "commit_message_negative": "truc",
                        "branch_name_regex": "^(.+)$",
                        "author_mail_regex": "^(.+)$",
                        "prohibited_file_name_regex": "^(.+)$",
                        "max_file_size": 500,
                        "reject_unsigned_commits": None,
                    }
                }
            ),
            # service_properties
            {
                "deny_delete_tag": False,
                "member_check": True,
                "prevent_secrets": True,
                "commit_message_regex": "^(.+)$",
                "commit_message_negative_regex": "truc",
                "branch_name_regex": "^(.+)$",
                "author_email_regex": "^(.+)$",
                "file_name_regex": "^(.+)$",
                "max_file_size": 500,
                "reject_unsigned_commits": None,
            },
            # expected_changes
            [
                {
                    "property_name": "push_rules",
                    "differences": {
                        "before": {
                            "member_check": True,
                            "dont_allow_users_to_remove_tags": False,
                            "name": "push_rules",
                            "prevent_secrets": True,
                            "commit_message": "^(.+)$",
                            "commit_message_negative": "truc",
                            "branch_name_regex": "^(.+)$",
                            "author_mail_regex": "^(.+)$",
                            "prohibited_file_name_regex": "^(.+)$",
                            "max_file_size": 500,
                            "reject_unsigned_commits": False,
                        },
                        "after": {
                            "member_check": True,
                            "dont_allow_users_to_remove_tags": False,
                            "name": "push_rules",
                            "prevent_secrets": True,
                            "commit_message": "^(.+)$",
                            "commit_message_negative": "truc",
                            "branch_name_regex": "^(.+)$",
                            "author_mail_regex": "^(.+)$",
                            "prohibited_file_name_regex": "^(.+)$",
                            "max_file_size": 500,
                            "reject_unsigned_commits": False,
                        },
                        "action": "kept",
                    },
                }
            ],
            # has_diff
            False,
            # query
            {
                "member_check": True,
                "deny_delete_tag": False,
                "prevent_secrets": True,
                "commit_message_regex": "^(.+)$",
                "commit_message_negative_regex": "truc",
                "branch_name_regex": "^(.+)$",
                "author_email_regex": "^(.+)$",
                "file_name_regex": "^(.+)$",
                "max_file_size": 500,
                "reject_unsigned_commits": False,
            },
        ),
    ],
)
def test_push_rules_setting(
    mocker,
    fake_gitlab,
    fake_project,
    project_rules,
    service_properties,
    expected_changes,
    has_diff,
    query,
):
    # Mock
    mocker.patch("gpc.tests.test_push_rules_setting.Project.save")
    mocker.patch(
        "gpc.tests.test_push_rules_setting.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    if service_properties is not None:
        mock_push_rules_manager = mocker.Mock()
        mock_push_rules_manager.deny_delete_tag = service_properties.get("deny_delete_tag", None)
        mock_push_rules_manager.member_check = service_properties.get("member_check", None)
        mock_push_rules_manager.prevent_secrets = service_properties.get("prevent_secrets", None)
        mock_push_rules_manager.commit_message_regex = service_properties.get(
            "commit_message_regex", None
        )
        mock_push_rules_manager.commit_message_negative_regex = service_properties.get(
            "commit_message_negative_regex", None
        )
        mock_push_rules_manager.branch_name_regex = service_properties.get(
            "branch_name_regex", None
        )
        mock_push_rules_manager.author_email_regex = service_properties.get(
            "author_email_regex", None
        )
        mock_push_rules_manager.file_name_regex = service_properties.get("file_name_regex", None)
        mock_push_rules_manager.max_file_size = service_properties.get("max_file_size", 0)
        mock_push_rules_manager.reject_unsigned_commits = service_properties.get(
            "reject_unsigned_commits", None
        )
        mock_push_rules_manager.save = mocker.Mock()
        mock_push_rules_manager.delete = mocker.Mock()
    else:
        mock_push_rules_manager = None
    mock_push_rules_services = mocker.Mock()
    mock_push_rules_services.get = mocker.Mock(return_value=mock_push_rules_manager)
    mock_push_rules_services.create = mocker.Mock()
    fake_project.pushrules = mock_push_rules_services
    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(config=mocker.Mock("fake_config"), mode=RunMode.APPLY),
    )
    p.execute()

    change_push_rules = get_change_value(p, "push_rules")
    assert change_push_rules.after.get_query() == query
    assert has_diff == p.has_changes()
    assert p.get_changes_json() == expected_changes
    if service_properties is not None:
        assert mock_push_rules_manager.save.called == has_diff
    else:
        assert mock_push_rules_services.create.called


@pytest.mark.parametrize(
    "project_rules, service_properties, expected_changes, has_diff, query",
    [
        # Execution 1
        (
            # project_rules
            Namespace(
                {
                    "push_rules": {
                        "remove": True,
                    }
                }
            ),
            # service_properties
            {
                "deny_delete_tag": False,
                "member_check": True,
                "prevent_secrets": True,
                "commit_message_regex": "^(.+)$",
                "commit_message_negative_regex": "truc",
                "branch_name_regex": "^(.+)$",
                "author_email_regex": "^(.+)$",
                "file_name_regex": "^(.+)$",
                "max_file_size": 500,
                "reject_unsigned_commits": False,
            },
            # expected_changes
            [
                {
                    "property_name": "push_rules",
                    "differences": {
                        "before": {
                            "member_check": True,
                            "dont_allow_users_to_remove_tags": False,
                            "name": "push_rules",
                            "prevent_secrets": True,
                            "commit_message": "^(.+)$",
                            "commit_message_negative": "truc",
                            "branch_name_regex": "^(.+)$",
                            "author_mail_regex": "^(.+)$",
                            "prohibited_file_name_regex": "^(.+)$",
                            "max_file_size": 500,
                            "reject_unsigned_commits": False,
                        },
                        "after": {
                            "member_check": False,
                            "dont_allow_users_to_remove_tags": None,
                            "name": "push_rules",
                            "prevent_secrets": False,
                            "commit_message": None,
                            "commit_message_negative": None,
                            "branch_name_regex": None,
                            "author_mail_regex": None,
                            "prohibited_file_name_regex": None,
                            "max_file_size": 0,
                            "reject_unsigned_commits": False,
                        },
                        "action": "removed",
                    },
                }
            ],
            # has_diff
            True,
            # query
            {
                "max_file_size": 0,
                "prevent_secrets": False,
                "member_check": False,
                "reject_unsigned_commits": False,
            },
        ),
        # Execution 2
        (
            # project_rules
            Namespace(
                {
                    "push_rules": {
                        "remove": True,
                    }
                }
            ),
            # service_properties
            {
                "deny_delete_tag": None,
                "member_check": False,
                "prevent_secrets": False,
                "commit_message_regex": None,
                "commit_message_negative_regex": None,
                "branch_name_regex": None,
                "author_email_regex": None,
                "file_name_regex": None,
                "max_file_size": 0,
                "reject_unsigned_commits": None,
            },
            # expected_changes
            [
                {
                    "property_name": "push_rules",
                    "differences": {
                        "before": {
                            "member_check": False,
                            "dont_allow_users_to_remove_tags": None,
                            "name": "push_rules",
                            "prevent_secrets": False,
                            "commit_message": None,
                            "commit_message_negative": None,
                            "branch_name_regex": None,
                            "author_mail_regex": None,
                            "prohibited_file_name_regex": None,
                            "max_file_size": 00,
                            "reject_unsigned_commits": False,
                        },
                        "after": {
                            "member_check": False,
                            "dont_allow_users_to_remove_tags": None,
                            "name": "push_rules",
                            "prevent_secrets": False,
                            "commit_message": None,
                            "commit_message_negative": None,
                            "branch_name_regex": None,
                            "author_mail_regex": None,
                            "prohibited_file_name_regex": None,
                            "max_file_size": 0,
                            "reject_unsigned_commits": False,
                        },
                        "action": "kept",
                    },
                }
            ],
            # has_diff
            False,
            # query
            {
                "max_file_size": 0,
                "prevent_secrets": False,
                "member_check": False,
                "reject_unsigned_commits": False,
            },
        ),
    ],
)
def test_remove_push_rules_setting(
    mocker,
    fake_gitlab,
    fake_project,
    project_rules,
    service_properties,
    expected_changes,
    has_diff,
    query,
):
    # Mock
    mocker.patch("gpc.tests.test_push_rules_setting.Project.save")
    mocker.patch(
        "gpc.tests.test_push_rules_setting.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    if service_properties is not None:
        mock_push_rules_manager = mocker.Mock()
        mock_push_rules_manager.deny_delete_tag = service_properties.get("deny_delete_tag", None)
        mock_push_rules_manager.member_check = service_properties.get("member_check", None)
        mock_push_rules_manager.prevent_secrets = service_properties.get("prevent_secrets", None)
        mock_push_rules_manager.commit_message_regex = service_properties.get(
            "commit_message_regex", None
        )
        mock_push_rules_manager.commit_message_negative_regex = service_properties.get(
            "commit_message_negative_regex", None
        )
        mock_push_rules_manager.branch_name_regex = service_properties.get(
            "branch_name_regex", None
        )
        mock_push_rules_manager.author_email_regex = service_properties.get(
            "author_email_regex", None
        )
        mock_push_rules_manager.reject_unsigned_commits = service_properties.get(
            "reject_unsigned_commits", None
        )
        mock_push_rules_manager.file_name_regex = service_properties.get("file_name_regex", None)
        mock_push_rules_manager.max_file_size = service_properties.get("max_file_size", 0)
        mock_push_rules_manager.save = mocker.Mock()
        mock_push_rules_manager.delete = mocker.Mock()
    else:
        mock_push_rules_manager = None
    mock_push_rules_services = mocker.Mock()
    mock_push_rules_services.get = mocker.Mock(return_value=mock_push_rules_manager)
    mock_push_rules_services.create = mocker.Mock()
    fake_project.pushrules = mock_push_rules_services
    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(config=mocker.Mock("fake_config"), mode=RunMode.APPLY),
    )
    p.execute()

    change_push_rules = get_change_value(p, "push_rules")
    assert change_push_rules.after.get_query() == query
    assert has_diff == p.has_changes()
    assert p.get_changes_json() == expected_changes
    assert mock_push_rules_manager.delete.called == has_diff
