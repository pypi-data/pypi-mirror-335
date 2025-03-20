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


def test_update_artifacts_keep_latest(mocker, fake_gitlab, fake_project):
    # Mock
    mocker.patch("gpc.tests.test_artifacts_keep_latest.Project.save")
    mocker.patch(
        "gpc.tests.test_artifacts_keep_latest.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    fake_project.keep_latest_artifact = True
    project_rules = Namespace({"artifacts": {"keep_latest_artifact": False}})
    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(config=mocker.Mock("fake_config"), mode=RunMode.APPLY),
    )
    p.update_settings()

    assert p.get_changes_json() == [
        {
            "property_name": "artifacts",
            "differences": {
                "before": {"keep_latest_artifact": True},
                "after": {"keep_latest_artifact": False},
                "action": "updated",
            },
        }
    ]
