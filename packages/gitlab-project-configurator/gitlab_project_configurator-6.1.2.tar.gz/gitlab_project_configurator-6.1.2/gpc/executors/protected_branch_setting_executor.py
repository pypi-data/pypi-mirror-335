"""
Make the update of protected branch.
"""

# Standard Library
from typing import List  # pylint: disable=unused-import

# Third Party Libraries
import attr
import click

from boltons.cacheutils import cachedproperty
from dictns import Namespace
from gitlab import exceptions as gl_exceptions
from gitlab.exceptions import GitlabCreateError
from gitlab.exceptions import GitlabDeleteError
from gitlab.exceptions import GitlabGetError
from structlog import get_logger

# Gitlab-Project-Configurator Modules
from gpc.change_setting import ChangePropertySetting
from gpc.executors.profile_member_mixin import GPCUser
from gpc.executors.profile_member_mixin import ProfileMemberMixin
from gpc.executors.properties_updator import ChangePropertyExecutor
from gpc.helpers.exceptions import GPCCreateError
from gpc.helpers.exceptions import GPCDeleteError
from gpc.helpers.exceptions import GpcMemberError
from gpc.helpers.exceptions import GpcPermissionError
from gpc.helpers.exceptions import GpcProtectedBranchesError
from gpc.helpers.gitlab_helper import MAP_ACCESS
from gpc.helpers.gitlab_helper import MAP_ACCESS_REVERT
from gpc.helpers.gitlab_helper import get_group
from gpc.helpers.gitlab_helper import get_subgroups
from gpc.helpers.gitlab_helper import get_user_by_id
from gpc.parameters import RunMode
from gpc.property_manager import PropertyBean
from gpc.property_manager import PropertyManager


MERGE_PERMISSION = "allowed_to_merge"
PUSH_PERMISSION = "allowed_to_push"

log = get_logger()

# pylint: disable=duplicate-code


