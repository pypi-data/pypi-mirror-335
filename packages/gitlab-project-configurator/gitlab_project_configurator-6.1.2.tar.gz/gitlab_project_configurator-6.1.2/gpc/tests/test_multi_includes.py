"""
Test executor factory.
"""

# Third Party Libraries
from dictns import Namespace
from path import Path

# Gitlab-Project-Configurator Modules
from gpc.general_executor import GpcGeneralExecutor
from gpc.parameters import GpcParameters


# pylint: disable=redefined-outer-name, unused-argument, protected-access
TEST_FILE_MULTI_INCLUDE = Path(__file__).parent / "vectors/test_multi_includes_project.yaml"


def test_multi_includes(fake_gitlab):
    parameters = GpcParameters(config=TEST_FILE_MULTI_INCLUDE)
    executor = GpcGeneralExecutor(parameters=parameters, gitlab=fake_gitlab)
    executor.load_includes()
    executor.validate()

    expected_result = Namespace(
        {
            "projects_configuration": [
                {"paths": ["fake/path/to/project_1"], "rule_name": "my_rule_1"},
                {"paths": ["fake/path/to/project_2"], "rule_name": "my_rule_2"},
                {"paths": ["fake/path/to/project_3"], "rule_name": "my_rule_2"},
            ],
            "projects_rules": [
                {
                    "rule_name": "my_rule_1",
                    "default_branch": "dev/test",
                    "protected_branches": [
                        {
                            "pattern": "my_rule_1_master",
                            "allowed_to_merge": "maintainers",
                            "allowed_to_push": "no one",
                        }
                    ],
                    "permissions": {"visibility": "private"},
                    "variables": [{"import": "GROUP_VAR1"}],
                },
                {
                    "rule_name": "my_rule_2",
                    "inherits_from": "my_rule_1",
                    "default_branch": "master",
                    "protected_branches": [
                        {
                            "pattern": "my_rule_2_master",
                            "allowed_to_merge": "maintainers",
                            "allowed_to_push": "no one",
                        },
                    ],
                    "permissions": {"visibility": "internal"},
                    "variables": [
                        {"import": "GROUP_VAR2"},
                        {"name": "LOCAL_VARIABLE", "value": "other value"},
                    ],
                },
            ],
            "variable_profiles": {
                "GROUP_VAR1": [{"name": "VAR1_1", "value": "val1_1"}],
                "GROUP_VAR2": [{"name": "VAR2_1", "value": "val21", "protected": False}],
            },
            "member_profiles": [
                {"name": "approvers_1", "role": "maintainers", "members": ["toto"]},
                {
                    "name": "approvers_2",
                    "role": "developers",
                    "members": ["gitlab-nestor-integ-useless"],
                },
            ],
            "groups_configuration": [],
        }
    )
    assert executor._uninited_config == expected_result


def test_multi_layer_includes(fake_gitlab):
    parameters = GpcParameters(
        config=Path(__file__).parent / "vectors/test_multi_layers_include.yaml"
    )
    executor = GpcGeneralExecutor(parameters=parameters, gitlab=fake_gitlab)
    executor.load_includes()
    executor.validate()

    expected_result = Namespace(
        {
            "projects_configuration": [
                {"paths": ["fake/path/to/project_1"], "rule_name": "my_rule_1"},
                {"paths": ["fake/path/to/project_2"], "rule_name": "my_rule_2"},
                {"paths": ["fake/path/to/project_3"], "rule_name": "my_rule_2"},
            ],
            "projects_rules": [
                {
                    "rule_name": "my_rule_1",
                    "default_branch": "dev/test",
                    "permissions": {"visibility": "private"},
                    "variables": [{"import": "GROUP_VAR1"}],
                },
                {
                    "rule_name": "my_rule_2",
                    "default_branch": "master",
                    "permissions": {"visibility": "internal"},
                    "variables": [
                        {"import": "GROUP_VAR2"},
                        {"name": "LOCAL_VARIABLE", "value": "other value"},
                    ],
                },
            ],
            "variable_profiles": {
                "GROUP_VAR1": [{"name": "VAR1_1", "value": "val1_1"}],
                "GROUP_VAR2": [{"name": "VAR2_1", "value": "val21", "protected": False}],
            },
            "member_profiles": [
                {"name": "approvers_1", "role": "maintainers", "members": ["toto"]},
                {
                    "name": "approvers_2",
                    "role": "developers",
                    "members": ["gitlab-nestor-integ-useless"],
                },
            ],
            "groups_configuration": [],
        }
    )
    assert executor._uninited_config == expected_result
    # check a setting that is inside the second level
    assert executor._uninited_config.member_profiles[1].name == "approvers_2"
