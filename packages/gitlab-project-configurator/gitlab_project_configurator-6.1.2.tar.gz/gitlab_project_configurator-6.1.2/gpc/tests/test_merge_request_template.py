"""
test_update merge requests template
-----------------------------------
"""

# Third Party Libraries
from dictns import Namespace
from gitlab.v4.objects import Project  # pylint: disable=unused-import

# Gitlab-Project-Configurator Modules
from gpc.parameters import GpcParameters
from gpc.parameters import RunMode
from gpc.project_rule_executor import ProjectRuleExecutor


# pylint: disable=redefined-outer-name, unused-argument, protected-access, duplicate-code


def test_update_merge_request_template(mocker, fake_gitlab, fake_project):
    # Mock
    mocker.patch("gpc.tests.test_project_description.Project.save")
    mocker.patch(
        "gpc.tests.test_project_description.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    fake_project.merge_requests_template = "old_merge_requests_template"
    project_rules = Namespace(
        {
            "mergerequests": {
                "default_template": "new_merge_requests_template",
            }
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
            "differences": {
                "action": "updated",
                "after": {"merge_requests_template": "new_merge_requests_template"},
                "before": {"merge_requests_template": "old_merge_requests_template"},
            },
            "property_name": "mergerequests",
        },
    ]
