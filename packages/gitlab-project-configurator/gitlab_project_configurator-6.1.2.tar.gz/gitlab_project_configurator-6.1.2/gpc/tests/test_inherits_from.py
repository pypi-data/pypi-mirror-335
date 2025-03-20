"""
Test executor factory.
"""

# Third Party Libraries
import pytest

from dictns import Namespace

# Gitlab-Project-Configurator Modules
from gpc.helpers.remerge import ListOverrideBehavior
from gpc.rule_matcher import GroupRuleMatcher
from gpc.rule_matcher import ProjectRuleMatcher


# pylint: disable=redefined-outer-name, unused-argument, protected-access


def get_fixture(rule_type: str) -> Namespace:
    return Namespace(
        {
            rule_type: [
                {
                    "rule_name": "rule1",
                    "mergerequests": {
                        "merge_method": "ff",
                        "printing_merge_request_link_enabled": False,
                    },
                    "permissions": {"visibility": "internal"},
                    "default_branch": "master",
                    "protected_branches": [
                        {
                            "pattern": "rule_1_master",
                            "allowed_to_merge": "maintainers",
                            "allowed_to_push": "no one",
                        },
                    ],
                },
                {
                    "rule_name": "rule2",
                    "inherits_from": "rule1",
                    "mergerequests": {"merge_method": "merge"},
                    "permissions": {"visibility": "internal"},
                    "default_branch": "dev1",
                    "protected_branches": [
                        {
                            "pattern": "rule_2_master",
                            "allowed_to_merge": "maintainers",
                            "allowed_to_push": "no one",
                        },
                    ],
                },
                {
                    "rule_name": "rule4",
                    "approvers": {"members": ["toto"], "minimum": 1},
                    "permissions": {"visibility": "private"},
                },
                {
                    "rule_name": "rule3",
                    "inherits_from": "rule2",
                    "mergerequests": {"merge_method": "rebase_merge"},
                    "default_branch": "rule/rev3",
                },
            ]
        }
    )


@pytest.mark.parametrize(
    "rule_type,rule_matcher",
    [
        ("projects_rules", ProjectRuleMatcher),
        ("groups_rules", GroupRuleMatcher),
    ],
)
def test_inherits_from(rule_type, rule_matcher, fake_gitlab):
    raw_config = get_fixture(rule_type)

    rm = rule_matcher(
        gitlab=fake_gitlab,
        raw_config=raw_config,
        list_update_behavior=ListOverrideBehavior.REPLACE,
    )
    rule = Namespace(
        {
            "rule_name": "rule3",
            "inherits_from": ["rule2", "rule4"],
            "mergerequests": {"merge_method": "rebase_merge"},
            "default_branch": "rule/rev3",
        }
    )
    # pylint: disable=protected-access
    assert rm._handle_rule_inherits_from(rule) == {
        "mergerequests": {
            "merge_method": "rebase_merge",
            "printing_merge_request_link_enabled": False,
        },
        "permissions": {"visibility": "private"},
        "default_branch": "rule/rev3",
        "approvers": {"members": ["toto"], "minimum": 1},
        "protected_branches": [
            {
                "pattern": "rule_2_master",
                "allowed_to_merge": "maintainers",
                "allowed_to_push": "no one",
            },
        ],
        "inherits_from": ["rule2", "rule4"],
        "rule_name": "rule3",
    }


@pytest.mark.parametrize(
    "rule_type,rule_matcher",
    [
        ("projects_rules", ProjectRuleMatcher),
        ("groups_rules", GroupRuleMatcher),
    ],
)
def test_inherits_from_list_append(rule_type, rule_matcher, fake_gitlab):
    raw_config = get_fixture(rule_type)

    rm = rule_matcher(
        gitlab=fake_gitlab,
        raw_config=raw_config,
        list_update_behavior=ListOverrideBehavior.APPEND,
    )
    rule = Namespace(
        {
            "rule_name": "rule3",
            "inherits_from": "rule2",  # <== is not a list
            "mergerequests": {"merge_method": "rebase_merge"},
            "default_branch": "rule/rev3",
        }
    )
    # pylint: disable=protected-access
    assert rm._handle_rule_inherits_from(rule) == {
        "mergerequests": {
            "merge_method": "rebase_merge",
            "printing_merge_request_link_enabled": False,
        },
        "permissions": {"visibility": "internal"},
        "default_branch": "rule/rev3",
        "protected_branches": [
            {
                "pattern": "rule_1_master",
                "allowed_to_merge": "maintainers",
                "allowed_to_push": "no one",
            },
            {
                "pattern": "rule_2_master",
                "allowed_to_merge": "maintainers",
                "allowed_to_push": "no one",
            },
        ],
        "inherits_from": ["rule1", "rule2"],
        "rule_name": "rule3",
    }


def test_multiple_rules(fake_gitlab):
    raw_config = get_fixture("projects_rules")

    rm = ProjectRuleMatcher(
        gitlab=fake_gitlab,
        raw_config=raw_config,
        list_update_behavior=ListOverrideBehavior.REPLACE,
    )
    rule = Namespace(
        {
            "rule_name": "rule3",
            "inherits_from": ["rule2"],
            "mergerequests": {"merge_method": "rebase_merge"},
            "default_branch": "rule/rev3",
        }
    )
    rule5 = Namespace(
        {
            "rule_name": "rule5",
            "mergerequests": {"merge_method": "rebase_merge"},
            "default_branch": "rule/rev5",
        }
    )
    merged_rules = rm._prepare_rule([rule, rule5], Namespace({}))
    assert merged_rules == {
        "mergerequests": {
            "merge_method": "rebase_merge",
            "printing_merge_request_link_enabled": False,
        },
        "permissions": {"visibility": "internal"},
        "default_branch": "rule/rev5",
        "protected_branches": [
            {
                "pattern": "rule_2_master",
                "allowed_to_merge": "maintainers",
                "allowed_to_push": "no one",
            }
        ],
        "inherits_from": ["rule2"],  # <= should be a list
        "rule_name": ["rule3", "rule5"],
    }
    # pylint: disable=protected-access
