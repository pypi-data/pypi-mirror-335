"""
test_update project description
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


def test_update_project_description(mocker, fake_gitlab, fake_project):
    # Mock
    mocker.patch("gpc.tests.test_project_description.Project.save")
    mocker.patch(
        "gpc.tests.test_project_description.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    fake_project.description = "old_description"
    project_rules = Namespace(
        {
            "default_branch": "master",
            "description": "new_description",
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
            "property_name": "default_branch",
            "differences": {
                "before": "old_default_branch",
                "after": "master",
                "action": "updated",
            },
        },
        {
            "property_name": "description",
            "differences": {
                "before": "old_description",
                "after": "new_description",
                "action": "updated",
            },
        },
    ]
