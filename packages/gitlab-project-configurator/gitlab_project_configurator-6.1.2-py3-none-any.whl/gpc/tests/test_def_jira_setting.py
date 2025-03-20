"""
test_update jira settings
----------------------------------
"""

# Third Party Libraries
import pytest

from dictns import Namespace
from gitlab.v4.objects import Project  # pylint: disable=unused-import

# Gitlab-Project-Configurator Modules
from gpc.executors.jira_setting_executor import JiraSettingExecutor
from gpc.parameters import GpcParameters
from gpc.parameters import RunMode
from gpc.project_rule_executor import ProjectRuleExecutor
from gpc.tests.test_helpers import get_change_value
from gpc.tests.test_helpers import get_executor


# pylint: disable=redefined-outer-name, unused-argument, protected-access, too-many-arguments, too-many-locals, duplicate-code

# flake8: noqa


@pytest.mark.parametrize(
    "project_rules, service_properties, active, var_envs, expected_changes, mode, has_changes",
    [
        (
            # project_rules:
            Namespace(
                {
                    "integrations": {
                        "jira": {
                            "url": "http://jira.test.com",
                            "jira_issue_transition_id": "120",
                            "username": "the.username",
                            "password_from_envvar": "THE_PASSWORD_ENVVAR",
                            "trigger_on_commit": True,
                            "comment_on_event_enabled": True,
                        }
                    }
                }
            ),
            # service_properties:
            {},
            # active:
            False,
            # var_envs:
            {"THE_PASSWORD_ENVVAR": "password"},
            # expected_changes:
            [
                {
                    "property_name": "jira",
                    "differences": {
                        "jira": {
                            "before": {
                                "name": "jira",
                                "url": None,
                                "username": None,
                                "jira_issue_transition_id": None,
                                "password": "Not defined",
                                "token": "Not defined",
                                "trigger_on_commit": True,
                                "trigger_on_mr": False,
                                "comment_on_event_enabled": False,
                                "authentication_method": None,
                            },
                            "after": {
                                "name": "jira",
                                "url": "http://jira.test.com",
                                "jira_issue_transition_id": "120",
                                "username": "the.username",
                                "password": "p****d",
                                "token": "Not defined",
                                "trigger_on_commit": True,
                                "trigger_on_mr": True,
                                "comment_on_event_enabled": True,
                                "authentication_method": "Basic",
                            },
                            "action": "updated",
                        }
                    },
                }
            ],
            # mode:
            RunMode.APPLY,
            # has_changes:
            True,
        ),
        (
            # project_rules:
            Namespace(
                {
                    "integrations": {
                        "jira": {
                            "url": "http://jira.test.com",
                            "jira_issue_transition_id": 120,
                            "username": "the.username",
                            "password_from_envvar": "THE_PASSWORD_ENVVAR",
                            "trigger_on_commit": False,
                            "trigger_on_mr": False,
                            "comment_on_event_enabled": False,
                        }
                    }
                }
            ),
            # service_properties:
            {
                "url": "http://jira.test.com",
                "jira_issue_transition_id": "120",
                "username": "the.username",
                "password": "same.password",
                "jira_auth_type": 0,
            },
            # active:
            True,
            # var_envs:
            {"THE_PASSWORD_ENVVAR": "same.password"},
            # expected_changes:
            [
                {
                    "property_name": "jira",
                    "differences": {
                        "jira": {
                            "before": {
                                "name": "jira",
                                "url": "http://jira.test.com",
                                "jira_issue_transition_id": "120",
                                "username": "the.username",
                                "password": "s****d",
                                "token": "Not defined",
                                "trigger_on_commit": True,
                                "trigger_on_mr": False,
                                "comment_on_event_enabled": False,
                                "authentication_method": "Basic",
                            },
                            "after": {
                                "name": "jira",
                                "url": "http://jira.test.com",
                                "jira_issue_transition_id": "120",
                                "username": "the.username",
                                "password": "s****d",
                                "token": "Not defined",
                                "trigger_on_commit": False,
                                "trigger_on_mr": False,
                                "comment_on_event_enabled": False,
                                "authentication_method": "Basic",
                            },
                            "action": "updated",
                        }
                    },
                }
            ],
            # mode:
            RunMode.APPLY,
            # has_changes:
            False,
        ),
        (
            # project_rules:
            Namespace(
                {
                    "integrations": {
                        "jira": {
                            "url": "http://jira.test.com",
                            "jira_issue_transition_id": "",
                            "username": "the.username",
                            "password_from_envvar": "THE_PASSWORD_ENVVAR",
                            "trigger_on_commit": False,
                            "trigger_on_mr": False,
                            "comment_on_event_enabled": True,
                        }
                    }
                }
            ),
            # service_properties:
            {
                "url": "http://jira.test.com",
                "jira_issue_transition_id": "120",
                "username": "the.username",
                "password": "old.password",
                "jira_auth_type": 0,
            },
            # active:
            True,
            # var_envs:
            {"THE_PASSWORD_ENVVAR": "new.password"},
            # expected_changes:
            [
                {
                    "property_name": "jira",
                    "differences": {
                        "jira": {
                            "before": {
                                "name": "jira",
                                "url": "http://jira.test.com",
                                "jira_issue_transition_id": "120",
                                "username": "the.username",
                                "password": "o****d",
                                "token": "Not defined",
                                "trigger_on_commit": True,
                                "trigger_on_mr": False,
                                "comment_on_event_enabled": False,
                                "authentication_method": "Basic",
                            },
                            "after": {
                                "name": "jira",
                                "url": "http://jira.test.com",
                                "jira_issue_transition_id": None,
                                "username": "the.username",
                                "password": "n****d",
                                "token": "Not defined",
                                "trigger_on_commit": False,
                                "trigger_on_mr": False,
                                "comment_on_event_enabled": True,
                                "authentication_method": "Basic",
                            },
                            "action": "updated",
                        }
                    },
                }
            ],
            # mode:
            RunMode.APPLY,
            # has_changes:
            True,
        ),
        (
            # project_rules:
            Namespace(
                {
                    "integrations": {
                        "jira": {
                            "url": "http://jira.test.com",
                            "jira_issue_transition_id": None,
                            "username": "the.username",
                            "password_from_envvar": "THE_PASSWORD_ENVVAR",
                            "trigger_on_commit": False,
                            "trigger_on_mr": False,
                            "comment_on_event_enabled": False,
                        }
                    }
                }
            ),
            # service_properties:
            {
                "url": "http://jira.test.com",
                "jira_issue_transition_id": "120",
                "username": "the.username",
                "password": "same.password",
                "jira_auth_type": 0,
            },
            # active:
            True,
            # var_envs:
            {"THE_PASSWORD_ENVVAR": "same.password"},
            # expected_changes:
            [
                {
                    "property_name": "jira",
                    "differences": {
                        "jira": {
                            "before": {
                                "name": "jira",
                                "url": "http://jira.test.com",
                                "jira_issue_transition_id": "120",
                                "username": "the.username",
                                "password": "s****d",
                                "token": "Not defined",
                                "trigger_on_commit": True,
                                "trigger_on_mr": False,
                                "comment_on_event_enabled": False,
                                "authentication_method": "Basic",
                            },
                            "after": {
                                "name": "jira",
                                "url": "http://jira.test.com",
                                "jira_issue_transition_id": "120",
                                "username": "the.username",
                                "password": "s****d",
                                "token": "Not defined",
                                "trigger_on_commit": False,
                                "trigger_on_mr": False,
                                "comment_on_event_enabled": False,
                                "authentication_method": "Basic",
                            },
                            "action": "updated",
                        }
                    },
                }
            ],
            # mode:
            RunMode.APPLY,
            # has_changes:
            False,
        ),
        (
            # project_rules:
            Namespace(
                {
                    "integrations": {
                        "jira": {
                            "url": "http://jira.test.com",
                            "jira_issue_transition_id": "120,58,12",
                            "username": "the.username",
                            "password_from_envvar": "THE_PASSWORD_ENVVAR",
                            "trigger_on_commit": False,
                            "trigger_on_mr": False,
                            "comment_on_event_enabled": True,
                        }
                    }
                }
            ),
            # service_properties:
            {
                "url": "http://jira.test.com",
                "jira_issue_transition_id": "120,58,12",
                "username": "the.username",
                "password": "old.password",
                "jira_auth_type": 0,
            },
            # active:
            True,
            # var_envs:
            {"THE_PASSWORD_ENVVAR": "new.password"},
            # expected_changes:
            [
                {
                    "property_name": "jira",
                    "differences": {
                        "jira": {
                            "before": {
                                "name": "jira",
                                "url": "http://jira.test.com",
                                "jira_issue_transition_id": "120,58,12",
                                "username": "the.username",
                                "password": "o****d",
                                "token": "Not defined",
                                "trigger_on_commit": True,
                                "trigger_on_mr": False,
                                "comment_on_event_enabled": False,
                                "authentication_method": "Basic",
                            },
                            "after": {
                                "name": "jira",
                                "url": "http://jira.test.com",
                                "jira_issue_transition_id": "120,58,12",
                                "username": "the.username",
                                "password": "n****d",
                                "token": "Not defined",
                                "trigger_on_commit": False,
                                "trigger_on_mr": False,
                                "comment_on_event_enabled": True,
                                "authentication_method": "Basic",
                            },
                            "action": "updated",
                        }
                    },
                }
            ],
            # mode:
            RunMode.APPLY,
            # has_changes:
            False,
        ),
        (
            # project_rules:
            Namespace(
                {
                    "integrations": {
                        "jira": {
                            "url": "http://jira.test.com",
                            "jira_issue_transition_id": "120",
                            "username_from_envvar": "THE_USERNAME_ENVVAR",
                            "password_from_envvar": "THE_PASSWORD_ENVVAR",
                            "trigger_on_commit": True,
                            "comment_on_event_enabled": True,
                        }
                    }
                }
            ),
            # service_properties:
            {},
            # active:
            False,
            # var_envs:
            {"THE_PASSWORD_ENVVAR": "password"},
            # expected_changes:
            [
                {
                    "property_name": "jira",
                    "differences": {
                        "jira": {
                            "before": {
                                "name": "jira",
                                "url": None,
                                "username": None,
                                "jira_issue_transition_id": None,
                                "password": "Not defined",
                                "token": "Not defined",
                                "trigger_on_commit": True,
                                "trigger_on_mr": False,
                                "comment_on_event_enabled": False,
                                "authentication_method": None,
                            },
                            "after": {
                                "name": "jira",
                                "url": "http://jira.test.com",
                                "jira_issue_transition_id": "120",
                                "username": "username_from_envvar",
                                "password": "p****d",
                                "token": "Not defined",
                                "trigger_on_commit": True,
                                "trigger_on_mr": True,
                                "comment_on_event_enabled": True,
                                "authentication_method": "Basic",
                            },
                            "action": "updated",
                        }
                    },
                }
            ],
            # mode:
            RunMode.APPLY,
            # has_changes:
            True,
        ),
        (
            # project_rules:
            Namespace(
                {
                    "integrations": {
                        "jira": {
                            "url": "http://jira.test.com",
                            "jira_issue_transition_id": "120",
                            "token_from_envvar": "THE_PASSWORD_ENVVAR",
                            "trigger_on_commit": True,
                            "comment_on_event_enabled": True,
                        }
                    }
                }
            ),
            # service_properties:
            {},
            # active:
            False,
            # var_envs:
            {"THE_PASSWORD_ENVVAR": "password"},
            # expected_changes:
            [
                {
                    "property_name": "jira",
                    "differences": {
                        "jira": {
                            "before": {
                                "name": "jira",
                                "url": None,
                                "username": None,
                                "jira_issue_transition_id": None,
                                "password": "Not defined",
                                "token": "Not defined",
                                "trigger_on_commit": True,
                                "trigger_on_mr": False,
                                "comment_on_event_enabled": False,
                                "authentication_method": None,
                            },
                            "after": {
                                "name": "jira",
                                "url": "http://jira.test.com",
                                "jira_issue_transition_id": "120",
                                "username": None,
                                "password": "Not defined",
                                "token": "p****d",
                                "trigger_on_commit": True,
                                "trigger_on_mr": True,
                                "comment_on_event_enabled": True,
                                "authentication_method": "Jira Access Token",
                            },
                            "action": "updated",
                        }
                    },
                }
            ],
            # mode:
            RunMode.APPLY,
            # has_changes:
            True,
        ),
    ],
)
def test_jira_settings(
    mocker,
    monkeypatch,
    fake_gitlab,
    fake_project,
    project_rules,
    service_properties,
    active,
    var_envs,
    expected_changes,
    mode,
    has_changes,
):
    # Mock
    mocker.patch("gpc.tests.test_def_jira_setting.Project.save")
    mocker.patch(
        "gpc.tests.test_def_jira_setting.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    monkeypatch.setenv("THE_USERNAME_ENVVAR", "username_from_envvar")
    for k, v in var_envs.items():
        monkeypatch.setenv(k, v)
    mock_jira_service = mocker.Mock()
    mock_jira_service._lazy = False
    mock_jira_service.properties = service_properties
    mock_jira_service.active = active
    mock_jira_service.commit_events = True
    mock_jira_service.merge_requests_events = False
    mock_jira_service.comment_on_event_enabled = False
    mock_jira_service.save = mocker.Mock()
    mock_jira_service.delete = mocker.Mock()
    mock_service = mocker.Mock()
    mock_service.get = mocker.Mock(return_value=mock_jira_service)
    fake_project.services = mock_service
    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(config=mocker.Mock("fake_config"), mode=mode),
    )
    p.update_settings()
    assert p.get_changes_json() == expected_changes
    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(config=mocker.Mock("fake_config"), mode=RunMode.APPLY),
    )

    if mode == RunMode.APPLY:
        p.execute()
        assert not mock_jira_service.delete.called


