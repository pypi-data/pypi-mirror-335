# pylint: disable=unused-import

# Third Party Libraries
import pytest

from dictns import Namespace

# Gitlab-Project-Configurator Modules
from gpc.general_executor import GpcGeneralExecutor
from gpc.helpers.types import ProjectPathRule
from gpc.project_rule_executor import ProjectRuleExecutor


# pylint: disable=redefined-outer-name


@pytest.fixture
def fake_gpc_params(mocker):
    fake_params = mocker.Mock()
    fake_params.projects = None
    fake_params.report_file = None
    yield fake_params


def test_with_group_and_duplicate(mocker, fake_gitlab, fake_gpc_params):
    gpc = GpcGeneralExecutor(parameters=fake_gpc_params, gitlab=fake_gitlab)
    group_path = "a/group"
    fake_project_list = [
        Namespace(
            {
                "path_with_namespace": group_path + "/found_project1",
                "shared_with_groups": [],
            }
        ),
        Namespace(
            {
                "path_with_namespace": group_path + "/found_project2",
                "shared_with_groups": [],
            }
        ),
    ]
    fake_group = mocker.Mock("fake_group")
    fake_group.full_path = group_path
    fake_group.projects = mocker.Mock("fake_projects")
    fake_group.projects.list = mocker.Mock("project_list", return_value=fake_project_list)
    mocker.patch.object(fake_gitlab.groups, "get", return_value=fake_group)

    def fake_is_path_a_group(p: str) -> bool:
        return p.strip("/") == group_path

    mocker.patch.object(gpc, "_is_path_a_group", side_effect=fake_is_path_a_group)
    fake_rule = Namespace({"a_fake": "rule"})

    def gen_prjt_rule():
        for i in range(5):
            fake_prjt_name = group_path + f"/project_{i}"
            yield ProjectPathRule(
                project_path=fake_prjt_name,
                rule=fake_rule,
                recursive=False,
                not_seen_yet_only=False,
            )
        yield ProjectPathRule(
            project_path=group_path + "/",
            rule=fake_rule,
            recursive=False,
            not_seen_yet_only=False,
        )
        # Just to verify group_path + '/found_project1' isn't twice in the result
        yield ProjectPathRule(
            project_path=group_path + "/found_project1",
            rule=fake_rule,
            recursive=False,
            not_seen_yet_only=False,
        )

    fake_matcher = mocker.Mock()
    fake_matcher.find_rules = gen_prjt_rule
    lst = list(gpc.iter_on_projets_with_rules(fake_matcher))

    assert lst == [
        ProjectPathRule(
            project_path="a/group/project_0",
            rule={"a_fake": "rule"},
            recursive=False,
            not_seen_yet_only=False,
        ),
        ProjectPathRule(
            project_path="a/group/project_1",
            rule={"a_fake": "rule"},
            recursive=False,
            not_seen_yet_only=False,
        ),
        ProjectPathRule(
            project_path="a/group/project_2",
            rule={"a_fake": "rule"},
            recursive=False,
            not_seen_yet_only=False,
        ),
        ProjectPathRule(
            project_path="a/group/project_3",
            rule={"a_fake": "rule"},
            recursive=False,
            not_seen_yet_only=False,
        ),
        ProjectPathRule(
            project_path="a/group/project_4",
            rule={"a_fake": "rule"},
            recursive=False,
            not_seen_yet_only=False,
        ),
        ProjectPathRule(
            project_path="a/group/found_project1",
            rule={"a_fake": "rule"},
            recursive=False,
            not_seen_yet_only=False,
        ),
        ProjectPathRule(
            project_path="a/group/found_project2",
            rule={"a_fake": "rule"},
            recursive=False,
            not_seen_yet_only=False,
        ),
        ProjectPathRule(
            project_path="a/group/found_project1",
            rule={"a_fake": "rule"},
            recursive=False,
            not_seen_yet_only=False,
        ),
    ]

    # There is only 1 instance of 'a/group/found_project1'


