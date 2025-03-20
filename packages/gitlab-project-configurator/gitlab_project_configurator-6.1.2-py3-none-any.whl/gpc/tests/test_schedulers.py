"""
test project schedulers
----------------------------------
"""

# Standard Library
from unittest.mock import Mock

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

SCHEDULES_DICT = {
    "schedule_3": Namespace(
        {
            "id": "schedule_3",
            "description": "schedule_3",
            "ref": "master",
            "cron": "* * * *",
            "active": False,
            "cron_timezone": "UTC",
            "attributes": {"variables": []},
        }
    ),
    "schedule_4": Namespace(
        {
            "id": "schedule_4",
            "description": "schedule_4",
            "ref": "master",
            "cron": "* * * 0 0",
            "active": True,
            "cron_timezone": "UTC",
            "attributes": {
                "variables": [{"key": "var_name", "value": "var_value1", "variable_type": "file"}]
            },
        }
    ),
}

SCHEDULES_LIST = [
    Namespace(
        {
            "id": "schedule_3",
            "description": "schedule_3",
            "ref": "master",
            "cron": "* * * *",
            "active": False,
            "cron_timezone": "UTC",
            "attributes": {"variables": []},
        }
    ),
    Namespace(
        {
            "id": "schedule_4",
            "description": "schedule_4",
            "ref": "master",
            "cron": "* * * 0 0",
            "active": True,
            "cron_timezone": "UTC",
            "attributes": {"variables": [{"key": "var_name", "value": "var_value1"}]},
        }
    ),
]
delete = Mock()
save = Mock()
update_var_api = Mock()
delete_var_api = Mock()
create_var_api = Mock()


def list_schedules(**kwargs):
    mock_schedule_3 = Mock()
    mock_schedule_3.id = "schedule_3"
    mock_schedule_3.description = "schedule_3"
    mock_schedule_3.ref = "master"
    mock_schedule_3.cron = "* * * *"
    mock_schedule_3.active = False
    mock_schedule_3.cron_timezone = "UTC"
    mock_schedule_3.attributes = {"variables": []}
    mock_schedule_3.delete = delete
    mock_schedule_3.save = save
    mock_schedule_4 = Mock()
    mock_schedule_4.id = "schedule_4"
    mock_schedule_4.description = "schedule_4"
    mock_schedule_4.ref = "master"
    mock_schedule_4.cron = "* * * 0 0"
    mock_schedule_4.active = True
    mock_schedule_4.cron_timezone = "UTC"
    mock_schedule_4.attributes = {"variables": []}
    mock_schedule_4.delete = delete
    mock_schedule_4.save = save
    variables = Mock()
    variables.create = create_var_api
    variables.delete = delete_var_api
    variables.update = update_var_api
    mock_schedule_4.variables = variables

    mock_schedule_5 = Mock()
    mock_schedule_5.id = "schedule_5"
    mock_schedule_5.description = "schedule_5"
    mock_schedule_5.ref = "master"
    mock_schedule_5.cron = "* * * * *"
    mock_schedule_5.active = False
    mock_schedule_5.cron_timezone = "UTC"
    mock_schedule_5.attributes = {"variables": []}
    mock_schedule_5.delete = delete
    mock_schedule_5.save = save
    return [mock_schedule_3, mock_schedule_4, mock_schedule_5]


def get_schedules(key, retry_transient_errors):
    mock_schedule_3 = Mock()
    mock_schedule_3.id = "schedule_3"
    mock_schedule_3.description = "schedule_3"
    mock_schedule_3.ref = "master"
    mock_schedule_3.cron = "* * * *"
    mock_schedule_3.active = False
    mock_schedule_3.cron_timezone = "UTC"
    mock_schedule_3.attributes = {"variables": []}
    mock_schedule_3.delete = delete
    mock_schedule_3.save = save

    mock_schedule_4 = Mock()
    mock_schedule_4.id = "schedule_4"
    mock_schedule_4.description = "schedule_4"
    mock_schedule_4.ref = "master"
    mock_schedule_4.cron = "* * * 0 0"
    mock_schedule_4.active = True
    mock_schedule_4.cron_timezone = "UTC"
    mock_schedule_4.attributes = {
        "variables": [
            {"key": "var_1", "value": "var_1", "variable_type": "file"},
            {"key": "var_2", "value": "var_2", "variable_type": "env_var"},
            {"key": "var_3", "value": "var_3", "variable_type": "env_var"},
        ]
    }
    mock_schedule_4.delete = delete
    mock_schedule_4.save = save
    variables = Mock()
    variables.create = create_var_api
    variables.delete = delete_var_api
    variables.update = update_var_api
    mock_schedule_4.variables = variables

    mock_schedule_5 = Mock()
    mock_schedule_5.id = "schedule_5"
    mock_schedule_5.description = "schedule_5"
    mock_schedule_5.ref = "master"
    mock_schedule_5.cron = "* * * * *"
    mock_schedule_5.active = False
    mock_schedule_5.cron_timezone = "UTC"
    mock_schedule_5.attributes = {"variables": []}
    mock_schedule_5.delete = delete
    mock_schedule_5.save = save
    return {
        "schedule_3": mock_schedule_3,
        "schedule_4": mock_schedule_4,
        "schedule_5": mock_schedule_5,
    }.get(key)


