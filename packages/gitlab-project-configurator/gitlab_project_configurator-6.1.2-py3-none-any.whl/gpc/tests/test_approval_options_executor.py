"""
test_update protected branch/tag
----------------------------------
"""

# Third Party Libraries
import pytest

from dictns import Namespace
from gitlab.v4.objects import Project  # pylint: disable=unused-import

# Gitlab-Project-Configurator Modules
from gpc.helpers.exceptions import GpcUserError
from gpc.parameters import GpcParameters
from gpc.parameters import RunMode
from gpc.project_rule_executor import ProjectRuleExecutor
from gpc.tests.test_helpers import get_change_value


# pylint: disable=redefined-outer-name, unused-argument, protected-access, duplicate-code
# flake8: noqa


def side_effect_user(username):
    if username == "toto":
        return [Namespace({"id": 1234, "name": "toto", "username": "toto"})]
    if username == "gitlab-nestor-integ":
        return [Namespace({"id": 123, "name": "nestor-dev", "username": "gitlab-nestor-integ"})]
    raise GpcUserError("ERROR")


def side_effect_group(group):
    if group == "test/group":
        return Namespace({"id": 666, "name": "test.group", "full_path": "test/group"})
    if group == "group/mock/test":
        return Namespace({"id": 123456, "name": "group_mock", "full_path": "group/mock/test"})
    raise GpcUserError("ERROR")


@pytest.mark.parametrize(
    "config_service, project_rules, expected_status, save_called",
    [
        (
            {
                "reset_approvals_on_push": True,
                "disable_overriding_approvers_per_merge_request": False,
                "merge_requests_disable_committers_approval": False,
            },
            Namespace(
                {
                    "approval_settings": {
                        "can_override_approvals_per_merge_request": True,
                        "remove_all_approvals_when_new_commits_are_pushed": False,
                        "enable_committers_approvers": True,
                    },
                }
            ),
            "updated",
            True,
        ),
        (
            {
                "reset_approvals_on_push": True,
                "disable_overriding_approvers_per_merge_request": False,
            },
            Namespace(
                {
                    "approval_settings": {
                        "can_override_approvals_per_merge_request": True,
                        "remove_all_approvals_when_new_commits_are_pushed": False,
                    },
                }
            ),
            "updated",
            True,
        ),
        (
            {
                "reset_approvals_on_push": True,
                "disable_overriding_approvers_per_merge_request": False,
            },
            Namespace(
                {
                    "approval_settings": {
                        "can_override_approvals_per_merge_request": True,
                        "remove_all_approvals_when_new_commits_are_pushed": False,
                    },
                }
            ),
            "updated",
            True,
        ),
        (
            {
                "reset_approvals_on_push": True,
                "disable_overriding_approvers_per_merge_request": False,
            },
            Namespace(
                {
                    "approval_settings": {
                        "reset_approvals_on_push": True,
                        "disable_overriding_approvers_per_merge_request": False,
                    },
                }
            ),
            "kept",
            False,
        ),
        (
            {
                "reset_approvals_on_push": True,
                "disable_overriding_approvers_per_merge_request": False,
                "merge_requests_disable_committers_approval": True,
            },
            Namespace(
                {
                    "approval_settings": {
                        "enable_committers_approvers": True,
                    },
                }
            ),
            "updated",
            True,
        ),
        (
            {
                "reset_approvals_on_push": False,
                "selective_code_owner_removals": True,
                "disable_overriding_approvers_per_merge_request": False,
                "merge_requests_author_approval": False,
                "merge_requests_disable_committers_approval": False,
            },
            Namespace(
                {
                    "approval_settings": {
                        "disable_overriding_approvers_per_merge_request": True,
                        "reset_approvals_on_push": True,
                        "selective_code_owner_removals": False,
                        "enable_self_approval": False,
                        "enable_committers_approvers": False,
                    },
                }
            ),
            "updated",
            True,
        ),
    ],
)
def test_project_approvers(
    mocker,
    fake_gitlab,
    fake_project,
    config_service,
    project_rules,
    expected_status,
    save_called,
):
    # Mock
    mocker.patch("gpc.tests.test_project_approvers.Project.save")
    mocker.patch(
        "gpc.tests.test_project_approvers.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )

    users_mock = mocker.Mock()
    users_mock.list = mocker.Mock(side_effect=side_effect_user)
    groups_mock = mocker.Mock()
    groups_mock.get = mocker.Mock(side_effect=side_effect_group)
    fake_gitlab.users = users_mock
    fake_gitlab.groups = groups_mock
    config = mocker.Mock()
    config.approvals_before_merge = config_service.get("approvals_before_merge", None)
    config.reset_approvals_on_push = config_service.get("reset_approvals_on_push", None)
    config.disable_overriding_approvers_per_merge_request = config_service.get(
        "disable_overriding_approvers_per_merge_request", None
    )
    config.enable_committers_approvers = not config_service.get(
        "merge_requests_disable_committers_approval", None
    )
    config.save = mocker.Mock()
    mocker.patch(
        "gpc.executors.approval_options_executor.ProjectApprovalSettings",
        mocker.Mock(return_value=config),
    )

    p = ProjectRuleExecutor(
        fake_gitlab,
        "fake/path/to/project",
        project_rules,
        gpc_params=GpcParameters(
            mocker.Mock("fake_config"),
            config_project_url="new project url",
            gpc_enabled_badge_url="new image url",
            mode=RunMode.APPLY,
        ),
    )
    p.execute()
    change_approvers = get_change_value(p, "approval_settings")
    assert change_approvers.to_dict().get("differences").get("action") == expected_status
    assert config.save.called == save_called
