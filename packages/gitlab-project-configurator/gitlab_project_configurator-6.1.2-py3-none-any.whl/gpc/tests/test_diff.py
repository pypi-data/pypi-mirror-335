"""
test_update default branch and visibility
----------------------------------
"""

# Third Party Libraries
import pytest

from dictns import Namespace

# Gitlab-Project-Configurator Modules
from gpc.parameters import GpcParameters
from gpc.parameters import RunMode
from gpc.project_rule_executor import ProjectRuleExecutor


# pylint: disable=redefined-outer-name, unused-argument, protected-access, duplicate-code
# flake8: noqa


@pytest.mark.parametrize(
    "config_rule, expected_str, not_expected_str, diff_json_expected",
    [
        (
            {"default_branch": "old_default_branch"},
            "No changes found.",
            None,
            {},
        ),
        (
            {
                "default_branch": "old_default_branch",
                "permissions": {"visibility": "private"},
                "labels": [
                    {"name": "label1", "color": "#FF0000"},
                    {"name": "label2", "color": "#FF0001"},
                    {"name": "label3", "color": "#FF0001"},
                ],
            },
            "private",
            "old_default_branch",
            {
                "permissions": {
                    "property_name": "permissions",
                    "differences": {
                        "before": {"visibility": "old_visibility"},
                        "after": {"visibility": "private"},
                        "action": "updated",
                    },
                },
                "labels": {
                    "property_name": "labels",
                    "differences": {
                        "label3": {
                            "status": "updated",
                            "before": {"name": "label3", "color": "#FF0000"},
                            "after": {"name": "label3", "color": "#FF0001"},
                        },
                        "label2": {
                            "status": "added",
                            "before": None,
                            "after": {"name": "label2", "color": "#FF0001"},
                        },
                    },
                },
            },
        ),
    ],
)
def test_diff(
    mocker,
    fake_gitlab,
    fake_project,
    config_rule,
    expected_str,
    not_expected_str,
    diff_json_expected,
):
    # Mock
    mocker.patch("gpc.tests.test_def_branch_visibility.ProjectRuleExecutor._apply_changes")
    mocker.patch(
        "gpc.tests.test_def_branch_visibility.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    labels = mocker.Mock()

    labels.list = mocker.Mock(
        return_value=[
            Namespace({"name": "label1", "color": "#FF0000"}),
            Namespace({"name": "label3", "color": "#FF0000"}),
            Namespace({"name": "label4", "color": "#FF0000"}),
        ]
    )
    fake_project.labels = labels
    project_rules = Namespace(config_rule)
    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(
            config=mocker.Mock("fake_config"), mode=RunMode.DRY_RUN, diff=True
        ),
    )
    p.update_settings()
    change_str = p.echo_execution()
    assert expected_str in change_str
    if not_expected_str:
        assert not_expected_str not in change_str
    diff_json = p.get_diff_json()
    assert diff_json == diff_json_expected