# flake8: qa


@pytest.mark.parametrize("keep_schedulers", [True, False])
def test_schedulers(mocker, fake_gitlab, fake_project, keep_schedulers):
    # Mock
    mocker.patch("gpc.tests.test_schedulers.Project.save")
    mocker.patch(
        "gpc.tests.test_schedulers.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    pipelineschedules = mocker.Mock()

    pipelineschedules.list = mocker.Mock(side_effect=list_schedules)
    pipelineschedules.get = mocker.Mock(side_effect=get_schedules)
    mock_sched_var = mocker.Mock()
    mock_sched_var.create = mocker.Mock()
    mock_sched_created = mocker.Mock()
    mock_sched_created.variables = mock_sched_var

    pipelineschedules.create = mocker.Mock(return_value=mock_sched_created)

    fake_project.pipelineschedules = pipelineschedules

    project_rules = Namespace(
        {
            "keep_existing_schedulers": keep_schedulers,
            "schedulers": [
                {
                    "name": "schedule_1",
                    "branch": "master",
                    "cron": "* * * 0 0",
                    "tz": "UTC",
                    "enabled": True,
                    "variables": [{"name": "var_name", "value": "var_value"}],
                },
                {
                    "name": "schedule_2",
                    "branch": "master",
                    "cron": "* * * 0 0",
                    "tz": "UTC",
                    "enabled": True,
                },
                {
                    "name": "schedule_4",
                    "branch": "master",
                    "cron": "* * * 0 0",
                    "tz": "UTC",
                    "enabled": True,
                    "variables": [
                        {"name": "var_name", "value": "var_value"},
                        {"name": "var_2", "value": "var_21", "variable_type": "file"},
                        {"name": "var_3", "value": "var_3"},
                    ],
                },
                {
                    "name": "schedule_5",
                    "branch": "master",
                    "cron": "* * * * *",
                    "tz": "UTC",
                    "enabled": False,
                    "variables": [],
                },
            ],
        }
    )

    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(mocker.Mock("fake_config"), mode=RunMode.APPLY),
    )
    p.execute()
    change_schedulers = get_change_value(p, "schedulers")
    expected_diff_to_dict = {
        "differences": {
            "schedule_1": {
                "after": {
                    "api_id": None,
                    "branch": "master",
                    "cron": "* * * 0 0",
                    "enabled": True,
                    "name": "schedule_1",
                    "tz": "UTC",
                    "variables": {
                        "var_name": {
                            "masked": False,
                            "name": "var_name",
                            "protected": False,
                            "value": "var_value",
                            "variable_type": "env_var",
                            "warning": "",
                        }
                    },
                },
                "before": None,
                "status": "added",
            },
            "schedule_2": {
                "after": {
                    "api_id": None,
                    "branch": "master",
                    "cron": "* * * 0 0",
                    "enabled": True,
                    "name": "schedule_2",
                    "tz": "UTC",
                    "variables": None,
                },
                "before": None,
                "status": "added",
            },
            "schedule_3": {
                "after": None,
                "before": {
                    "api_id": "schedule_3",
                    "branch": "master",
                    "cron": "* * * *",
                    "enabled": False,
                    "name": "schedule_3",
                    "tz": "UTC",
                    "variables": {},
                },
                "status": "removed",
            },
            "schedule_4": {
                "after": {
                    "api_id": None,
                    "branch": "master",
                    "cron": "* * * 0 0",
                    "enabled": True,
                    "name": "schedule_4",
                    "tz": "UTC",
                    "variables": {
                        "var_2": {
                            "masked": False,
                            "name": "var_2",
                            "protected": False,
                            "value": "v****1",
                            "variable_type": "file",
                            "warning": "",
                        },
                        "var_3": {
                            "masked": False,
                            "name": "var_3",
                            "protected": False,
                            "value": "var_3",
                            "variable_type": "env_var",
                            "warning": "",
                        },
                        "var_name": {
                            "masked": False,
                            "name": "var_name",
                            "protected": False,
                            "value": "var_value",
                            "variable_type": "env_var",
                            "warning": "",
                        },
                    },
                },
                "before": {
                    "api_id": "schedule_4",
                    "branch": "master",
                    "cron": "* * * 0 0",
                    "enabled": True,
                    "name": "schedule_4",
                    "tz": "UTC",
                    "variables": {
                        "var_1": {
                            "masked": False,
                            "name": "var_1",
                            "protected": False,
                            "value": "var_1",
                            "variable_type": "file",
                            "warning": "",
                        },
                        "var_2": {
                            "masked": False,
                            "name": "var_2",
                            "protected": False,
                            "value": "v****2",
                            "variable_type": "env_var",
                            "warning": "",
                        },
                        "var_3": {
                            "masked": False,
                            "name": "var_3",
                            "protected": False,
                            "value": "var_3",
                            "variable_type": "env_var",
                            "warning": "",
                        },
                    },
                },
                "status": "updated",
            },
        },
        "property_name": "schedulers",
    }
    expected_to_dict = {
        "property_name": "schedulers",
        "differences": {
            "schedule_3": {
                "status": "removed",
                "before": {
                    "name": "schedule_3",
                    "branch": "master",
                    "cron": "* * * *",
                    "tz": "UTC",
                    "enabled": False,
                    "variables": {},
                    "api_id": "schedule_3",
                },
                "after": None,
            },
            "schedule_4": {
                "status": "updated",
                "before": {
                    "name": "schedule_4",
                    "branch": "master",
                    "cron": "* * * 0 0",
                    "tz": "UTC",
                    "enabled": True,
                    "variables": {
                        "var_1": {
                            "name": "var_1",
                            "protected": False,
                            "warning": "",
                            "variable_type": "file",
                            "masked": False,
                            "value": "var_1",
                        },
                        "var_2": {
                            "name": "var_2",
                            "protected": False,
                            "warning": "",
                            "variable_type": "env_var",
                            "masked": False,
                            "value": "v****2",
                        },
                        "var_3": {
                            "name": "var_3",
                            "protected": False,
                            "warning": "",
                            "variable_type": "env_var",
                            "masked": False,
                            "value": "var_3",
                        },
                    },
                    "api_id": "schedule_4",
                },
                "after": {
                    "name": "schedule_4",
                    "branch": "master",
                    "cron": "* * * 0 0",
                    "tz": "UTC",
                    "enabled": True,
                    "variables": {
                        "var_name": {
                            "name": "var_name",
                            "protected": False,
                            "warning": "",
                            "variable_type": "env_var",
                            "masked": False,
                            "value": "var_value",
                        },
                        "var_2": {
                            "name": "var_2",
                            "protected": False,
                            "warning": "",
                            "variable_type": "file",
                            "masked": False,
                            "value": "v****1",
                        },
                        "var_3": {
                            "name": "var_3",
                            "protected": False,
                            "warning": "",
                            "variable_type": "env_var",
                            "masked": False,
                            "value": "var_3",
                        },
                    },
                    "api_id": None,
                },
            },
            "schedule_5": {
                "status": "kept",
                "before": {
                    "name": "schedule_5",
                    "branch": "master",
                    "cron": "* * * * *",
                    "tz": "UTC",
                    "enabled": False,
                    "variables": {},
                    "api_id": "schedule_5",
                },
                "after": {
                    "name": "schedule_5",
                    "branch": "master",
                    "cron": "* * * * *",
                    "tz": "UTC",
                    "enabled": False,
                    "variables": {},
                    "api_id": None,
                },
            },
            "schedule_1": {
                "status": "added",
                "before": None,
                "after": {
                    "name": "schedule_1",
                    "branch": "master",
                    "cron": "* * * 0 0",
                    "tz": "UTC",
                    "enabled": True,
                    "variables": {
                        "var_name": {
                            "name": "var_name",
                            "protected": False,
                            "warning": "",
                            "variable_type": "env_var",
                            "masked": False,
                            "value": "var_value",
                        }
                    },
                    "api_id": None,
                },
            },
            "schedule_2": {
                "status": "added",
                "before": None,
                "after": {
                    "name": "schedule_2",
                    "branch": "master",
                    "cron": "* * * 0 0",
                    "tz": "UTC",
                    "enabled": True,
                    "variables": None,
                    "api_id": None,
                },
            },
        },
    }

    if not keep_schedulers:
        assert change_schedulers.diff_to_dict() == expected_diff_to_dict
        assert change_schedulers.to_dict() == expected_to_dict

    assert len(change_schedulers.after) == 4
    assert len(change_schedulers.before) == 3

    assert change_schedulers.differences["schedule_1"]["status"] == "added"
    assert change_schedulers.differences["schedule_2"]["status"] == "added"
    if keep_schedulers:
        assert change_schedulers.differences["schedule_3"]["status"] == "kept"
    else:
        assert change_schedulers.differences["schedule_3"]["status"] == "removed"

    assert change_schedulers.differences["schedule_4"]["status"] == "updated"
    assert change_schedulers.differences["schedule_5"]["status"] == "kept"