def test_project_exclusion(mocker, fake_gitlab, fake_gpc_params):
    gpc = GpcGeneralExecutor(parameters=fake_gpc_params, gitlab=fake_gitlab)
    group_path = "a/group/path"

    fake_rule = Namespace({"name": "fakerule"})
    project_excludes = [
        "a/group/path/project_1",
        "a/group/path/lvl1_1/sub_p",
        "a/group/path/lvl1_2/lvl2/sub_group_to_exclude",
        "^.*exclude_through_regex$",
    ]

    def gen_prjt_rule():
        # Projects:
        # a/group/path/project_0                                      | kept
        # a/group/path/project_1                                      | exclude
        # a/group/path/project_2                                      | kept
        # a/group/path/project_3                                      | kept
        # a/group/path/project_4                                      | kept
        # a/group/path/                                               | kept
        # a/group/path/lvl1_1/sub_p/p1                                | exclude
        # a/group/path/lvl1_1/sub_p_v1                                | kept
        # a/group/path/lvl1_2/lvl2/sub_group_to_exclude/project1      | exclude
        # a/group/path/lvl1_2/lvl2/sub_group_to_keep/project1_kept    | kept
        # a/group/path/a/project/to/exclude_through_regex             | exclude
        for i in range(5):
            fake_prjt_name = group_path + f"/project_{i}"
            yield ProjectPathRule(
                project_path=fake_prjt_name,
                rule=fake_rule,
                recursive=False,
                excludes=project_excludes,
                not_seen_yet_only=True,
            )

        yield ProjectPathRule(
            project_path=group_path + "/",
            rule=fake_rule,
            recursive=True,
            excludes=project_excludes,
            not_seen_yet_only=True,
        )

        yield ProjectPathRule(
            project_path="a/group/path/lvl1_1/sub_p/p1",
            rule=fake_rule,
            recursive=False,
            excludes=project_excludes,
            not_seen_yet_only=True,
        )

        yield ProjectPathRule(
            project_path="a/group/path/lvl1_1/sub_p_v1",
            rule=fake_rule,
            recursive=False,
            excludes=project_excludes,
            not_seen_yet_only=True,
        )

        yield ProjectPathRule(
            project_path="a/group/path/lvl1_2/lvl2/sub_group_to_exclude/project1",
            rule=fake_rule,
            recursive=False,
            excludes=project_excludes,
            not_seen_yet_only=True,
        )

        yield ProjectPathRule(
            project_path="a/group/path/lvl1_2/lvl2/sub_group_to_keep/project1_kept",
            rule=fake_rule,
            recursive=False,
            excludes=project_excludes,
            not_seen_yet_only=True,
        )

        yield ProjectPathRule(
            project_path="a/group/path/a/project/to/exclude_through_regex",
            rule=fake_rule,
            recursive=False,
            excludes=project_excludes,
            not_seen_yet_only=True,
        )

    matcher = mocker.Mock(name="fake_matcher")
    matcher.find_rules = mocker.Mock("find_rules", side_effect=gen_prjt_rule)

    def mk_fake_project(path_with_namespace):
        p = mocker.Mock(name=path_with_namespace)
        p.path_with_namespace = path_with_namespace
        p.shared_with_groups = []
        return p

    def fake_get_group(_gl, wanted_group):
        fake_a_group_path = mocker.Mock(name="a/group/path")
        fake_a_group_path.projects = mocker.Mock(name="fake_a_group_path.projects")
        fake_a_group_path.projects.list = mocker.Mock(
            name="fake_a_group_path.list.projects",
            return_value=[
                mk_fake_project("a/group/path/project_0"),
                mk_fake_project("a/group/path/project_1"),
                mk_fake_project("a/group/path/project_2"),
                mk_fake_project("a/group/path/project_3"),
                mk_fake_project("a/group/path/project_4"),
                mk_fake_project("a/group/path/project_5"),
                mk_fake_project("a/group/path/project_6"),
                mk_fake_project("a/group/path/project_7"),
                mk_fake_project("a/group/path/project_8"),
                mk_fake_project("a/group/path/project_9"),
            ],
        )
        fake_a_group_path.subgroups = mocker.Mock(name="fake_a_group_path.subgroups")
        a_group_path_lvl1_1_sub_p = mocker.Mock(name="a_group_path_lvl1_1_sub_p")
        a_group_path_lvl1_1_sub_p.full_path = "a/group/path/lvl1_1/sub_p"
        a_group_path_lvl1_1_sub_p.projects.list = mocker.Mock(
            name="a_group_path_lvl1_1_sub_p.projects.list",
            return_value=[mk_fake_project("a/group/path/lvl1_1/sub_p/p1")],
        )
        a_group_path_lvl1_1_sub_p.subgroups.list = mocker.Mock(
            name="a_group_path_lvl1_1_sub_p.subgroups.list", return_value=[]
        )

        a_group_path_lvl1_1 = mocker.Mock(name="a_group_path_lvl1_1")
        a_group_path_lvl1_1.full_path = "a/group/path/lvl1_1"
        a_group_path_lvl1_1.projects.list = mocker.Mock(
            name="a_group_path_lvl1_1.projects.list",
            return_value=[
                mk_fake_project("a/group/path/lvl1_1/sub_p_v1"),
            ],
        )
        a_group_path_lvl1_1.subgroups.list = mocker.Mock(
            name="a_group_path_lvl1_1.subgroups.list",
            return_value=[
                a_group_path_lvl1_1_sub_p,
            ],
        )
        a_group_path_subgroups = [a_group_path_lvl1_1]
        fake_a_group_path.subgroups.list = mocker.Mock(
            name="fake_a_group_path.subgroups.list", return_value=a_group_path_subgroups
        )

        groups = {
            "a/group/path": fake_a_group_path,
            "a/group/path/lvl1_1": a_group_path_lvl1_1,
            "a/group/path/lvl1_1/sub_p": a_group_path_lvl1_1_sub_p,
        }
        return groups[wanted_group]

    def fake_is_path_a_group(wanted_path):
        is_a_group = {
            "a/group/path/project_0": False,
            "a/group/path/project_1": False,
            "a/group/path/project_2": False,
            "a/group/path/project_3": False,
            "a/group/path/project_4": False,
            "a/group/path": True,
            "a/group/path/lvl1_1": True,
            "a/group/path/lvl1_1/sub_p": True,
            "a/group/path/lvl1_1/sub_p/p1": False,
            "a/group/path/lvl1_1/sub_p_v1": False,
            "a/group/path/lvl1_2/lvl2/sub_group_to_exclude/project1": False,
            "a/group/path/lvl1_2/lvl2/sub_group_to_keep/project1_kept": False,
            "a/group/path/a/project/to/exclude_through_regex": False,
        }
        return is_a_group[wanted_path]

    mocker.patch.object(gpc, "_is_path_a_group", side_effect=fake_is_path_a_group)
    mocker.patch("gpc.general_executor.get_group", side_effect=fake_get_group)
    lst = list(gpc.iter_on_projets_with_rules(matcher))

    lst_projects = [p.project_path for p in lst]

    assert lst_projects == [
        "a/group/path/project_0",
        "a/group/path/project_2",
        "a/group/path/project_3",
        "a/group/path/project_4",
        "a/group/path/project_5",
        "a/group/path/project_6",
        "a/group/path/project_7",
        "a/group/path/project_8",
        "a/group/path/project_9",
        "a/group/path/lvl1_1/sub_p_v1",
        "a/group/path/lvl1_2/lvl2/sub_group_to_keep/project1_kept",
    ]
    assert "a/group/path/project_1" not in lst_projects
    assert "a/group/path/a/project/to/exclude_through_regex" not in lst_projects


