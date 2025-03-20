# Third Party Libraries
import pytest

from path import Path

# Gitlab-Project-Configurator Modules
from gpc.config_validator import GpcConfigValidator
from gpc.helpers.exceptions import GpcDuplicateKey
from gpc.helpers.exceptions import GpcProfileError
from gpc.helpers.exceptions import GpcValidationError
from gpc.parameters import GpcParameters


VECTOR_CONFIG_DIR = Path(__file__).parent / "vectors"
BEHAVE_CONFIG_DIR = (
    Path(__file__).parent.parent.parent / "behave_test/integration_tests/features/config"
)


def validate_with_error(config_name, match, excep_type=GpcValidationError):
    gpcv = GpcConfigValidator(GpcParameters(config=VECTOR_CONFIG_DIR / config_name))
    with pytest.raises(excep_type, match=match):
        gpcv.run()


def test_mutual_excl():
    validate_with_error("err_mutual_excl.yaml", "Failed validating 'anyOf' in schema")


def test_validation_syntax_err_include():
    validate_with_error(
        "syntax_err_include.yaml",
        (
            r"Additional properties are not allowed "
            r"\('include_with_syntaxerror' was unexpected\)"
        ),
    )


def test_validation_syntax_err_type():
    validate_with_error(
        "err_invalid_type.yaml",
        r"Error: 123 is not valid under any of the given schemas(.|\n)*"
        r"'string'(.|\n)*'default_branch'",
    )


def test_validation_syntax_err_variable():
    validate_with_error(
        "err_syntax_in_variable.yaml",
        r"Error: 'SOME_VARIABLE_GROUP' is not valid under any of the given schemas"
        r"(.|\n)*'type': 'object'",
    )


# def test_validation_invalid_allowed():
#     validate_with_error(
#         "err_invalid_allowed.yaml",
#         r"Error: 'kurt cobain' is not one of "
#         r"\['maintainers', 'developers', 'none', 'no one'\]")


def test_validation_variable_import_and_name():
    validate_with_error(
        "err_variable_import_and_name.yaml",
        r"Error: (.|\n)* is not valid under any of the given schemas(.|\n)*'import'",
    )


def test_validation_variable_profile():
    validate_with_error(
        "err_syntax_in_variable_profile.yaml",
        r"Additional properties are not allowed \('potected' was unexpected\)",
    )


def test_validation_err_in_override():
    validate_with_error(
        "err_in_override.yaml",
        r"Error: (.|\n)*label(.|\n)* is not valid under any of the"
        r" given schemas(.|\n)*'custom_rules'",
    )


def test_validation_empty_branch_name():
    validate_with_error("err_empty_branch_name.yaml", r"\'\' does not match \'\^\(\.\+\)\$\'")


def test_validation_err_in_include():
    validate_with_error(
        "err_in_include.yaml",
        r"Additional properties are not allowed \(\'protectd_branches\' was unexpected\)",
    )


def test_validation_err_invalid_rule_name():
    validate_with_error(
        "err_invalid_rule_name.yaml",
        r"Project configuration in file 'err_invalid_rule_name.yaml' "
        r"declares an invalid rule name: '\['wrong_rule_name'\]'. "
        r"Available: \['myteam_master_rule'\]",
        excep_type=GpcProfileError,
    )


def test_validation_err_invalid_inherits_from():
    validate_with_error(
        r"err_invalid_inherits_from.yaml",
        r"In rule 'derived_rule', inherits_from declares an invalid rule name: "
        r"\['invalid_rule_name'\]. Available: \['myteam_master_rule', 'derived_rule'\]",
        excep_type=GpcProfileError,
    )


def test_validation_err_in_include2():
    validate_with_error(
        "err_in_include2.yaml",
        r"Additional properties are not allowed \(\'rules\' was unexpected\)",
    )


def test_project_members_err():
    validate_with_error(
        "err_in_project_members.yaml",
        r"Error: 'me.not.an.array' is not of type 'array'",
    )


def test_single_file_valid():
    gpcv = GpcConfigValidator(
        GpcParameters(config=VECTOR_CONFIG_DIR / "valid_single_file_config.yaml")
    )
    gpcv.run()
    assert gpcv.raw_config.get("projects_rules", [])[0].rule_name == "myteam_master_rule"
    assert gpcv.raw_config.get("projects_rules", [])[0].default_branch == "master"
    assert gpcv.raw_config.projects_configuration[0].paths == ["path/to/a/group"]


def test_override_to_null():
    gpcv = GpcConfigValidator(
        GpcParameters(config=Path(__file__).parent / "vectors" / "override_to_null.yaml")
    )
    gpcv.run()
    assert gpcv.raw_config.projects_configuration[0].custom_rules.protected_branches is None


@pytest.mark.parametrize("filename", [str(f.basename()) for f in BEHAVE_CONFIG_DIR.glob("*.yaml")])
def test_behave_test_config(filename: str):
    gpcv = GpcConfigValidator(GpcParameters(config=BEHAVE_CONFIG_DIR / filename))
    gpcv.run()


def test_config_duplicate():
    gpcv = GpcConfigValidator(GpcParameters(config=VECTOR_CONFIG_DIR / "duplicate_keys.yaml"))
    with pytest.raises(
        GpcDuplicateKey, match="'projects_configuration' appears 2 times in your configuration file"
    ):
        gpcv.check_duplicate_keys(VECTOR_CONFIG_DIR / "duplicate_keys.yaml")
