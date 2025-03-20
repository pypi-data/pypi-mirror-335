"""
test_update pipelines email settings
----------------------------------
"""

# Standard Library
from os import environ

# Third Party Libraries
import pytest

from dictns import Namespace
from gitlab.v4.objects import Project  # pylint: disable=unused-import

# Gitlab-Project-Configurator Modules
from gpc.parameters import GpcParameters
from gpc.parameters import RunMode
from gpc.project_rule_executor import ProjectRuleExecutor
from gpc.tests.test_helpers import get_change_value


# pylint: disable=redefined-outer-name, unused-argument, protected-access, too-many-arguments, duplicate-code

# flake8: noqa


@pytest.mark.parametrize(
    "project_rules, service_properties, active, expected_changes, mode, has_changes",
    [
        (
            Namespace(
                {
                    "integrations": {
                        "pipelines_email": {
                            "recipients": ["poule@laferme.fr", "renard@laforet.com"],
                            "notify_only_broken_pipelines": False,
                            "notify_only_default_branch": True,
                            "pipeline_events": True,
                        }
                    }
                }
            ),
            {},
            False,
            [
                {
                    "property_name": "pipelines_email",
                    "differences": {
                        "pipelines_email": {
                            "before": {
                                "name": "pipelines_email",
                                "recipients": [],
                                "notify_only_broken_pipelines": None,
                                "notify_only_default_branch": None,
                                "pipeline_events": None,
                            },
                            "after": {
                                "name": "pipelines_email",
                                "recipients": [
                                    "poule@laferme.fr",
                                    "renard@laforet.com",
                                ],
                                "notify_only_broken_pipelines": False,
                                "notify_only_default_branch": True,
                                "pipeline_events": True,
                            },
                            "action": "updated",
                        }
                    },
                }
            ],
            RunMode.APPLY,
            True,
        ),
        (
            Namespace(
                {
                    "integrations": {
                        "pipelines_email": {
                            "recipients": ["poule@laferme.fr", "poussin@laferme.fr"],
                            "notify_only_broken_pipelines": True,
                            "notify_only_default_branch": False,
                            "pipeline_events": True,
                        }
                    }
                }
            ),
            {
                "recipients": "poule@laferme.fr,poussin@laferme.fr",
                "notify_only_broken_pipelines": True,
                "notify_only_default_branch": False,
                "pipeline_events": True,
            },
            True,
            [
                {
                    "property_name": "pipelines_email",
                    "differences": {
                        "pipelines_email": {
                            "before": {
                                "name": "pipelines_email",
                                "recipients": [
                                    "poule@laferme.fr",
                                    "poussin@laferme.fr",
                                ],
                                "notify_only_broken_pipelines": True,
                                "notify_only_default_branch": False,
                                "pipeline_events": True,
                            },
                            "after": {
                                "name": "pipelines_email",
                                "recipients": [
                                    "poule@laferme.fr",
                                    "poussin@laferme.fr",
                                ],
                                "notify_only_broken_pipelines": True,
                                "notify_only_default_branch": False,
                                "pipeline_events": True,
                            },
                            "action": "kept",
                        }
                    },
                }
            ],
            RunMode.APPLY,
            False,
        ),
    ],
)
def test_pipelines_email_settings(
    mocker,
    fake_gitlab,
    fake_project,
    project_rules,
    service_properties,
    active,
    expected_changes,
    mode,
    has_changes,
):
    # Mock
    mocker.patch("gpc.tests.test_def_pipelines_email_setting.Project.save")
    mocker.patch(
        "gpc.tests.test_def_pipelines_email_setting.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    mock_pipelines_email_service = mocker.Mock()
    mock_pipelines_email_service._lazy = False
    mock_pipelines_email_service.properties = service_properties
    mock_pipelines_email_service.active = active
    mock_pipelines_email_service.save = mocker.Mock()
    mock_pipelines_email_service.delete = mocker.Mock()
    mock_service = mocker.Mock()
    mock_service.get = mocker.Mock(return_value=mock_pipelines_email_service)
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
        assert mock_pipelines_email_service.save.called == has_changes
        assert not mock_pipelines_email_service.delete.called


def test_disabled_pipelines_email(mocker, fake_gitlab, fake_project):
    # Mock
    mocker.patch("gpc.tests.test_def_pipelines_email_setting.Project.save")
    mocker.patch(
        "gpc.tests.test_def_pipelines_email_setting.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    mocker.patch.dict(environ, {"PWD": "password"})
    mock_pipelines_email_service = mocker.Mock()
    mock_pipelines_email_service._lazy = False
    mock_pipelines_email_service.properties = {}
    mock_pipelines_email_service.active = True
    mock_pipelines_email_service.save = mocker.Mock()
    mock_pipelines_email_service.delete = mocker.Mock()
    mock_service = mocker.Mock()
    mock_service.get = mocker.Mock(return_value=mock_pipelines_email_service)
    fake_project.services = mock_service
    project_rules = Namespace(
        {
            "integrations": {
                "pipelines_email": {
                    "disabled": True,
                    "recipients": [],
                    "notify_only_broken_pipelines": None,
                    "notify_only_default_branch": None,
                    "pipeline_events": None,
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

    assert not mock_pipelines_email_service.save.called
    assert mock_pipelines_email_service.delete.called
    change_pipelines_email_setting = get_change_value(p, "pipelines_email")
    assert change_pipelines_email_setting.action == "removed"
