"""
test_update protected branches
----------------------------------
"""

# pylint: disable=unused-import

# Standard Library
from collections import Counter

# Third Party Libraries
import pytest

from dictns import Namespace
from dotmap import DotMap
from gitlab.exceptions import GitlabCreateError
from gitlab.exceptions import GitlabDeleteError
from gitlab.exceptions import GitlabGetError
from gitlab.v4.objects import Project

# Gitlab-Project-Configurator Modules
from gpc.executors.protected_branch_setting_executor import ChangeProtectedBranch
from gpc.executors.protected_branch_setting_executor import ProtectedBranch
from gpc.executors.protected_branch_setting_executor import ProtectedBranchManager
from gpc.executors.protected_branch_setting_executor import ProtectedBranchSettingExecutor
from gpc.executors.protected_branch_setting_executor import ProtectedRefMember
from gpc.executors.protected_branch_setting_executor import ProtectedRefsAuth
from gpc.helpers.exceptions import GPCCreateError
from gpc.helpers.exceptions import GPCDeleteError
from gpc.helpers.exceptions import GpcUserError
from gpc.helpers.gitlab_helper import get_subgroups
from gpc.parameters import GpcParameters
from gpc.parameters import RunMode
from gpc.project_rule_executor import ProjectRuleExecutor
from gpc.tests.test_helpers import get_change_value
from gpc.tests.test_helpers import get_executor


# pylint: disable=redefined-outer-name, unused-argument, protected-access, duplicate-code


def side_effect_user(username, retry_transient_errors):
    if username == "user.toto":
        return [Namespace({"id": 1234, "name": "user.toto", "username": "user.toto"})]
    raise GpcUserError("ERROR")


def side_effect_create_error(name, retry_transient_errors):
    if name == "no_fail":
        return {}
    raise GitlabCreateError("403 forbidden")


def side_effect_GPCcreate_error(variable, path):
    if path == "no_fail":
        return {}
    raise GPCCreateError("403 forbidden", 403)


def side_effect_delete_error(name, property_bean):
    if name == "no_fail":
        return {}
    raise GitlabDeleteError("403 forbidden")


def side_effect_get_group(gl, group_path):
    get_group_dict = {
        "test.group1": DotMap(
            {
                "group_full_path": "test.group1",
                "group_id": 1,
                "group_access_level": 40,
                "shared_with_groups": [],
            }
        ),
        "test.group2": DotMap(
            {
                "group_full_path": "test.group2",
                "group_id": 2,
                "group_access_level": 40,
                "shared_with_groups": [
                    DotMap(
                        {
                            "group_full_path": "test.subgroup2_1",
                            "group_id": 3,
                            "group_access_level": 40,
                            "shared_with_groups": [
                                DotMap(
                                    {
                                        "group_full_path": "test.subgroup2_2",
                                        "group_id": 4,
                                        "group_access_level": 40,
                                        "shared_with_groups": [],
                                    }
                                )
                            ],
                        }
                    )
                ],
            }
        ),
        "test.subgroup2_1": DotMap(
            {
                "group_full_path": "test.subgroup2_1",
                "group_id": 3,
                "group_access_level": 40,
                "shared_with_groups": [
                    DotMap(
                        {
                            "group_full_path": "test.subgroup2_2",
                            "group_id": 4,
                            "group_access_level": 40,
                            "shared_with_groups": [],
                        }
                    )
                ],
            }
        ),
        "test.group2_2": DotMap(
            {
                "group_full_path": "test.subgroup2_2",
                "group_id": 4,
                "group_access_level": 40,
                "shared_with_groups": [],
            }
        ),
        "test.group3": DotMap(
            {
                "group_full_path": "test.group3",
                "group_id": 1,
                "group_access_level": 40,
                "shared_with_groups": [
                    DotMap(
                        {
                            "group_full_path": "test.subgroup3_1",
                            "group_id": 1,
                            "group_access_level": 40,
                            "shared_with_groups": [],
                        }
                    ),
                    DotMap(
                        {
                            "group_full_path": "test.subgroup3_2",
                            "group_id": 1,
                            "group_access_level": 40,
                            "shared_with_groups": [],
                        }
                    ),
                ],
            }
        ),
        "test.subgroup3_1": DotMap(
            {
                "group_full_path": "test.subgroup3_1",
                "group_id": 1,
                "group_access_level": 40,
                "shared_with_groups": [],
            }
        ),
        "test.subgroup3_2": DotMap(
            {
                "group_full_path": "test.subgroup3_2",
                "group_id": 1,
                "group_access_level": 40,
                "shared_with_groups": [],
            }
        ),
    }

    return get_group_dict[group_path]


