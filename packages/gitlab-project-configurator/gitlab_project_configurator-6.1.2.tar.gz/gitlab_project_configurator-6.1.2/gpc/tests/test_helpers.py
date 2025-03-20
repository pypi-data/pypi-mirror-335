"""
Functions used by unit tests
"""

# Gitlab-Project-Configurator Modules
from gpc.executors.base_setting_executor import ClusterSetting
from gpc.project_rule_executor import ProjectRuleExecutor


# pylint: disable=too-many-nested-blocks


def get_change_value(
    project_rule_executor: ProjectRuleExecutor,
    change_property_name,
    sub_prop=None,
):
    for executor in project_rule_executor.executors:
        for change in executor.changes:
            if change.property_name == change_property_name:
                if sub_prop and isinstance(change, ClusterSetting):
                    for change_setting in change.change_settings:
                        if change_setting.property_name == sub_prop:
                            return change_setting
                else:
                    return change
    return None


def get_executor(project_rule_executor: ProjectRuleExecutor, executor_class):
    for executor in project_rule_executor.executors:
        if isinstance(executor, executor_class):
            return executor
    return None
