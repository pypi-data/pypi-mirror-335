"""
Make the update of visibility.
"""

# Third Party Libraries
from boltons.cacheutils import cachedproperty
from gitlab.v4.objects import Group

# Gitlab-Project-Configurator Modules
from gpc.executors.base_setting_executor import BaseSettingExecutor
from gpc.executors.base_setting_executor import ClusterUpdator
from gpc.executors.base_setting_executor import VisibilityUpdator
from gpc.helpers.types import GroupRule


class GroupSettingExecutor(BaseSettingExecutor):
    applicable_to = ["group"]
    sections = ["permissions"]

    @cachedproperty
    def updators(self):
        return GroupUpdatorFactory.init_updators(self.item, self.rule, self.show_diff_only)


class GroupUpdatorFactory:
    @staticmethod
    def init_updators(group: Group, rule: GroupRule, show_diff_only: bool):
        updators = [
            ClusterUpdator(
                "permissions",
                [
                    VisibilityUpdator,
                ],
                group,
                rule,
                show_diff_only,
            ),
        ]
        return updators
