"""
test_update default branch and visibility
----------------------------------
"""

# Third Party Libraries
from dictns import Namespace
from gitlab.exceptions import GitlabGetError
from gitlab.v4.objects import Project  # pylint: disable=unused-import

# Gitlab-Project-Configurator Modules
from gpc.executors.project_setting_executor import ProjectSettingExecutor
from gpc.parameters import GpcParameters
from gpc.parameters import RunMode
from gpc.project_rule_executor import ProjectRuleExecutor
from gpc.tests.test_helpers import get_executor


# pylint: disable=redefined-outer-name, unused-argument, protected-access, duplicate-code


def test_update_default_branch_visibility(mocker, fake_gitlab, fake_project):
    # Mock
    mocker.patch("gpc.tests.test_def_branch_visibility.Project.save")
    mocker.patch(
        "gpc.tests.test_def_branch_visibility.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )

    project_rules = Namespace(
        {
            "default_branch": "master",
            "permissions": {
                "visibility": "private",
                "request_access_enabled": True,
                "wiki_access_level": "disabled",
                "issues_access_level": "disabled",
                "snippets_access_level": "disabled",
                "lfs_enabled": False,
                "container_registry_access_level": "disabled",
                "packages_enabled": False,
                "builds_access_level": "disabled",
                "merge_requests_access_level": "disabled",
                "infrastructure_access_level": "Private",
                "releases_access_level": "Private",
                "feature_flags_access_level": "Private",
                "environments_access_level": "Private",
                "monitor_access_level": "Private",
                "pages_access_level": "Private",
                "analytics_access_level": "Private",
                "forking_access_level": "Private",
                "security_and_compliance_access_level": "Private",
            },
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
                "before": {
                    "visibility": "old_visibility",
                    "request_access_enabled": False,
                    "wiki_access_level": "enabled",
                    "issues_access_level": "enabled",
                    "snippets_access_level": "enabled",
                    "lfs_enabled": True,
                    "container_registry_access_level": "enabled",
                    "packages_enabled": True,
                    "builds_access_level": "enabled",
                    "merge_requests_access_level": "enabled",
                    "infrastructure_access_level": "disabled",
                    "releases_access_level": "disabled",
                    "feature_flags_access_level": "disabled",
                    "environments_access_level": "disabled",
                    "monitor_access_level": "disabled",
                    "pages_access_level": "disabled",
                    "analytics_access_level": "disabled",
                    "forking_access_level": "disabled",
                    "security_and_compliance_access_level": "disabled",
                },
                "after": {
                    "visibility": "private",
                    "request_access_enabled": True,
                    "wiki_access_level": "disabled",
                    "issues_access_level": "disabled",
                    "snippets_access_level": "disabled",
                    "lfs_enabled": False,
                    "container_registry_access_level": "disabled",
                    "builds_access_level": "disabled",
                    "merge_requests_access_level": "disabled",
                    "packages_enabled": False,
                    "infrastructure_access_level": "Private",
                    "releases_access_level": "Private",
                    "feature_flags_access_level": "Private",
                    "environments_access_level": "Private",
                    "monitor_access_level": "Private",
                    "pages_access_level": "Private",
                    "analytics_access_level": "Private",
                    "forking_access_level": "Private",
                    "security_and_compliance_access_level": "Private",
                },
                "action": "updated",
            },
        },
    ]


def test_update_default_branch_ko(mocker, fake_gitlab, fake_project):
    # Mock
    mocker.patch("gpc.tests.test_def_branch_visibility.Project.save")
    mocker.patch(
        "gpc.tests.test_def_branch_visibility.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    branches_service = mocker.Mock()
    branches_service.get = mocker.Mock(
        side_effect=GitlabGetError(response_code=404, response_body="Branch not found")
    )
    fake_project.branches = branches_service
    project_rules = Namespace(
        {
            "default_branch": "master",
            "permissions": {
                "visibility": "private",
                "request_access_enabled": True,
                "wiki_access_level": "disabled",
                "issues_access_level": "disabled",
                "snippets_access_level": "disabled",
                "lfs_enabled": False,
                "builds_access_level": "disabled",
                "merge_requests_access_level": "disabled",
                "releases_access_level": "Private",
                "infrastructure_access_level": "Private",
            },
        }
    )
    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(config=mocker.Mock("fake_config"), mode=RunMode.APPLY),
    )
    p.update_settings()
    executor = get_executor(p, ProjectSettingExecutor)
    assert not executor.default_branch_updator.success


def test_update_visibility_ko(mocker, fake_gitlab, fake_project):
    # Mock
    mocker.patch("gpc.tests.test_def_branch_visibility.Project.save")
    mocker.patch(
        "gpc.tests.test_def_branch_visibility.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )

    project_rules = Namespace({"permissions": {"visibility": "toto"}})
    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(config=mocker.Mock("fake_config")),
    )
    p.update_settings()
    executor = get_executor(p, ProjectSettingExecutor)
    assert "not acceptable" in executor.error_message
    report = p.get_report()
    assert report["errors"]
