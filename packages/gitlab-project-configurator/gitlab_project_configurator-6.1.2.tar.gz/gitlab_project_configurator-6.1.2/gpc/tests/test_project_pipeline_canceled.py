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
    "project_value, auto_cancel_pending_pipelines, expected_diff",
    [
        (
            None,
            "enabled",
            {
                "property_name": "auto_cancel_pending_pipelines",
                "differences": {
                    "before": None,
                    "after": "enabled",
                    "action": "added",
                },
            },
        ),
        (
            "disabled",
            "enabled",
            {
                "property_name": "auto_cancel_pending_pipelines",
                "differences": {
                    "before": "disabled",
                    "after": "enabled",
                    "action": "updated",
                },
            },
        ),
    ],
)
def test_update_project_pipeline_canceled(
    mocker,
    fake_gitlab,
    fake_project,
    project_value,
    auto_cancel_pending_pipelines,
    expected_diff,
):
    # Mock
    mocker.patch("gpc.tests.test_project_description.Project.save")
    mocker.patch(
        "gpc.tests.test_project_description.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    fake_project.auto_cancel_pending_pipelines = project_value
    project_rules = Namespace(
        {
            "default_branch": "master",
            "auto_cancel_pending_pipelines": auto_cancel_pending_pipelines,
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
        expected_diff,
        {
            "property_name": "default_branch",
            "differences": {
                "before": "old_default_branch",
                "after": "master",
                "action": "updated",
            },
        },
    ]