@attr.s(eq=False)
class ProtectedBranch(PropertyBean):
    allowed_to_merge = attr.ib()  # type: ProtectedRefsAuth
    allowed_to_push = attr.ib()  # type: ProtectedRefsAuth
    allow_force_push = attr.ib()
    code_owner_approval_required = attr.ib()
    allowed_to_unprotect = attr.ib()

    @staticmethod
    def to_protected_branches(gitlab, api_protected_branches):
        protected_branches = []  # type: List[ProtectedBranch]
        for api_protected_branch in api_protected_branches:
            protected_branches.append(
                ProtectedBranch.to_protected_branch(gitlab, api_protected_branch)
            )
        return protected_branches

    @staticmethod
    def get_unprotect_access_levels(access_levels):
        if not access_levels:
            return None
        level = access_levels[0]["access_level"]
        return MAP_ACCESS_REVERT[level]

    def copy(self):
        return ProtectedBranch(
            name=self.name,
            allowed_to_merge=self.allowed_to_merge,
            allowed_to_push=self.allowed_to_push,
            allow_force_push=self.allow_force_push,
            code_owner_approval_required=self.code_owner_approval_required,
            allowed_to_unprotect=self.allowed_to_unprotect,
        )

    @staticmethod
    def to_protected_branch(gitlab, api_protected_branch):
        merge_role, merge_users = ProtectedBranch.get_role_and_users(
            api_protected_branch.merge_access_levels, gitlab
        )

        push_role, push_users = ProtectedBranch.get_role_and_users(
            api_protected_branch.push_access_levels, gitlab
        )

        allowed_to_merge = ProtectedRefsAuth(role=merge_role, users=merge_users)
        allowed_to_push = ProtectedRefsAuth(role=push_role, users=push_users)
        allow_force_push = api_protected_branch.allow_force_push
        code_owner_approval_required = getattr(
            api_protected_branch, "code_owner_approval_required", None
        )
        allowed_to_unprotect = ProtectedBranch.get_unprotect_access_levels(
            getattr(api_protected_branch, "unprotect_access_levels", {})
        )

        return ProtectedBranch(
            name=api_protected_branch.name,
            allowed_to_merge=allowed_to_merge,
            allowed_to_push=allowed_to_push,
            code_owner_approval_required=code_owner_approval_required,
            allow_force_push=allow_force_push,
            allowed_to_unprotect=allowed_to_unprotect,
        )

    @staticmethod
    def get_role_and_users(access_levels, gitlab):
        users = []
        role = None
        for access in access_levels:
            if access.get("user_id") is not None:
                user_id = access.get("user_id")
                user = get_user_by_id(gitlab, user_id)
                users.append(ProtectedRefMember(user_id, user.username))
            else:  # get role
                role_id = access.get("access_level")
                role = ProtectedRefMember(role_id, MAP_ACCESS_REVERT.get(role_id))
        return role, users

    def get_query(self):
        allow_to_merge = ProtectedBranch.prepare_allow_action(self.allowed_to_merge)
        allow_to_push = ProtectedBranch.prepare_allow_action(self.allowed_to_push)

        obj = {
            "name": self.name,
            "allowed_to_push": allow_to_push,
            "allowed_to_merge": allow_to_merge,
        }
        if self.allowed_to_unprotect and self.allowed_to_unprotect in MAP_ACCESS:
            obj["allowed_to_unprotect"] = [{"access_level": MAP_ACCESS[self.allowed_to_unprotect]}]
        if self.allow_force_push is not None:
            obj.update({"allow_force_push": self.allow_force_push})
        if self.code_owner_approval_required is not None:
            obj.update({"code_owner_approval_required": self.code_owner_approval_required})
        return obj

    @staticmethod
    def prepare_allow_action(allow_action):
        actions_list = []
        if allow_action.role:
            actions_list.append({"access_level": allow_action.role.member_id})
        if allow_action.users:
            for identifier in allow_action.users:
                actions_list.append({"user_id": identifier.member_id})
        if allow_action.groups:
            for identifier in allow_action.groups:
                actions_list.append({"group_id": identifier.member_id})
        return actions_list

    def to_dict(self):
        obj = {
            "name": self.name,
            "allowed_to_merge": self.allowed_to_merge.get_members_hr(),
            "allowed_to_push": self.allowed_to_push.get_members_hr(),
            "allowed_to_unprotect": self.allowed_to_unprotect,
        }
        if self.allow_force_push is not None:
            obj.update({"allow_force_push": self.allow_force_push})
        if self.code_owner_approval_required is not None:
            obj.update({"code_owner_approval_required": self.code_owner_approval_required})
        return obj

    def __eq__(self, other):
        if not isinstance(other, ProtectedBranch):
            return False

        comp = (
            self.name == other.name
            and self.allowed_to_push == other.allowed_to_push
            and self.allowed_to_merge == other.allowed_to_merge
            and self.allowed_to_unprotect == other.allowed_to_unprotect
        )

        if self.allow_force_push is None or other.allow_force_push is None:  # ignore
            pass
        else:
            comp = comp and self.allow_force_push == other.allow_force_push

        if (
            self.code_owner_approval_required is None or other.code_owner_approval_required is None
        ):  # ignore
            pass
        else:
            comp = comp and self.code_owner_approval_required == other.code_owner_approval_required

        return comp


