# Third Party Libraries
import pytest

from dictns import Namespace

# Gitlab-Project-Configurator Modules
from gpc.general_executor import GpcGeneralExecutor
from gpc.helpers.remerge import ListOverrideBehavior
from gpc.helpers.types import ProjectPathRule
from gpc.rule_matcher import GroupRuleMatcher
from gpc.rule_matcher import ProjectRuleMatcher


# pylint: disable=unused-argument,protected-access


def test_is_path_group(mocker):
    fake_gitlab = mocker.Mock("gitlab")
    fake_gitlab.groups = mocker.Mock("groups")

    def get_group(_group_name, retry_transient_errors):
        fake_group = mocker.Mock("Fake group")
        fake_group.full_path = "full/path/of/the/group"
        return fake_group

    fake_gitlab.groups.get = mocker.Mock("groups.get", side_effect=get_group)
    gpc = GpcGeneralExecutor(mocker.Mock("params"), fake_gitlab)
    assert gpc._is_path_a_group("a/fake/group") is True  # pylint: disable=protected-access


def test_generates_project_from_path(mocker):
    def get_group(_group_name, retry_transient_errors):
        fake_group = mocker.Mock("Fake group")
        fake_group.full_path = "full/path/of/the/group"
        fake_group.projects = mocker.Mock()
        project = mocker.Mock()
        project.shared_with_groups = []
        project.path_with_namespace = "group/sub/project"
        fake_group.projects.list = mocker.Mock(return_value=[project])
        return fake_group

    def get_projects(*args, **kwargs):
        project1 = mocker.Mock()
        project1.shared_with_groups = []
        project1.path_with_namespace = "group/sub/project"

        project2 = mocker.Mock()
        project2.shared_with_groups = []
        project2.path_with_namespace = "team1/project"

        project3 = mocker.Mock()
        project3.shared_with_groups = []
        project3.path_with_namespace = "team2/project"
        return [project1, project2, project3]

    fake_gitlab = mocker.Mock("gitlab")
    fake_gitlab.projects = mocker.Mock()
    fake_gitlab.projects.list = mocker.Mock(side_effect=get_projects)

    fake_gitlab.groups = mocker.Mock()
    fake_gitlab.groups.get = mocker.Mock(side_effect=get_group)
    ppr = ProjectPathRule("a/fake/group", "rule", False, True)
    gpc = GpcGeneralExecutor(mocker.Mock("params"), fake_gitlab)
    sub_group_projects = list(gpc._generates_project_from_path(ppr))
    assert sub_group_projects == [ProjectPathRule("group/sub/project", "rule", False, True)]

    ppr_all = ProjectPathRule("/", "rule", False, True)
    all_projects = list(gpc._generates_project_from_path(ppr_all))
    assert all_projects == [
        ProjectPathRule("group/sub/project", "rule", False, True),
        ProjectPathRule("team1/project", "rule", False, True),
        ProjectPathRule("team2/project", "rule", False, True),
    ]


@pytest.mark.parametrize("rule_matcher", [GroupRuleMatcher, ProjectRuleMatcher])
@pytest.mark.parametrize(
    "rule, project_cfg, list_override_behavior, expected_rule",
    [
        ({}, {}, ListOverrideBehavior.REPLACE, {}),
        ({"a_rule": "a_val"}, {}, ListOverrideBehavior.REPLACE, {"a_rule": "a_val"}),
        (
            {"a_rule": "a_val"},
            {"custom_rules": {"another_rule": "another_val"}},
            ListOverrideBehavior.REPLACE,
            {"a_rule": "a_val", "another_rule": "another_val", "custom_rules": "yes"},
        ),
        (
            {"a_rule": "a_val"},
            {"custom_rules": {"a_rule": "another_val"}},
            ListOverrideBehavior.REPLACE,
            {"a_rule": "another_val", "custom_rules": "yes"},
        ),
        (
            {"a_dict_rule": {"key1": "val1", "key2": "val2"}},
            {"custom_rules": {"a_dict_rule": {"other_key": "other_val"}}},
            ListOverrideBehavior.REPLACE,
            {
                "a_dict_rule": {"key1": "val1", "key2": "val2", "other_key": "other_val"},
                "custom_rules": "yes",
            },
        ),
        (
            {"a_dict_rule": {"key1": "val1", "a_list": ["a", "b"]}},
            {"custom_rules": {"a_dict_rule": {"a_list": ["c", "d"]}}},
            ListOverrideBehavior.REPLACE,
            {"a_dict_rule": {"a_list": ["c", "d"], "key1": "val1"}, "custom_rules": "yes"},
        ),
        (
            {"a_dict_rule": {"key1": "val1", "a_list": ["a", "b"]}},
            {"custom_rules": {"a_dict_rule": {"a_list": ["c", "d"]}}},
            ListOverrideBehavior.APPEND,
            {
                "a_dict_rule": {"a_list": ["a", "b", "c", "d"], "key1": "val1"},
                "custom_rules": "yes",
            },
        ),
        (
            {"a_dict_rule": {"key1": "val1", "a_list": []}},
            {"custom_rules": {"a_dict_rule": {"a_list": ["c", "d"]}}},
            ListOverrideBehavior.REPLACE,
            {"a_dict_rule": {"a_list": ["c", "d"], "key1": "val1"}, "custom_rules": "yes"},
        ),
        (
            {"a_dict_rule": {"key1": "val1", "a_list": ["a", "b"]}},
            {"custom_rules": {"a_dict_rule": {"a_list": []}}},
            ListOverrideBehavior.REPLACE,
            {"a_dict_rule": {"a_list": [], "key1": "val1"}, "custom_rules": "yes"},
        ),
        (
            {"a_dict_rule": {"key1": "val1", "a_list": ["a", "b"]}},
            {"custom_rules": {"a_dict_rule": {"a_list": []}}},
            ListOverrideBehavior.APPEND,
            {"a_dict_rule": {"a_list": ["a", "b"], "key1": "val1"}, "custom_rules": "yes"},
        ),
        (
            {"a_dict_rule": {"key1": "val1", "a_list": ["a", "b"]}},
            {"custom_rules": {"a_dict_rule": {"a_list": None}}},
            ListOverrideBehavior.REPLACE,
            {"a_dict_rule": {"a_list": None, "key1": "val1"}, "custom_rules": "yes"},
        ),
        (
            {"a_dict_rule": {"key1": "val1", "a_list": ["a", "b"]}},
            {"custom_rules": {"a_dict_rule": {"a_list": None}}},
            ListOverrideBehavior.APPEND,
            {"a_dict_rule": {"a_list": None, "key1": "val1"}, "custom_rules": "yes"},
        ),
    ],
)
def test_rule_override(
    mocker,
    fake_gitlab,
    rule_matcher,
    rule,
    project_cfg,
    list_override_behavior,
    expected_rule,
):
    rm = rule_matcher(
        gitlab=fake_gitlab,
        raw_config=mocker.Mock("raw_config"),
        list_update_behavior=list_override_behavior,
    )
    rule = Namespace(rule)
    project_cfg = Namespace(project_cfg)
    # pylint: disable=protected-access
    assert rm._handle_custom_rules(rule, project_cfg) == expected_rule
    # pylint: enable=protected-access
