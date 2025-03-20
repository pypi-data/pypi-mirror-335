"""
Make the approval setting.
"""

# Third Party Libraries
import attr

from boltons.cacheutils import cachedproperty
from structlog import get_logger

# Gitlab-Project-Configurator Modules
from gpc.executors.approvers_mixin import ApproverExecutorMixin
from gpc.executors.approvers_mixin import ApproverGroup
from gpc.executors.approvers_mixin import ApproverUser
from gpc.executors.approvers_mixin import OptionApproversMixin
from gpc.executors.approvers_mixin import ProjectApproversBean
from gpc.executors.properties_updator import ChangePropertyExecutor
from gpc.helpers.exceptions import GpcImpossibleConf
from gpc.helpers.project_approval import ProjectApproval
from gpc.parameters import RunMode


log = get_logger()


@attr.s
class ProjectApprovers(ProjectApproversBean, OptionApproversMixin):
    reset_approvals_on_push = attr.ib(default=None)  # type: bool
    can_override_approvals_per_merge_request = attr.ib(default=None)  # type: bool
    enable_self_approval = attr.ib(default=None)  # type: bool
    enable_committers_approvers = attr.ib(default=None)  # type: bool
    selective_code_owner_removals = attr.ib(default=None)  # type: bool

    @property
    def disable_overriding_approvers_per_merge_request(self):
        return not self.can_override_approvals_per_merge_request

    @staticmethod
    def to_project_approvers(api_approvers):
        project_approvers = ProjectApprovers(name="approvers")
        project_approvers.approvals_before_merge = api_approvers.approvals_before_merge
        project_approvers.reset_approvals_on_push = api_approvers.reset_approvals_on_push
        project_approvers.enable_self_approval = api_approvers.merge_requests_author_approval
        project_approvers.enable_committers_approvers = api_approvers.enable_committers_approvers
        project_approvers.can_override_approvals_per_merge_request = (
            not api_approvers.disable_overriding_approvers_per_merge_request
        )
        project_approvers.selective_code_owner_removals = (
            api_approvers.selective_code_owner_removals
        )

        groups = {}
        if api_approvers.approver_groups:
            for group in api_approvers.approver_groups:
                group_id = group.get("id")
                name = group.get("name")
                full_path = group.get("full_path")
                groups[group_id] = ApproverGroup(group_id, name, full_path)
        project_approvers.groups = groups
        users = {}
        if api_approvers.approvers():
            for user in api_approvers.approvers():
                user_id = user.get("id")
                name = user.get("username")
                users[user_id] = ApproverUser(user_id, name)
        project_approvers.users = users
        return project_approvers

    def get_query(self):
        pass

    def to_dict(self):
        dict_variable = self.option_dict()
        dict_variable.update(super().to_dict())
        return dict_variable


class ApprovalSettingExecutor(ChangePropertyExecutor, ApproverExecutorMixin):
    order = 60
    name = "approval_settings"
    sections = ["approvers"]
    section_name = "approvers"

    def _apply(self):
        if self.changes:
            approvers = self.changes[0]
            if approvers.action == "kept":
                return
            self.is_problematic_rule()
            manager = ProjectApproval(self.item)
            approvers_to_change = approvers.after  # type: ProjectApprovers
            manager.reset_approvals_on_push = approvers_to_change.reset_approvals_on_push
            manager.merge_requests_author_approval = approvers_to_change.enable_self_approval
            manager.enable_committers_approvers = approvers_to_change.enable_committers_approvers
            manager.disable_overriding_approvers_per_merge_request = (
                approvers_to_change.disable_overriding_approvers_per_merge_request
            )
            if manager.reset_approvals_on_push:
                manager.selective_code_owner_removals = False
            else:
                manager.selective_code_owner_removals = (
                    approvers_to_change.selective_code_owner_removals
                )

            manager.save()
            query = {"approvals_required": approvers_to_change.approvals_before_merge}

            user_errors = self._apply_members(manager, approvers_to_change, query)
            self._approver_raise_user_errors(user_errors)

    @cachedproperty
    def project_approval(self):
        return ProjectApproval(self.item)  # type: ignore

    def _update(self, mode: RunMode, members_user, members_group):
        if "approvers" not in self.rule or self.rule.approvers is None:
            return
        self._add_change_approvers(self.rule.approvers)

    def get_old_approvers(self, rule_name=""):
        return ProjectApprovers.to_project_approvers(self.project_approval)

    def is_problematic_rule(self):
        if "approvers" in self.rule and self.rule.approvers.get("options"):
            rule_options = self.rule.approvers.options
            if (
                "remove_all_approvals_when_new_commits_are_pushed" in rule_options
                and "selective_code_owner_removals" in rule_options
            ):
                if (
                    rule_options.remove_all_approvals_when_new_commits_are_pushed
                    and rule_options.selective_code_owner_removals
                ):
                    raise GpcImpossibleConf(
                        "remove_all_approvals_when_new_commits_are_pushed and"
                        " selective_code_owner_removals can't be enabled at the same time"
                    )

    def get_approvers_bean(self, old_approvers, approvers):
        project_approvers = ProjectApprovers(name="approvers")
        project_approvers.approvals_before_merge = approvers.get(
            "minimum", old_approvers.approvals_before_merge
        )
        ApprovalSettingExecutor.init_options(approvers, project_approvers, old_approvers)
        return project_approvers

    @staticmethod
    def init_options(approvers, project_approvers, old_approvers):
        options = approvers.get("options")
        if options:
            project_approvers.reset_approvals_on_push = options.get(
                "remove_all_approvals_when_new_commits_are_pushed",
                old_approvers.reset_approvals_on_push,
            )
            project_approvers.can_override_approvals_per_merge_request = options.get(
                "can_override_approvals_per_merge_request",
                old_approvers.can_override_approvals_per_merge_request,
            )
            project_approvers.enable_self_approval = options.get(
                "enable_self_approval", old_approvers.enable_self_approval
            )
            project_approvers.enable_committers_approvers = options.get(
                "enable_committers_approvers", old_approvers.enable_committers_approvers
            )
            project_approvers.selective_code_owner_removals = options.get(
                "selective_code_owner_removals", old_approvers.selective_code_owner_removals
            )

        else:
            project_approvers.reset_approvals_on_push = old_approvers.reset_approvals_on_push
            project_approvers.enable_self_approval = old_approvers.enable_self_approval
            project_approvers.enable_committers_approvers = (
                old_approvers.enable_committers_approvers
            )
            project_approvers.can_override_approvals_per_merge_request = (
                old_approvers.can_override_approvals_per_merge_request
            )
            project_approvers.selective_code_owner_removals = (
                old_approvers.selective_code_owner_removals
            )
