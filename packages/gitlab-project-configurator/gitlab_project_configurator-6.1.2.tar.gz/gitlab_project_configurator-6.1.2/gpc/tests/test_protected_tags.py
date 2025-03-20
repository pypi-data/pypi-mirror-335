"""
test_update protected tags
----------------------------------
"""

# pylint: disable=unused-import

# Third Party Libraries
import pytest

from dictns import Namespace
from gitlab.v4.objects import Project

# Gitlab-Project-Configurator Modules
from gpc.executors.protected_tag_setting_executor import ProtectedTagRefUser
from gpc.parameters import GpcParameters
from gpc.parameters import RunMode
from gpc.project_rule_executor import FAIL
from gpc.project_rule_executor import ProjectRuleExecutor
from gpc.tests.test_helpers import get_change_value


developers = ProtectedTagRefUser(user_id=30, name="developers")
maintainers = ProtectedTagRefUser(user_id=40, name="maintainers")


def side_effect_users_list(**kwargs):
    user1 = Namespace({"id": 1, "username": "user1"})
    if "search" not in kwargs:
        return [user1]
    if kwargs["search"] == "user1":
        return [user1]
    return []


@pytest.mark.parametrize("keep_variables", [True, False])
def test_create_protected_tags(mocker, fake_gitlab, fake_project, keep_variables):
    # Mock
    mocker.patch("gpc.tests.test_protected_tags.Project.save")
    mocker.patch(
        "gpc.tests.test_protected_tags.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    mock_manager_tag = mocker.patch(
        "gitlab.v4.objects.ProjectProtectedTagManager.create", mocker.Mock()
    )

    protectedtags = mocker.Mock()
    protectedtags.list = mocker.Mock(
        return_value=[
            Namespace({"name": "master", "create_access_levels": [{"access_level": 40}]}),
            Namespace(
                {"name": "tag1", "create_access_levels": [{"access_level": 40, "user_id": 1}]}
            ),
        ]
    )

    fake_project.protectedtags = protectedtags
    fake_project.users.list.return_value = [
        Namespace({"id": 1, "username": "user1"}),
        Namespace({"id": 2, "username": "user2"}),
    ]

    project_rules = Namespace(
        {
            "keep_existing_protected_tags": keep_variables,
            "protected_tags": [
                {"pattern": "master", "allowed_to_create": "maintainers", "users": None},
                {"pattern": "dev*", "allowed_to_create": "developers"},
                {"pattern": "test_tag", "allowed_to_create": {"role": "maintainers"}},
                {
                    "pattern": "test_tag2",
                    "allowed_to_create": {"role": "maintainers", "users": ["user1", "user2"]},
                },
            ],
        }
    )

    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(
            config=mocker.Mock("fake_config"), executor="protected_tags", mode=RunMode.APPLY
        ),
    )
    p.execute()
    change_protected_tags = get_change_value(p, "protected_tags")
    change_str = p.echo_execution()

    assert len(change_protected_tags.after) == 4
    master = [pt for pt in change_protected_tags.after if pt.name == "master"][0]
    assert master.allowed_to_create.role == maintainers
    assert master.allowed_to_create.users == []
    assert change_protected_tags.differences.get("master").get("status") == "kept"

    dev = [pt for pt in change_protected_tags.after if pt.name == "dev*"][0]
    assert dev.allowed_to_create.role == developers
    assert dev.allowed_to_create.users == []
    assert change_protected_tags.differences.get("dev*").get("status") == "added"

    test_tag = [pt for pt in change_protected_tags.after if pt.name == "test_tag"][0]
    assert test_tag.allowed_to_create.role == maintainers
    assert test_tag.allowed_to_create.users == []
    assert change_protected_tags.differences.get("test_tag").get("status") == "added"

    test_tag2 = [pt for pt in change_protected_tags.after if pt.name == "test_tag2"][0]
    assert test_tag2.allowed_to_create.role == maintainers
    assert test_tag2.allowed_to_create.users[0] == ProtectedTagRefUser(user_id=1, name="user1")
    assert test_tag2.allowed_to_create.users[1] == ProtectedTagRefUser(user_id=2, name="user2")

    if keep_variables:
        assert change_protected_tags.differences.get("tag1").get("status") == "kept"
    else:
        assert change_protected_tags.differences.get("tag1").get("status") == "removed"
    assert mock_manager_tag.is_called
    assert "maintainers" in change_str


