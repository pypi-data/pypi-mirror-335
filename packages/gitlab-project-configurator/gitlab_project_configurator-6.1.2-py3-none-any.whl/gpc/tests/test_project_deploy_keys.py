# Third Party Libraries
from dictns import Namespace
from gitlab.v4.objects import Project  # pylint: disable=unused-import

# Gitlab-Project-Configurator Modules
from gpc.parameters import GpcParameters
from gpc.parameters import RunMode
from gpc.project_rule_executor import ProjectRuleExecutor


# pylint: disable=duplicate-code


def test_update_deploy_key(mocker, fake_gitlab, fake_project):
    fake_project.keys = mocker.Mock()
    fake_project.keys.list = mocker.Mock(
        return_value=[
            Namespace({"id": 1, "can_push": True}),
            Namespace({"id": 2, "can_push": True}),
        ]
    )
    project_rules = Namespace(
        {"deploy_keys": [{"id": 1, "can_push": False}, {"id": 3, "can_push": False}]}
    )
    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(config=mocker.Mock("fake_config"), mode=RunMode.APPLY),
    )
    p.update_settings()
    p.save()
