"""
test_update protected branch/tag
----------------------------------
"""

# Standard Library
from os import environ

# Third Party Libraries
from dictns import Namespace
from gitlab.exceptions import GitlabGetError
from gitlab.v4.objects import Project  # pylint: disable=unused-import

# Gitlab-Project-Configurator Modules
from gpc.general_executor import GpcGeneralExecutor
from gpc.helpers.exceptions import GpcPermissionError
from gpc.parameters import GpcParameters
from gpc.parameters import RunMode
from gpc.project_rule_executor import FAIL
from gpc.project_rule_executor import ProjectRuleExecutor


# pylint: disable=redefined-outer-name, unused-argument, protected-access, duplicate-code


def test_variable_exception(mocker, fake_gitlab, fake_project):
    # Mock
    mocker.patch("gpc.tests.test_corner_cases.Project.save")
    mocker.patch(
        "gpc.tests.test_corner_cases.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    mocker.patch("gitlab.v4.objects.ProjectVariableManager.create", mocker.Mock())
    mocker.patch.dict(environ, {"ENV_2": "env_2"})
    variables = mocker.Mock()
    variables.list = mocker.Mock(
        return_value=[
            Namespace({"key": "ENV_2", "value": "toto12", "protected": "True"}),
            Namespace({"key": "ENV_3", "value": "env3", "protected": "True"}),
        ]
    )
    fake_project.variables = variables

    project_rules = Namespace(
        {
            "variables": [
                {
                    "import": "NO_EXIST_VAR",
                }
            ],
            "variable_profiles": {
                "SOME_PROFILE_NAME": [
                    {
                        "name": "some_name",
                        "value": "some value",
                    }
                ]
            },
        }
    )

    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(config=mocker.Mock("fake_config"), mode=RunMode.APPLY),
    )
    p.update_settings()
    assert p.status == FAIL