def get_members_error(user_id, retry_transient_errors):
    raise GitlabGetError


# flake8: noqa
@pytest.mark.parametrize(
    "project_rules, members_users, group_projects_list, exception_msg",
    [
        # 1 execution
        # project_rules
        # Rule to apply for the project
        (
            Namespace(
                {
                    "protected_branches": [
                        {
                            "pattern": "master",
                            "allowed_to_merge": "maintainers",
                            "allowed_to_push": {
                                "role": "kurt cobain",
                                "users": ["user.toto"],
                            },
                        },
                        {
                            "pattern": "dev*",
                            "allowed_to_merge": {"role": "developers"},
                            "allowed_to_push": {"role": "no one"},
                        },
                    ]
                }
            ),
            # members_users
            # Users which are members of the project
            [Namespace({"id": 1234, "name": "user.toto", "username": "user.toto"})],
            # group_projects_list
            # A list of projects which groups can access
            [
                {
                    "group_full_path": "test.group",
                    "group_id": 13,
                    "group_access_level": 666,
                }
            ],
            # exception_msg
            # Part of the exception message expected
            "The role 'kurt cobain' is not acceptable",
        ),
        # 2 execution
        # project_rules
        # Rule to apply for the project
        (
            Namespace(
                {
                    "member_profiles": [
                        Namespace({"name": "useless_profiles", "members": ["test/group/2"]}),
                        Namespace({"name": "mytest_profiles", "members": ["test/group"]}),
                    ],
                    "protected_branches": [
                        {
                            "pattern": "master",
                            "allowed_to_merge": "maintainers",
                            "allowed_to_push": {
                                "members": ["user.toto"],
                                "profiles": ["mytest_profiles"],
                            },
                        }
                    ],
                }
            ),
            # members_users
            # Users which are members of the project
            [Namespace({"id": 6859, "name": "member.user", "username": "member.user"})],
            # group_projects_list
            # A list of projects which groups can access
            [
                {
                    "group_full_path": "test.group",
                    "group_id": 13,
                    "group_access_level": 666,
                }
            ],
            # exception_msg
            # Part of the exception message expected
            "user.toto,test/group",
        ),
    ],
)
# flake8: qa
def test_invalid_allow(
    mocker,
    fake_gitlab,
    fake_project,
    project_rules,
    members_users,
    group_projects_list,
    exception_msg,
):
    # Mock
    mocker.patch("gpc.tests.test_protected_ref.Project.save")
    mocker.patch(
        "gpc.tests.test_protected_ref.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    mocker.patch(
        "gpc.tests.test_protected_ref.ProtectedBranchSettingExecutor.is_really_unauthorized"
    )
    users_mock = mocker.Mock()
    users_mock.list = mocker.Mock(side_effect=side_effect_user)
    fake_gitlab.users = users_mock

    groups_mock = get_groups_service_mock(mocker)
    fake_gitlab.groups = groups_mock
    fake_project.shared_with_groups = group_projects_list
    protectedbranches = mocker.Mock()

    protectedbranches.list = mocker.Mock(
        return_value=[
            Namespace(
                {
                    "name": "master",
                    "merge_access_levels": [{"access_level": 40}],
                    "push_access_levels": [{"access_level": 0}, {"user_id": 1234}],
                }
            )
        ]
    )

    fake_project.protectedbranches = protectedbranches

    fake_project.users.list.return_value = []

    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(config=mocker.Mock("fake_config"), mode=RunMode.APPLY),
    )
    p.execute()
    executor = get_executor(p, ProtectedBranchSettingExecutor)
    assert exception_msg in str(executor.errors)


def get_groups_service_mock(mocker):
    group_mocked = mocker.Mock()
    group_mocked.id = 666
    group_mocked.name = "test.group"
    group_mocked.full_path = "test/group"
    group_mocked.shared_with_groups = []
    members_all = mocker.Mock(
        return_value=[Namespace({"id": 1664, "name": "user.titi", "username": "user.titi"})]
    )
    mock_members = mocker.Mock()
    mock_members.list = members_all
    group_mocked.members_all = mock_members
    group_projects = mocker.Mock()
    group_mocked.projects = group_projects
    groups_mock = mocker.Mock()
    groups_mock.get = mocker.Mock(return_value=group_mocked)
    return groups_mock


