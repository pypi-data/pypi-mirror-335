"""
test_update protected branch/tag
----------------------------------
"""

# Third Party Libraries
import pytest

from dictns import Namespace
from dotmap import DotMap
from gitlab.v4.objects import Project  # pylint: disable=unused-import

# Gitlab-Project-Configurator Modules
from gpc.executors.approval_rules_executor import ApprovalRulesExecutor
from gpc.executors.approval_settings_executor import ApprovalSettingExecutor
from gpc.executors.approval_settings_executor import ApproverGroup
from gpc.executors.approval_settings_executor import ApproverUser
from gpc.executors.approval_settings_executor import ProjectApprovers
from gpc.helpers.exceptions import GpcMemberError
from gpc.helpers.exceptions import GpcUserError
from gpc.helpers.project_approval import ProjectApprovalRules
from gpc.parameters import GpcParameters
from gpc.parameters import RunMode
from gpc.project_rule_executor import ProjectRuleExecutor
from gpc.tests.test_helpers import get_change_value


# pylint: disable=redefined-outer-name, unused-argument, protected-access, duplicate-code
# flake8: noqa


def side_effet_user(username, retry_transient_errors):
    if username == "toto":
        return [Namespace({"id": 1234, "name": "toto", "username": "toto"})]
    if username == "gitlab-nestor-integ":
        return [Namespace({"id": 123, "name": "nestor-dev", "username": "gitlab-nestor-integ"})]
    raise GpcUserError("ERROR")


def side_effect_group(group, retry_transient_errors):
    if group == "test/group":
        return Namespace({"id": 666, "name": "test.group", "full_path": "test/group"})
    if group == "group/mock/test":
        return Namespace({"id": 123456, "name": "group_mock", "full_path": "group/mock/test"})
    raise GpcUserError("ERROR")


