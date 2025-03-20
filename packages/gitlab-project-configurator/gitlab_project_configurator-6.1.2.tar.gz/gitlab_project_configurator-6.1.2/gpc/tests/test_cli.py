"""
test_gpc
----------------------------------
Tests for `gpc` module.
"""

# Standard Library
import os

# Third Party Libraries
import pytest

from click.testing import CliRunner
from click.testing import Result
from path import Path

# Gitlab-Project-Configurator Modules
from gpc.cli import entrypoint
from gpc.cli import init_gitlab
from gpc.cli import sentry_before_send
from gpc.general_executor import GpcGeneralExecutor
from gpc.parameters import GpcParameters


# pylint: disable=redefined-outer-name, unused-argument, protected-access


def invoke_gpc_validate(config_file: Path) -> Result:
    runner = CliRunner()
    result = runner.invoke(
        entrypoint,
        [
            "-c",
            str(config_file),
            "--validate",
            "--debug",
            "--gitlab-url",
            "fake.gitlab.url",
        ],
    )
    print("\nstdout:", getattr(result, "stdout", ""))  # To make Mypy happy
    print("exception:", result.exception)
    return result


def test_invoke_validate_from_cli():
    result = invoke_gpc_validate(Path(__file__).parent / "vectors" / "test_with_include.yaml")
    assert result.exit_code == 0


@pytest.fixture
def fake_projectrule_executor(mocker):
    """
    Fake the project rule executor.

    To avoid unwanted requests to our fake gitlab.

    Yields the constructor of the executor
    """

    build_fake_executor = mocker.Mock(name="fake_constructor")
    build_fake_executor.raise_if_error = False

    def mock_init(*args, **kwargs):
        return build_fake_executor

    mocked = mocker.patch("gpc.general_executor.ProjectRuleExecutor", side_effect=mock_init)

    yield mocked


@pytest.fixture
def fake_iter_project_from_path(mocker):
    def donotdeglob(iter_p_n):
        yield from iter_p_n

    mocker.patch(
        "gpc.tests.test_cli.GpcGeneralExecutor._iter_list_project_from_path",
        side_effect=donotdeglob,
    )


@pytest.fixture
def fake_gpc(request, mocker, fake_gitlab, fake_iter_project_from_path):
    gpc = GpcGeneralExecutor(
        GpcParameters(config=Path(__file__).parent / "vectors" / request.param, debug=True),
        gitlab=fake_gitlab,
    )
    mocker.patch("gpc.tests.test_cli.GpcGeneralExecutor.notify_changes")

    yield gpc


def test_exit_code(mocker):
    mocker.patch("gpc.tests.test_cli.GpcGeneralExecutor.run", mocker.Mock(return_value=10))
    mocker.patch("gpc.cli.init_gitlab", mocker.Mock())
    with pytest.raises(SystemExit) as e:
        # pylint: disable=no-value-for-parameter
        entrypoint(["-c", "fake_config.yaml", "--gitlab-url", "fake.gitlab_url"])
        # pylint: enable=no-value-for-parameter
    assert e.value.code == 10


# Trick: https://hackebrot.github.io/pytest-tricks/mark_parametrize_with_indirect/
@pytest.mark.parametrize(
    "fake_gpc",
    ["test_with_include.yaml"],
    indirect=True,
)
def test_invoke_from_obj(mocker, fake_gpc, fake_projectrule_executor):
    mocker.patch("gpc.general_executor.GpcGeneralExecutor._check_warnings")
    exit_code = fake_gpc.run()
    fake_gpc._warnings = {}
    assert exit_code == 0
    assert len(fake_projectrule_executor.call_args_list) == 3
    fake_executor_constructor = fake_projectrule_executor.call_args_list[0][1]
    assert fake_executor_constructor["project_path"] == "fake/path/to/a_project_with_specific_rule"
    assert fake_executor_constructor["rule"]["rule_name"] == ["derived_rule"]
    assert fake_executor_constructor["rule"]["permissions"]["visibility"] == "internal"
    assert (
        fake_executor_constructor["rule"]["default_branch"] == "master"
    ), "master should inherits from 'myteam_master_rule'"

    fake_executor_constructor = fake_projectrule_executor.call_args_list[1][1]
    assert fake_executor_constructor["project_path"] == "fake/path/to/project"
    assert fake_executor_constructor["rule"]["rule_name"] == ["myteam_master_rule"]
    assert fake_executor_constructor["rule"]["default_branch"] == "master"
    assert fake_executor_constructor["rule"]["permissions"]["visibility"] == "private"

    fake_executor_constructor = fake_projectrule_executor.call_args_list[2][1]
    assert fake_executor_constructor["project_path"] == "other/path/other_project"
    assert fake_executor_constructor["rule"]["rule_name"] == ["myteam_master_rule"]
    assert fake_executor_constructor["rule"]["default_branch"] == "master"
    assert fake_executor_constructor["rule"]["permissions"]["visibility"] == "private"