@pytest.mark.parametrize("keep_variables", [True, False])
def test_create_protected_branch(
    mocker, fake_gitlab, fake_project, keep_variables
):  # pylint: disable=too-many-locals,too-many-statements
    # Mock
    mocker.patch("gpc.tests.test_protected_ref.Project.save")
    mocker.patch(
        "gpc.tests.test_protected_ref.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    mock_manager_branch = mocker.patch(
        "gitlab.v4.objects.ProjectProtectedBranchManager.create", mocker.Mock()
    )
    users_mock = mocker.Mock()
    users_mock.list = mocker.Mock(side_effect=side_effect_user)
    fake_gitlab.users = users_mock
    fake_gitlab.groups = get_groups_service_mock(mocker)
    fake_project.shared_with_groups = [
        {"group_full_path": "test/group", "group_id": 66, "group_access_level": 30}
    ]
    fake_project.users.list.return_value = [
        Namespace({"id": 1234, "name": "user.toto", "username": "user.toto"})
    ]

    protectedbranches = mocker.Mock()

    def protected_branches_get_mocker(attribute):
        return_value = {
            "master": DotMap(
                {
                    "name": "master",
                    "merge_access_levels": [{"access_level": 40}],
                    "push_access_levels": [{"access_level": 0}, {"user_id": 1234}],
                    "allow_force_push": False,
                    "unprotect_access_levels": [
                        {
                            "access_level": 40,
                            "access_level_description": "Maintainers",
                            "user_id": None,
                            "group_id": None,
                        }
                    ],
                    "code_owner_approval_required": False,
                }
            ),
            "other": DotMap(
                {
                    "name": "other",
                    "merge_access_levels": [{"access_level": 40}],
                    "push_access_levels": [{"access_level": 0}, {"user_id": 1234}],
                    "allow_force_push": False,
                    "unprotect_access_levels": [
                        {
                            "access_level": 0,
                            "access_level_description": "No one",
                            "user_id": None,
                            "group_id": None,
                        }
                    ],
                    "code_owner_approval_required": False,
                }
            ),
            "locked": DotMap(
                {
                    "name": "locked",
                    "merge_access_levels": [{"access_level": 40}],
                    "push_access_levels": [{"access_level": 0}, {"user_id": 1234}],
                    "allow_force_push": False,
                    "unprotect_access_levels": [
                        {
                            "access_level": 0,
                            "access_level_description": "No one",
                            "user_id": None,
                            "group_id": None,
                        }
                    ],
                    "code_owner_approval_required": False,
                }
            ),
            "existing_to_check": DotMap(
                {
                    "name": "existing_to_check",
                    "merge_access_levels": [{"access_level": 40}],
                    "push_access_levels": [{"access_level": 0}, {"user_id": 1234}],
                    "allow_force_push": False,
                    "unprotect_access_levels": [
                        {
                            "access_level": 0,
                            "access_level_description": "Maintainers",
                            "user_id": None,
                            "group_id": None,
                        }
                    ],
                    "code_owner_approval_required": False,
                }
            ),
            "existing_not_check": DotMap(
                {
                    "name": "existing_not_check",
                    "merge_access_levels": [{"access_level": 40}],
                    "push_access_levels": [{"access_level": 0}, {"user_id": 1234}],
                    "allow_force_push": False,
                    "unprotect_access_levels": [
                        {
                            "access_level": 0,
                            "access_level_description": "Maintainers",
                            "user_id": None,
                            "group_id": None,
                        }
                    ],
                    "code_owner_approval_required": False,
                }
            ),
        }
        resultat = return_value.get(attribute)
        if resultat:
            return resultat

        raise GitlabGetError

    protectedbranches.list = mocker.Mock(
        return_value=[
            Namespace(
                {
                    "name": "master",
                    "merge_access_levels": [{"access_level": 40}],
                    "push_access_levels": [{"access_level": 0}, {"user_id": 1234}],
                    "allow_force_push": False,
                    "unprotect_access_levels": [
                        {
                            "access_level": 40,
                            "access_level_description": "Maintainers",
                            "user_id": None,
                            "group_id": None,
                        }
                    ],
                    "code_owner_approval_required": False,
                }
            ),
            Namespace(
                {
                    "name": "other",
                    "merge_access_levels": [{"access_level": 40}],
                    "push_access_levels": [{"access_level": 0}, {"user_id": 1234}],
                    "allow_force_push": False,
                    "unprotect_access_levels": [
                        {
                            "access_level": 0,
                            "access_level_description": "No one",
                            "user_id": None,
                            "group_id": None,
                        }
                    ],
                    "code_owner_approval_required": False,
                }
            ),
            Namespace(
                {
                    "name": "locked",
                    "merge_access_levels": [{"access_level": 40}],
                    "push_access_levels": [{"access_level": 0}, {"user_id": 1234}],
                    "allow_force_push": False,
                    "unprotect_access_levels": [
                        {
                            "access_level": 0,
                            "access_level_description": "No one",
                            "user_id": None,
                            "group_id": None,
                        }
                    ],
                    "code_owner_approval_required": False,
                }
            ),
            Namespace(
                {
                    "name": "existing_to_check",
                    "merge_access_levels": [{"access_level": 40}],
                    "push_access_levels": [{"access_level": 0}, {"user_id": 1234}],
                    "allow_force_push": False,
                    "unprotect_access_levels": [
                        {
                            "access_level": 0,
                            "access_level_description": "Maintainers",
                            "user_id": None,
                            "group_id": None,
                        }
                    ],
                    "code_owner_approval_required": False,
                }
            ),
            Namespace(
                {
                    "name": "existing_not_check",
                    "merge_access_levels": [{"access_level": 40}],
                    "push_access_levels": [{"access_level": 0}, {"user_id": 1234}],
                    "allow_force_push": False,
                    "unprotect_access_levels": [
                        {
                            "access_level": 0,
                            "access_level_description": "Maintainers",
                            "user_id": None,
                            "group_id": None,
                        }
                    ],
                    "code_owner_approval_required": False,
                }
            ),
        ]
    )
    fake_project.protectedbranches = protectedbranches
    fake_project.protectedbranches.get = protected_branches_get_mocker

    project_rules = Namespace(
        {
            "member_profiles": [
                Namespace({"name": "useless_profiles", "members": ["test/group/2"]}),
                Namespace({"name": "mytest_profiles", "members": ["test/group"]}),
            ],
            "keep_existing_protected_branches": keep_variables,
            "protected_branches": [
                {
                    "pattern": "master",
                    "allowed_to_merge": "maintainers",
                    "allowed_to_push": {"role": "no one", "members": ["user.toto"]},
                    "allow_force_push": True,
                    "code_owner_approval_required": True,
                    "allowed_to_unprotect": "maintainers",
                },
                {
                    "pattern": "dev*",
                    "allowed_to_merge": {
                        "members": ["user.toto"],
                        "profiles": ["mytest_profiles"],
                    },
                    "allowed_to_push": {"role": "no one"},
                    "allowed_to_unprotect": "maintainers",
                },
                {
                    "pattern": "existing_to_check",
                    "allowed_to_merge": "maintainers",
                    "allowed_to_push": {"role": "no one", "members": ["user.toto"]},
                    "allow_force_push": True,
                    "code_owner_approval_required": True,
                },
                {
                    "pattern": "existing_not_check",
                    "allowed_to_merge": "maintainers",
                    "allowed_to_push": {"role": "no one", "members": ["user.toto"]},
                    "allow_force_push": True,
                    "code_owner_approval_required": True,
                    "allowed_to_unprotect": "maintainers",
                },
            ],
        }
    )

    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(config=mocker.Mock("fake_config"), mode=RunMode.APPLY),
    )
    p.execute()
    change_str = p.echo_execution()
    change_protected_branches = get_change_value(p, "protected_branches")
    assert len(change_protected_branches.differences) == 6
    assert change_protected_branches.differences.get("master").get("status") == "updated"
    assert change_protected_branches.differences.get("dev*").get("status") == "added"
    if keep_variables:
        assert change_protected_branches.differences.get("other").get("status") == "kept"
    else:
        assert change_protected_branches.differences.get("other").get("status") == "removed"

    assert len(change_protected_branches.after) == 4
    assert change_protected_branches.after[3].name == "master"
    assert change_protected_branches.after[3].allowed_to_push.role.member_id == 0
    assert change_protected_branches.after[3].allowed_to_merge.role.member_id == 40
    assert change_protected_branches.differences.get("master").get("status") == "updated"
    assert change_protected_branches.after[3].allowed_to_push.users[0].member_id == 1234
    assert change_protected_branches.after[3].allowed_to_push.users[0].name == "user.toto"
    assert change_protected_branches.after[0].name == "dev*"
    assert change_protected_branches.after[0].allowed_to_push.role.member_id == 0
    assert change_protected_branches.after[0].allowed_to_merge.groups[0].name == "test/group"
    assert not change_protected_branches.after[0].allowed_to_merge.role
    assert change_protected_branches.differences.get("dev*").get("status") == "added"
    assert "maintainers" in change_str
    assert mock_manager_branch.is_called