@attr.s
class ChangeProtectedBranch(ChangePropertySetting):
    sub_properties = [
        "allowed_to_merge",
        "allowed_to_push",
        "allow_force_push",
        "code_owner_approval_required",
        "allowed_to_unprotect",
    ]
    status_to_process = ["removed", "updated", "kept", "added", "error"]
    errors = attr.ib(default=[])  # type: List

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

        allowed_to_merge_errors = [
            e["member"] for e in self.errors if e.get("permission_type") == MERGE_PERMISSION
        ]
        allowed_to_push_errors = [
            e["member"] for e in self.errors if e.get("permission_type") == PUSH_PERMISSION
        ]

        failed_creation_branches = [
            e["branch"] for e in self.errors if e.get("permission_type") == "create"
        ]

        branch_names = list(self.differences.keys())
        branch_names.sort()

        for change in self.differences.values():
            properties = []
            if change["before"]:
                properties = list(change["before"].keys())
            else:
                properties = list(change["after"].keys())

            for prop in properties:
                if (
                    prop == "name"
                    and change["after"]
                    and change["after"][prop] in failed_creation_branches
                ):
                    before = str(change["before"][prop]) if change["before"] else ""
                    after = str(change["after"][prop]) if change["after"] else ""

                    table_rows.append(
                        (
                            (
                                self.wrap_text(prop, console, "property_name"),
                                self.wrap_text(
                                    before,
                                    console,
                                    "before",
                                ),
                                self.wrap_text(
                                    f"{after} (creation failed)",
                                    console,
                                    "after",
                                ),
                                "error",
                            ),
                            "red",
                        )
                    )
                    table_rows.append("new_line")
                    break

                before = str(change["before"][prop]) if change["before"] else ""
                after = str(change["after"][prop]) if change["after"] else ""
                status = self.status(before, after)
                table_rows.append(
                    (
                        (
                            self.wrap_text(prop, console, "property_name"),
                            self.wrap_text(
                                before,
                                console,
                                "before",
                            ),
                            self.wrap_text(
                                after,
                                console,
                                "after",
                            ),
                            status,
                        ),
                        self.get_line_color(status),
                    )
                )
                if prop == MERGE_PERMISSION and allowed_to_merge_errors:
                    table_rows.append(
                        (
                            (
                                "",
                                "",
                                self.wrap_text(
                                    str(allowed_to_merge_errors),
                                    console,
                                    "after",
                                ),
                                "error",
                            ),
                            self.get_line_color("error"),
                        )
                    )
                if prop == PUSH_PERMISSION and allowed_to_push_errors:
                    table_rows.append(
                        (
                            (
                                "",
                                "",
                                self.wrap_text(
                                    str(allowed_to_push_errors),
                                    console,
                                    "after",
                                ),
                                "error",
                            ),
                            self.get_line_color("error"),
                        )
                    )
            table_rows.append("new_line")

        table_rows.append("new_section")
        return table_rows


@attr.s(eq=False)
class ProtectedRefMember:
    member_id = attr.ib()  # type: int
    name = attr.ib()  # type: str

    def __eq__(self, other):
        if not isinstance(other, ProtectedRefMember):
            return False
        return self.member_id == other.member_id and self.name.replace(
            "none", "no one"
        ) == other.name.replace("none", "no one")


@attr.s(eq=False)
class ProtectedRefsAuth:
    role = attr.ib(default=None)  # type: ProtectedRefMember
    users = attr.ib(default=[])  # type: List[ProtectedRefMember]
    groups = attr.ib(default=[])  # type: List[ProtectedRefMember]
    code_owner_approval_required = attr.ib(default=None)
    allow_force_push = attr.ib(default=None)

    def sorted_users(self):
        return (
            sorted((c for c in self.users), key=lambda x: x.member_id)
            if self.users is not None
            else None
        )

    def sorted_groups(self):
        return (
            sorted((c for c in self.groups), key=lambda x: x.member_id)
            if self.groups is not None
            else None
        )

    def get_members_hr(self):
        roles_name = []
        users_name = []
        groups_name = []
        if self.role:
            roles_name = [MAP_ACCESS_REVERT.get(self.role.member_id)]
        if self.users:
            users_name = sorted(x.name for x in self.users)
        if self.groups:
            groups_name = sorted(x.name for x in self.groups)
        return roles_name + users_name + groups_name

    def __eq__(self, other):
        if not isinstance(other, ProtectedRefsAuth):
            return False

        return (
            self.role == other.role
            and self.sorted_users() == other.sorted_users()
            and self.sorted_groups() == other.sorted_groups()
            and self.allow_force_push == other.allow_force_push
            and self.code_owner_approval_required == other.code_owner_approval_required
        )