@pytest.mark.parametrize(
    "project_rules, service_properties, active, var_envs, expected_changes, mode",
    [
        (
            # project_rules:
            Namespace(
                {
                    "integrations": {
                        "jira": {
                            "url": "http://jira.test.com",
                            "jira_issue_transition_id": "120",
                            "username": "the.username",
                            "password_from_envvar": "THE_PASSWORD_ENVVAR",
                            "trigger_on_commit": True,
                            "comment_on_event_enabled": True,
                        }
                    }
                }
            ),
            # service_properties:
            {},
            # active:
            True,
            # var_envs:
            {},
            # expected_changes:
            [
                {
                    "property_name": "jira",
                    "differences": {
                        "jira": {
                            "before": {
                                "name": "jira",
                                "url": None,
                                "username": None,
                                "jira_issue_transition_id": None,
                                "password": "Not defined",
                                "token": "Not defined",
                                "trigger_on_commit": True,
                                "trigger_on_mr": False,
                                "comment_on_event_enabled": False,
                                "authentication_method": None,
                            },
                            "after": {
                                "name": "jira",
                                "url": "http://jira.test.com",
                                "jira_issue_transition_id": "120",
                                "username": "the.username",
                                "password": "Not defined",
                                "token": "Not defined",
                                "warning": (
                                    "/!\\ Environment variable" " THE_PASSWORD_ENVVAR not found."
                                ),
                                "trigger_on_commit": True,
                                "trigger_on_mr": True,
                                "comment_on_event_enabled": True,
                                "authentication_method": "Basic",
                            },
                            "action": "warning",
                        }
                    },
                }
            ],
            # mode:
            RunMode.DRY_RUN,
        ),
        (
            # project_rules:
            Namespace(
                {
                    "integrations": {
                        "jira": {
                            "url": "http://jira.test.com",
                            "jira_issue_transition_id": "120",
                            "username": "the.username",
                            "password_from_envvar": "THE_PASSWORD_ENVVAR",
                            "trigger_on_commit": True,
                            "comment_on_event_enabled": False,
                        }
                    }
                }
            ),
            # service_properties:
            {},
            # active:
            True,
            # var_envs:
            {},
            # expected_changes:
            [
                {
                    "property_name": "jira",
                    "differences": {
                        "jira": {
                            "before": {
                                "name": "jira",
                                "url": None,
                                "username": None,
                                "jira_issue_transition_id": None,
                                "password": "Not defined",
                                "token": "Not defined",
                                "trigger_on_commit": True,
                                "trigger_on_mr": False,
                                "comment_on_event_enabled": False,
                                "authentication_method": None,
                            },
                            "after": {
                                "name": "jira",
                                "url": "http://jira.test.com",
                                "jira_issue_transition_id": "120",
                                "username": "the.username",
                                "password": "Not defined",
                                "token": "Not defined",
                                "warning": (
                                    "/!\\ Environment variable" " THE_PASSWORD_ENVVAR not found."
                                ),
                                "trigger_on_commit": True,
                                "trigger_on_mr": True,
                                "comment_on_event_enabled": False,
                                "authentication_method": "Basic",
                            },
                            "action": "warning",
                        }
                    },
                }
            ],
            # mode:
            RunMode.DRY_RUN,
        ),
        (
            # project_rules:
            Namespace(
                {
                    "integrations": {
                        "jira": {
                            "url": "http://jira.test.com",
                            "jira_issue_transition_id": "120",
                            "username": "the.username",
                            "password_from_envvar": "THE_PASSWORD_ENVVAR",
                            "trigger_on_commit": True,
                            "comment_on_event_enabled": False,
                        }
                    }
                }
            ),
            # service_properties:
            {},
            # active:
            True,
            # var_envs:
            {},
            # expected_changes:
            [
                {
                    "property_name": "jira",
                    "differences": {
                        "jira": {
                            "before": {
                                "name": "jira",
                                "url": None,
                                "username": None,
                                "jira_issue_transition_id": None,
                                "password": "****",
                                "token": "Not defined",
                                "trigger_on_commit": True,
                                "trigger_on_mr": False,
                                "comment_on_event_enabled": False,
                                "authentication_method": None,
                            },
                            "after": {
                                "name": "jira",
                                "url": "http://jira.test.com",
                                "jira_issue_transition_id": "120",
                                "username": "the.username",
                                "token": "Not defined",
                                "warning": (
                                    "/!\\ Environment variable" " THE_PASSWORD_ENVVAR not found."
                                ),
                                "trigger_on_commit": True,
                                "trigger_on_mr": True,
                                "comment_on_event_enabled": False,
                                "authentication_method": "Basic",
                            },
                            "action": "warning",
                        }
                    },
                }
            ],
            # mode:
            RunMode.APPLY,
        ),
    ],
)
def test_jira_settings_ko(
    mocker,
    monkeypatch,
    fake_gitlab,
    fake_project,
    project_rules,
    service_properties,
    active,
    var_envs,
    expected_changes,
    mode,
):
    # Mock
    mocker.patch("gpc.tests.test_def_jira_setting.Project.save")
    mocker.patch(
        "gpc.tests.test_def_jira_setting.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    for k, v in var_envs.items():
        monkeypatch.setenv(k, v)
    mock_jira_service = mocker.Mock()
    mock_jira_service._lazy = False
    mock_jira_service.properties = service_properties
    mock_jira_service.active = active
    mock_jira_service.commit_events = True
    mock_jira_service.merge_requests_events = False
    mock_jira_service.comment_on_event_enabled = False
    mock_jira_service.save = mocker.Mock()
    mock_jira_service.delete = mocker.Mock()
    mock_service = mocker.Mock()
    mock_service.get = mocker.Mock(return_value=mock_jira_service)
    fake_project.services = mock_service
    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(config=mocker.Mock("fake_config"), mode=mode),
    )

    if mode == RunMode.APPLY:
        p.update_settings()
        executor = get_executor(p, JiraSettingExecutor)
        assert executor.error_message == "/!\\ Environment variable THE_PASSWORD_ENVVAR not found."
    else:
        p.update_settings()
        assert p.get_changes_json() == expected_changes


