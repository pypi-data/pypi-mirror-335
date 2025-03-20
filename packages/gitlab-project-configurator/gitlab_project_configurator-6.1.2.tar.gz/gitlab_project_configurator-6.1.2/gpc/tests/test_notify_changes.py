# Third Party Libraries
import pytest

from dotmap import DotMap
from path import Path

# Gitlab-Project-Configurator Modules
from gpc.general_executor import GpcGeneralExecutor
from gpc.parameters import RunMode


# pylint: disable=protected-access


@pytest.mark.parametrize(
    "groups_report,projects_report",
    [
        (
            [
                {"group": "project1", "changes": "no_changes"},
                {"exception": "This is a fake exception !"},
            ],
            [
                {"project": "project1", "changes": "no_changes"},
                {"errors": "This is a fake error !"},
            ],
        ),
        (
            [
                {"group": "project1", "changes": "no_changes"},
            ],
            [
                {"project": "project1", "changes": "no_changes"},
                {"errors": "This is a fake error !"},
                {"exception": "This is a fake exception !"},
            ],
        ),
        (
            [],
            [
                {"project": "project1", "changes": "no_changes"},
                {"errors": "This is a fake error !"},
                {"exception": "This is a fake exception !"},
            ],
        ),
        (
            [
                {"group": "project1", "changes": "no_changes"},
                {"errors": "This is a fake error !"},
                {"exception": "This is a fake exception !"},
            ],
            [],
        ),
    ],
    ids=[
        "groups_and_projects_errors",
        "projects_errors",
        "only_projects_errors",
        "only_groups_errors",
    ],
)
def test_get_errors(mocker, groups_report, projects_report):
    gpc = GpcGeneralExecutor(mocker.Mock(), mocker.Mock())

    gpc._group_report = groups_report
    gpc._project_report = projects_report

    errors = gpc.get_errors()

    assert len(errors) == 2


def test_notify_changes(mocker, monkeypatch):
    monkeypatch.setenv("CI_PIPELINE_URL", "CI_PIPELINE_URL")
    params = DotMap(
        mode=RunMode.APPLY,
        watchers="loup@laforet.com;coq@laferme.com\n  poule@laferme.com  ",
        smtp_server="fake.smtp.fr",
        smtp_port="1234",
    )
    gpc = GpcGeneralExecutor(params, mocker.Mock())
    gpc._group_report = [
        {
            "project_name": "laferme/poule",
            "errors": [
                {"exception": "This is a fake error !"},
                {"exception": "This is another fake error"},
            ],
        },
        {"group_name": "laferme", "exception": "This is a fake exception !"},
    ]

    changes = {
        "laferme/poule": {
            "approvers": {
                "property_name": "approvers",
                "action": "updated",
                "differences": {
                    "before": {
                        "name": "approvers",
                        "approvals_before_merge": 1,
                        "reset_approvals_on_push": False,
                        "can_override_approvals_per_merge_request": True,
                        "users": ["gitlab-nestor-integ"],
                    },
                    "after": {
                        "name": "approvers",
                        "approvals_before_merge": 1,
                        "reset_approvals_on_push": False,
                        "can_override_approvals_per_merge_request": False,
                        "users": ["gitlab-nestor-integ-useless", "gitlab-nestor-integ"],
                    },
                },
            },
        }
    }

    send_email_mock = mocker.patch("gpc.helpers.mail_reporter.send_email")

    gpc.notify_changes(changes)

    with open(
        Path(__file__).parent / "vectors" / "test-email.html", encoding="utf-8"
    ) as email_body:
        expected_body = [r.replace("\n", "") for r in email_body.readlines()]

    assert send_email_mock.call_args_list[0][1]["to"] == [
        "loup@laforet.com",
        "coq@laferme.com",
        "poule@laferme.com",
    ]
    body_lines = [r.strip() for r in send_email_mock.call_args_list[0][1]["body"].splitlines()]
    assert body_lines == expected_body
