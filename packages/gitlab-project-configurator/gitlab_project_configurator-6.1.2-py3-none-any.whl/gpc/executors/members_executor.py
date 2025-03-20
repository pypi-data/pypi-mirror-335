"""
Executor to manage the members of a project.
"""

# Standard Library
from typing import List  # pylint: disable=unused-import

# Third Party Libraries
import attr
import gitlab
import gitlab.const

from boltons.cacheutils import cachedproperty
from structlog import get_logger

# Gitlab-Project-Configurator Modules
from gpc.change_setting import ChangePropertySetting
from gpc.executors.profile_member_mixin import GPCUser
from gpc.executors.profile_member_mixin import ProfileMemberMixin
from gpc.executors.properties_updator import ChangePropertyExecutor
from gpc.helpers.exceptions import GpcMemberError
from gpc.helpers.gitlab_helper import MAP_ACCESS
from gpc.helpers.gitlab_helper import MAP_ACCESS_REVERT
from gpc.helpers.gitlab_helper import is_bot_user_for_project_member
from gpc.parameters import RunMode
from gpc.property_manager import PropertyBean


log = get_logger()

GROUP = "group"
USER = "user"


@attr.s
class ProjectMember(PropertyBean):
    role = attr.ib()  # type: int
    member_type = attr.ib()  # type: str
    member_id = attr.ib()  # type: int

    @property
    def role_name(self):
        return MAP_ACCESS_REVERT[self.role]

    def get_query(self):
        pass

    def to_dict(self):
        return {"name": self.name, "role": self.role_name}


class ChangeProjectMembers(ChangePropertySetting):
    sub_properties = ["role"]  # type: List[str]
    status_to_process = ["removed", "updated", "kept", "added", "error"]

    def has_diff(self):
        if "error" in {v["status"] for v in self.differences.values()}:
            return True
        return super().has_diff()

    @cachedproperty
    def action(self):
        if {m["status"] for m in self.differences.values()} == {"kept"}:
            return "kept"
        if self.after and not self.before:
            return "added"
        if not self.after and self.before:
            return "removed"
        return "updated"

    def rich_rows(self, console):
        table_rows = []

        # If there is no difference, don't return any rows. This matches the behavior
        # of the HTML report.
        if not self.before and not self.after:
            return table_rows

        table_rows.append(
            (
                (
                    self.wrap_text(self.property_name, console, "property_name"),
                    "",
                    "",
                    self.action,
                ),
                self.get_line_color(self.action),
            )
        )
        table_rows.append("new_line")

        for change in self.differences.values():
            name_before = change["before"]["name"] if change["before"] else ""
            name_after = change["after"]["name"] if change["after"] else ""
            name_status = self.status(name_before, name_after)
            table_rows.append(
                (
                    (
                        self.wrap_text("name", console, "property_name"),
                        self.wrap_text(
                            name_before,
                            console,
                            "before",
                        ),
                        self.wrap_text(
                            name_after,
                            console,
                            "after",
                        ),
                        name_status,
                    ),
                    self.get_line_color(name_status),
                )
            )

            role_before = change["before"]["role"] if change["before"] else ""
            role_after = change["after"]["role"] if change["after"] else ""
            role_status = self.status(role_before, role_after)
            table_rows.append(
                (
                    (
                        self.wrap_text("role", console, "property_name"),
                        self.wrap_text(
                            role_before,
                            console,
                            "before",
                        ),
                        self.wrap_text(
                            role_after,
                            console,
                            "after",
                        ),
                        role_status,
                    ),
                    self.get_line_color(role_status),
                )
            )
            table_rows.append("new_line")

        table_rows.append("new_section")
        return table_rows


