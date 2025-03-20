# Standard Library
import re

from typing import Iterator
from typing import Optional
from typing import Union  # pylint: disable=unused-import

# Third Party Libraries
import boltons.cacheutils
import gitlab.const

from boltons.urlutils import URL
from boltons.urlutils import parse_url
from gitlab import Gitlab  # pylint: disable=unused-import
from gitlab.exceptions import GitlabGetError
from gitlab.v4.objects import Group as GitlabGroup
from gitlab.v4.objects import GroupProject as GitlabGroupProject
from gitlab.v4.objects import Project as GitlabProject
from wcmatch.fnmatch import fnmatch

# Gitlab-Project-Configurator Modules
from gpc.helpers.exceptions import GpcUserError
from gpc.helpers.types import ProjectName
from gpc.helpers.types import Url


cache_users = boltons.cacheutils.LRI(10000)
cache_users_id = boltons.cacheutils.LRI(10000)
cache_groups = boltons.cacheutils.LRI(10000)
cache_subgroups = boltons.cacheutils.LRI(10000)
cache_allgroups = boltons.cacheutils.LRI(10000)

VISIBILITY_VALUES = ["internal", "private", "public"]
MERGE_METHODS = ["merge", "rebase_merge", "ff"]
SQUASH_OPTIONS = {
    "do not allow": "never",
    "allow": "default_off",
    "encourage": "default_on",
    "require": "always",
}
INV_SQUASH_OPTIONS = {
    "never": "do not allow",
    "default_off": "allow",
    "default_on": "encourage",
    "always": "require",
}

MAP_ACCESS = {
    "no one": 0,
    "none": 0,
    "maintainers": gitlab.const.MAINTAINER_ACCESS,
    "guests": gitlab.const.GUEST_ACCESS,
    "reporters": gitlab.const.REPORTER_ACCESS,
    "owners": gitlab.const.OWNER_ACCESS,
    "developers": gitlab.const.DEVELOPER_ACCESS,
    "admins": 60,
}

MAP_ACCESS_REVERT = {
    0: "no one",
    gitlab.const.MAINTAINER_ACCESS: "maintainers",
    gitlab.const.GUEST_ACCESS: "guests",
    gitlab.const.REPORTER_ACCESS: "reporters",
    gitlab.const.OWNER_ACCESS: "owners",
    gitlab.const.DEVELOPER_ACCESS: "developers",
    60: "admins",
}


@boltons.cacheutils.cached(cache_users)
def get_user_by_username(gl: Gitlab, username):
    # In some cases Name and Username are different
    # jhon.smith may have jhon.slith1 as username,
    # we may use gl.users.list(search=...) in this case
    users = gl.users.list(username=username, retry_transient_errors=True) or gl.users.list(
        search=username, retry_transient_errors=True
    )
    if users:
        # The username is an unique field
        return users[0]  # type: ignore

    raise GpcUserError(f"User {username} does not exist")


@boltons.cacheutils.cached(cache_users_id)
def get_user_by_id(gl: Gitlab, user_id):
    return gl.users.get(user_id, retry_transient_errors=True)


@boltons.cacheutils.cached(cache_groups)
def get_group(gl: Gitlab, group_path):
    return gl.groups.get(group_path, retry_transient_errors=True)


@boltons.cacheutils.cached(cache_subgroups)
def _get_subgroups(gl: Gitlab, group_path):
    group = get_group(gl, group_path)
    subgroups = []
    if group.shared_with_groups:
        subgroups = [x.get("group_full_path") for x in group.shared_with_groups]
    return subgroups


@boltons.cacheutils.cached(cache_allgroups)
def get_subgroups(gl: Gitlab, group_path):
    all_groups = []
    subgroups = _get_subgroups(gl, group_path)
    if not subgroups:
        return []
    all_groups.extend(subgroups)
    for subgroup in subgroups:
        all_groups.extend(_get_subgroups(gl, subgroup))
    return all_groups


def clean_gitlab_project_name(project_name_or_url: Union[ProjectName, Url]) -> ProjectName:
    if project_name_or_url.startswith("https://"):
        o = parse_url(project_name_or_url)
        project_name = o["path"]
    else:
        project_name = project_name_or_url
    project_name = project_name.strip("/").lower()
    if project_name.endswith(".git"):
        project_name = project_name[:-4]
    return project_name


def is_archived_project(gl: Gitlab, project_path):
    gl_project = gl.projects.get(project_path)
    return gl_project.archived


def is_shared_project(project, group):
    return group.full_path in (sg["group_full_path"] for sg in project.shared_with_groups)


def is_existing_project(gl: Gitlab, project_path):
    try:
        gl.projects.get(project_path)
        return True
    except GitlabGetError:
        return False


