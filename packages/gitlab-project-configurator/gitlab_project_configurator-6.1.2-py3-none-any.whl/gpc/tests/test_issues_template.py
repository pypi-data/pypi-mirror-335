"""
test_update issues template
---------------------------
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
    fake_project.issues_template = "old_issues_template"
    project_rules = Namespace(
        {
            "issues_template": "new_issues_template",
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
            "property_name": "issues_template",
            "differences": {
                "before": "old_issues_template",
                "after": "new_issues_template",
                "action": "updated",
            },
        },
    ]
