# Third Party Libraries
from gitlab.exceptions import GitlabGetError

# Gitlab-Project-Configurator Modules
from gpc.helpers.gitlab_helper import clean_gitlab_project_name
from gpc.helpers.gitlab_helper import is_archived_project
from gpc.helpers.gitlab_helper import is_existing_group
from gpc.helpers.gitlab_helper import is_existing_project
from gpc.helpers.gitlab_helper import is_shared_project


def test_clean_project_name():
    assert clean_gitlab_project_name("/a/project/name/") == "a/project/name"
    assert (
        clean_gitlab_project_name("/A/project/NAME/with/UPPderCase")
        == "a/project/name/with/uppdercase"
    )
    assert (
        clean_gitlab_project_name("https://gitlab.server.com:8060/a/project/name/")
        == "a/project/name"
    )

    assert clean_gitlab_project_name("/a/project/name.git") == "a/project/name"


def test_is_shared_project(mocker):
    p = mocker.Mock()
    p.shared_with_groups = [{"group_full_path": "group/path/shared"}]
    g = mocker.Mock()
    g.full_path = "group/path/shared"
    g1 = mocker.Mock()
    g1.full_path = "group/path/not_shared"
    assert is_shared_project(p, g)
    assert not is_shared_project(p, g1)


def test_is_archived_project(mocker):
    gl = mocker.Mock()
    prj_mock = mocker.Mock()
    prj_mock.archived = True
    gl.projects.get.return_value = prj_mock
    assert is_archived_project(gl, "la/ferme/poule")

    prj_mock.archived = False
    gl.projects.get.return_value = prj_mock
    assert not is_archived_project(gl, "la/ferme/poule")


def test_is_existing_project(mocker):
    gl = mocker.Mock()
    gl.projects.get.return_value = mocker.Mock()
    assert is_existing_project(gl, "la/ferme/poule")

    gl.projects.get.side_effect = GitlabGetError("Not found", 404)
    assert not is_existing_project(gl, "la/ferme/poule")


def test_is_existing_group(mocker):
    gl = mocker.Mock()
    gl.groups.get.return_value = mocker.Mock()
    assert is_existing_group(gl, "la/ferme")

    gl.groups.get.side_effect = GitlabGetError("Not found", 404)
    assert not is_existing_group(gl, "la/ferme")
