"""
test_update protected branch/tag
----------------------------------
"""

# Standard Library
import re

# Third Party Libraries
import pytest

from dictns import Namespace
from gitlab.v4.objects import Project  # pylint: disable=unused-import

# Gitlab-Project-Configurator Modules
from gpc.executors.variables_setting_executor import REGEX_MASKED_VARIABLE
from gpc.executors.variables_setting_executor import ItemVariable
from gpc.executors.variables_setting_executor import VariablesSettingExecutor
from gpc.parameters import GpcParameters
from gpc.parameters import RunMode
from gpc.project_rule_executor import ProjectRuleExecutor
from gpc.tests.test_helpers import get_change_value
from gpc.tests.test_helpers import get_executor


# pylint: disable=redefined-outer-name, unused-argument, protected-access, duplicate-code


def test_project_variable():
    pv = ItemVariable(name="TOTO", protected=False, value="")
    assert pv.value_hidden == "Not defined"
    pv = ItemVariable(name="TOTO", protected=False, value=None)
    assert pv.value_hidden == "Not defined"
    pv = ItemVariable(name="TOTO", protected=False, value="t")
    assert pv.value_hidden == "***"
    pv = ItemVariable(name="TOTO", protected=False, value="to")
    assert pv.value_hidden == "***"
    pv = ItemVariable(name="TOTO", protected=False, value="totototo")
    assert pv.value_hidden == "t****o"


def test_no_change_variables(mocker, fake_project, fake_gitlab):
    # Mock
    mocker.patch("gpc.tests.test_variables.Project.save")
    mocker.patch(
        "gpc.tests.test_variables.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )

    variables = mocker.Mock()
    variables.list = mocker.Mock(
        return_value=[
            Namespace(
                {
                    "key": "ENV_2",
                    "value": "toto12",
                    "protected": "True",
                    "variable_type": "env_var",
                }
            )
        ]
    )
    fake_project.variables = variables

    project_rules = Namespace(
        {
            "variables": [
                {
                    "name": "ENV_2",
                    "value": "toto12",
                    "protected": "True",
                    "variable_type": "env_var",
                }
            ]
        }
    )

    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(config=mocker.Mock("fake_config"), mode=RunMode.APPLY),
    )
    p.execute()
    change_variables = get_change_value(p, "variables")
    variables_setting_executor = [
        e for e in p.executors if isinstance(e, VariablesSettingExecutor)
    ][0]
    assert variables_setting_executor.changes[0].action == "kept"
    assert len(change_variables.differences) == 1
    assert change_variables.differences.get("ENV_2").get("status") == "kept"


def test_add_new_variable(mocker, fake_project, fake_gitlab):
    # Mock
    mocker.patch("gpc.tests.test_variables.Project.save")
    mocker.patch(
        "gpc.tests.test_variables.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )

    variables = mocker.Mock()
    variables.list = mocker.Mock(return_value=[])
    fake_project.variables = variables

    project_rules = Namespace(
        {
            "variables": [
                {
                    "name": "ENV_1",
                    "value": "toto12",
                    "protected": "True",
                    "variable_type": "env_var",
                }
            ]
        }
    )

    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(config=mocker.Mock("fake_config"), mode=RunMode.APPLY),
    )
    p.execute()
    change_variables = get_change_value(p, "variables")
    variables_setting_executor = [
        e for e in p.executors if isinstance(e, VariablesSettingExecutor)
    ][0]
    assert variables_setting_executor.changes[0].action == "added"
    assert len(change_variables.differences) == 1
    assert change_variables.differences.get("ENV_1").get("status") == "added"


def test_remove_existing_variable(mocker, fake_project, fake_gitlab):
    # Mock
    mocker.patch("gpc.tests.test_variables.Project.save")
    mocker.patch(
        "gpc.tests.test_variables.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )

    variables = mocker.Mock()
    variables.list = mocker.Mock(
        return_value=[
            Namespace(
                {
                    "key": "ENV_1",
                    "value": "toto12",
                    "protected": "True",
                    "variable_type": "env_var",
                }
            )
        ]
    )
    fake_project.variables = variables

    project_rules = Namespace({"keep_existing_variables": False, "variables": []})

    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(config=mocker.Mock("fake_config"), mode=RunMode.APPLY),
    )
    p.execute()
    change_variables = get_change_value(p, "variables")
    variables_setting_executor = [
        e for e in p.executors if isinstance(e, VariablesSettingExecutor)
    ][0]
    assert variables_setting_executor.changes[0].action == "removed"
    assert len(change_variables.after) == 0
    assert change_variables.differences.get("ENV_1").get("status") == "removed"