def test_disabled_jira(mocker, monkeypatch, fake_gitlab, fake_project):
    # Mock
    mocker.patch("gpc.tests.test_def_jira_setting.Project.save")
    mocker.patch(
        "gpc.tests.test_def_jira_setting.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    monkeypatch.setenv("PWD", "password")
    mock_jira_service = mocker.Mock()
    mock_jira_service.properties = {}
    mock_jira_service.active = True
    mock_jira_service.save = mocker.Mock()
    mock_jira_service.delete = mocker.Mock()
    mock_jira_service.delete = mocker.Mock()
    mock_service = mocker.Mock()
    mock_service.get = mocker.Mock(return_value=mock_jira_service)
    fake_project.services = mock_service
    project_rules = Namespace(
        {
            "integrations": {
                "jira": {
                    "url": "http://jira.test.com",
                    "jira_issue_transition_id": "120",
                    "username": "the.username",
                    "disabled": True,
                    "password_from_envvar": "PWD",
                }
            }
        }
    )
    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(config=mocker.Mock("fake_config"), mode=RunMode.APPLY),
    )
    p.execute()

    assert not mock_jira_service.save.called
    assert mock_jira_service.delete.called
    change_jira_setting = get_change_value(p, "jira")
    assert change_jira_setting.action == "removed"


