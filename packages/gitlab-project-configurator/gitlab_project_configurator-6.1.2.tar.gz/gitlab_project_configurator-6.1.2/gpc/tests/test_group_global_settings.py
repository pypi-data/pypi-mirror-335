# Third Party Libraries
from dictns import Namespace

# Gitlab-Project-Configurator Modules
from gpc.parameters import GpcParameters
from gpc.parameters import RunMode
from gpc.project_rule_executor import GroupRuleExecutor
from gpc.tests.conftest import FakeGitlabGroup


def test_update_visibility(mocker, fake_gitlab, fake_group):
    # Mock
    mocker.patch("gpc.change_executors_factory.Group", FakeGitlabGroup)
    mocker.patch(
        "gpc.tests.test_group_global_settings.GroupRuleExecutor.group",
        mocker.PropertyMock(return_value=fake_group),
    )

    group_rules = Namespace({"permissions": {"visibility": "private"}})
    p = GroupRuleExecutor(
        gl=fake_gitlab,
        group_path="fake/group/path",
        rule=group_rules,
        gpc_params=GpcParameters(config=mocker.Mock("fake_config"), mode=RunMode.APPLY),
    )
    assert fake_group.visibility == "old_visibility"  # initial value from fake_project
    p.update_settings()
    assert fake_group.visibility == "private"
    report = p.get_report()
    assert report["status"] == "success"