def test_create_new_protected_tag(mocker, fake_gitlab, fake_project):
    # Mock
    mocker.patch("gpc.tests.test_protected_tags.Project.save")
    mocker.patch(
        "gpc.tests.test_protected_tags.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )

    mock_manager_tag = mocker.patch(
        "gitlab.v4.objects.ProjectProtectedTagManager.create", mocker.Mock()
    )
    protectedtags = mocker.Mock()

    protectedtags.list = mocker.Mock(return_value=[])

    fake_project.protectedtags = protectedtags
    fake_project.users.list.return_value = [Namespace({"id": 1, "username": "user1"})]

    project_rules = Namespace(
        {
            "keep_existing_protected_tags": False,
            "protected_tags": [
                {
                    "pattern": "master",
                    "allowed_to_create": {"role": "maintainers", "users": ["user1"]},
                },
            ],
        }
    )

    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(
            config=mocker.Mock("fake_config"), executor="protected_tags", mode=RunMode.APPLY
        ),
    )
    p.execute()
    change_protected_tags = get_change_value(p, "protected_tags")
    assert change_protected_tags.action == "added"
    assert len(change_protected_tags.before) == 0
    assert len(change_protected_tags.after) == 1
    master = [pt for pt in change_protected_tags.after if pt.name == "master"][0]
    assert master.allowed_to_create.role == maintainers
    assert master.allowed_to_create.users[0] == ProtectedTagRefUser(user_id=1, name="user1")
    assert change_protected_tags.differences.get("master").get("status") == "added"
    assert mock_manager_tag.is_called


def test_create_protected_tag_user_not_in_project(mocker, fake_gitlab, fake_project):
    # Mock
    mocker.patch("gpc.tests.test_protected_tags.Project.save")
    mocker.patch(
        "gpc.tests.test_protected_tags.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )

    mock_manager_tag = mocker.patch(
        "gitlab.v4.objects.ProjectProtectedTagManager.create", mocker.Mock()
    )

    protectedtags = mocker.Mock()
    protectedtags.list = mocker.Mock(return_value=[])
    fake_project.protectedtags = protectedtags
    fake_project.users.list.side_effect = side_effect_users_list

    fake_gitlab.users.list.return_value = [Namespace({"id": 2, "username": "user2"})]

    project_rules = Namespace(
        {
            "keep_existing_protected_tags": False,
            "protected_tags": [
                {
                    "pattern": "master",
                    "allowed_to_create": {"role": "maintainers", "users": ["user1", "user2"]},
                },
            ],
        }
    )

    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(
            config=mocker.Mock("fake_config"),
            debug=True,
            executor="protected_tags",
            mode=RunMode.APPLY,
        ),
    )
    p.execute()
    change_protected_tags = get_change_value(p, "protected_tags")
    change_str = p.echo_execution()

    assert p.status == FAIL
    assert p.errors[0]["user"] == "user2"
    assert len(change_protected_tags.before) == 0
    assert len(change_protected_tags.after) == 1
    master = [pt for pt in change_protected_tags.after if pt.name == "master"][0]
    assert master.name == "master"
    assert master.allowed_to_create.role == ProtectedTagRefUser(user_id=40, name="maintainers")
    assert master.allowed_to_create.users == [ProtectedTagRefUser(user_id=1, name="user1")]
    assert change_protected_tags.differences.get("master").get("status") == "added"
    assert mock_manager_tag.is_called
    assert "maintainers" in change_str
    assert "user1" in change_str
    assert "error" in change_str


