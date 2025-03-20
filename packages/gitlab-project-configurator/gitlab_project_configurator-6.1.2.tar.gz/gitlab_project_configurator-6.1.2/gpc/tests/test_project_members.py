"""
test project members
----------------------------------
"""

# Third Party Libraries
import pytest

from dictns import Namespace
from gitlab.exceptions import GitlabGetError
from gitlab.v4.objects import Project  # pylint: disable=unused-import

# Gitlab-Project-Configurator Modules
from gpc.executors.members_executor import MembersProjectExecutor
from gpc.helpers.exceptions import GpcUserError
from gpc.parameters import GpcParameters
from gpc.parameters import RunMode
from gpc.project_rule_executor import ProjectRuleExecutor
from gpc.tests.test_helpers import get_change_value
from gpc.tests.test_helpers import get_executor


# pylint: disable=redefined-outer-name, unused-argument,
# pylint: disable=protected-access, too-many-arguments, too-many-locals


def side_effet_user(username, retry_transient_errors):
    username = username.lower()
    users = {
        "case.matters": [
            Namespace({"id": 1234, "name": "Case.Matters", "username": "Case.Matters"})
        ],
        "user.tipi": [Namespace({"id": 1243, "name": "user.tipi", "username": "user.tipi"})],
        "user.piti": [Namespace({"id": 1432, "name": "user.piti", "username": "user.piti"})],
        "roger.new_user": [
            Namespace({"id": 1664, "name": "roger.new_user", "username": "roger.new_user"})
        ],
    }

    if username in users:
        return users[username]

    raise GpcUserError("ERROR")


def side_effect_group(group_path, retry_transient_errors):
    if group_path == "test/group":
        return Namespace({"id": 12, "name": "test/group", "full_path": "test/group"})
    if group_path == "test/group_rm":
        return Namespace({"id": 13, "name": "test/group_rm", "full_path": "test/group_rm"})
    if group_path == "test/group_update":
        return Namespace({"id": 14, "name": "test/group_update", "full_path": "test/group_update"})
    raise GitlabGetError("ERROR")


