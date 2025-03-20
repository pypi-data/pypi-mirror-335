"""
test project badges
----------------------------------
"""

# Third Party Libraries
import pytest

from dictns import Namespace
from gitlab.v4.objects import Project  # pylint: disable=unused-import

# Gitlab-Project-Configurator Modules
from gpc.parameters import GpcParameters
from gpc.parameters import RunMode
from gpc.project_rule_executor import ProjectRuleExecutor
from gpc.tests.test_helpers import get_change_value


# pylint: disable=redefined-outer-name, unused-argument, protected-access, duplicate-code


@pytest.mark.parametrize(
    "existing_badges_services, project_rules, expected_diff",
    [
        # existing_badges
        (
            [
                Namespace(
                    {
                        "id": 1,
                        "name": None,
                        "link_url": "link of a badge to remove",
                        "image_url": "image url of a badge to remove",
                        "kind": "group",
                    }
                ),
                Namespace(
                    {
                        "id": 2,
                        "name": "badge_to_keep",
                        "link_url": "link of a badge to keep",
                        "image_url": "image url of a badge to keep",
                        "kind": "project",
                    }
                ),
                Namespace(
                    {
                        "id": 3,
                        "name": "another_badge_to_keep",
                        "link_url": "link of another badge to keep",
                        "image_url": "https://fake.gitlab.url to keep",
                        "kind": "project",
                    }
                ),
            ],
            # project_rules
            Namespace(
                {
                    "keep_existing_badges": False,
                    "badges": [
                        {
                            "link_url": "http://link/to/some/url",
                            "image_url": "http://image/url",
                        },
                        {
                            "link_url": "%{gpc_gitlab_url}/some/sub/path",
                            "image_url": "http://another/image/url",
                        },
                        {
                            "name": "badge_to_keep",
                            "link_url": "link of a badge to keep",
                            "image_url": "image url of a badge to keep",
                        },
                        {
                            "name": "another_badge_to_keep",
                            "link_url": "link of another badge to keep",
                            "image_url": "%{gpc_gitlab_url} to keep",
                        },
                    ],
                }
            ),
            # expected_diff
            {
                "badge_to_keep": {
                    "before": {
                        "name": "badge_to_keep",
                        "image_url": "image url of a badge to keep",
                        "link_url": "link of a badge to keep",
                        "kind": "project",
                    },
                    "after": {
                        "name": "badge_to_keep",
                        "image_url": "image url of a badge to keep",
                        "link_url": "link of a badge to keep",
                        "kind": "project",
                    },
                    "status": "kept",
                },
                "another_badge_to_keep": {
                    "before": {
                        "name": "another_badge_to_keep",
                        "link_url": "link of another badge to keep",
                        "image_url": "https://fake.gitlab.url to keep",
                        "kind": "project",
                    },
                    "after": {
                        "name": "another_badge_to_keep",
                        "link_url": "link of another badge to keep",
                        "image_url": "https://fake.gitlab.url to keep",
                        "kind": "project",
                    },
                    "status": "kept",
                },
                "UNDER_GPC_BADGE": {
                    "before": None,
                    "after": {
                        "name": "UNDER_GPC_BADGE",
                        "image_url": "new image url",
                        "link_url": "new project url",
                        "kind": "project",
                    },
                    "status": "added",
                },
                "http://link/to/some/url": {
                    "before": None,
                    "after": {
                        "name": "http://link/to/some/url",
                        "image_url": "http://image/url",
                        "link_url": "http://link/to/some/url",
                        "kind": "project",
                    },
                    "status": "added",
                },
                "https://fake.gitlab.url/some/sub/path": {
                    "before": None,
                    "after": {
                        "name": "https://fake.gitlab.url/some/sub/path",
                        "image_url": "http://another/image/url",
                        "link_url": "https://fake.gitlab.url/some/sub/path",
                        "kind": "project",
                    },
                    "status": "added",
                },
            },
        ),
        # existing_badges
        (
            [
                Namespace(
                    {
                        "id": 1,
                        "name": None,
                        "link_url": "link of a badge to remove",
                        "image_url": "image url of a badge to remove",
                        "kind": "project",
                    }
                ),
                Namespace(
                    {
                        "id": 2,
                        "name": "badge_to_kept",
                        "link_url": "link of a badge to keep",
                        "image_url": "image url of a badge to keep",
                        "kind": "project",
                    }
                ),
                Namespace(
                    {
                        "id": 3,
                        "name": None,
                        "link_url": "link of badge to replace",
                        "image_url": "https://fake.gitlab.url to keep",
                        "kind": "project",
                    }
                ),
            ],
            # project_rules
            Namespace(
                {
                    "badges": [
                        {
                            "link_url": "http://link/to/some/url",
                            "image_url": "http://image/url",
                        },
                        {
                            "link_url": "%{gpc_gitlab_url}/some/sub/path",
                            "image_url": "http://another/image/url",
                        },
                        {
                            "name": "badge_to_kept",
                            "link_url": "link of a badge to keep",
                            "image_url": "image url of a badge to keep",
                        },
                        {
                            "name": "badge_to_replace",
                            "link_url": "link of badge to replace",
                            "image_url": "%{gpc_gitlab_url} to keep",
                        },
                    ]
                }
            ),
            # expected_diff
            {
                "badge_to_kept": {
                    "before": {
                        "name": "badge_to_kept",
                        "image_url": "image url of a badge to keep",
                        "link_url": "link of a badge to keep",
                        "kind": "project",
                    },
                    "after": {
                        "name": "badge_to_kept",
                        "image_url": "image url of a badge to keep",
                        "link_url": "link of a badge to keep",
                        "kind": "project",
                    },
                    "status": "kept",
                },
                "3": {
                    "before": {
                        "name": "3",
                        "link_url": "link of badge to replace",
                        "image_url": "https://fake.gitlab.url to keep",
                        "kind": "project",
                    },
                    "after": None,
                    "status": "removed",
                },
                "badge_to_replace": {
                    "before": None,
                    "after": {
                        "name": "badge_to_replace",
                        "link_url": "link of badge to replace",
                        "image_url": "https://fake.gitlab.url to keep",
                        "kind": "project",
                    },
                    "status": "added",
                },
                "UNDER_GPC_BADGE": {
                    "before": None,
                    "after": {
                        "name": "UNDER_GPC_BADGE",
                        "image_url": "new image url",
                        "link_url": "new project url",
                        "kind": "project",
                    },
                    "status": "added",
                },
                "http://link/to/some/url": {
                    "before": None,
                    "after": {
                        "name": "http://link/to/some/url",
                        "image_url": "http://image/url",
                        "link_url": "http://link/to/some/url",
                        "kind": "project",
                    },
                    "status": "added",
                },
                "https://fake.gitlab.url/some/sub/path": {
                    "before": None,
                    "after": {
                        "name": "https://fake.gitlab.url/some/sub/path",
                        "image_url": "http://another/image/url",
                        "link_url": "https://fake.gitlab.url/some/sub/path",
                        "kind": "project",
                    },
                    "status": "added",
                },
            },
        ),
    ],
)
def test_project_badge(
    mocker,
    fake_gitlab,
    fake_project,
    existing_badges_services,
    project_rules,
    expected_diff,
):
    # Mock
    mocker.patch("gpc.tests.test_project_badges.Project.save")
    mocker.patch(
        "gpc.tests.test_project_badges.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    existing_badges = mocker.Mock()

    existing_badges.list = mocker.Mock(return_value=existing_badges_services)
    fake_project.badges = existing_badges

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
    # flake8: noqa

    diff = get_change_value(p, "project_badges").differences
    assert diff == expected_diff
