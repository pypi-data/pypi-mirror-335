# Standard Library
import collections.abc

from typing import Any
from typing import Generator
from typing import List
from typing import Optional
from typing import Sequence
from typing import Union

# Third Party Libraries
import attr


Url = str
ProjectName = str
RuleName = str
ProjectRule = Any
GroupRule = Any
Rule = Any
Something = Any


@attr.s
class ProjectPathRule:
    @property
    def project_path(self):
        # To avoid cyclic import, set the import in the getter
        # pylint: disable=import-outside-toplevel, cyclic-import

        # Gitlab-Project-Configurator Modules
        from gpc.helpers.gitlab_helper import clean_gitlab_project_name

        # pylint: enable=import-outside-toplevel
        return clean_gitlab_project_name(self._project_path)

    _project_path = attr.ib()  # type: ignore
    rule = attr.ib()  # type: ProjectRule
    recursive = attr.ib()  # type: bool
    not_seen_yet_only = attr.ib()  # type: bool
    excludes = attr.ib(default=None)  # type: Optional[List[str]]
    gpc_badge_name = attr.ib(default=None)  # type: Optional[str]
    gpc_badge_image_url = attr.ib(default=None)  # type: Optional[str]

    def is_root_path(self) -> bool:
        return self._project_path == "/"


@attr.s
class GroupPathRule:
    group_path = attr.ib()  # type: ignore
    rule = attr.ib()  # type: GroupRule


GenProjectPathRules = Generator[ProjectPathRule, None, None]
GenGroupPathRules = Generator[GroupPathRule, None, None]
OptionalProjectNameList = Optional[List[ProjectName]]
OptionalRuleName = Optional[RuleName]


def listify(c: Union[Sequence[Something], Something]) -> List[Something]:
    """
    Ensure to always have a list.

    Returns:
        If c is None, return an empty list.
        If the input is a list, it returns it exactly.
        If the input is a sequence (except strings), it create a list of it.
        If the input is not a list, it creates a list with a single element.
    """
    if c is None:
        return []
    if isinstance(c, list):
        return c
    if isinstance(c, str):
        return [c]
    if isinstance(c, collections.abc.Sequence):
        return list(c)
    return [c]
