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


@pytest.mark.parametrize(
    "run_mode, click_called, apply_called",
    [
        (RunMode.APPLY, False, True),
        (RunMode.DRY_RUN, False, False),
        (RunMode.INTERACTIVE, True, True),
        (RunMode.INTERACTIVE, False, False),
    ],
)
def test_run_mode(mocker, fake_gitlab, fake_project, run_mode, click_called, apply_called):
    # Mock
    apply_mock = mocker.patch(
        "gpc.tests.test_def_branch_visibility.ProjectRuleExecutor._apply_changes"
    )
    mocker.patch(
        "gpc.tests.test_def_branch_visibility.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    mocker.patch(
        "gpc.tests.test_def_branch_visibility.ProjectRuleExecutor._do_you_update",
        mocker.MagicMock(return_value=click_called),
    )

    project_rules = Namespace(
        {"default_branch": "master", "permissions": {"visibility": "private"}}
    )
    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(config=mocker.Mock("fake_config"), mode=run_mode),
    )
    p.execute()
    change_str = p.echo_execution()
    assert "master" in change_str
    assert apply_mock.called == apply_called

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
            "property_name": "permissions",
            "differences": {
                "before": {"visibility": "old_visibility"},
                "after": {"visibility": "private"},
                "action": "updated",
            },
        },
    ]
