"""
test project runners
----------------------------------
"""

# Third Party Libraries
import pytest

from dictns import Namespace
from gitlab.exceptions import GitlabCreateError
from gitlab.exceptions import GitlabDeleteError
from gitlab.exceptions import GitlabGetError
from gitlab.v4.objects import Project  # pylint: disable=unused-import

# Gitlab-Project-Configurator Modules
from gpc.parameters import GpcParameters
from gpc.parameters import RunMode
from gpc.project_rule_executor import ProjectRuleExecutor
from gpc.tests.test_helpers import get_change_value


# pylint: disable=redefined-outer-name, unused-argument
# pylint: disable=protected-access,too-many-locals, duplicate-code

project_runners = [1235, 1236, 666]
project_runners_str = [str(x) for x in project_runners]
gitlab_runners = [1234, 1237] + project_runners


def project_runners_list(iterator, retry_transient_errors):
    return [
        Namespace({"id": 1235, "is_shared": False}),
        Namespace({"id": 1237, "is_shared": False}),
        Namespace({"id": 666, "is_shared": True}),
    ]


def gl_runners_get(runner_id, retry_transient_errors):
    if runner_id not in gitlab_runners:
        raise GitlabGetError("NotFound")


def p_runners_create(query, retry_transient_errors):
    if query.get("runner_id") in project_runners_str:
        raise GitlabCreateError("Runner already exist")


def p_runners_delete(runner_id, retry_transient_errors):
    if runner_id not in project_runners_str:
        raise GitlabDeleteError("Runner does not enabled")


@pytest.mark.parametrize(
    "project_rules, env_value, expected_diff, error_messages",
    [
        # Enable 1 runner and keep 1.
        (
            # project_rules
            Namespace(
                {
                    "runners": [
                        {"runner_id": 1234, "enabled": True},
                        {"runner_id": 1235, "enabled": True},
                    ]
                }
            ),
            None,
            {
                "1234": {
                    "status": "updated",
                    "before": {"runner_id": "1234", "enabled": False},
                    "after": {"runner_id": "1234", "enabled": True},
                },
                "1235": {
                    "status": "kept",
                    "before": {"runner_id": "1235", "enabled": True},
                    "after": {"runner_id": "1235", "enabled": True},
                },
            },
            [],
        ),
        # Enable 1 runner and disable 1.
        (
            # project_rules
            Namespace(
                {
                    "runners": [
                        {"runner_id": 1234, "enabled": True},
                        {"runner_id": 1235, "enabled": False},
                    ]
                }
            ),
            None,
            {
                "1234": {
                    "status": "updated",
                    "before": {"runner_id": "1234", "enabled": False},
                    "after": {"runner_id": "1234", "enabled": True},
                },
                "1235": {
                    "status": "updated",
                    "before": {"runner_id": "1235", "enabled": True},
                    "after": {"runner_id": "1235", "enabled": False},
                },
            },
            [],
        ),
        # Enable 1 runner, and try to enable an unexisting runner
        (
            # project_rules
            Namespace(
                {
                    "runners": [
                        {"runner_id": 1234, "enabled": True},
                        {"runner_id": 12, "enabled": True},
                    ]
                }
            ),
            None,
            {
                "1234": {
                    "status": "updated",
                    "before": {"runner_id": "1234", "enabled": False},
                    "after": {"runner_id": "1234", "enabled": True},
                }
            },
            ["The runner 12 does not exist."],
        ),
        # Enable 1 runner, and try to disable a shared runner
        (
            # project_rules
            Namespace(
                {
                    "runners": [
                        {"runner_id": 1234, "enabled": True},
                        {"runner_id": 666, "enabled": False},
                    ]
                }
            ),
            None,
            {
                "1234": {
                    "status": "updated",
                    "before": {"runner_id": "1234", "enabled": False},
                    "after": {"runner_id": "1234", "enabled": True},
                }
            },
            [
                "We can not update the runner 666 for the project fake/path/to/project because it"
                " is a shared runner."
            ],
        ),
        # Errors which should not expect.
        (
            # project_rules
            Namespace(
                {
                    "runners": [
                        {"runner_id": 1236, "enabled": True},
                        {"runner_id": 1237, "enabled": False},
                    ]
                }
            ),
            None,
            {
                "1236": {
                    "status": "updated",
                    "before": {"runner_id": "1236", "enabled": False},
                    "after": {"runner_id": "1236", "enabled": True},
                },
                "1237": {
                    "status": "updated",
                    "before": {"runner_id": "1237", "enabled": True},
                    "after": {"runner_id": "1237", "enabled": False},
                },
            },
            [
                "The runner 1237 is already disabled for the project fake/path/to/project.",
                "The runner 1236 is already enabled for the project fake/path/to/project.",
            ],
        ),
        # Runner ID from environment variable
        (
            # project_rules
            Namespace({"runners": [{"runner_id_from_envvar": "RUNNER_ID", "enabled": True}]}),
            "1234",
            {
                "1234": {
                    "status": "updated",
                    "before": {"runner_id": "1234", "enabled": False},
                    "after": {"runner_id": "1234", "enabled": True},
                },
            },
            [],
        ),
        # Runner ID from environment variable but empty
        (
            Namespace({"runners": [{"runner_id_from_envvar": "RUNNER_ID", "enabled": True}]}),
            None,
            {},
            ["Environment variable RUNNER_ID not set."],
        ),
        # No runner_id or runner_id_from_envvar
        (
            Namespace({"runners": [{"enabled": True}]}),
            None,
            {},
            ["Neither runner_id or runner_id_from_envvar are not set in your configuration."],
        ),
    ],
)
def test_project_runners(
    mocker,
    monkeypatch,
    capfd,
    fake_gitlab,
    fake_project,
    project_rules,
    env_value,
    expected_diff,
    error_messages,
):
    # Mock
    mocker.patch(
        "gpc.tests.test_project_runners.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    if not env_value:
        monkeypatch.delenv("RUNNER_ID", raising=False)
    else:
        monkeypatch.setenv("RUNNER_ID", env_value)

    project_runners_api = mocker.Mock()
    project_runners_api.create = mocker.Mock(side_effect=p_runners_create)
    project_runners_api.delete = mocker.Mock(side_effect=p_runners_delete)
    project_runners_api.list = mocker.Mock(side_effect=project_runners_list)
    fake_project.runners = project_runners_api
    gitlab_runners_api = mocker.Mock()
    gitlab_runners_api.get = mocker.Mock(side_effect=gl_runners_get)
    fake_gitlab.runners = gitlab_runners_api

    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(
            mocker.Mock("fake_config"),
            config_project_url="new project url",
            gpc_enabled_badge_url="new image url",
            mode=RunMode.APPLY,
        ),
    )
    p.execute()
    out, err = capfd.readouterr()
    # flake8: noqa

    if expected_diff:
        diff = get_change_value(p, "runners").differences
        assert diff == expected_diff

    for error_msg in error_messages:
        assert error_msg in out or error_msg in err