class ProtectedBranchManager(PropertyManager):
    def create(self, property_bean: PropertyBean, project_path):
        try:
            self.rm_existing(property_bean.name)
            obj_create = property_bean.get_query()
            self.manager.create(obj_create, retry_transient_errors=True)
        except GitlabCreateError as e:
            error_message = (
                f"branch '{property_bean.name}' could "
                f"not be created (project {project_path}): {str(e.error_message)}"
            )
            click.secho(error_message, fg="red")
            if e.response_code == 403:
                click.secho(
                    f"On project {project_path}: Access forbidden. "
                    "Please ensure your Gitlab token has "
                    "'owner' membership to the projects",
                    fg="red",
                )
            else:
                raise GPCCreateError(error_message, e.response_code) from e
        except GitlabDeleteError as e:
            error_message = (
                f"branch '{property_bean.name}' (project {project_path}) "
                "seems to be blocked (it is probably due to a Gitlab Bug) "
                "we are not abble to update it"
            )
            click.secho(error_message, fg="red")
            raise GPCDeleteError(
                f"branch '{property_bean.name}' (project {project_path}): {str(e.error_message)}"
            ) from e


class ProtectedBranchSettingExecutor(ChangePropertyExecutor, ProfileMemberMixin):
    order = 20
    name = "protected_branches"
    sections = ["protected_branches"]

    @cachedproperty
    def members_id(self):
        members = [
            x.id
            for x in self.item.users.list(get_all=True, retry_transient_errors=True, iterator=True)
        ]
        for group_path in self.all_groups:
            group = get_group(self.gitlab, group_path)
            for member in group.members_all.list(
                all=True, iterator=True, retry_transient_errors=True
            ):
                members.append(member.id)
        return list(set(members))

    @cachedproperty
    def members_group(self):
        return [x.get("group_full_path") for x in self.item.shared_with_groups]

    @cachedproperty
    def all_groups(self):
        all_groups = []
        for group_path in self.members_group:
            subgroup = get_subgroups(self.gitlab, group_path)
            all_groups.extend(subgroup)
        return all_groups + self.members_group

    @cachedproperty
    def keep_existing(self):
        return self.rule.get("keep_existing_protected_branches", False)

    @cachedproperty
    def apply_group_best_effort(self):
        return self.rule.get("apply_group_best_effort", False)

    def _update_or_create(self, manager, change_properties, properties):
        # target to update or create
        variables_to_cu = change_properties.update_or_create
        for variable in properties:
            if variable.name in variables_to_cu:
                try:
                    manager.create(variable, self.item_path)
                except GPCCreateError as e:
                    change_properties.differences[variable.name]["status"] = "error"
                    if e.original_response_code == 422:
                        self.errors.append(
                            {
                                "branch": variable.name,
                                "exception": str(e),
                                "permission_type": "create",
                            }
                        )
                        change_properties.action = "error"

                    click.secho(
                        f"CREATE ERROR: {str(e)}",
                        fg="red",
                    )
                except GPCDeleteError as e:
                    change_properties.differences[variable.name]["status"] = "error"
                    click.secho(f"UPDATE ERROR: {str(e)} ", fg="red")

    def _apply(self):
        if self.changes:
            protected_branches = self.changes[0]
            try:
                self._save_properties(
                    ProtectedBranchManager(self.item.protectedbranches),
                    protected_branches,
                    protected_branches.after,
                )
            except gl_exceptions.GitlabCreateError as e:
                if e.response_code == 422:
                    raise GpcPermissionError(
                        "Are you sure yours users or groups are members"
                        f" of the project {self.item_path} ?\nError: {str(e)}"
                    ) from e
        if self.errors:
            error_message = ""
            error_users = []
            failed_creation_branches = []
            for error in self.errors:
                if error.get("permission_type") == "create":
                    failed_creation_branches.append(error.get("branch"))
                else:
                    error_users.append(error.get("member"))
                    execption = error.get("exception")
                    error_message += f"{execption}\n"

            raise_message = (
                f"ERROR with users {error_users}:\n {error_message}\n" if error_users else ""
            )
            raise_message += (
                f"Creation of the following protected branches failed: {failed_creation_branches}"
            )

            raise GpcProtectedBranchesError(raise_message)

    def _update(self, mode: RunMode, members_user, members_group):
        if "protected_branches" in self.rule and self.rule.protected_branches is not None:
            protected_branches = []

            for protected_branch in self.rule.protected_branches:
                protected_branches.append(
                    self._to_protected_branch(protected_branch, members_user, members_group)
                )
            old_protected_branches = ProtectedBranch.to_protected_branches(
                self.gitlab,
                self.item.protectedbranches.list(  # type: ignore
                    iterator=True, retry_transient_errors=True
                ),
            )
            self.changes.append(
                ChangeProtectedBranch(
                    property_name="protected_branches",
                    before=sorted(old_protected_branches, key=lambda x: x.name),
                    after=sorted(protected_branches, key=lambda x: x.name),
                    show_diff_only=self.show_diff_only,
                    keep_existing=self.keep_existing,
                    errors=self.errors,
                )
            )

    def _to_protected_branch(self, protected_branch, future_members_user, future_members_group):
        new_protected_branch = self.prepare_protected_branch(protected_branch)
        allowed_to_merge = self.init_protected_refs_auth(
            new_protected_branch.allowed_to_merge,
            future_members_user,
            future_members_group,
            MERGE_PERMISSION,
        )
        allowed_to_push = self.init_protected_refs_auth(
            new_protected_branch.allowed_to_push,
            future_members_user,
            future_members_group,
            PUSH_PERMISSION,
        )

        options = self.init_protected_branch_options(new_protected_branch)

        params = options.copy()
        params.update(
            {
                "name": new_protected_branch.pattern,
                "allowed_to_merge": allowed_to_merge,
                "allowed_to_push": allowed_to_push,
            }
        )

        return ProtectedBranch(**params)

    def init_protected_branch_options(self, protected_branch):
        pb_name = protected_branch.get("pattern", "")
        try:
            old_pb = self.item.protectedbranches.get(pb_name)
        except GitlabGetError:
            old_pb = None
        if old_pb:
            opts = {
                "allow_force_push": old_pb.allow_force_push,
                "code_owner_approval_required": getattr(
                    old_pb, "code_owner_approval_required", None
                ),
                "allowed_to_unprotect": (
                    old_pb.unprotect_access_levels[0].get("access_level_description", "").lower()
                    if (
                        hasattr(old_pb, "unprotect_access_levels")
                        and old_pb.unprotect_access_levels
                    )
                    else None
                ),
            }
        else:
            opts = {
                "allow_force_push": False,
                "code_owner_approval_required": False,
                "allowed_to_unprotect": "maintainers",
            }

        if "allow_force_push" in protected_branch and protected_branch.allow_force_push is not None:
            opts.update({"allow_force_push": protected_branch.allow_force_push})
        if (
            "code_owner_approval_required" in protected_branch
            and protected_branch.code_owner_approval_required is not None
        ):
            opts.update(
                {"code_owner_approval_required": protected_branch.code_owner_approval_required}
            )
        if (
            "allowed_to_unprotect" in protected_branch
            and protected_branch.allowed_to_unprotect is not None
        ):
            opts.update({"allowed_to_unprotect": protected_branch.allowed_to_unprotect})

        return opts

    def prepare_protected_branch(self, protected_branch: Namespace):
        new_protected_branch = Namespace(protected_branch.copy())
        self._update_members_from_profiles(new_protected_branch.allowed_to_merge)
        self._update_members_from_profiles(new_protected_branch.allowed_to_push)
        if "allow_force_push" not in protected_branch:
            new_protected_branch["allow_force_push"] = None
        if "code_owner_approval_required" not in protected_branch:
            new_protected_branch["code_owner_approval_required"] = None
        return new_protected_branch

    def _update_members_from_profiles(self, allowed_action):
        if "profiles" in allowed_action:
            merge_profiles = self.get_merged_profiles(allowed_action.get("profiles"))
            members = allowed_action.get("members", [])
            allowed_action["members"] = list(set(merge_profiles + members))
            del allowed_action["profiles"]

    def init_protected_refs_auth(
        self, protected_branch_config, future_members_user, future_members_group, permission_type
    ):
        if isinstance(protected_branch_config, str):
            return ProtectedRefsAuth(
                role=ProtectedRefMember(
                    self._get_role_id(protected_branch_config), protected_branch_config
                )
            )
        users = []
        groups = []
        role = None
        if "role" in protected_branch_config:
            role = ProtectedRefMember(
                self._get_role_id(protected_branch_config.role),
                protected_branch_config.role,
            )
        if "members" in protected_branch_config:
            self._init_members(protected_branch_config.members, users, groups, permission_type)
            users, groups = self._check_members(
                users, groups, future_members_user, future_members_group, permission_type
            )
        return ProtectedRefsAuth(role=role, users=users, groups=groups)

    def _init_members(self, members, gpc_users, gpc_groups, permission_type):
        for member_name in members:
            try:
                member = self._find_member(member_name)
            except GpcMemberError as e:
                self.errors.append(
                    {"member": member_name, "exception": str(e), "permission_type": permission_type}
                )
                continue

            if isinstance(member, GPCUser):
                gpc_users.append(ProtectedRefMember(member.gl_id, member_name))
            else:
                # GPCGroup
                gpc_groups.append(ProtectedRefMember(member.gl_id, member.full_path))

    def _check_members(
        self, users, groups, future_members_user, future_members_group, permission_type
    ):
        unauthorize_groups, groups_to_expand = self._get_unauthorize_groups(
            groups, future_members_group
        )
        expanded_users = self.expand_groups(users, groups_to_expand) + users
        unauthorize_members = (
            self._get_unauthorize_users(expanded_users, future_members_user) + unauthorize_groups
        )

        if unauthorize_members:
            error_msg = (
                f"Impossible to configure protected branches on project '{self.item_path}' "
                f"because these users and groups defined {','.join(unauthorize_members)}"
                " are not members of project"
            )
            self.errors.append(
                {
                    "member": ",".join(unauthorize_members),
                    "exception": error_msg,
                    "permission_type": permission_type,
                }
            )

            def filter_func(member):
                return ProtectedBranchSettingExecutor.filter_unauthorized(
                    member, unauthorize_members
                )

            expanded_users = list(filter(filter_func, expanded_users))
            groups = list(filter(filter_func, groups))
        return expanded_users, [g for g in groups if g.name not in groups_to_expand]

    @staticmethod
    def filter_unauthorized(member, unauthorize_members):
        return member.name not in unauthorize_members

    def _get_unauthorize_users(self, users, future_members_user):
        members_id = self.members_id + future_members_user
        unauthorize_users = []
        for user in users:
            if user.member_id not in members_id:
                if not bool(self.item.users.list(search=user.name)):
                    unauthorize_users.append(user.name)
        return unauthorize_users

    def _get_unauthorize_groups(self, groups, future_members_group):
        unauthorize_groups = []
        _unauthorize_groups = []
        groups_to_expand = []
        members_group = self.members_group + future_members_group
        for group in groups:
            if group.name not in members_group:
                _unauthorize_groups.append(group.name)
        if not self.apply_group_best_effort:
            return _unauthorize_groups, []
        for unauthorized_group in _unauthorize_groups:
            if self.is_really_unauthorized(unauthorized_group):
                unauthorize_groups.append(unauthorized_group)
            else:
                groups_to_expand.append(unauthorized_group)
        return unauthorize_groups, groups_to_expand

    def is_really_unauthorized(self, unauthorized_group):
        for _group in self.item.groups.list(iterator=True, get_all=True):
            group = self.gitlab.groups.get(_group.id)
            if unauthorized_group in [x.get("group_full_path") for x in group.shared_with_groups]:
                return False
        return True

    def expand_groups(self, users, groups):
        user_ids = [user.member_id for user in users]
        users_from_groups = []
        for _group in groups:
            log.info(f"Expanding group: {_group} \nAdding each member separately")
            group_members = self.gitlab.groups.get(_group).members_all.list(
                iterator=True, get_all=True
            )
            users_from_groups.extend(
                [
                    ProtectedRefMember(member.id, member.username)
                    for member in group_members
                    if member.id not in user_ids
                ]
            )

        return users_from_groups
