"""
test_update project description
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


# pylint: disable=redefined-outer-name, unused-argument, protected-access, duplicate-code


@pytest.mark.parametrize(
    "action, old_val, new_val",
    [("updated", 30, 20), ("kept", 0, None), ("added", 0, 20)],
)
def test_update_project_git_shallow(mocker, fake_gitlab, fake_project, action, old_val, new_val):
    # Mock
    mocker.patch("gpc.tests.test_project_ci_git_shallow_clone.Project.save")
    mocker.patch(
        "gpc.tests.test_project_ci_git_shallow_clone.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    fake_project.ci_default_git_depth = old_val
    project_rules = Namespace(
        {
            "default_branch": "master",
            "ci_git_shallow_clone": new_val,
        }
    )
    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(config=mocker.Mock("fake_config"), mode=RunMode.APPLY),
    )
    p.update_settings()
    if old_val == 0:
        old_val = None
    if new_val == 0:
        new_val = None
    assert p.get_changes_json() == [
        {
            "property_name": "ci_git_shallow_clone",
            "differences": {
                "before": old_val,
                "after": new_val,
                "action": action,
            },
        },
        {
            "property_name": "default_branch",
            "differences": {
                "before": "old_default_branch",
                "after": "master",
                "action": "updated",
            },
        },
    ]