def test_force_jira_settings(
    mocker,
    monkeypatch,
    fake_gitlab,
    fake_project,
):
    # Mock
    mocker.patch("gpc.tests.test_def_jira_setting.Project.save")
    mocker.patch(
        "gpc.tests.test_def_jira_setting.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    monkeypatch.setenv("THE_PASSWORD_ENVVAR", "same.password")
    mock_jira_service = mocker.Mock()
    mock_jira_service._lazy = False
    mock_jira_service.properties = {
        "url": "http://jira.test.com",
        "jira_issue_transition_id": "120",
        "username": "the.username",
        "password": "same.password",
        "jira_auth_type": 0,
    }
    mock_jira_service.active = True
    mock_jira_service.commit_events = True
    mock_jira_service.merge_requests_events = False
    mock_jira_service.comment_on_event_enabled = False
    mock_jira_service.save = mocker.Mock()
    mock_jira_service.delete = mocker.Mock()
    mock_service = mocker.Mock()
    mock_service.get = mocker.Mock(return_value=mock_jira_service)
    fake_project.services = mock_service

    p_rule = Namespace(
        {
            "integrations": {
                "jira": {
                    "url": "http://jira.test.com",
                    "jira_issue_transition_id": 120,
                    "username": "the.username",
                    "password_from_envvar": "THE_PASSWORD_ENVVAR",
                    "trigger_on_commit": False,
                    "trigger_on_mr": False,
                    "comment_on_event_enabled": False,
                }
            }
        }
    )
    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=p_rule,
        gpc_params=GpcParameters(
            config=mocker.Mock("fake_config"), mode=RunMode.APPLY, force="jira"
        ),
    )
    p.update_settings()
    assert p.get_changes_json() == [
        {
            "property_name": "jira",
            "differences": {
                "jira": {
                    "before": {
                        "name": "jira",
                        "url": "http://jira.test.com",
                        "jira_issue_transition_id": "120",
                        "username": "the.username",
                        "password": "s****d",
                        "token": "Not defined",
                        "trigger_on_commit": True,
                        "trigger_on_mr": False,
                        "comment_on_event_enabled": False,
                        "authentication_method": "Basic",
                    },
                    "after": {
                        "name": "jira",
                        "url": "http://jira.test.com",
                        "jira_issue_transition_id": "120",
                        "username": "the.username",
                        "password": "s****d",
                        "token": "Not defined",
                        "trigger_on_commit": False,
                        "trigger_on_mr": False,
                        "comment_on_event_enabled": False,
                        "authentication_method": "Basic",
                    },
                    "action": "updated",
                }
            },
        }
    ]
    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=p_rule,
        gpc_params=GpcParameters(
            config=mocker.Mock("fake_config"), mode=RunMode.APPLY, force="jira"
        ),
    )

    p.execute()
    assert mock_jira_service.save.called
    assert not mock_jira_service.delete.called
