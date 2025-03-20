"""
Make the approval rules for Gitlab Premium.
"""

# Standard Library
from typing import List

# Third Party Libraries
import attr
import click

from boltons.cacheutils import cachedproperty
from structlog import get_logger

# Gitlab-Project-Configurator Modules
from gpc.executors.approvers_mixin import ApproverExecutorMixin
from gpc.executors.approvers_mixin import ApproverGroup
from gpc.executors.approvers_mixin import ApproverUser
from gpc.executors.approvers_mixin import ProjectApproversBean
from gpc.executors.properties_updator import ChangePropertyExecutor
from gpc.helpers.project_approval import ProjectApprovalRules
from gpc.parameters import RunMode


log = get_logger()


@attr.s
class ProjectApproversRules(ProjectApproversBean):
    protected_branches = attr.ib(factory=list)  # type: List

    @staticmethod
    def to_project_approvers(api_approvers, rule_name):
        project_approvers = ProjectApproversRules()
        if rule_name in api_approvers.rule_names:
            project_approvers.name = rule_name
            project_approvers.protected_branches = api_approvers.protected_branches_per_rule.get(
                rule_name, []
            )
            project_approvers.approvals_before_merge = (
                api_approvers.approvals_before_merge_per_rule.get(rule_name, 0)
            )
            groups = {}
            if api_approvers.approver_groups_per_rule.get(rule_name):
                for group in api_approvers.approver_groups_per_rule.get(rule_name):
                    group_id = group.get("id")
                    group_name = group.get("name")
                    full_path = group.get("full_path")
                    groups[group_id] = ApproverGroup(group_id, group_name, full_path)
            project_approvers.groups = groups
            users = {}

            if api_approvers.approvers_per_rule.get(rule_name):
                for user in api_approvers.approvers_per_rule.get(rule_name):
                    user_id = user.get("id")
                    user_name = user.get("username")
                    users[user_id] = ApproverUser(user_id, user_name)
            project_approvers.users = users
        return project_approvers

    def get_query(self):
        pass

    def to_dict(self):
        dict_variable = super().to_dict()
        dict_variable["protected_branches"] = self.protected_branches
        return dict_variable

    @property
    def is_empty(self):
        return (
            not self.approvals_before_merge
            and not self.groups
            and not self.name
            and not self.protected_branches
            and not self.remove_members
            and not self.users
        )


class ApprovalRulesExecutor(ChangePropertyExecutor, ApproverExecutorMixin):
    order = 55
    name = "approval_rules"
    sections = ["approval_rules"]
    section_name = "approval_rules"

    def _apply(self):  # noqa: C901
        if not self.changes:
            return
        # We delete the rules that are not in common_policies.yml
        project_rules = self.item.approvalrules.list(all=True)
        conf_rules = [rule["name"] for rule in self.rule.approval_rules]
        for rule in project_rules:
            if rule.attributes["name"] not in conf_rules:
                self.item.approvalrules.delete(
                    id=rule.attributes["id"], retry_transient_errors=True
                )

        user_errors = []
        for change in self.changes:
            if change.action == "kept":
                continue

            approvals_rule = change
            manager = ProjectApprovalRules(self.item)
            approvers_to_change = approvals_rule.after  # type: ProjectApproversRules
            protected_branches = self.compute_branches(approvers_to_change.protected_branches)

            if not protected_branches and approvers_to_change.protected_branches:
                # If all the given protected branches are invalid (absent from Gitlab) we won't
                # create an approval rule
                warning = (
                    f'Approval rule "{approvers_to_change.name}" was not applied because none '
                    "of the given protected branches were present in Gitlab"
                )
                click.secho(warning, fg="yellow")
                continue
            if len(protected_branches) < len(approvers_to_change.protected_branches):
                # If some protected branches are invalid, we create an approval rule
                # just for the valid ones
                warning = (
                    f'Approval rule "{approvers_to_change.name}" partially applied '
                    "(some of the given protected branches were not present on your project)"
                )
                click.secho(warning, fg="yellow")

            query = {
                "approvals_required": approvers_to_change.approvals_before_merge,
                "name": approvers_to_change.name,
                "premium": True,
            }

            if protected_branches:
                query["protected_branches"] = protected_branches

            user_errors += self._apply_members(manager, approvers_to_change, query)
        self._approver_raise_user_errors(user_errors)

    @cachedproperty
    def project_approval(self):
        return ProjectApprovalRules(self.item)  # type: ignore

    def _update(self, mode: RunMode, members_user, members_group):
        if "approval_rules" not in self.rule or self.rule.approval_rules is None:
            return
        for rule in self.rule.approval_rules:
            self._add_change_approvers(rule)

    def get_old_approvers(self, rule_name=""):
        return ProjectApproversRules.to_project_approvers(self.project_approval, rule_name)

    def get_approvers_bean(self, old_approvers, approvers):
        project_approvers = ProjectApproversRules()
        project_approvers.name = approvers.name
        project_approvers.protected_branches = approvers.get("protected_branches", [])

        project_approvers.approvals_before_merge = approvers.get(
            "minimum", old_approvers.approvals_before_merge
        )
        return project_approvers

    def compute_branches(self, protected_branches):
        """Compute protected branches ids.

        This function will keep protected branches ids if given and transform an existing
        branch name into an id if a string is given

        Returns
        -------
        Protected branches ids for the merge request approval rule we want to create
        """

        pb = []
        if not protected_branches:
            return pb
        remote_pbs = self.item.protectedbranches.list(
            iterator=False, all=True, retry_transient_errors=True
        )
        for branch in protected_branches:
            if isinstance(branch, int):
                pb.append(branch)
            if isinstance(branch, str):
                is_warning = True
                for b in remote_pbs:
                    if b.attributes["name"] == branch:
                        is_warning = False
                        pb.append(b.attributes["id"])
                        break
                if is_warning:
                    warning = (
                        f"{branch} is not a protected branch of {self.item.path_with_namespace},"
                        " please make sure to add it to your GPC schema or to your project"
                    )
                    click.secho(warning, fg="yellow")
        return pb
