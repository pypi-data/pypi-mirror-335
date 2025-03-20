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
from gpc.executors.approval_rules_executor import ApproverGroup
from gpc.executors.approval_rules_executor import ApproverUser
from gpc.executors.approval_rules_executor import ProjectApproversRules
from gpc.helpers.exceptions import GpcMemberError
from gpc.helpers.exceptions import GpcUserError
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
    executor = ApprovalRulesExecutor(None, "project/path", None, None, None)
    with pytest.raises(GpcMemberError) as e:
        user_errors = executor._check_approvers(approvers, manager)
        assert executor._approver_raise_user_errors(user_errors)
    assert (
        str(e.value) == "For the project 'project/path', "
        "these users can not be added as approvers: dinde.glouglouglou."
        "\nPlease check that these users are members "
        "of the project, or the parent project."
    )


@pytest.mark.parametrize(
    "approve1, approve2, result",
    [
        (
            {
                "name": "rule",
                "approvals_before_merge": 2,
                "users": {123: ApproverUser(123, "toto")},
                "groups": {1234: ApproverGroup(1234, "toto", "path/toto")},
            },
            {
                "name": "rule",
                "approvals_before_merge": 2,
                "users": {123: ApproverUser(123, "toto")},
                "groups": {1234: ApproverGroup(1234, "toto", "path/toto")},
            },
            True,
        ),
        (
            {
                "name": "rule",
                "approvals_before_merge": 2,
                "users": {123: ApproverUser(123, "toto")},
                "groups": {1234: ApproverGroup(1234, "toto", "path/toto")},
            },
            {
                "name": "rule",
                "approvals_before_merge": 1,
                "users": {123: ApproverUser(123, "toto")},
                "groups": {1234: ApproverGroup(1234, "toto", "path/toto")},
            },
            False,
        ),
        (
            {
                "name": "rule",
                "approvals_before_merge": 2,
                "users": {123: ApproverUser(123, "toto")},
                "groups": {1234: ApproverGroup(1234, "toto", "path/toto")},
            },
            {
                "name": "rule",
                "approvals_before_merge": 2,
                "users": {124: ApproverUser(124, "toto")},
                "groups": {1234: ApproverGroup(1234, "toto", "path/toto")},
            },
            False,
        ),
        (
            {
                "name": "rule",
                "approvals_before_merge": 2,
                "users": {123: ApproverUser(123, "toto")},
                "groups": {1234: ApproverGroup(1234, "toto", "path/toto")},
            },
            {
                "name": "rule",
                "approvals_before_merge": 2,
                "users": {123: ApproverUser(123, "tata")},
                "groups": {1234: ApproverGroup(1234, "toto", "path/toto")},
            },
            False,
        ),
        (
            {
                "name": "rule",
                "approvals_before_merge": 2,
                "users": {123: ApproverUser(123, "toto")},
                "groups": {1234: ApproverGroup(1234, "toto", "path/toto")},
            },
            {
                "name": "rule",
                "approvals_before_merge": 2,
                "users": {123: ApproverUser(123, "toto")},
                "groups": {12345: ApproverGroup(12345, "toto", "path/toto")},
            },
            False,
        ),
        (
            {
                "name": "rule",
                "approvals_before_merge": 2,
                "users": {123: ApproverUser(123, "toto")},
                "groups": {1234: ApproverGroup(1234, "toto", "path/toto")},
            },
            {
                "name": "rule",
                "approvals_before_merge": 2,
                "users": {123: ApproverUser(123, "toto")},
                "groups": {},
            },
            False,
        ),
    ],
)
def test_eq_project_approvers(approve1, approve2, result):
    project_approvers1 = ProjectApproversRules()
    project_approvers1.name = approve1.get("name")
    project_approvers1.users = approve1.get("users")
    project_approvers1.groups = approve1.get("groups")
    project_approvers1.approvals_before_merge = approve1.get("approvals_before_merge")

    project_approvers2 = ProjectApproversRules()
    project_approvers2.name = approve2.get("name")
    project_approvers2.users = approve2.get("users")
    project_approvers2.groups = approve2.get("groups")
    project_approvers2.approvals_before_merge = approve2.get("approvals_before_merge")
    assert project_approvers1.name == "rule"
    assert (project_approvers1 == project_approvers2) == result


@pytest.mark.parametrize(
    "config_service, project_rules, expected_status, val_in_change",
    [
        (
            # config_service
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
                "name": "approval_rules",
            },
            # project_rules
            Namespace(
                {
                    "approval_rules": [
                        {
                            "name": "approval_rules",
                            "profiles": ["mytest_master_approvers"],
                            "minimum": 2,
                            "protected_branches": ["branch"],
                        }
                    ],
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
            # expected_status
            "updated",
            # val_in_change
            "toto",
        ),
        (
            {
                "config_approvers": None,
                "config_groups": None,
                "approvals_before_merge": 1,
                "name": "approval_rules",
            },
            Namespace(
                {
                    "approval_rules": [
                        {
                            "name": "approval_rules",
                            "profiles": ["mytest_master_approvers"],
                            "minimum": 2,
                            "protected_branches": ["branch"],
                        }
                    ],
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
                "name": "approval_rules",
            },
            Namespace(
                {
                    "approval_rules": [
                        {
                            "name": "approval_rules",
                            "minimum": 2,
                            "protected_branches": ["branch"],
                        }
                    ],
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
                "name": "approval_rules",
            },
            Namespace(
                {
                    "approval_rules": [
                        {
                            "name": "approval_rules",
                            "profiles": ["mytest_master_approvers"],
                            "minimum": 1,
                            "protected_branches": ["branch"],
                        }
                    ],
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
):
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

    config.approvers = config_service.get("config_approvers", None)
    config.approver_groups = config_service.get("config_groups", None)
    config.name = config_service.get("name", None)
    config.rule_names = [config_service.get("name", None)]
    config.approver_groups_per_rule = {"approval_rules": config_service.get("config_groups", None)}
    config.approvers_per_rule = {"approval_rules": config_service.get("config_approvers", None)}
    mocker.patch(
        "gpc.executors.approval_rules_executor.ProjectApprovalRules",
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
    change_approvers = get_change_value(p, "approval_rules")
    assert val_in_change in change_str
    assert change_approvers.to_dict().get("differences").get("action") == expected_status


def test_compute_branches(mocker):
    App_re = ApprovalRulesExecutor(
        mocker.Mock(), mocker.Mock(), mocker.Mock(), mocker.Mock(), mocker.Mock()
    )
    App_re.item = DotMap(
        {
            "protectedbranches": {
                "list": mocker.Mock(
                    return_value=[
                        DotMap({"attributes": {"name": "toto", "id": 4}}),
                        DotMap({"attributes": {"name": "branch", "id": 2}}),
                    ]
                )
            }
        }
    )
    pb = App_re.compute_branches([1, "branch"])
    assert 1 in pb and 2 in pb
