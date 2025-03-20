# Third Party Libraries
import pytest

from dictns import Namespace

# Gitlab-Project-Configurator Modules
from gpc.executors.project_setting_executor import DefaultBranchUpdator


@pytest.mark.parametrize(
    "force_create_default_branch, ",
    [True, False],
)
@pytest.mark.parametrize(
    "ignore_inexistant_branch, ",
    [True, False],
)
def test_branch_treatment(mocker, force_create_default_branch, ignore_inexistant_branch):
    rule = Namespace(
        {
            "default_branch": "branch",
            "force_create_default_branch": force_create_default_branch,
            "ignore_inexistant_branch": ignore_inexistant_branch,
        }
    )
    mock_create_default_branch = mocker.Mock(return_value=True)
    mock_exist_branch = mocker.Mock(return_value=True)
    DefaultBranch = DefaultBranchUpdator(
        item=mocker.Mock(),
        rule=rule,
        show_diff_only=False,
    )
    DefaultBranch.create_default_branch = mock_create_default_branch
    DefaultBranch.exist_branch = mock_exist_branch
    DefaultBranch.update()
    if force_create_default_branch:
        assert DefaultBranch.create_default_branch.called
        assert not DefaultBranch.exist_branch.called
    else:
        assert not DefaultBranch.create_default_branch.called
        assert DefaultBranch.exist_branch.call_count == (2 if ignore_inexistant_branch else 1)

    # Setting the name to None to disable the default branch's overwrite
    rule_bis = Namespace(
        {"default_branch": None, "force_create_default_branch": force_create_default_branch}
    )
    mock_create_default_branch = mocker.Mock(return_value=True)
    mock_exist_branch = mocker.Mock(return_value=True)
    DefaultBranch_none = DefaultBranchUpdator(
        item=mocker.Mock(),
        rule=rule_bis,
        show_diff_only=False,
    )
    DefaultBranch_none.create_default_branch = mock_create_default_branch
    DefaultBranch_none.exist_branch = mock_exist_branch
    DefaultBranch_none.update()
    assert not DefaultBranch_none.exist_branch.called
