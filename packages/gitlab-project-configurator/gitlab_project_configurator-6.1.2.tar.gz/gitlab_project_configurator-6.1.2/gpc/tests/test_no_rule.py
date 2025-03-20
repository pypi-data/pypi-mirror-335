# Standard Library
from pathlib import Path

# Gitlab-Project-Configurator Modules
from gpc.config_validator import GpcConfigValidator
from gpc.parameters import GpcParameters


VECTOR_CONFIG_DIR = Path(__file__).parent / "vectors"


def test_no_rule():
    gpcv = GpcConfigValidator(GpcParameters(config=VECTOR_CONFIG_DIR / "no_rule_config.yaml"))
    assert gpcv.run() == 0
    assert gpcv.raw_config == {
        "variable_profiles": {
            "variable_profile_name": [{"name": "profile_variable", "value": "profile_value"}]
        },
        "groups_configuration": [
            {
                "paths": ["path/to/some/group"],
                "custom_rules": {
                    "variables": [
                        {"name": "GROUP_VARIABLE", "value": "group_value"},
                        {"import": "variable_profile_name"},
                    ]
                },
            }
        ],
        "projects_configuration": [
            {
                "paths": ["path/to/some/project"],
                "custom_rules": {
                    "variables": [
                        {"name": "PROJECT_VARIABLE", "value": "project_value"},
                        {"import": "variable_profile_name"},
                    ]
                },
            }
        ],
        "include": [],
    }