# flake8: noqa
@pytest.mark.parametrize(
    [
        "project_rules",
        "members_list",
        "inherited_members",
        "shared_groups",
        "expected_differences",
        "member_api_action",
        "share_action",
    ],
    [
        (
            # project_rules
            Namespace(
                {
                    "project_members": {
                        "profiles": ["mytest_master_approvers"],
                        "members": [
                            {"role": "maintainers", "name": "casE.matterS"},
                            {"role": "reporters", "name": "user.piti"},
                            {
                                "role": "maintainers",
                                "names": ["user.tipi", "casE.matterS"],
                            },
                        ],
                    },
                    "member_profiles": [
                        Namespace(
                            {
                                "name": "mytest_master_approvers",
                                "role": "developers",
                                "members": ["test/group"],
                            }
                        )
                    ],
                }
            ),
            # members_list
            [Namespace({"username": "roger", "id": 98, "access_level": 30})],
            # inherited_members
            [Namespace({"username": "pierre", "id": 99, "access_level": 30})],
            # shared_groups
            [],
            # expected_differences
            {
                "roger": {
                    "status": "removed",
                    "before": {"name": "roger", "role": "developers"},
                    "after": None,
                },
                "test/group": {
                    "status": "added",
                    "before": None,
                    "after": {"name": "test/group", "role": "developers"},
                },
                "Case.Matters": {
                    "status": "added",
                    "before": None,
                    "after": {"name": "Case.Matters", "role": "maintainers"},
                },
                "user.tipi": {
                    "status": "added",
                    "before": None,
                    "after": {"name": "user.tipi", "role": "maintainers"},
                },
                "user.piti": {
                    "status": "added",
                    "before": None,
                    "after": {"name": "user.piti", "role": "reporters"},
                },
            },
            # member_api_action
            ["create", "delete"],
            # share_action
            ["share", "unshare"],
        ),
        (
            # project_rules
            Namespace(
                {
                    "project_members": {"profiles": ["mytest_master_approvers"]},
                    "member_profiles": [
                        Namespace(
                            {
                                "name": "mytest_master_approvers",
                                "role": "developers",
                                "members": ["test/group", "Case.Matters"],
                            }
                        )
                    ],
                }
            ),
            # members_list
            [Namespace({"username": "Case.Matters", "id": 1234, "access_level": 40})],
            # inherited_members
            [Namespace({"username": "pierre", "id": 99, "access_level": 30})],
            # shared_groups
            [
                {
                    "group_full_path": "test/group",
                    "group_id": 12,
                    "group_access_level": 30,
                }
            ],
            # expected_differences
            {
                "test/group": {
                    "status": "kept",
                    "before": {"name": "test/group", "role": "developers"},
                    "after": {"name": "test/group", "role": "developers"},
                },
                "Case.Matters": {
                    "status": "updated",
                    "before": {"name": "Case.Matters", "role": "maintainers"},
                    "after": {"name": "Case.Matters", "role": "developers"},
                },
            },
            # member_api_action
            None,
            # share_action
            None,
        ),
        (
            # project_rules
            Namespace(
                {
                    "project_members": {
                        "members": [
                            {"role": "developers", "name": "test/group"},
                            {"role": "developers", "name": "Case.Matters"},
                            {"role": "maintainers", "name": "test/group_update"},
                        ]
                    },
                    "member_profiles": [
                        Namespace(
                            {
                                "name": "mytest_master_approvers",
                                "role": "developers",
                                "members": ["test/group", "Case.Matters"],
                            }
                        )
                    ],
                }
            ),
            # members_list
            [Namespace({"username": "Case.Matters", "id": 1234, "access_level": 40})],
            # inherited_members
            [Namespace({"username": "pierre", "id": 99, "access_level": 30})],
            # shared_groups
            [
                {
                    "group_full_path": "test/group",
                    "group_id": 12,
                    "group_access_level": 30,
                },
                {
                    "group_full_path": "test/group_rm",
                    "group_id": 13,
                    "group_access_level": 30,
                },
                {
                    "group_full_path": "test/group_update",
                    "group_id": 14,
                    "group_access_level": 30,
                },
            ],
            # expected_differences
            {
                "test/group": {
                    "status": "kept",
                    "before": {"name": "test/group", "role": "developers"},
                    "after": {"name": "test/group", "role": "developers"},
                },
                "test/group_update": {
                    "status": "updated",
                    "before": {"name": "test/group_update", "role": "developers"},
                    "after": {"name": "test/group_update", "role": "maintainers"},
                },
                "test/group_rm": {
                    "status": "removed",
                    "before": {"name": "test/group_rm", "role": "developers"},
                    "after": None,
                },
                "Case.Matters": {
                    "status": "updated",
                    "before": {"name": "Case.Matters", "role": "maintainers"},
                    "after": {"name": "Case.Matters", "role": "developers"},
                },
            },
            # member_api_action
            ["save"],
            # share_action
            ["share", "unshare"],
        ),
        (
            # project_rules
            Namespace(
                {
                    "project_members": {"members": [{"role": "developers", "name": "test/group"}]},
                    "member_profiles": [
                        Namespace(
                            {
                                "name": "mytest_master_approvers",
                                "role": "developers",
                                "members": ["test/group"],
                            }
                        )
                    ],
                }
            ),
            # members_list
            [],
            # inherited_members
            [Namespace({"username": "pierre", "id": 99, "access_level": 30})],
            # shared_groups
            [
                {
                    "group_full_path": "test/group",
                    "group_id": 12,
                    "group_access_level": 30,
                }
            ],
            # expected_differences
            {
                "test/group": {
                    "status": "kept",
                    "before": {"name": "test/group", "role": "developers"},
                    "after": {"name": "test/group", "role": "developers"},
                }
            },
            # member_api_action
            None,
            # share_action
            None,
        ),
        (
            # project_rules
            Namespace(
                {
                    "keep_existing_members": True,
                    "project_members": {
                        "members": [
                            {"role": "developers", "name": "roger.new_user"},
                        ]
                    },
                }
            ),
            # members_list
            [Namespace({"username": "Case.Matters", "id": 1234, "access_level": 40})],
            # inherited_members
            [Namespace({"username": "pierre", "id": 99, "access_level": 30})],
            # shared_groups
            [
                {
                    "group_full_path": "test/group",
                    "group_id": 12,
                    "group_access_level": 30,
                },
                {
                    "group_full_path": "test/group_update",
                    "group_id": 14,
                    "group_access_level": 30,
                },
            ],
            # expected_differences
            {
                "test/group": {
                    "status": "kept",
                    "before": {"name": "test/group", "role": "developers"},
                    "after": {"name": "test/group", "role": "developers"},
                },
                "test/group_update": {
                    "status": "kept",
                    "before": {"name": "test/group_update", "role": "developers"},
                    "after": {"name": "test/group_update", "role": "developers"},
                },
                "Case.Matters": {
                    "status": "kept",
                    "before": {"name": "Case.Matters", "role": "maintainers"},
                    "after": {"name": "Case.Matters", "role": "maintainers"},
                },
                "roger.new_user": {
                    "status": "added",
                    "before": None,
                    "after": {"name": "roger.new_user", "role": "developers"},
                },
            },
            # member_api_action
            ["save"],
            # share_action
            ["share", "unshare"],
        ),
    ],
)
# flake8: qa
def test_project_members(
    mocker,
    fake_gitlab,
    fake_project,
    project_rules,
    members_list,
    inherited_members,
    shared_groups,
    expected_differences,
    member_api_action,
    share_action,
):
    # Mock
    mocker.patch("gpc.tests.test_project_members.Project.save")
    mocker.patch(
        "gpc.tests.test_project_members.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    fake_project.share = mocker.Mock()
    fake_project.unshare = mocker.Mock()
    users_mock = mocker.Mock()
    users_mock.list = mocker.Mock(side_effect=side_effet_user)
    mock_members = mocker.Mock()

    mock_members.list = mocker.Mock(return_value=members_list)
    mock_members.delete = mocker.Mock(return_value=members_list)
    mock_members.create = mocker.Mock()

    member_mock = mocker.Mock()
    member_mock.save = mocker.Mock()

    mock_members.get = mocker.Mock(side_effect=member_mock)
    all_members = members_list + inherited_members

    mock_members.all = mocker.Mock(return_value=all_members)
    fake_project.members = mock_members
    fake_project.shared_with_groups = shared_groups

    fake_gitlab.users = users_mock
    group_projects = mocker.Mock()
    group_projects_get = mocker.Mock(side_effect=side_effect_group)
    group_projects.get = group_projects_get
    fake_gitlab.groups = group_projects

    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(mocker.Mock("fake_config"), mode=RunMode.APPLY),
    )
    p.execute()
    change_members = get_change_value(p, "members")
    assert change_members.differences == expected_differences
    # Check if methods are called.
    if member_api_action:
        for action in member_api_action:
            if action == "create":
                assert mock_members.create.is_called
            if action == "delete":
                assert mock_members.delete.is_called
    if share_action:
        for action in share_action:
            if action == "share":
                assert fake_project.share.is_called
            if action == "unshare":
                assert fake_project.unshare.is_called


