"""
test_update mergerequest config
----------------------------------
"""

# Third Party Libraries
from dictns import Namespace
from gitlab.v4.objects import Project  # pylint: disable=unused-import

# Gitlab-Project-Configurator Modules
from gpc.executors.project_setting_executor import ProjectSettingExecutor
from gpc.parameters import GpcParameters
from gpc.parameters import RunMode
from gpc.project_rule_executor import ProjectRuleExecutor
from gpc.tests.test_helpers import get_change_value
from gpc.tests.test_helpers import get_executor


# pylint: disable=redefined-outer-name, unused-argument, protected-access, duplicate-code


def test_merge_request_description(mocker, fake_gitlab, fake_project):
    # Mock
    mocker.patch("gpc.tests.test_def_branch_visibility.Project.save")
    fake_project.only_allow_merge_if_all_discussions_are_resolved = False
    fake_project.only_allow_merge_if_pipeline_succeeds = True
    fake_project.resolve_outdated_diff_discussions = False
    fake_project.printing_merge_request_link_enabled = True
    fake_project.remove_source_branch_after_merge = False
    fake_project.merge_method = "merge"

    project_rules = Namespace(
        {
            "mergerequests": {
                "only_allow_merge_if_all_discussions_are_resolved": True,
                "only_allow_merge_if_pipeline_succeeds": True,
                "resolve_outdated_diff_discussions": True,
                "printing_merge_request_link_enabled": True,
                "remove_source_branch_after_merge": True,
                "merge_method": "ff",
            }
        }
    )
    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(config=mocker.Mock("fake_config"), mode=RunMode.APPLY),
    )
    p.execute()
    assert get_change_value(p, "mergerequests", "merge_method").action == "updated"
    assert (
        get_change_value(
            p, "mergerequests", "only_allow_merge_if_all_discussions_are_resolved"
        ).action
        == "updated"
    )
    assert (
        get_change_value(p, "mergerequests", "only_allow_merge_if_pipeline_succeeds").action
        == "kept"
    )
    assert (
        get_change_value(p, "mergerequests", "resolve_outdated_diff_discussions").action
        == "updated"
    )
    assert (
        get_change_value(p, "mergerequests", "printing_merge_request_link_enabled").action == "kept"
    )
    assert (
        get_change_value(p, "mergerequests", "remove_source_branch_after_merge").action == "updated"
    )


def test_merge_request_description_ko(mocker, fake_gitlab, fake_project):
    # Mock
    mocker.patch("gpc.tests.test_def_branch_visibility.Project.save")
    mocker.patch(
        "gpc.tests.test_def_branch_visibility.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    fake_project.only_allow_merge_if_all_discussions_are_resolved = False
    fake_project.only_allow_merge_if_pipeline_succeeds = True
    fake_project.merge_method = "merge"

    project_rules = Namespace(
        {
            "mergerequests": {
                "only_allow_merge_if_all_discussions_are_resolved": True,
                "only_allow_merge_if_pipeline_succeeds": True,
                "merge_method": "toto",
            }
        }
    )
    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(config=mocker.Mock("fake_config"), mode=RunMode.APPLY),
    )

    p.execute()
    executor = get_executor(p, ProjectSettingExecutor)
    assert "Invalid merge method" in executor.error_message


def test_squash_options_ok(mocker, fake_gitlab, fake_project):
    mocker.patch("gpc.tests.test_def_branch_visibility.Project.save")
    fake_project.squash_option = "never"

    project_rules = Namespace(
        {
            "mergerequests": {
                "squash_option": "allow",
            }
        }
    )
    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(config=mocker.Mock("fake_config"), mode=RunMode.APPLY),
    )
    p.execute()
    assert get_change_value(p, "mergerequests", "squash_option").action == "updated"


def test_squash_options_ko(mocker, fake_gitlab, fake_project):
    mocker.patch("gpc.tests.test_def_branch_visibility.Project.save")
    fake_project.squash_option = "never"

    project_rules = Namespace(
        {
            "mergerequests": {
                "squash_option": "invalid",
            }
        }
    )
    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(config=mocker.Mock("fake_config"), mode=RunMode.APPLY),
    )
    p.execute()
    assert "Invalid squash option" in p.errors[0]["exception"]
