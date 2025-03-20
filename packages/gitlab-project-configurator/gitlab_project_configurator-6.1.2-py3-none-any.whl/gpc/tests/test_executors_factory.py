"""
Test executor factory.
"""

# Gitlab-Project-Configurator Modules
# Gitlab-Project-Configurator Modules# Gitlab-Project-Configurator Modules
from gpc.change_executors_factory import ChangeExecutorsFactory


# pylint: disable=redefined-outer-name, unused-argument, protected-access

EXECUTOR_CLASS_NAME = [
    "ProtectedTagSettingExecutor",
    "LabelSettingExecutor",
    "ProjectSettingExecutor",
    "GroupSettingExecutor",
    "ProtectedBranchSettingExecutor",
    "VariablesSettingExecutor",
    "ProjectBadgeExecutor",
    "ApprovalSettingExecutor",
    "JiraSettingExecutor",
    "PipelinesEmailSettingExecutor",
    "PushRulesSettingExecutor",
    "MembersProjectExecutor",
    "RunnersSettingExecutor",
    "SchedulersSettingExecutor",
    "DeployKeysExecutor",
    "MergeRequestApprovalSettingExecutor",
    "ApprovalRulesExecutor",
]


def test_factory():
    factory = ChangeExecutorsFactory()
    lst_class = factory.executors
    classes_name = [executor.__name__ for executor in lst_class]
    assert len(lst_class) == len(EXECUTOR_CLASS_NAME)
    # We compare the name to no import the class before the use of factory.
    # To test the dynamic import in factory class
    assert not set(classes_name) - set(EXECUTOR_CLASS_NAME)
