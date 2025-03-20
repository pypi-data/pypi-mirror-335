"""
Mixin to extract members of profiles section.
"""

# Standard Library
from typing import TYPE_CHECKING
from typing import Any
from typing import Dict
from typing import Union

# Third Party Libraries
import attr

from gitlab import exceptions as gl_exceptions
from structlog import get_logger

# Gitlab-Project-Configurator Modules
from gpc.helpers.exceptions import GpcMemberError
from gpc.helpers.exceptions import GpcUserError
from gpc.helpers.gitlab_helper import get_group
from gpc.helpers.gitlab_helper import get_user_by_username


if TYPE_CHECKING:
    # Third Party Libraries
    from gitlab.v4.objects import Group
    from gitlab.v4.objects import Project

log = get_logger()


@attr.s
class GPCMember:
    name = attr.ib()  # type: str
    gl_id = attr.ib()  # type: int


class GPCUser(GPCMember):
    pass


@attr.s
class GPCGroup(GPCMember):
    full_path = attr.ib()  # type: str


class ProfileMemberMixin:
    item: Union["Project", "Group"]
    item_path: str
    gitlab: Any
    rule: Dict[str, Any]

    def get_merged_profiles(self, profiles):
        merged_profiles = []
        for profile_name in profiles:
            log.debug(f"Injecting profile from : {profile_name}")
            profile = self.get_member_profile(profile_name)
            merged_profiles += profile.members
        return merged_profiles

    def get_member_profile(self, profile_name: str) -> Dict[str, str]:
        if not self.rule.get("member_profiles"):
            raise GpcMemberError(
                f"ERROR on project {self.item_path}: "
                f"The import of member_profiles profile '{profile_name}' is impossible, because "
                "the section 'member_profiles' does not exist."
            )
        for member_profile in self.rule["member_profiles"]:
            if member_profile.name == profile_name:
                return member_profile
        raise GpcMemberError(
            f"ERROR on project {self.item_path}: "
            f"The import of member profile '{profile_name}' is impossible, because "
            "this profile name is not found in the 'member_profiles' "
            "section."
        )

    def get_member(self, member_name: str) -> GPCMember:
        try:
            gl_user = get_user_by_username(self.gitlab, member_name)
            return GPCUser(name=gl_user.username, gl_id=gl_user.id)
        except GpcUserError:
            pass
        try:
            group = get_group(self.gitlab, member_name)
            return GPCGroup(name=group.name, gl_id=group.id, full_path=group.full_path)
        except gl_exceptions.GitlabGetError as e:
            raise GpcMemberError(
                f"The username or group name '{member_name}'" f" does not exist"
            ) from e

    def _find_member(self, member_name: str) -> GPCMember:
        member_name = member_name.lower()
        for user in self.item.users.list(
            search=member_name, iterator=True, get_all=True, retry_transient_errors=True
        ):
            if user.username.lower() == member_name:
                return GPCUser(name=member_name, gl_id=user.id)
        try:
            return self.get_member(member_name)
        except GpcMemberError as e:
            raise GpcMemberError(
                f"ERROR on project {self.item_path}: "
                f"I am unable to get information about the user {member_name}. "
                "Remember external users need to be added "
                "as members of the project, because the Gitlab API "
                "does not allow to search for information "
                "about this particular type of users."
            ) from e