@pytest.mark.parametrize("keep_variables", [True, False])
def test_variables(monkeypatch, keep_variables, mocker, fake_gitlab, fake_project):
    # Mock
    mocker.patch("gpc.tests.test_variables.Project.save")
    mocker.patch(
        "gpc.tests.test_variables.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    mock_manager_variable = mocker.patch(
        "gitlab.v4.objects.ProjectVariableManager.create", mocker.Mock()
    )
    monkeypatch.setenv("ENV_2", "masked_test")
    variables = mocker.Mock()
    variables.list = mocker.Mock(
        return_value=[
            Namespace(
                {
                    "key": "ENV_2",
                    "value": "toto12",
                    "protected": "True",
                    "variable_type": "env_var",
                }
            ),
            Namespace(
                {
                    "key": "ENV_3",
                    "value": "env3",
                    "protected": "True",
                    "variable_type": "env_var",
                }
            ),
            Namespace(
                {
                    "key": "ENV_4",
                    "value": "env4env4",
                    "protected": "True",
                    "variable_type": "env_var",
                }
            ),
        ]
    )
    fake_project.variables = variables

    project_rules = Namespace(
        {
            "keep_existing_variables": keep_variables,
            "variables": [
                {"name": "ENV_1", "value": "env_1", "protected": False},
                {
                    "name": "ENV_2",
                    "value_from_envvar": "ENV_2",
                    "protected": True,
                    "variable_type": "file",
                    "masked": True,
                },
                {"name": "ENV_3", "value": None},
                {
                    "import": "SOME_PROFILE_NAME",
                },
            ],
            "variable_profiles": {
                "SOME_PROFILE_NAME": [
                    {
                        "name": "some_name",
                        "masked": True,
                        "value": "somevalue13",
                    }
                ]
            },
        }
    )

    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(config=mocker.Mock("fake_config"), mode=RunMode.APPLY),
    )
    p.execute()
    change_variables = get_change_value(p, "variables")
    assert len(change_variables.differences) == 5

    if keep_variables:
        assert change_variables.differences.get("ENV_2").get("status") == "updated"
        assert change_variables.differences.get("ENV_2").get("before").get("value") == "t****2"
        assert change_variables.differences.get("ENV_2").get("after").get("value") == "m****t"

        assert change_variables.differences.get("ENV_3").get("status") == "removed"

        assert change_variables.differences.get("ENV_1").get("status") == "added"

        assert change_variables.differences.get("ENV_4").get("status") == "kept"
        assert change_variables.differences.get("ENV_4").get("before").get("value") == "e****4"
        assert change_variables.differences.get("ENV_4").get("after").get("value") == "e****4"
    else:
        assert change_variables.after[0].name == "ENV_1"
        assert change_variables.after[0].value == "env_1"
        assert not change_variables.after[0].is_hidden
        assert change_variables.after[1].name == "ENV_2"
        assert change_variables.after[1].value == "masked_test"
        assert change_variables.after[1].value_hidden == "m****t"
        assert change_variables.after[1].variable_type == "file"
        assert change_variables.after[1].is_hidden
        assert change_variables.differences.get("ENV_1").get("status") == "added"
        assert change_variables.differences.get("ENV_2").get("after").get("value") == "m****t"
        assert change_variables.differences.get("ENV_2").get("before").get("value") == "t****2"
        assert change_variables.differences.get("ENV_3").get("status") == "removed"
        assert change_variables.differences.get("some_name").get("status") == "added"
        assert (
            change_variables.differences.get("some_name").get("after").get("value") == "somevalue13"
        )
        assert change_variables.differences.get("some_name").get("after").get("masked")
        assert change_variables.differences.get("ENV_4").get("status") == "removed"
        assert mock_manager_variable.is_called


def test_variables_ko(mocker, monkeypatch, fake_gitlab, fake_project):
    # Mock
    mocker.patch("gpc.tests.test_variables.Project.save")
    mocker.patch(
        "gpc.tests.test_variables.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    monkeypatch.setenv("ENV_2", "env_2")
    variables = mocker.Mock()
    variables.list = mocker.Mock(
        return_value=[
            Namespace({"key": "ENV_2", "value": "toto12", "protected": "True"}),
            Namespace({"key": "ENV_3", "value": "env3", "protected": "True"}),
            Namespace({"key": "ENV_4", "value": "env4", "protected": "True"}),
        ]
    )
    fake_project.variables = variables

    project_rules = Namespace(
        {
            "variables": [
                {"name": "ENV_1", "value": "env_1", "protected": False},
                {"name": "ENV_2", "value_from_envvar": "ENV_2", "protected": True},
                {"name": "ENV_4", "value_from_envvar": "ENV_4", "protected": True},
                {"name": "ENV_3", "value": None},
            ]
        }
    )

    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(config=mocker.Mock("fake_config"), mode=RunMode.APPLY),
    )
    success = p.execute()
    assert not success
    executor = get_executor(p, VariablesSettingExecutor)
    assert executor.error_message == "/!\\ Environment variable ENV_4 not found."


