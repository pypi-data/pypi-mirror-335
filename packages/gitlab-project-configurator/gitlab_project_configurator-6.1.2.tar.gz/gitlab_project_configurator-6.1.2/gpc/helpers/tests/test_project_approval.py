# Gitlab-Project-Configurator Modules
from gpc.helpers.project_approval import ProjectApproval


def test_project_approval(mocker):
    project = mocker.Mock()
    approval_config = mocker.Mock()
    approval_config.reset_approvals_on_push = True
    approval_config.selective_code_owner_removals = False
    approval_config.disable_overriding_approvers_per_merge_request = True
    approval_config.merge_requests_author_approval = True
    approval_config.merge_requests_disable_committers_approval = True
    approval_config.save = mocker.Mock()
    approvals = mocker.Mock()
    approvals.get = mocker.Mock(return_value=approval_config)

    approvalrules_config = mocker.Mock()
    approvalrules_config.users = [123, 456]
    approvalrules_config.groups = [789]
    approvalrules_config.approvals_required = 2

    approvalrules = mocker.Mock()
    approvalrules.list = mocker.Mock(return_value=[approvalrules_config])
    approvalrules.delete = mocker.Mock()
    approvalrules.create = mocker.Mock()

    project.approvals = approvals
    project.approvalrules = approvalrules
    pa = ProjectApproval(project)
    pa.save()
    pa.set_approvers()

    assert pa.reset_approvals_on_push
    assert not pa.selective_code_owner_removals
    assert pa.disable_overriding_approvers_per_merge_request
    assert pa.merge_requests_author_approval
    assert pa.merge_requests_disable_committers_approval
    assert pa.approvals_before_merge == 2
    assert pa.approvers() == [123, 456]
    assert pa.approver_groups == [789]

    assert approval_config.save.called
    assert approvalrules.delete.called
    assert approvalrules.create.called
