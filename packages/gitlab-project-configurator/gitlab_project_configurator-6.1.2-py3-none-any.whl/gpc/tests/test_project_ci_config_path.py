"""
test_update project ci_config_path
----------------------------------
"""

# Third Party Libraries
from dictns import Namespace
from gitlab.v4.objects import Project  # pylint: disable=unused-import

# Gitlab-Project-Configurator Modules
from gpc.parameters import GpcParameters
from gpc.parameters import RunMode
from gpc.project_rule_executor import ProjectRuleExecutor


# pylint: disable=redefined-outer-name, unused-argument, protected-access, duplicate-code


def test_update_project_ci_config_path(mocker, fake_gitlab, fake_project):
    # Mock
    mocker.patch("gpc.tests.test_project_ci_config_path.Project.save")
    mocker.patch(
        "gpc.tests.test_project_ci_config_path.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    fake_project.ci_config_path = "old_ci_config_path"
    project_rules = Namespace(
        {
            "ci_config_path": "new_ci_config_path",
        }
    )
    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(config=mocker.Mock("fake_config"), mode=RunMode.APPLY),
    )
    p.update_settings()

    assert p.get_changes_json() == [
        {
            "property_name": "ci_config_path",
            "differences": {
                "before": "old_ci_config_path",
                "after": "new_ci_config_path",
                "action": "updated",
            },
        },
    ]
