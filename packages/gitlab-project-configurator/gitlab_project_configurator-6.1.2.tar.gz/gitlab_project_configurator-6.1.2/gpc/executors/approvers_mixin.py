# Standard Library
from abc import ABC
from abc import abstractmethod

# Third Party Libraries
import attr

from boltons.cacheutils import cachedproperty
from dictns import Namespace
from structlog import get_logger

# Gitlab-Project-Configurator Modules
from gpc.change_setting import ChangeSettingSubProperty
from gpc.executors.profile_member_mixin import GPCUser
from gpc.executors.profile_member_mixin import ProfileMemberMixin
from gpc.helpers.exceptions import GpcMemberError
from gpc.property_manager import PropertyBean


log = get_logger()


@attr.s
class ProjectApproversBean(PropertyBean, ABC):
    name = attr.ib(default="")  # type: str
    users = attr.ib(default=None)  # type: dict
    groups = attr.ib(default=None)  # type: dict
    approvals_before_merge = attr.ib(default=0)  # type: int

    @property
    def remove_members(self):
        return (
            self.users is not None
            and self.groups is not None
            and (len(self.users) + len(self.groups)) == 0
        )

    def to_dict(self):
        dict_variable = {
            "name": self.name,
            "approvals_before_merge": self.approvals_before_merge,
        }
        if self.users:
            dict_variable["users"] = [user.name for user in self.users.values()]
        if self.groups:
            dict_variable["groups"] = [group.full_path for group in self.groups.values()]
        return dict_variable

    def get_user_ids(self):
        if self.users:
            return list(self.users.keys())
        return None

    def get_group_ids(self):
        if self.groups:
            return list(self.groups.keys())
        return None

    @property
    def is_empty(self):
        return False


class OptionApproversMixin:
    @property
    def disable_overriding_approvers_per_merge_request(self):
        return not self.can_override_approvals_per_merge_request

    def option_dict(self):
        can_override = self.can_override_approvals_per_merge_request
        dict_variable = {
            "reset_approvals_on_push": self.reset_approvals_on_push,
            "can_override_approvals_per_merge_request": can_override,
            "enable_self_approval": self.enable_self_approval,
            "enable_committers_approvers": self.enable_committers_approvers,
            "selective_code_owner_removals": self.selective_code_owner_removals,
        }
        return dict_variable


@attr.s
class ChangeApprovers(ChangeSettingSubProperty):
    @cachedproperty
    def action(self):
        if self.after and self.before.is_empty:
            return "added"
        return super().action


@attr.s
class ApproverUser:
    user_id = attr.ib()  # type: int
    name = attr.ib()  # type: str

    def __str__(self):
        return self.name


@attr.s
class ApproverGroup:
    group_id = attr.ib()  # type: int
    name = attr.ib()  # type: str
    full_path = attr.ib()  # type: str

    def __str__(self):
        return self.full_path


class ApproverExecutorMixin(ProfileMemberMixin):
    def _prepare_approvers(self, ns_approvers: Namespace) -> Namespace:
        approvers = ns_approvers.copy()
        if "profiles" in approvers:
            merged_profiles = self.get_merged_profiles(approvers.get("profiles"))
            members = approvers.get("members", [])
            approvers["members"] = list(set(merged_profiles + members))
            del approvers["profiles"]
        return Namespace(approvers)

    def _update_approvers(self, name, users_approver, groups_approver):
        member = self._find_member(name)
        if isinstance(member, GPCUser):
            users_approver[member.gl_id] = ApproverUser(member.gl_id, name)
        else:
            # GPCGroup
            groups_approver[member.gl_id] = ApproverGroup(
                member.gl_id, member.name, member.full_path
            )

    def _apply_members(self, manager, approvers_to_change, query):
        user_errors = []
        if not approvers_to_change.remove_members:
            if approvers_to_change.users:
                query["approver_ids"] = approvers_to_change.get_user_ids()
            if approvers_to_change.groups:
                query["approver_group_ids"] = approvers_to_change.get_group_ids()

        api_return = manager.set_approvers(**query)
        rule_id = api_return["id"]
        if approvers_to_change.users:
            user_errors += self._check_approvers(approvers_to_change, manager, rule_id)
        return user_errors

    def _add_change_approvers(self, rule):
        old_approvers = self.get_old_approvers(rule.get("name", ""))
        approvers = self._prepare_approvers(rule)
        project_approvers = self.to_project_approvers(old_approvers, approvers)
        self.changes.append(
            ChangeApprovers(
                self.section_name, old_approvers, project_approvers, self.show_diff_only
            )
        )

    def _check_approvers(self, approvers_to_change, manager, rule_id=-1):
        users = approvers_to_change.users
        remote_approvers = [a["id"] for a in manager.approvers(rule_id)]
        users_error = list(set(users) - set(remote_approvers))
        user_errors = [approvers_to_change.users[user_id].name for user_id in users_error]
        return user_errors

    def _approver_raise_user_errors(self, user_errors=None):
        if user_errors:
            raise GpcMemberError(
                f"For the project '{self.item_path}', "
                f"these users can not be added as "
                f"approvers: {', '.join(user_errors)}.\n"
                f"Please check that these users are members "
                f"of the project, or the parent project."
            )

    @abstractmethod
    def get_old_approvers(self, rule_name=""):
        raise NotImplementedError()

    @abstractmethod
    def get_approvers_bean(self, old_approvers, approvers):
        raise NotImplementedError()

    @cachedproperty
    @abstractmethod
    def project_approval(self):
        raise NotImplementedError()

    def to_project_approvers(self, old_approvers, approvers):
        # If field is None in config, we set the value of current config.
        # To display we keep the value
        project_approvers = self.get_approvers_bean(old_approvers, approvers)
        if approvers.get("members") is not None:
            users = {}
            groups = {}
            for member_name in approvers.get("members"):
                self._update_approvers(member_name, users, groups)
            project_approvers.users = users
            project_approvers.groups = groups
        else:
            project_approvers.users = old_approvers.users
            project_approvers.groups = old_approvers.groups
        return project_approvers