def test_update_existing__protected_tag(mocker, fake_gitlab, fake_project):
    # Mock
    mocker.patch("gpc.tests.test_protected_tags.Project.save")
    mocker.patch(
        "gpc.tests.test_protected_tags.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )

    mock_manager_tag = mocker.patch(
        "gitlab.v4.objects.ProjectProtectedTagManager.create", mocker.Mock()
    )

    protectedtags = mocker.Mock()
    protectedtags.list = mocker.Mock(
        return_value=[
            Namespace({"name": "master", "create_access_levels": [{"access_level": 40}]}),
        ]
    )
    fake_project.protectedtags = protectedtags

    fake_project.users.list.return_value = [Namespace({"id": 1, "username": "user1"})]

    project_rules = Namespace(
        {
            "keep_existing_protected_tags": False,
            "protected_tags": [
                {
                    "pattern": "master",
                    "allowed_to_create": {"role": "maintainers", "users": ["user1"]},
                },
            ],
        }
    )

    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(
            config=mocker.Mock("fake_config"),
            debug=True,
            executor="protected_tags",
            mode=RunMode.APPLY,
        ),
    )
    p.execute()
    change_protected_tags = get_change_value(p, "protected_tags")
    change_str = p.echo_execution()

    assert len(change_protected_tags.before) == 1
    assert len(change_protected_tags.after) == 1
    master = [pt for pt in change_protected_tags.after if pt.name == "master"][0]
    assert master.allowed_to_create.role == ProtectedTagRefUser(user_id=40, name="maintainers")
    assert master.allowed_to_create.users == [ProtectedTagRefUser(user_id=1, name="user1")]
    assert change_protected_tags.differences.get("master").get("status") == "updated"
    assert mock_manager_tag.is_called
    assert "maintainers" in change_str
    assert "user1" in change_str


def test_remove_existing_protected_tag(mocker, fake_gitlab, fake_project):
    # Mock
    mocker.patch("gpc.tests.test_protected_tags.Project.save")
    mocker.patch(
        "gpc.tests.test_protected_tags.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )

    mock_manager_tag = mocker.patch(
        "gitlab.v4.objects.ProjectProtectedTagManager.create", mocker.Mock()
    )
    protectedtags = mocker.Mock()

    protectedtags.list = mocker.Mock(
        return_value=[
            Namespace({"name": "master", "create_access_levels": [{"access_level": 40}]}),
        ]
    )

    fake_project.protectedtags = protectedtags

    project_rules = Namespace({"keep_existing_protected_tags": False, "protected_tags": []})

    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(
            config=mocker.Mock("fake_config"), executor="protected_tags", mode=RunMode.APPLY
        ),
    )
    p.execute()
    change_protected_tags = get_change_value(p, "protected_tags")
    assert change_protected_tags.action == "removed"
    assert len(change_protected_tags.after) == 0
    assert change_protected_tags.differences.get("master").get("status") == "removed"
    assert mock_manager_tag.is_called


def test_keep_existing_protected_tag(mocker, fake_gitlab, fake_project):
    # Mock
    mocker.patch("gpc.tests.test_protected_tags.Project.save")
    mocker.patch(
        "gpc.tests.test_protected_tags.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )

    mock_manager_tag = mocker.patch(
        "gitlab.v4.objects.ProjectProtectedTagManager.create", mocker.Mock()
    )
    protectedtags = mocker.Mock()

    protectedtags.list = mocker.Mock(
        return_value=[
            Namespace({"name": "master", "create_access_levels": [{"access_level": 40}]}),
        ]
    )

    fake_project.protectedtags = protectedtags

    project_rules = Namespace({"keep_existing_protected_tags": True, "protected_tags": []})

    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(config=mocker.Mock("fake_config"), mode=RunMode.APPLY),
    )
    p.execute()
    change_protected_tags = get_change_value(p, "protected_tags")
    assert change_protected_tags.action == "kept"
    assert change_protected_tags.differences.get("master").get("status") == "kept"
    assert change_protected_tags.differences.get("master").get(
        "before"
    ) == change_protected_tags.differences.get("master").get("after")
    assert mock_manager_tag.is_called