@pytest.mark.parametrize("value", ["123", "12345678\n"], ids=["too_short", "with_return"])
def test_variables_ko_masked(value, mocker, fake_gitlab, fake_project):
    # Mock
    mocker.patch("gpc.tests.test_variables.Project.save")
    mocker.patch(
        "gpc.tests.test_variables.ItemVariable.to_item_variables",
        mocker.Mock(return_value=[]),
    )
    mocker.patch(
        "gpc.tests.test_variables.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )

    project_rules = Namespace({"variables": [{"name": "ENV_1", "value": value, "masked": True}]})

    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(config=mocker.Mock("fake_config"), mode=RunMode.APPLY),
    )
    success = p.execute()
    assert not success
    executor = get_executor(p, VariablesSettingExecutor)
    assert executor.error_message == (
        "The 'ENV_1' value does not respect the requirements for masked variable. "
        "See the requirements here: "
        "https://docs.gitlab.com/ee/ci/variables/index.html#mask-a-cicd-variable"
    )


def test_variables_warning(mocker, tmp_path, monkeypatch, fake_gitlab, fake_project):
    # Mock
    mocker.patch("gpc.tests.test_variables.Project.save")
    mocker.patch(
        "gpc.tests.test_variables.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    mock_manager_variable = mocker.patch(
        "gitlab.v4.objects.ProjectVariableManager.create", mocker.Mock()
    )
    env_file = tmp_path / "file_1234.txt"
    env_file.write_text("important value", encoding="utf-8")
    monkeypatch.setenv("ENV_2", "masked_test")
    monkeypatch.setenv("ENV_1234", str(env_file))
    variables = mocker.Mock()
    variables.list = mocker.Mock(
        return_value=[
            Namespace(
                {
                    "key": "ENV_2",
                    "value": "toto12",
                    "protected": "True",
                    "variable_type": "env_var",
                }
            ),
            Namespace(
                {
                    "key": "ENV_3",
                    "value": "env3",
                    "protected": "True",
                    "variable_type": "env_var",
                }
            ),
            Namespace(
                {
                    "key": "ENV_4",
                    "value": "env4",
                    "protected": "True",
                    "variable_type": "env_var",
                }
            ),
        ]
    )
    fake_project.variables = variables

    project_rules = Namespace(
        {
            "variables": [
                {"name": "ENV_1", "value": "env_1", "protected": False},
                {"name": "ENV_2", "value_from_envvar": "ENV_2", "protected": True, "masked": True},
                {"name": "ENV_4", "value_from_envvar": "ENV_4", "protected": True},
                {"name": "ENV_3", "value": None},
                {"name": "ENV_1234", "value_from_envvar": "ENV_1234", "variable_type": "file"},
            ]
        }
    )

    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(config=mocker.Mock("fake_config"), mode=RunMode.DRY_RUN),
    )
    p.execute()
    change_variables = get_change_value(p, "variables")
    p.echo_execution()
    assert len(change_variables.after) == 5
    assert change_variables.after[0].name == "ENV_1"
    assert change_variables.after[0].value == "env_1"
    assert not change_variables.after[0].is_hidden
    assert change_variables.after[1].name == "ENV_1234"
    assert change_variables.after[1].value == "important value"
    assert change_variables.after[1].value_hidden == "i****e"
    assert change_variables.after[1].is_hidden
    assert change_variables.after[2].name == "ENV_2"
    assert change_variables.after[2].value == "masked_test"
    assert change_variables.after[2].value_hidden == "m****t"
    assert change_variables.after[2].is_hidden
    assert change_variables.differences.get("ENV_1").get("status") == "added"
    assert change_variables.differences.get("ENV_1234").get("status") == "added"
    assert not change_variables.differences.get("ENV_1234").get("before")
    assert change_variables.differences.get("ENV_1234").get("after").get("value") == "i****e"
    assert change_variables.differences.get("ENV_2").get("after").get("value") == "m****t"
    assert change_variables.differences.get("ENV_2").get("before").get("value") == "t****2"
    assert change_variables.differences.get("ENV_3").get("status") == "removed"
    assert change_variables.differences.get("ENV_4").get("status") == "warning"
    assert mock_manager_variable.is_called


def test_masked_regex():
    assert re.match(REGEX_MASKED_VARIABLE, "thisisgood")  # min 8 ascii ok
    assert re.match(REGEX_MASKED_VARIABLE, "goodwith@and:")
    assert re.match(REGEX_MASKED_VARIABLE, "goodwith-and_")
    assert not re.match(REGEX_MASKED_VARIABLE, "bad")  # too short
    assert not re.match(REGEX_MASKED_VARIABLE, "badwith#")  # invalid char