@pytest.mark.parametrize(
    "fake_gpc",
    ["variables_overrides.yaml"],
    indirect=True,
)
def test_variables_overwrite(mocker, fake_gpc, fake_projectrule_executor):
    mocker.patch("gpc.general_executor.GpcGeneralExecutor._check_warnings")
    exit_code = fake_gpc.run()
    assert exit_code == 0
    project_executor_calls = fake_projectrule_executor.call_args_list

    assert len(project_executor_calls) == 3

    # Assert 'path/to/some/project' has overrided variables
    fake_executor_constructor = project_executor_calls[0][1]
    assert fake_executor_constructor["project_path"] == "path/to/some/project"
    assert fake_executor_constructor["rule"] == {
        "rule_name": ["master_rule"],
        "default_branch": "master",
        "variables": [{"name": "FORCED_VARIABLE", "value": "forced_value"}],
        "custom_rules": "yes",
    }

    # Assert 'path/to/another/project' has won't loose its variables
    fake_executor_constructor = project_executor_calls[1][1]
    assert fake_executor_constructor["project_path"] == "path/to/another/project"
    assert fake_executor_constructor["rule"] == {
        "default_branch": "master",
        "rule_name": ["master_rule"],
        "variables": None,
        "custom_rules": "yes",
    }

    # Assert 'path/to/yet/another/project' will set the variables defined in the rules
    fake_executor_constructor = project_executor_calls[2][1]
    assert fake_executor_constructor["project_path"] == "path/to/yet/another/project"
    assert fake_executor_constructor["rule"] == {
        "default_branch": "master",
        "rule_name": ["master_rule"],
        "variables": [{"name": "PREDEFINED_VARIABLE", "value": "predefined_value"}],
    }


def test_init_gitlab_from_arg():
    gl = init_gitlab(
        gitlab_cfg=None,
        gitlab_profile=None,
        gitlab_url="fake.url",
        gitlab_token="faketoken",  # nosec B106
    )
    assert gl.url == "fake.url"


def test_init_gitlab_from_profile(mocker):
    fake_gl = mocker.Mock(name="gl")
    fake_gl.url = "fake.profile.url"
    fake_gl.private_token = "fake.profile.token"  # nosec
    mocker.patch("gpc.cli.gl.Gitlab.from_config", return_value=fake_gl)
    gl = init_gitlab(
        gitlab_cfg="~/.fakegitlab.cfg",
        gitlab_profile="fakeprofile",
        gitlab_url=None,
        gitlab_token=None,
    )
    assert gl.url == "fake.profile.url"


def test_sentry_before_send(mocker):
    mocker.patch("gpc.cli.gpc_version", mocker.Mock(return_value="1.1.1"))
    oldenvion = os.environ.copy()
    try:
        os.environ["CI_JOB_URL"] = "CI_JOB_URL"
        os.environ["CI_PIPELINE_URL"] = "CI_PIPELINE_URL"
        os.environ["GPC_CONFIG"] = "GPC_CONFIG"
        event = {}
        sentry_before_send(event, "useless")
        assert event == {
            "environ": {
                "CI_JOB_URL": "CI_JOB_URL",
                "CI_PIPELINE_URL": "CI_PIPELINE_URL",
                "GPC_CONFIG": "GPC_CONFIG",
            },
            "gpc_version": "1.1.1",
        }
    finally:
        os.environ = oldenvion
