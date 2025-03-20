# Third Party Libraries
from gitlab.exceptions import GitlabCreateError
from gitlab.v4.objects import Project


class ProjectApprovalSettings:
    """Wrapper class to manage project approval global configuration.

    https://docs.gitlab.com/ee/api/merge_request_approvals.html#get-configuration

    /projects/:id/approvals: manage globals configuration.
    """

    def __init__(self, project: Project):
        self._approvals_manager = project.approvals.get(retry_transient_errors=True)

    @property
    def reset_approvals_on_push(self):
        return self._approvals_manager.reset_approvals_on_push

    @reset_approvals_on_push.setter
    def reset_approvals_on_push(self, value):
        self._approvals_manager.reset_approvals_on_push = value

    @property
    def disable_overriding_approvers_per_merge_request(self):
        return self._approvals_manager.disable_overriding_approvers_per_merge_request

    @disable_overriding_approvers_per_merge_request.setter
    def disable_overriding_approvers_per_merge_request(self, value):
        self._approvals_manager.disable_overriding_approvers_per_merge_request = value

    @property
    def merge_requests_author_approval(self):
        return self._approvals_manager.merge_requests_author_approval

    @merge_requests_author_approval.setter
    def merge_requests_author_approval(self, value):
        self._approvals_manager.merge_requests_author_approval = value

    @property
    def enable_committers_approvers(self):
        return not self._approvals_manager.merge_requests_disable_committers_approval

    @enable_committers_approvers.setter
    def enable_committers_approvers(self, value):
        self._approvals_manager.merge_requests_disable_committers_approval = not value

    @property
    def selective_code_owner_removals(self):
        return self._approvals_manager.selective_code_owner_removals

    @selective_code_owner_removals.setter
    def selective_code_owner_removals(self, value):
        self._approvals_manager.selective_code_owner_removals = value

    @property
    def merge_requests_disable_committers_approval(self):
        return self._approvals_manager.merge_requests_disable_committers_approval

    @merge_requests_disable_committers_approval.setter
    def merge_requests_disable_committers_approval(self, value):
        self._approvals_manager.merge_requests_disable_committers_approval = value

    def save(self):
        self._approvals_manager.save(retry_transient_errors=True)


class ProjectApprovalRules:
    """
    Wrapper class to manage project approval rules.

    https://docs.gitlab.com/ee/api/merge_request_approvals.html#get-configuration

    /projects/:id/approval_rules: allow to create rules to define list
    of users and groups which will act as approvers
    """

    def __init__(self, project: Project):
        self._approvalrules_manager = project.approvalrules

    def approval_rule(self, rule_id=-1):
        approval_rules = self.approval_rules_list or [None]
        if rule_id != -1:
            approvalrule = [rule for rule in approval_rules if rule.attributes["id"] == rule_id][0]
        else:
            approvalrule = approval_rules[0]
        return approvalrule

    @property
    def approval_rules_list(self):
        return self._approvalrules_manager.list(
            all=True, iterator=False, retry_transient_errors=True
        )

    @property
    def rule_names(self):
        return [rule.attributes["name"] for rule in self.approval_rules_list]

    @property
    def approver_groups(self):
        if self.approval_rule():
            return self.approval_rule().groups
        return []

    @property
    def approver_groups_per_rule(self):
        groups = {}
        for rule in self.approval_rules_list:
            groups[rule.attributes["name"]] = rule.groups
        return groups

    def approvers(self, rule_id=-1):
        if self.approval_rule():
            return self.approval_rule(rule_id).users
        return []

    @property
    def approvers_per_rule(self):
        approvers = {}
        for rule in self.approval_rules_list:
            approvers[rule.attributes["name"]] = rule.users
        return approvers

    @property
    def approvals_before_merge(self):
        if self.approval_rule():
            return self.approval_rule().approvals_required
        return 0

    @property
    def approvals_before_merge_per_rule(self):
        approvals_before_merge = {}
        for rule in self.approval_rules_list:
            approvals_before_merge[rule.attributes["name"]] = rule.approvals_required or 0
        return approvals_before_merge

    @property
    def protected_branches_per_rule(self):
        pb = {}
        for rule in self.approval_rules_list:
            pb[rule.attributes["name"]] = [
                branch["name"] for branch in rule.attributes["protected_branches"]
            ]
        return pb

    @property
    def ids_per_rule(self):
        ids = {}
        for rule in self.approval_rules_list:
            ids[rule.attributes["name"]] = rule.id
        return ids

    def set_approvers(  # noqa: C901
        self,
        name="Default",
        approver_ids=None,
        approver_group_ids=None,
        approvals_required=0,
        protected_branches=None,
        premium=False,
    ):
        result = {}
        config = {
            "name": name,
            "approvals_required": approvals_required,
        }
        if approver_ids:
            config["user_ids"] = approver_ids
        if approver_group_ids:
            config["group_ids"] = approver_group_ids

        if protected_branches:
            config["protected_branch_ids"] = protected_branches
        # Due to issue in approval rules API
        # https://gitlab.com/gitlab-org/gitlab/-/issues/211665
        # Approval rules is not correctly updated when users/groups are empty
        # To be sure that it is updated we delete the current one and recreate a new one
        # self._approvalrules_manager.delete(self.approval_rules.id, retry_transient_errors=True)
        if not premium and self.approval_rule():
            self._approvalrules_manager.delete(self.approval_rule().id, retry_transient_errors=True)
        else:
            if config["name"] == "License-Check":
                config["report_type"] = "license_scanning"
                config["rule_type"] = "report_approver"
            if config["name"] == "Coverage-Check":
                config["report_type"] = "code_coverage"
                config["rule_type"] = "report_approver"
        try:
            api_return = self._approvalrules_manager.create(config, retry_transient_errors=True)
            result = api_return.attributes
        except GitlabCreateError as e:
            if e.response_code == 400:
                result = self._approvalrules_manager.update(
                    id=self.ids_per_rule[name], new_data=config, retry_transient_errors=True
                )
        return result


class ProjectApproval(ProjectApprovalSettings, ProjectApprovalRules):
    def __init__(self, project: Project):
        ProjectApprovalSettings.__init__(self, project)
        ProjectApprovalRules.__init__(self, project)