def test_protectedbranch_get_query(mocker):
    protectedbranch = ProtectedBranch(
        name="branch",
        allowed_to_merge=ProtectedRefsAuth(
            role=ProtectedRefMember(member_id=40, name="maintainers"),
            users=[],
            groups=[],
            code_owner_approval_required=None,
            allow_force_push=None,
        ),
        allowed_to_push=ProtectedRefsAuth(
            role=ProtectedRefMember(member_id=0, name="no one"),
            users=[],
            groups=[],
            code_owner_approval_required=None,
            allow_force_push=None,
        ),
        allow_force_push=True,
        code_owner_approval_required=False,
        allowed_to_unprotect="no one",
    )

    query = protectedbranch.get_query()
    assert query["name"] == "branch"
    assert query["allowed_to_push"] == [{"access_level": 0}]
    assert query["allowed_to_merge"] == [{"access_level": 40}]
    assert query["allowed_to_unprotect"] == [{"access_level": 0}]
    assert query["allow_force_push"]
    assert not query["code_owner_approval_required"]


@pytest.mark.parametrize(
    "subgroups,group_path",
    [
        (
            [],
            "test.group1",
        ),
        (
            ["test.subgroup2_1", "test.subgroup2_2"],
            "test.group2",
        ),
        (
            ["test.subgroup3_1", "test.subgroup3_2"],
            "test.group3",
        ),
    ],
    ids=["group_without_subgroups", "subgroup_with_subgroup", "group_with_2_subgroups"],
)
def test_get_subgroups(mocker, subgroups, group_path):
    gitlab_mock = mocker.Mock()

    mocker.patch("gpc.helpers.gitlab_helper.get_group", side_effect=side_effect_get_group)

    groups = get_subgroups(gitlab_mock, group_path)
    assert Counter(set(groups)) == Counter(subgroups)