class MembersProjectExecutor(ChangePropertyExecutor, ProfileMemberMixin):
    # Last section displayed
    order = 11
    applicable_to = ["group", "project"]
    sections = ["members"]
    name = "members"

    @cachedproperty
    def inherited_members(self):
        members = {}
        # We kept members_all api here even though it is not always
        # accurate because users api does not return  access level
        for user in self.item.members_all.list(
            iterator=False, all=True, retry_transient_errors=True
        ):
            members[user.username] = ProjectMember(
                name=user.username,
                member_id=user.id,
                member_type=USER,
                role=user.access_level,
            )
        return members

    def _apply(self):
        members_error = []
        if self.changes:
            members = self.changes[0]
            if members.has_diff():
                before = {prop.name: prop for prop in members.before}
                after = {prop.name: prop for prop in members.after}
                for member, diff in members.differences.items():
                    try:
                        status = diff["status"]
                        match status:
                            case "added":
                                self._create_member(after, member)
                            case "updated":
                                self._update_member(after, member)
                            case "removed":
                                self._rm_member(before, member)
                            case "error":
                                raise GpcMemberError(f"An error occurred with member '{member}'")

                    except Exception as e:
                        diff["status"] = "error"
                        log.error(
                            f"An error occurred with member '{member}' on {self.item_path}",
                            error_message=str(e),
                        )
                        members_error.append(member)
        if members_error:
            raise GpcMemberError(f"An error with the following members: {members_error}")

    @property
    def raise_errors(self):
        return bool(self.errors)

    def _create_member(self, dict_project_members, member_name):
        pm = dict_project_members[member_name]
        if pm.member_type == USER:
            self.item.members.create(
                {"user_id": pm.member_id, "access_level": pm.role}, retry_transient_errors=True
            )
        else:
            self.item.share(pm.member_id, pm.role, retry_transient_errors=True)

    def _update_member(self, dict_project_members, member_name):
        pm = dict_project_members[member_name]
        if pm.member_type == GROUP:
            self.item.unshare(pm.member_id, retry_transient_errors=True)
            self.item.share(pm.member_id, pm.role, retry_transient_errors=True)
        else:
            member = self.item.members.get(pm.member_id, retry_transient_errors=True)
            member.access_level = pm.role
            member.save(retry_transient_errors=True)

    def _rm_member(self, dict_project_members, member_name):
        pm = dict_project_members[member_name]
        if pm.member_type == GROUP:
            self.item.unshare(pm.member_id, retry_transient_errors=True)
        else:
            self.item.members.delete(pm.member_id, retry_transient_errors=True)

    def _update(self, mode: RunMode, members_user, members_group):
        if (
            self.rule.get("project_members") is not None
            or self.rule.get("group_members") is not None
        ):
            project_members = self.get_project_members_to_update(members_user, members_group)
            keep_existing_members = self.rule.get("keep_existing_members", False)

            old_project_members = self.get_current_members()
            keep_existing_groups = self.rule.get("keep_existing_groups", False)
            if keep_existing_groups:
                kept_groups = {
                    k: v for k, v in old_project_members.items() if v.member_type == "group"
                }
                for k, v in kept_groups.items():
                    project_members.setdefault(k, v)
            skip_members = self._check_members(old_project_members, project_members)

            self.changes.append(
                ChangeProjectMembers(
                    "members",
                    list(old_project_members.values()),
                    list(project_members.values()),
                    self.show_diff_only,
                    keep_existing=keep_existing_members,
                )
            )
            for member in skip_members:
                self.changes[0].differences[member]["status"] = "kept"  # type: ignore

            for error in self.errors:
                member_error = error.get("member")
                str_exception = error.get("exception")
                self.changes[0].differences[member_error]["status"] = "error"  # type: ignore
                self.changes[0].differences[member_error]["after"]["role"] = str_exception  # type: ignore # pylint: disable=line-too-long
                self.changes[0].action = "error"

    def _check_members(self, old_project_members, project_members):
        members_error = []
        skip_members = []
        for member_name in old_project_members:
            if is_bot_user_for_project_member(member_name):
                log.info(f"{member_name} is a bot user, skipping the member")
                skip_members.append(member_name)
        for member_name in project_members:
            if member_name not in old_project_members and member_name in self.inherited_members:
                # Check if member is not inherited from parents groups.
                inherited_member = self.inherited_members[member_name]
                if self.rule.get("skip_permission_error", False):
                    if inherited_member.role > project_members[member_name].role:
                        log.info(
                            f"skip_permission_error enabled: {member_name} has"
                            f" already '{MAP_ACCESS_REVERT[inherited_member.role]}' rights on"
                            f" the project {self.item_path}, skipping..."
                        )
                        skip_members.append(member_name)

                elif inherited_member.role == gitlab.const.OWNER_ACCESS:
                    # If the member is inherited and has higher right, we prevent
                    # an error from the API.
                    members_error.append(member_name)
        if members_error:
            raise GpcMemberError(
                f"The users '{members_error}' can not be add to"
                f" the project {self.item_path} because "
                "they are inherited members "
                "with owner access."
            )
        return skip_members

    def get_project_members_to_update(self, members_user, members_group):
        project_members_settings = (
            self.rule.get("project_members")
            if self.rule.get("project_members")
            else self.rule.get("group_members")
        )
        project_members = {}
        if "profiles" in project_members_settings:
            for profile_name in project_members_settings.profiles:
                profile = self.get_member_profile(profile_name)
                if "role" not in profile:
                    raise GpcMemberError(
                        "The role is missing in your "
                        f"member_profiles definition '{profile_name}'."
                    )
                for member in profile.members:
                    project_members[member] = self._init_project_member(
                        member, profile.role, members_user, members_group
                    )
        if "members" in project_members_settings:
            project_members.update(
                self._extract_members(members_group, members_user, project_members_settings.members)
            )
        return project_members

    def _extract_members(self, members_group, members_user, members):
        project_members = {}
        for member in members:
            if "names" in member:
                for name in member.names:
                    project_members[name] = self._init_project_member(
                        name, member.role, members_user, members_group
                    )
            if "name" in member:
                project_members[member.name] = self._init_project_member(
                    member.name, member.role, members_user, members_group
                )
        return project_members

    def _init_project_member(self, member_name, role, members_user, members_group):
        try:
            member = self.get_member(member_name)
        except GpcMemberError as e:
            self.errors.append({"member": member_name, "exception": str(e)})
            self.error_message = str(e)
            return ProjectMember(
                name=member_name,
                role=MAP_ACCESS.get("none"),
                member_id=-1,
                member_type=USER,
            )
        if isinstance(member, GPCUser):
            members_user.append(member.gl_id)
            return ProjectMember(
                name=member.name,
                role=MAP_ACCESS.get(role),
                member_id=member.gl_id,
                member_type=USER,
            )
        # GPCGroup
        members_group.append(member.full_path)
        return ProjectMember(
            name=member.full_path,
            role=MAP_ACCESS.get(role),
            member_id=member.gl_id,
            member_type=GROUP,
        )

    def get_current_members(self):
        current_members = {}
        for user in self.item.members.list(iterator=True, retry_transient_errors=True):
            current_members[user.username] = ProjectMember(
                name=user.username,
                member_type=USER,
                member_id=user.id,
                role=user.access_level,
            )
        for group in self.item.shared_with_groups:
            current_members[group["group_full_path"]] = ProjectMember(
                name=group["group_full_path"],
                member_type=GROUP,
                member_id=group["group_id"],
                role=group["group_access_level"],
            )
        return current_members
