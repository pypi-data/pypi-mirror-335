"""
Make the update of protected tag.
"""

# Standard Library
from typing import List  # pylint: disable=unused-import

# Third Party Libraries
import attr

from boltons.cacheutils import cachedproperty
from gitlab import exceptions as gl_exceptions

# Gitlab-Project-Configurator Modules
from gpc.change_setting import ChangePropertySetting
from gpc.executors.profile_member_mixin import GPCUser
from gpc.executors.profile_member_mixin import ProfileMemberMixin
from gpc.executors.properties_updator import ChangePropertyExecutor
from gpc.helpers.exceptions import GpcPermissionError
from gpc.helpers.exceptions import GpcProtectedTagsError
from gpc.helpers.exceptions import GpcUserError
from gpc.helpers.gitlab_helper import MAP_ACCESS_REVERT
from gpc.helpers.gitlab_helper import get_user_by_id
from gpc.parameters import RunMode
from gpc.property_manager import PropertyBean
from gpc.property_manager import PropertyManager


CREATE_PERMISSION = "allowed_to_create"


@attr.s(eq=False)
class ProtectedTag(PropertyBean):
    allowed_to_create = attr.ib()  # type: ProtectedTagRefsAuth

    @staticmethod
    def to_protected_tags(gitlab, api_protected_tags):
        protected_tags = []  # type: List[ProtectedTag]
        for api_protected_tag in api_protected_tags:
            protected_tags.append(ProtectedTag.to_protected_tag(gitlab, api_protected_tag))
        return protected_tags

    @staticmethod
    def to_protected_tag(gitlab, api_protected_tag):
        create_role, create_users = ProtectedTag.get_role_and_users(
            api_protected_tag.create_access_levels, gitlab
        )

        allowed_to_create = ProtectedTagRefsAuth(role=create_role, users=create_users)

        return ProtectedTag(
            name=api_protected_tag.name,
            allowed_to_create=allowed_to_create,
        )

    @staticmethod
    def get_role_and_users(access_levels, gitlab):
        users = []
        role = None
        for access in access_levels:
            if access.get("user_id") is not None:
                user_id = access.get("user_id")
                user = get_user_by_id(gitlab, user_id)
                users.append(ProtectedTagRefUser(user_id, user.username))
            else:  # get role
                role_id = access.get("access_level")
                role = ProtectedTagRefUser(role_id, MAP_ACCESS_REVERT.get(role_id))
        return role, users

    def get_query(self):
        allow_to_create = ProtectedTag.prepare_allow_action(self.allowed_to_create)

        obj = {
            "name": self.name,
            "allowed_to_create": allow_to_create,
        }

        return obj

    @staticmethod
    def prepare_allow_action(allow_action):
        actions_list = []
        if allow_action.role:
            actions_list.append({"access_level": allow_action.role.user_id})
        if allow_action.users:
            for identifier in allow_action.users:
                actions_list.append({"user_id": identifier.user_id})
        return actions_list

    def to_dict(self):
        obj = {
            "name": self.name,
            "allowed_to_create": self.allowed_to_create.get_users_hr(),
        }
        return obj

    def __eq__(self, other):
        if not isinstance(other, ProtectedTag):
            return False
        return self.name == other.name and self.allowed_to_create == other.allowed_to_create