@pytest.mark.parametrize(
    "config_service, project_rules, expected_status, val_in_change, save_called",
    [
        (
            {
                "config_approvers": [
                    Namespace(
                        {
                            "id": 123,
                            "name": "nestor-dev",
                            "username": "gitlab-nestor-integ",
                        }
                    )
                ],
                "config_groups": [
                    Namespace(
                        {
                            "id": 123456,
                            "name": "group_mock",
                            "full_path": "group/mock/test",
                        }
                    )
                ],
                "approvals_before_merge": 1,
                "reset_approvals_on_push": True,
                "disable_overriding_approvers_per_merge_request": False,
                "merge_requests_disable_committers_approval": False,
            },
            Namespace(
                {
                    "approvers": {
                        "profiles": ["mytest_master_approvers"],
                        "minimum": 2,
                        "options": {
                            "can_override_approvals_per_merge_request": True,
                            "remove_all_approvals_when_new_commits_are_pushed": False,
                            "enable_committers_approvers": True,
                        },
                    },
                    "member_profiles": [
                        Namespace(
                            {
                                "name": "mytest_master_approvers",
                                "members": ["toto", "test/group"],
                            }
                        )
                    ],
                }
            ),
            "updated",
            "toto",
            True,
        ),
        (
            {
                "config_approvers": None,
                "config_groups": None,
                "approvals_before_merge": 1,
                "reset_approvals_on_push": True,
                "disable_overriding_approvers_per_merge_request": False,
            },
            Namespace(
                {
                    "approvers": {
                        "profiles": ["mytest_master_approvers"],
                        "minimum": 2,
                        "options": {
                            "can_override_approvals_per_merge_request": True,
                            "remove_all_approvals_when_new_commits_are_pushed": False,
                        },
                    },
                    "member_profiles": [
                        Namespace(
                            {
                                "name": "mytest_master_approvers",
                                "members": ["toto", "test/group"],
                            }
                        )
                    ],
                }
            ),
            "updated",
            "toto",
            True,
        ),
        (
            {
                "config_approvers": [
                    Namespace(
                        {
                            "id": 123,
                            "name": "nestor-dev",
                            "username": "gitlab-nestor-integ",
                        }
                    )
                ],
                "config_groups": [
                    Namespace(
                        {
                            "id": 123456,
                            "name": "group_mock",
                            "full_path": "group/mock/test",
                        }
                    )
                ],
                "approvals_before_merge": 1,
                "reset_approvals_on_push": True,
                "disable_overriding_approvers_per_merge_request": False,
            },
            Namespace(
                {
                    "approvers": {
                        "minimum": 2,
                        "options": {
                            "can_override_approvals_per_merge_request": True,
                            "remove_all_approvals_when_new_commits_are_pushed": False,
                        },
                    },
                    "member_profiles": [
                        Namespace(
                            {
                                "name": "mytest_master_approvers",
                                "members": ["toto", "test/group"],
                            }
                        )
                    ],
                }
            ),
            "updated",
            "gitlab-nestor-integ",
            True,
        ),
        (
            {
                "config_approvers": [
                    Namespace(
                        {
                            "id": 123,
                            "name": "nestor-dev",
                            "username": "gitlab-nestor-integ",
                        }
                    )
                ],
                "config_groups": [
                    Namespace(
                        {
                            "id": 123456,
                            "name": "group_mock",
                            "full_path": "group/mock/test",
                        }
                    )
                ],
                "approvals_before_merge": 1,
                "reset_approvals_on_push": True,
                "disable_overriding_approvers_per_merge_request": False,
            },
            Namespace(
                {
                    "approvers": {
                        "profiles": ["mytest_master_approvers"],
                        "minimum": 1,
                    },
                    "member_profiles": [
                        Namespace(
                            {
                                "name": "mytest_master_approvers",
                                "members": ["gitlab-nestor-integ", "group/mock/test"],
                            }
                        )
                    ],
                }
            ),
            "kept",
            "gitlab-nestor-integ",
            False,
        ),
        (
            {
                "config_approvers": [
                    Namespace(
                        {
                            "id": 123,
                            "name": "nestor-dev",
                            "username": "gitlab-nestor-integ",
                        }
                    )
                ],
                "config_groups": [
                    Namespace(
                        {
                            "id": 123456,
                            "name": "group_mock",
                            "full_path": "group/mock/test",
                        }
                    )
                ],
                "approvals_before_merge": 1,
                "reset_approvals_on_push": True,
                "disable_overriding_approvers_per_merge_request": False,
                "merge_requests_disable_committers_approval": True,
            },
            Namespace(
                {
                    "approvers": {
                        "profiles": ["mytest_master_approvers"],
                        "minimum": 1,
                        "options": {
                            "enable_committers_approvers": True,
                        },
                    },
                    "member_profiles": [
                        Namespace(
                            {
                                "name": "mytest_master_approvers",
                                "members": ["gitlab-nestor-integ", "group/mock/test"],
                            }
                        )
                    ],
                }
            ),
            "updated",
            "gitlab-nestor-integ",
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
    val_in_change,
    save_called,
):
    # Mock
    mocker.patch("gpc.tests.test_project_approvers.Project.save")
    mocker.patch(
        "gpc.tests.test_project_approvers.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )

    users_mock = mocker.Mock()
    users_mock.list = mocker.Mock(side_effect=side_effet_user)
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
    config.approvers.return_value = config_service.get("config_approvers", None)
    config.approver_groups = config_service.get("config_groups", None)
    config.save = mocker.Mock()
    mocker.patch(
        "gpc.executors.approval_settings_executor.ProjectApproval",
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
    change_str = p.echo_execution()
    change_approvers = get_change_value(p, "approvers")
    assert change_approvers.to_dict().get("differences").get("action") == expected_status
    assert val_in_change in change_str
    assert config.save.called == save_called


@pytest.mark.parametrize(
    "approve1, approve2, result",
    [
        (
            {
                "approvals_before_merge": 2,
                "reset_approvals_on_push": True,
                "disable_overriding": True,
                "users": {123: ApproverUser(123, "toto")},
                "groups": {1234: ApproverGroup(1234, "toto", "path/toto")},
            },
            {
                "approvals_before_merge": 2,
                "reset_approvals_on_push": True,
                "disable_overriding": True,
                "users": {123: ApproverUser(123, "toto")},
                "groups": {1234: ApproverGroup(1234, "toto", "path/toto")},
            },
            True,
        ),
        (
            {
                "approvals_before_merge": 2,
                "reset_approvals_on_push": True,
                "disable_overriding": True,
                "users": {123: ApproverUser(123, "toto")},
                "groups": {1234: ApproverGroup(1234, "toto", "path/toto")},
            },
            {
                "approvals_before_merge": 1,
                "reset_approvals_on_push": True,
                "disable_overriding": True,
                "users": {123: ApproverUser(123, "toto")},
                "groups": {1234: ApproverGroup(1234, "toto", "path/toto")},
            },
            False,
        ),
        (
            {
                "approvals_before_merge": 2,
                "reset_approvals_on_push": False,
                "disable_overriding": True,
                "users": {123: ApproverUser(123, "toto")},
                "groups": {1234: ApproverGroup(1234, "toto", "path/toto")},
            },
            {
                "approvals_before_merge": 2,
                "reset_approvals_on_push": True,
                "disable_overriding": True,
                "users": {123: ApproverUser(123, "toto")},
                "groups": {1234: ApproverGroup(1234, "toto", "path/toto")},
            },
            False,
        ),
        (
            {
                "approvals_before_merge": 2,
                "reset_approvals_on_push": True,
                "disable_overriding": True,
                "users": {123: ApproverUser(123, "toto")},
                "groups": {1234: ApproverGroup(1234, "toto", "path/toto")},
            },
            {
                "approvals_before_merge": 2,
                "reset_approvals_on_push": True,
                "disable_overriding": False,
                "users": {123: ApproverUser(123, "toto")},
                "groups": {1234: ApproverGroup(1234, "toto", "path/toto")},
            },
            False,
        ),
        (
            {
                "approvals_before_merge": 2,
                "reset_approvals_on_push": True,
                "disable_overriding": True,
                "users": {123: ApproverUser(123, "toto")},
                "groups": {1234: ApproverGroup(1234, "toto", "path/toto")},
            },
            {
                "approvals_before_merge": 2,
                "reset_approvals_on_push": True,
                "disable_overriding": True,
                "users": {124: ApproverUser(124, "toto")},
                "groups": {1234: ApproverGroup(1234, "toto", "path/toto")},
            },
            False,
        ),
        (
            {
                "approvals_before_merge": 2,
                "reset_approvals_on_push": True,
                "disable_overriding": True,
                "users": {123: ApproverUser(123, "toto")},
                "groups": {1234: ApproverGroup(1234, "toto", "path/toto")},
            },
            {
                "approvals_before_merge": 2,
                "reset_approvals_on_push": True,
                "disable_overriding": True,
                "users": {123: ApproverUser(123, "tata")},
                "groups": {1234: ApproverGroup(1234, "toto", "path/toto")},
            },
            False,
        ),
        (
            {
                "approvals_before_merge": 2,
                "reset_approvals_on_push": True,
                "disable_overriding": True,
                "users": {123: ApproverUser(123, "toto")},
                "groups": {1234: ApproverGroup(1234, "toto", "path/toto")},
            },
            {
                "approvals_before_merge": 2,
                "reset_approvals_on_push": True,
                "disable_overriding": True,
                "users": {123: ApproverUser(123, "toto")},
                "groups": {12345: ApproverGroup(12345, "toto", "path/toto")},
            },
            False,
        ),
        (
            {
                "approvals_before_merge": 2,
                "reset_approvals_on_push": True,
                "disable_overriding": True,
                "users": {123: ApproverUser(123, "toto")},
                "groups": {1234: ApproverGroup(1234, "toto", "path/toto")},
            },
            {
                "approvals_before_merge": 2,
                "reset_approvals_on_push": True,
                "disable_overriding": True,
                "users": {123: ApproverUser(123, "toto")},
                "groups": {},
            },
            False,
        ),
    ],
)
def test_eq_project_approvers(approve1, approve2, result):
    project_approvers1 = ProjectApprovers()
    project_approvers1.users = approve1.get("users")
    project_approvers1.groups = approve1.get("groups")
    project_approvers1.approvals_before_merge = approve1.get("approvals_before_merge")
    project_approvers1.reset_approvals_on_push = approve1.get("reset_approvals_on_push")
    project_approvers1.can_override_approvals_per_merge_request = approve1.get("disable_overriding")

    project_approvers2 = ProjectApprovers()
    project_approvers2.users = approve2.get("users")
    project_approvers2.groups = approve2.get("groups")
    project_approvers2.approvals_before_merge = approve2.get("approvals_before_merge")
    project_approvers2.reset_approvals_on_push = approve2.get("reset_approvals_on_push")
    project_approvers2.can_override_approvals_per_merge_request = approve2.get("disable_overriding")
    assert (project_approvers1 == project_approvers2) == result


def test_approvers_result(mocker):
    manager = mocker.Mock()
    manager.approvers = mocker.Mock(return_value=[{"id": 12}, {"id": 28}, {"id": 42}, {"id": 59}])
    approvers = mocker.Mock()
    approvers.users = {
        12: DotMap(name="poussin.piou"),
        28: DotMap(name="poule.cotcot"),
        42: DotMap(name="coq.cocorico"),
        48: DotMap(name="dinde.glouglouglou"),
        59: DotMap(name="pigeon.roucoule"),
    }
    approvers.get_users = mocker.Mock(return_value=list(approvers.users.keys()))
    executor = ApprovalSettingExecutor(None, "project/path", None, None, None)
    with pytest.raises(GpcMemberError) as e:
        user_errors = executor._check_approvers(approvers, manager)
        assert user_errors
        executor._approver_raise_user_errors(user_errors)
    assert (
        str(e.value) == "For the project 'project/path', "
        "these users can not be added as approvers: dinde.glouglouglou."
        "\nPlease check that these users are members "
        "of the project, or the parent project."
    )


def test_multiple_rules(mocker):
    project = mocker.Mock()

    user1 = {"id": 123}
    user2 = {"id": 456}
    user3 = {"id": 789}
    user4 = {"id": 90}

    approvalrules_config_a = mocker.Mock()
    approvalrules_config_a.id = 1
    approvalrules_config_a.users = [user1, user2]
    approvalrules_config_a.groups = [789]
    approvalrules_config_a.approvals_required = 2
    approvalrules_config_a.attributes = {"id": approvalrules_config_a.id}

    approvalrules_config_b = mocker.Mock()
    approvalrules_config_b.id = 2
    approvalrules_config_b.users = [user1, user3, user4]
    approvalrules_config_b.groups = [765]
    approvalrules_config_b.approvals_required = 1
    approvalrules_config_b.attributes = {"id": approvalrules_config_b.id}

    approvalrules = mocker.Mock()
    approvalrules.list = mocker.Mock(return_value=[approvalrules_config_a, approvalrules_config_b])

    project.approvalrules = approvalrules

    manager = ProjectApprovalRules(project)

    approvers = mocker.Mock()

    executor = ApprovalRulesExecutor(None, "project/path", None, None, None)

    # test rule 1
    approvers.users = [user1["id"], user2["id"]]

    user_errors = executor._check_approvers(approvers, manager, 1)

    assert len(user_errors) == 0

    # test rule 2
    approvers.users = [user1["id"], user3["id"], user4["id"]]

    user_errors = executor._check_approvers(approvers, manager, 2)

    assert len(user_errors) == 0