def test_protectedbranch_manager(mocker):
    error_msg = (
        "branch 'error_branch' could not be created (project test_project_path): 403 forbidden"
    )
    property_bean = ProtectedBranch(
        name="error_branch",
        allowed_to_merge=ProtectedRefsAuth(
            role=ProtectedRefMember(member_id=50, name="owners"),
            users=[ProtectedRefMember(member_id=490, name="gitlab-nestor-integ-useless")],
            groups=[],
            code_owner_approval_required=None,
            allow_force_push=None,
        ),
        allowed_to_push=ProtectedRefsAuth(
            role=ProtectedRefMember(member_id=0, name="no one"),
            users=[],
            groups=[],
            code_owner_approval_required=None,
            allow_force_push=None,
        ),
        allow_force_push=False,
        code_owner_approval_required=False,
        allowed_to_unprotect="developers",
    )
    mocker.patch(
        "gpc.executors.protected_branch_setting_executor.ProtectedBranchManager.rm_existing"
    )
    manager_mock = mocker.Mock()
    manager_mock.create = side_effect_create_error
    manager = ProtectedBranchManager(manager_mock)
    with pytest.raises(GPCCreateError, match="403 forbidden") as exc_info:
        manager.create(property_bean, "test_project_path")
    assert error_msg == str(exc_info.value)

    error_msg = "branch 'error_branch' (project test_project_path): 403 forbidden"
    property_bean = ProtectedBranch(
        name="error_branch",
        allowed_to_merge=ProtectedRefsAuth(
            role=ProtectedRefMember(member_id=50, name="maintainers"),
            users=[ProtectedRefMember(member_id=490, name="gitlab-nestor-integ-useless")],
            groups=[],
            code_owner_approval_required=None,
            allow_force_push=None,
        ),
        allowed_to_push=ProtectedRefsAuth(
            role=ProtectedRefMember(member_id=0, name="no one"),
            users=[],
            groups=[],
            code_owner_approval_required=None,
            allow_force_push=None,
        ),
        allow_force_push=False,
        code_owner_approval_required=False,
        allowed_to_unprotect="developers",
    )
    mocker.patch(
        "gpc.executors.protected_branch_setting_executor.ProtectedBranchManager.rm_existing",
        side_effect_delete_error,
    )
    manager_mock = mocker.Mock()
    manager = ProtectedBranchManager(manager_mock)
    with pytest.raises(GPCDeleteError, match="403 forbidden") as exc_info:
        manager.create(property_bean, "test_project_path")
    assert error_msg == str(exc_info.value)