@attr.s
class ChangeProtectedTag(ChangePropertySetting):
    sub_properties = ["allowed_to_create", "users"]
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

        allowed_to_create_errors = [
            e["user"] for e in self.errors if e.get("permission_type") == CREATE_PERMISSION
        ]

        tag_names = list(self.differences.keys())
        tag_names.sort()

        for change in self.differences.values():
            properties = []
            if change["before"]:
                properties = list(change["before"].keys())
            else:
                properties = list(change["after"].keys())

            for prop in properties:
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
                if prop == CREATE_PERMISSION and allowed_to_create_errors:
                    table_rows.append(
                        (
                            (
                                "",
                                "",
                                self.wrap_text(
                                    str(allowed_to_create_errors),
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
class ProtectedTagRefUser:
    user_id = attr.ib()  # type: int
    name = attr.ib()  # type: str

    def __eq__(self, other):
        if not isinstance(other, ProtectedTagRefUser):
            return False
        return self.user_id == other.user_id and self.name.replace(
            "none", "no one"
        ) == other.name.replace("none", "no one")


@attr.s(eq=False)
class ProtectedTagRefsAuth:
    role = attr.ib(default=None)  # type: ProtectedTagRefUser
    users = attr.ib(default=[])  # type: List[ProtectedTagRefUser]

    def sorted_users(self):
        return (
            sorted((c for c in self.users), key=lambda x: x.user_id)
            if self.users is not None
            else None
        )

    def get_users_hr(self):
        roles_name = []
        users_name = []
        if self.role:
            roles_name = [MAP_ACCESS_REVERT.get(self.role.user_id)]
        if self.users:
            users_name = sorted(x.name for x in self.users)
        return roles_name + users_name

    def __eq__(self, other):
        if not isinstance(other, ProtectedTagRefsAuth):
            return False

        return self.role == other.role and self.sorted_users() == other.sorted_users()


class ProtectedTagSettingExecutor(ChangePropertyExecutor, ProfileMemberMixin):
    order = 30
    name = "protected_tags"
    sections = ["protected_tags"]

    @cachedproperty
    def users_id(self):
        users = [
            x.id
            for x in self.item.users.list(get_all=True, retry_transient_errors=True, iterator=True)
        ]
        return list(set(users))

    @cachedproperty
    def keep_existing(self):
        return self.rule.get("keep_existing_protected_tags", False)

    def _apply(self):
        if self.changes:
            protected_tags = self.changes[0]
            try:
                self._save_properties(
                    PropertyManager(self.item.protectedtags),
                    protected_tags,
                    protected_tags.after,
                )
            except gl_exceptions.GitlabCreateError as e:
                if e.response_code == 422:
                    raise GpcPermissionError(
                        "Are you sure yours users are members"
                        f" of the project {self.item_path} ?\nError: {str(e)}"
                    ) from e
        if self.errors:
            error_message = ""
            error_users = []
            for error in self.errors:
                error_users.append(error.get("user"))
                execption = error.get("exception")
                error_message += f"{execption}\n"
            raise GpcProtectedTagsError(f"ERROR with users {error_users}:\n {error_message}")

    def _update(self, mode: RunMode, members_user, _):
        if "protected_tags" in self.rule and self.rule.protected_tags is not None:
            protected_tags = []

            for protected_tag in self.rule.protected_tags:
                protected_tags.append(self._to_protected_tag(protected_tag, members_user))
            old_protected_tags = ProtectedTag.to_protected_tags(
                self.gitlab,
                self.item.protectedtags.list(  # type: ignore
                    iterator=True, retry_transient_errors=True
                ),
            )
            self.changes.append(
                ChangeProtectedTag(
                    property_name="protected_tags",
                    before=sorted(old_protected_tags, key=lambda x: x.name),
                    after=sorted(protected_tags, key=lambda x: x.name),
                    show_diff_only=self.show_diff_only,
                    keep_existing=self.keep_existing,
                    errors=self.errors,
                )
            )

    def _to_protected_tag(self, protected_tag, future_members_user):
        allowed_to_create = self.init_protected_refs_auth(
            protected_tag.allowed_to_create,
            future_members_user,
            CREATE_PERMISSION,
        )

        params = {"name": protected_tag.pattern, "allowed_to_create": allowed_to_create}

        protected_tag = ProtectedTag(**params)
        return protected_tag

    def init_protected_refs_auth(self, protected_tag_config, future_members_user, permission_type):
        if isinstance(protected_tag_config, str):
            return ProtectedTagRefsAuth(
                role=ProtectedTagRefUser(
                    self._get_role_id(protected_tag_config), protected_tag_config
                )
            )
        users = []
        role = None
        if "role" in protected_tag_config:
            role = ProtectedTagRefUser(
                self._get_role_id(protected_tag_config.role),
                protected_tag_config.role,
            )
        if "users" in protected_tag_config:
            self._init_users(protected_tag_config.users, users, permission_type)
            users = self._check_users(users, future_members_user, permission_type)
        return ProtectedTagRefsAuth(role=role, users=users)

    def _init_users(self, users, gpc_users, permission_type):
        for user_name in users:
            try:
                user = self._find_member(user_name)
            except GpcUserError as e:
                self.errors.append(
                    {"user": user_name, "exception": str(e), "permission_type": permission_type}
                )
                continue

            if isinstance(user, GPCUser):
                gpc_users.append(ProtectedTagRefUser(user.gl_id, user_name))
            else:
                raise GpcUserError(
                    f"User {user_name} should be an instance of GPCUser, "
                    "but is actually a {type(user)}"
                )

    def _check_users(self, users, future_members_users, permission_type):
        expanded_users = users
        unauthorized_users = self._get_unauthorized_users(expanded_users, future_members_users)

        if unauthorized_users:
            error_msg = (
                f"Impossible to configure protected tags on project '{self.item_path}' "
                f"because these users defined {','.join(unauthorized_users)}"
                " are not members of project"
            )
            self.errors.append(
                {
                    "user": ",".join(unauthorized_users),
                    "exception": error_msg,
                    "permission_type": permission_type,
                }
            )

            def filter_func(user):
                return ProtectedTagSettingExecutor.filter_unauthorized(user, unauthorized_users)

            expanded_users = list(filter(filter_func, expanded_users))
        return expanded_users

    @staticmethod
    def filter_unauthorized(user, unauthorized_users):
        return user.name not in unauthorized_users

    def _get_unauthorized_users(self, users, future_members_user):
        users_id = self.users_id + future_members_user
        unauthorized_users = []
        for user in users:
            if user.user_id not in users_id:
                if not bool(self.item.users.list(search=user.name)):
                    unauthorized_users.append(user.name)
        return unauthorized_users