def is_existing_group(gl: Gitlab, group_path):
    try:
        gl.groups.get(group_path)
        return True
    except GitlabGetError:
        return False


def is_bot_user_for_project_member(name):
    """
    Check if a member name has the format: project_{project_id}_bot_{random_string}

    Parameters:
    name (str): The member name to check.

    Returns:
    bool: True if the name matches the pattern, False otherwise.
    """
    # See format here
    # https://docs.gitlab.com/ee/user/project/settings/project_access_tokens.html#bot-users-for-projects
    pattern = r"^project_\d+_bot_[a-zA-Z0-9]+$"
    return bool(re.match(pattern, name))


def remove_creds_in_url(url: str) -> str:
    """Remove the credential section of a URL."""
    uurl = URL(url)
    uurl.username = None
    uurl.password = None
    return uurl.to_text()


def url_path_relative_to(url: str, url_base: str) -> str:
    """Return the path of a URL relative to another one.

    It automatically ignores user credentials in the urls, and also abstract the
    schemes (http/https).

    Arguments:
        url: the candidate URL to compute the relative path from
        url_base: base URL (with a path section if wanted) to compute against.

    Returns:
        The relative path of the candiate URL (so without any leading '/')
        if the base url belong to the candidate URL.
        If both URL are on different host, it will return the untouched candidate URL.
    """
    orig_url = url
    url = remove_creds_in_url(url)
    url_base = remove_creds_in_url(url_base)
    url = url.replace("https://", "http://").strip("/")
    url_base = url_base.replace("https://", "http://").strip("/")
    if not url.startswith(url_base):
        return orig_url
    return url[len(url_base) :].strip("/")


def maybe_get_project(
    gl: Gitlab,
    path: str,
    lazy=False,
) -> Optional[GitlabProject]:
    """
    Retrieve a project by its name or id or return None without failing.
    """
    try:
        return gl.projects.get(
            id=path,
            lazy=lazy,
        )
    except GitlabGetError:
        pass
    return None


def maybe_get_group(
    gl: Gitlab,
    path: str,
    lazy=False,
) -> Optional[GitlabGroup]:
    """
    Retrieve a group by its name or id or return None without failing.
    """
    try:
        return gl.groups.get(
            id=path,
            lazy=lazy,
        )
    except GitlabGetError:
        pass
    return None


def walk_gitlab_projects(
    gl: Gitlab,
    full_path: str,
) -> Iterator[GitlabProject]:

    base_path = URL(full_path).path.strip("/")
    before_globbing, _, pattern_match = base_path.partition("*")
    pattern_match = "*" + pattern_match

    fixed_base, _, project_or_group_chunk = before_globbing.rpartition("/")
    if not fixed_base:
        raise ValueError("Cannot search from root with globbing, you need at minimum a group !")
    if project_or_group_chunk:
        pattern_match = project_or_group_chunk + pattern_match

    yield from _walk_gitlab_projects(
        gl=gl,
        fixed_base=fixed_base,
        pattern_match=pattern_match,
        base_path=fixed_base,
    )


def _walk_gitlab_projects(
    gl: Gitlab,
    fixed_base: str,
    pattern_match: str,
    base_path: str,
) -> Iterator[GitlabProject]:
    base_path = base_path.strip()
    project = maybe_get_project(gl, fixed_base, lazy=False)
    if project:
        yield project.path_with_namespace
        return

    group_base = maybe_get_group(gl, fixed_base, lazy=False)
    if not group_base:
        raise ValueError(f"Find base group: {fixed_base}")

    project_candidate: "GitlabGroupProject"
    for project_candidate in group_base.projects.list(  # type: ignore
        get_all=True,
        iterator=True,
        lazy=False,
    ):
        if pattern_match:
            project_path_rel_to_base_path = url_path_relative_to(
                project_candidate.path_with_namespace,
                base_path,
            )
            if not fnmatch(project_path_rel_to_base_path, pattern_match):
                continue
        # The shared projects of a group are excluded
        if is_shared_project(project_candidate, group_base):
            continue
        if project_candidate.archived:
            continue

        gitlab_project_path = project_candidate.path_with_namespace
        if gitlab_project_path:
            yield gitlab_project_path

    for subgrp in group_base.subgroups.list(iterator=True, all=True, lazy=True):
        if pattern_match:
            subgroup_path_rel_to_base_path = url_path_relative_to(
                subgrp.full_path,
                base_path,
            )
            if not fnmatch(subgroup_path_rel_to_base_path, pattern_match.partition("/")[0]):
                continue
        yield from _walk_gitlab_projects(
            gl=gl,
            fixed_base=subgrp.full_path,
            pattern_match=pattern_match,
            base_path=base_path,
        )