def test_rule_not_used(mocker, fake_gitlab, fake_project):
    # Mock
    mocker.patch("gpc.tests.test_corner_cases.Project.save")
    mocker.patch(
        "gpc.tests.test_corner_cases.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    mocker.patch("gitlab.v4.objects.ProjectProtectedBranchManager.create", mocker.Mock())
    protectedbranches = mocker.Mock()

    protectedbranches.list = mocker.Mock(
        return_value=[
            Namespace(
                {
                    "name": "master",
                    "merge_access_levels": [{"access_level": 40}],
                    "push_access_levels": [{"access_level": 0}],
                }
            )
        ]
    )
    fake_project.protectedbranches = protectedbranches

    config = Namespace(
        {
            "projects_rules": [
                {
                    "rule_name": "rule_used",
                    "protected_branches": [
                        {
                            "pattern": "master",
                            "allowed_to_merge": "maintainers",
                            "allowed_to_push": "no one",
                        },
                        {
                            "pattern": "dev*",
                            "allowed_to_merge": "developers",
                            "allowed_to_push": "no one",
                        },
                    ],
                },
                {
                    "rule_name": "rule_no_used",
                    "protected_branches": [
                        {
                            "pattern": "master",
                            "allowed_to_merge": "maintainers",
                            "allowed_to_push": "no one",
                        },
                        {
                            "pattern": "dev*",
                            "allowed_to_merge": "developers",
                            "allowed_to_push": "no one",
                        },
                    ],
                },
            ]
        }
    )
    parameters = GpcParameters(config=config, projects="fake/path/to/project")
    executor = GpcGeneralExecutor(parameters=parameters, gitlab=fake_gitlab)
    executor.raw_config = config
    executor.iter_on_projets_with_rules = mocker.Mock(
        return_value=[
            Namespace(
                {
                    "project_path": "fake/path/to/project",
                    "rule": {
                        "rule_name": ["rule_used"],
                        "protected_branches": [
                            {
                                "pattern": "master",
                                "allowed_to_merge": "maintainers",
                                "allowed_to_push": "no one",
                            },
                            {
                                "pattern": "dev*",
                                "allowed_to_merge": "developers",
                                "allowed_to_push": "no one",
                            },
                        ],
                    },
                    "gpc_badge_name": None,
                    "gpc_badge_image_url": None,
                }
            )
        ]
    )
    changed_projects = {}
    executor.apply_for_projects(changed_projects)
    executor.format_report()
    assert executor._report["rules_not_used"] == ["rule_no_used"]


def test_unexisting_project(mocker, fake_gitlab, fake_project):
    # Mock
    mocker.patch("gpc.tests.test_corner_cases.Project.save")
    mocker.patch(
        "gpc.tests.test_corner_cases.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    mocker.patch("gpc.general_executor.is_existing_project", return_value=False)
    mocker.patch("gitlab.v4.objects.ProjectProtectedBranchManager.create", mocker.Mock())
    protectedbranches = mocker.Mock()

    protectedbranches.list = mocker.Mock(
        return_value=[
            Namespace(
                {
                    "name": "master",
                    "merge_access_levels": [{"access_level": 40}],
                    "push_access_levels": [{"access_level": 0}],
                }
            )
        ]
    )
    fake_project.protectedbranches = protectedbranches

    config = Namespace(
        {
            "projects_rules": [
                {
                    "rule_name": "rule_used",
                    "protected_branches": [
                        {
                            "pattern": "master",
                            "allowed_to_merge": "maintainers",
                            "allowed_to_push": "no one",
                        },
                        {
                            "pattern": "dev*",
                            "allowed_to_merge": "developers",
                            "allowed_to_push": "no one",
                        },
                    ],
                },
                {
                    "rule_name": "rule_no_used",
                    "protected_branches": [
                        {
                            "pattern": "master",
                            "allowed_to_merge": "maintainers",
                            "allowed_to_push": "no one",
                        },
                        {
                            "pattern": "dev*",
                            "allowed_to_merge": "developers",
                            "allowed_to_push": "no one",
                        },
                    ],
                },
            ]
        }
    )
    parameters = GpcParameters(config=config, projects="fake/path/to/project")
    executor = GpcGeneralExecutor(parameters=parameters, gitlab=fake_gitlab)
    executor.raw_config = config
    executor.iter_on_projets_with_rules = mocker.Mock(
        return_value=[
            Namespace(
                {
                    "project_path": "fake/path/to/project",
                    "rule": {
                        "rule_name": "rule_used",
                        "protected_branches": [
                            {
                                "pattern": "master",
                                "allowed_to_merge": "maintainers",
                                "allowed_to_push": "no one",
                            },
                            {
                                "pattern": "dev*",
                                "allowed_to_merge": "developers",
                                "allowed_to_push": "no one",
                            },
                        ],
                    },
                    "gpc_badge_name": None,
                    "gpc_badge_image_url": None,
                }
            )
        ]
    )
    changed_projects = {}
    succeed = executor.apply_for_projects(changed_projects)
    assert not succeed


def test_archived_project(mocker, fake_gitlab, fake_project):
    # Mock
    mocker.patch("gpc.tests.test_corner_cases.Project.save")
    mocker.patch(
        "gpc.tests.test_corner_cases.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    mocker.patch(
        "gpc.project_rule_executor.echo_report_header",
        mocker.Mock(
            side_effect=GitlabGetError(
                "404 not found", response_body="Not found", response_code=404
            )
        ),
    )
    fake_project.archived = True
    config = Namespace(
        {
            "projects_rules": [
                {
                    "rule_name": "rule_used",
                    "protected_branches": [
                        {
                            "pattern": "master",
                            "allowed_to_merge": "maintainers",
                            "allowed_to_push": "no one",
                        },
                        {
                            "pattern": "dev*",
                            "allowed_to_merge": "developers",
                            "allowed_to_push": "no one",
                        },
                    ],
                },
                {
                    "rule_name": "rule_no_used",
                    "protected_branches": [
                        {
                            "pattern": "master",
                            "allowed_to_merge": "maintainers",
                            "allowed_to_push": "no one",
                        },
                        {
                            "pattern": "dev*",
                            "allowed_to_merge": "developers",
                            "allowed_to_push": "no one",
                        },
                    ],
                },
            ]
        }
    )
    parameters = GpcParameters(config=config, projects="fake/path/to/project")
    executor = GpcGeneralExecutor(parameters=parameters, gitlab=fake_gitlab)
    executor.raw_config = config
    executor.iter_on_projets_with_rules = mocker.Mock(
        return_value=[
            Namespace(
                {
                    "project_path": "fake/path/to/project",
                    "rule": {
                        "rule_name": "rule_used",
                        "protected_branches": [
                            {
                                "pattern": "master",
                                "allowed_to_merge": "maintainers",
                                "allowed_to_push": "no one",
                            },
                            {
                                "pattern": "dev*",
                                "allowed_to_merge": "developers",
                                "allowed_to_push": "no one",
                            },
                        ],
                    },
                    "gpc_badge_name": None,
                    "gpc_badge_image_url": None,
                },
            )
        ]
    )
    changed_projects = {}
    executor.apply_for_projects(changed_projects)
    assert not executor._report


def test_forbidden(mocker, fake_gitlab, fake_project):
    # Mock
    mocker.patch("gpc.tests.test_corner_cases.Project.save")
    mocker.patch(
        "gpc.tests.test_corner_cases.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    mocker.patch(
        "gpc.general_executor.ProjectRuleExecutor.__init__",
        mocker.Mock(
            side_effect=GpcPermissionError(
                "ERROR on project fake/path/to/project: Access forbidden. "
                "Please ensure your Gitlab token has 'owner' "
                "membership to the projects"
            )
        ),
    )
    mocker.patch("gitlab.v4.objects.ProjectProtectedBranchManager.create", mocker.Mock())
    protectedbranches = mocker.Mock()

    protectedbranches.list = mocker.Mock(
        return_value=[
            Namespace(
                {
                    "name": "master",
                    "merge_access_levels": [{"access_level": 40}],
                    "push_access_levels": [{"access_level": 0}],
                }
            )
        ]
    )
    fake_project.protectedbranches = protectedbranches

    config = Namespace(
        {
            "projects_rules": [
                {
                    "rule_name": "rule_used",
                    "protected_branches": [
                        {
                            "pattern": "master",
                            "allowed_to_merge": "maintainers",
                            "allowed_to_push": "no one",
                        },
                        {
                            "pattern": "dev*",
                            "allowed_to_merge": "developers",
                            "allowed_to_push": "no one",
                        },
                    ],
                },
                {
                    "rule_name": "rule_no_used",
                    "protected_branches": [
                        {
                            "pattern": "master",
                            "allowed_to_merge": "maintainers",
                            "allowed_to_push": "no one",
                        },
                        {
                            "pattern": "dev*",
                            "allowed_to_merge": "developers",
                            "allowed_to_push": "no one",
                        },
                    ],
                },
            ]
        }
    )
    parameters = GpcParameters(config=config, projects="fake/path/to/project")
    executor = GpcGeneralExecutor(parameters=parameters, gitlab=fake_gitlab)
    executor.raw_config = config
    executor.iter_on_projets_with_rules = mocker.Mock(
        return_value=[
            Namespace(
                {
                    "project_path": "fake/path/to/project",
                    "rule": {
                        "rule_name": "rule_used",
                        "protected_branches": [
                            {
                                "pattern": "master",
                                "allowed_to_merge": "maintainers",
                                "allowed_to_push": "no one",
                            },
                            {
                                "pattern": "dev*",
                                "allowed_to_merge": "developers",
                                "allowed_to_push": "no one",
                            },
                        ],
                    },
                    "gpc_badge_name": None,
                    "gpc_badge_image_url": None,
                }
            )
        ]
    )
    changed_projects = {}
    succeed = executor.apply_for_projects(changed_projects)
    assert not succeed


GROUP_CONFIG = Namespace(
    {
        "groups_rules": [
            {
                "rule_name": "rule_used",
                "variables": [
                    {
                        "name": "VARIABLE1",
                        "value": "VALUE1",
                    },
                ],
            },
        ],
        "groups_configuration": [
            {
                "paths": [
                    "fake/group/path",
                ],
                "rule_name": "rule_used",
            }
        ],
    }
)


def test_unexisting_group(mocker, fake_gitlab, fake_group):
    parameters = GpcParameters(config=GROUP_CONFIG)
    executor = GpcGeneralExecutor(parameters=parameters, gitlab=fake_gitlab)
    executor.raw_config = GROUP_CONFIG
    mocker.patch("gpc.general_executor.is_existing_group", return_value=False)

    changed_groups = {}
    succeed = executor.apply_for_groups(changed_groups)
    assert not succeed


def test_group_executor_exception(mocker, fake_gitlab, fake_group):
    parameters = GpcParameters(config=GROUP_CONFIG)
    executor = GpcGeneralExecutor(parameters=parameters, gitlab=fake_gitlab)
    executor.raw_config = GROUP_CONFIG
    mocker.patch("gpc.general_executor.is_existing_group", return_value=True)
    mocker.patch(
        "gpc.general_executor.GroupRuleExecutor",
        side_effect=Exception("Error during configuration"),
    )

    changed_groups = {}
    succeed = executor.apply_for_groups(changed_groups)
    assert not succeed
    assert executor._group_report[0]["exception"] == "Error during configuration"
    assert executor._group_report[0]["group_name"] == "fake/group/path"
    assert executor._group_report[0]["rule"].rule_name == ["rule_used"]
    assert executor._group_report[0]["rule"].variables == [
        {
            "name": "VARIABLE1",
            "value": "VALUE1",
        },
    ]
