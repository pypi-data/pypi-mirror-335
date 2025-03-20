"""
test project labels
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
    "project_rules",
    [
        # All those cases will have the same result
        Namespace(
            {
                "labels": [
                    {"name": "label1", "color": "#FF0000"},
                    {"name": "label2", "color": "#FF0001"},
                    {"name": "label3", "color": "#FF0002"},
                ],
            }
        ),
        Namespace(
            {
                "labels": [
                    {"name": "label1", "color": "#FF0000"},
                    {"profile": "label_profile_1"},
                ],
                "label_profiles": [
                    {
                        "name": "label_profile_1",
                        "labels": [
                            {"name": "label2", "color": "#FF0001"},
                            {"name": "label3", "color": "#FF0002"},
                        ],
                    },
                ],
            }
        ),
        Namespace(
            {
                "labels": [
                    {"name": "label1", "color": "#FF0000"},  # overwrite
                    {"profile": "label_profile_1"},
                    {"profile": "label_profile_2"},
                ],
                "label_profiles": [
                    {
                        "name": "label_profile_1",
                        "labels": [
                            {"name": "label1", "color": "#FF0042"},  # overwritten
                            {"name": "label2", "color": "#FF0001"},
                        ],
                    },
                    {
                        "name": "label_profile_2",
                        "labels": [
                            {"name": "label3", "color": "#FF0002"},
                        ],
                    },
                ],
            }
        ),
    ],
)
def test_create_labels(mocker, fake_gitlab, fake_project, project_rules):
    # Mock
    mocker.patch("gpc.tests.test_project_labels.Project.save")
    mocker.patch(
        "gpc.tests.test_project_labels.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    mock_manager_label = mocker.patch("gitlab.v4.objects.ProjectLabelManager.create", mocker.Mock())
    labels = mocker.Mock()

    labels.list = mocker.Mock(
        return_value=[
            Namespace({"name": "label1", "color": "#FF0000"}),
            Namespace({"name": "label3", "color": "#FF0000"}),
            Namespace({"name": "label4", "color": "#FF0000"}),
        ]
    )
    fake_project.labels = labels

    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(mocker.Mock("fake_config"), mode=RunMode.APPLY),
    )
    p.execute()
    change_labels = get_change_value(p, "labels")
    assert len(change_labels.after) == 3
    diff_label_1 = change_labels.differences.get("label1")
    diff_label_2 = change_labels.differences.get("label2")
    diff_label_3 = change_labels.differences.get("label3")
    diff_label_4 = change_labels.differences.get("label4")
    assert diff_label_1.get("after").get("color") == "#FF0000"
    assert diff_label_2.get("after").get("color") == "#FF0001"
    assert diff_label_3.get("after").get("color") == "#FF0002"
    assert diff_label_1.get("status") == "kept"
    assert diff_label_2.get("status") == "added"
    assert diff_label_3.get("status") == "updated"
    assert diff_label_4.get("status") == "kept"
    assert mock_manager_label.is_called