@pytest.mark.parametrize(
    "project_rules, members_list, inherited_members, shared_groups, error_msg",
    [
        (
            # project_rules
            Namespace(
                {
                    "project_members": {
                        "profiles": ["mytest_master_approvers"],
                        "members": [{"role": "maintainers", "name": "Case.Matters"}],
                    },
                    "member_profiles": [
                        Namespace(
                            {
                                "name": "mytest_master_approvers",
                                "role": "developers",
                                "members": ["test/group_err"],
                            }
                        )
                    ],
                }
            ),
            # members_list
            [Namespace({"username": "roger", "id": 98, "access_level": 30})],
            # inherited_members
            [Namespace({"username": "pierre", "id": 99, "access_level": 30})],
            # shared_groups
            [],
            # error_msg
            "The username or group name 'test/group_err' does not exist",
        ),
        (
            # project_rules
            Namespace(
                {
                    "project_members": {
                        "profiles": ["mytest_master_approvers"],
                        "members": [{"role": "maintainers", "name": "Case.Matters"}],
                    },
                    "member_profiles": [
                        Namespace(
                            {
                                "name": "mytest_master_approvers",
                                "members": ["test/group_err"],
                            }
                        )
                    ],
                }
            ),
            # members_list
            [Namespace({"username": "roger", "id": 98, "access_level": 30})],
            # inherited_members
            [Namespace({"username": "pierre", "id": 99, "access_level": 30})],
            # shared_groups
            [],
            # error_msg
            "The role is missing in your member_profiles definition",
        ),
        (
            # project_rules
            Namespace(
                {
                    "project_members": {"profiles": ["mytest_master_approvers"]},
                    "member_profiles": [
                        Namespace(
                            {
                                "name": "mytest_master_approvers",
                                "role": "developers",
                                "members": ["test/group", "Case.Matters"],
                            }
                        )
                    ],
                }
            ),
            # members_list
            [],
            # inherited_members
            [
                Namespace({"username": "pierre", "id": 99, "access_level": 30}),
                Namespace({"username": "Case.Matters", "id": 1234, "access_level": 50}),
            ],
            # shared_groups
            [
                {
                    "group_full_path": "test/group",
                    "group_id": 12,
                    "group_access_level": 30,
                }
            ],
            # error_msg
            "they are inherited members with owner access.",
        ),
        # NO ERROR
        (
            # project_rules
            Namespace(
                {
                    "project_members": {"profiles": ["mytest_master_approvers"]},
                    "member_profiles": [
                        Namespace(
                            {
                                "name": "mytest_master_approvers",
                                "role": "developers",
                                "members": ["test/group", "Case.Matters"],
                            }
                        )
                    ],
                }
            ),
            # members_list
            [],
            # inherited_members
            [
                Namespace({"username": "pierre", "id": 99, "access_level": 30}),
                Namespace({"username": "Case.Matters", "id": 1234, "access_level": 30}),
            ],
            # shared_groups
            [
                {
                    "group_full_path": "test/group",
                    "group_id": 12,
                    "group_access_level": 30,
                }
            ],
            # error_msg
            "",
        ),
    ],
)
def test_project_members_ko(
    mocker,
    fake_gitlab,
    fake_project,
    project_rules,
    members_list,
    inherited_members,
    shared_groups,
    error_msg,
):
    # Mock
    mocker.patch("gpc.tests.test_project_members.Project.save")
    mocker.patch(
        "gpc.tests.test_project_members.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    fake_project.share = mocker.Mock()
    fake_project.unshare = mocker.Mock()
    users_mock = mocker.Mock()
    users_mock.list = mocker.Mock(side_effect=side_effet_user)
    mock_members = mocker.Mock()
    mock_members.list = mocker.Mock(return_value=members_list)
    mock_members.delete = mocker.Mock(return_value=members_list)
    mock_members.create = mocker.Mock()

    member_mock = mocker.Mock()
    member_mock.save = mocker.Mock()

    mock_members.get = mocker.Mock(side_effect=member_mock)
    mock_members.all = mocker.Mock(return_value=members_list + inherited_members)

    mock_members_all = mocker.Mock()
    mock_members_all.list = mocker.Mock(return_value=members_list + inherited_members)
    fake_project.members_all = mock_members_all

    fake_project.members = mock_members
    fake_project.shared_with_groups = shared_groups

    fake_gitlab.users = users_mock
    group_projects = mocker.Mock()
    group_projects_get = mocker.Mock(side_effect=side_effect_group)
    group_projects.get = group_projects_get
    fake_gitlab.groups = group_projects

    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(mocker.Mock("fake_config"), mode=RunMode.APPLY),
    )

    p.update_settings()
    members_executor = get_executor(p, MembersProjectExecutor)
    assert error_msg in members_executor.error_message
