"""
Conftest
----------------------------------
"""

# Third Party Libraries
import pytest


# pylint: disable=redefined-outer-name
class FakeGitlabGroup:
    def __init__(
        self,
        web_url,
        name,
        path,
        full_path,
        description,
        default_branch,
        visibility,
        request_access_enabled,
        runners_token,
    ):
        self.web_url = web_url
        self.name = name
        self.path = path
        self.full_path = full_path
        self.description = description
        self.default_branch = default_branch
        self.visibility = visibility
        self.request_access_enabled = request_access_enabled
        self.runners_token = runners_token


@pytest.fixture
def fake_group():
    return FakeGitlabGroup(
        web_url="https://fake.gitlab.server/fake/group/path",
        name="Fake Group",
        path="fake/group/path",
        full_path="fake/group/path",
        description="My Fake Group",
        default_branch="old_default_branch",
        visibility="old_visibility",
        request_access_enabled=False,
        runners_token="ba324ca7b1c77fc20bb9",
    )


@pytest.fixture
def fake_project(mocker):
    fp = mocker.Mock(name="Fake Gitlab Project")
    fp.web_url = "https://fake.gitlab.server/fake/project/path"
    fp.default_branch = "old_default_branch"
    fp.visibility = "old_visibility"
    fp.request_access_enabled = False
    fp.wiki_access_level = "enabled"
    fp.lfs_enabled = True
    fp.builds_access_level = "enabled"
    fp.merge_requests_access_level = "enabled"
    fp.archived = False
    fp.issues_access_level = "enabled"
    fp.snippets_access_level = "enabled"
    fp.packages_enabled = True
    fp.infrastructure_access_level = "disabled"
    fp.releases_access_level = "disabled"
    fp.feature_flags_access_level = "disabled"
    fp.environments_access_level = "disabled"
    fp.monitor_access_level = "disabled"
    fp.pages_access_level = "disabled"
    fp.analytics_access_level = "disabled"
    fp.forking_access_level = "disabled"
    fp.security_and_compliance_access_level = "disabled"
    fp.container_registry_access_level = "enabled"
    fp.keep_latest_artifact = True
    fake_badges = mocker.Mock(name="fake badge list")
    fake_badges.list = mocker.Mock(return_value=[])
    fp.badges = fake_badges
    fp.members_all.list = mocker.Mock(return_value=[])
    fp.users.list.return_value = []
    fp.empty_repo = False
    return fp


@pytest.fixture
def fake_gitlab(mocker, fake_group, fake_project):
    fgl = mocker.Mock(name="Fake Gitlab")
    fgl.url = "https://fake.gitlab.url/"
    fgl.projects = mocker.Mock()
    fgl.projects.get = mocker.Mock(return_value=fake_project)
    fgl.groups = mocker.Mock()
    fgl.groups.get = mocker.Mock(return_value=fake_group)
    return fgl