def test_update_or_create(mocker):
    manager_mock = mocker.Mock()
    manager = ProtectedBranchManager(manager_mock)
    manager.create = side_effect_GPCcreate_error
    # mocker.patch(
    #     "gpc.executors.protected_branch_setting_executor.ProtectedBranchManager.create",
    #     side_effect_create_error,
    # )
    change_properties = ChangeProtectedBranch(
        property_name="protected_branches",
        before=[
            ProtectedBranch(
                name="master",
                allowed_to_merge=ProtectedRefsAuth(
                    role=ProtectedRefMember(member_id=30, name="developers"),
                    users=[],
                    groups=[],
                    code_owner_approval_required=None,
                    allow_force_push=None,
                ),
                allowed_to_push=ProtectedRefsAuth(
                    role=ProtectedRefMember(member_id=0, name="no one"),
                    users=[],
                    groups=[],
                    code_owner_approval_required=None,
                    allow_force_push=None,
                ),
                allow_force_push=False,
                code_owner_approval_required=False,
                allowed_to_unprotect="maintainers",
            ),
        ],
        after=[
            ProtectedBranch(
                name="master",
                allowed_to_merge=ProtectedRefsAuth(
                    role=ProtectedRefMember(member_id=40, name="maintainers"),
                    users=[],
                    groups=[],
                    code_owner_approval_required=None,
                    allow_force_push=None,
                ),
                allowed_to_push=ProtectedRefsAuth(
                    role=ProtectedRefMember(member_id=0, name="none"),
                    users=[],
                    groups=[],
                    code_owner_approval_required=None,
                    allow_force_push=None,
                ),
                allow_force_push=False,
                code_owner_approval_required=False,
                allowed_to_unprotect="maintainers",
            ),
        ],
        show_diff_only=False,
        sub_level=0,
        keep_existing=False,
    )

    properties = [
        ProtectedBranch(
            name="master",
            allowed_to_merge=ProtectedRefsAuth(
                role=ProtectedRefMember(member_id=40, name="maintainers"),
                users=[],
                groups=[],
                code_owner_approval_required=None,
                allow_force_push=None,
            ),
            allowed_to_push=ProtectedRefsAuth(
                role=ProtectedRefMember(member_id=0, name="none"),
                users=[],
                groups=[],
                code_owner_approval_required=None,
                allow_force_push=None,
            ),
            allow_force_push=False,
            code_owner_approval_required=False,
            allowed_to_unprotect="maintainers",
        )
    ]

    ProtectedBranchSettingExecutor._update_or_create(
        mocker.Mock(), manager, change_properties, properties
    )

    assert change_properties.differences["master"]["status"] == "error"


def test_expand_groups(mocker, fake_gitlab, fake_project, fake_group):
    users = [
        ProtectedRefMember(member_id=1, name="user1"),
        ProtectedRefMember(member_id=4, name="user4"),
    ]
    group = mocker.Mock("Fake group")
    group.id = 789
    group.members_all = mocker.Mock()
    group.members_all.list.return_value = [
        DotMap({"id": 1, "username": "user1", "access_level": 50}),
        DotMap({"id": 2, "username": "user2", "access_level": 50}),
        DotMap({"id": 3, "username": "user3", "access_level": 50}),
        DotMap({"id": 4, "username": "user4", "access_level": 50}),
    ]
    fake_gitlab.groups.get.return_value = group
    pbs = ProtectedBranchSettingExecutor(
        fake_gitlab,
        "fake/path/to/project",
        fake_project,
        mocker.Mock(),
        mocker.Mock(),
    )

    users_from_groups = pbs.expand_groups(users, groups=["fake/group/path"])
    assert len(users_from_groups) == 2
    assert Counter([u.member_id for u in users_from_groups]) == Counter([2, 3])