def test_not_seen_yet_only(mocker, fake_gitlab, fake_gpc_params):
    gpc = GpcGeneralExecutor(parameters=fake_gpc_params, gitlab=fake_gitlab)
    mocker.patch(
        "gpc.tests.test_project_listing.GpcGeneralExecutor.raw_config",
        mocker.PropertyMock(return_value={}),
    )
    mocker.patch("gpc.tests.test_project_listing.ProjectRuleExecutor.execute", mocker.Mock())
    group_path = "a/group/path"
    fake_rule = Namespace({"name": "fakerule"})

    def gen_prjt_rule():
        yield ProjectPathRule(
            project_path=group_path + "/project_1",
            rule=fake_rule,
            recursive=False,
            not_seen_yet_only=False,
        )
        for i in range(5):
            fake_prjt_name = group_path + f"/project_{i}"
            yield ProjectPathRule(
                project_path=fake_prjt_name,
                rule=fake_rule,
                recursive=False,
                not_seen_yet_only=True,
            )

    lst = list(gpc._handle_project_exclusion(gen_prjt_rule()))  # pylint: disable=protected-access
    lst_projects = [p.project_path for p in lst]
    assert lst_projects == [
        "a/group/path/project_1",
        "a/group/path/project_0",
        "a/group/path/project_2",
        "a/group/path/project_3",
        "a/group/path/project_4",
    ]
    assert lst_projects.count("a/group/path/project_1") == 1
