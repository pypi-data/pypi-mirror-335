"""
Make the update of default branch, visibility, merge method and merge restriction.
"""

# Standard Library
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import List
from typing import Optional
from typing import Union

# Third Party Libraries
import attr
import click

from boltons.cacheutils import cachedproperty
from gitlab.exceptions import GitlabUpdateError
from gitlab.v4.objects import Group

# Gitlab-Project-Configurator Modules
from gpc.change_setting import ChangeSetting
from gpc.executors.change_executor import ChangeExecutor
from gpc.helpers.exceptions import GpcPermissionError
from gpc.helpers.gitlab_helper import VISIBILITY_VALUES
from gpc.parameters import GpcParameters
from gpc.parameters import RunMode


if TYPE_CHECKING:
    # Third Party Libraries
    from gitlab.v4.objects import Project

    # Gitlab-Project-Configurator Modules
    from gpc.helpers.types import Rule


class BaseSettingExecutor(ChangeExecutor, ABC):
    applicable_to = []  # type: List[str]
    order = 10
    name = "global_settings"
    sections = []  # type: List[str]

    @cachedproperty
    @abstractmethod
    def updators(self):
        raise NotImplementedError

    def _apply(self):
        if self.changes:
            try:
                self.item.save(retry_transient_errors=True)
            except GitlabUpdateError as e:
                if e.response_code == 403:
                    item_type = "group" if isinstance(self.item, Group) else "project"
                    error_message = (
                        f"On {item_type} {self.item_path}: Access forbidden.\n"
                        "To update the permission, your Gitlab token should"
                        f" be administrator of the {item_type}."
                    )
                    raise GpcPermissionError(error_message) from e
                raise

    def _update(self, mode: RunMode, members_user, members_group):
        """Update settings."""
        for updator in self.updators:
            change_setting = updator.update()
            if updator.error:
                self.warnings.append(updator.error)
            if change_setting:
                self.changes.append(change_setting)


@attr.s
class ClusterSetting(ChangeSetting):
    change_settings = attr.ib(default=None)  # type: List[ChangeSetting]

    def to_dict(self):
        before = {}
        after = {}
        differences = {"before": before, "after": after, "action": self.action}
        result = {"property_name": self.property_name, "differences": differences}
        for change_setting in self.change_settings:
            before[change_setting.property_name] = change_setting.before
            after[change_setting.property_name] = change_setting.after
        return result

    def rich_rows(self, console):
        table_rows = []
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

        for k, _ in enumerate(self.change_settings):
            table_rows.append(
                (
                    (
                        self.wrap_text(
                            self.change_settings[k].property_name, console, "property_name"
                        ),
                        self.wrap_text(str(self.change_settings[k].before), console, "before"),
                        self.wrap_text(str(self.change_settings[k].after), console, "after"),
                        self.change_settings[k].action,
                    ),
                    self.get_line_color(self.change_settings[k].action),
                )
            )
        table_rows.append("new_section")
        return table_rows

    @cachedproperty
    def action(self):
        for change_setting in self.change_settings:
            if change_setting.action != "kept":
                return "updated"
        return "kept"


class LocalUpdator(ABC):
    def __init__(
        self,
        item: Union["Project", Group],
        rule: "Rule",
        show_diff_only: bool,
        sub_level: int = 0,
        params: Optional[GpcParameters] = None,
    ):
        self.item = item
        self.rule = rule
        self.show_diff_only = show_diff_only
        self.sub_level = sub_level
        self.success = True
        self.error = ""
        self.params = params

    @abstractmethod
    def update(self):
        raise NotImplementedError()


class ClusterUpdator(LocalUpdator):
    def __init__(
        self,
        property_name: str,
        cluster_setting_updators: List,
        item: Union["Project", Group],
        rule: "Rule",
        show_diff_only: bool,
        sub_level: int = 0,
        params: Optional[GpcParameters] = None,
    ):
        super().__init__(item, rule, show_diff_only, sub_level)
        self.property_name = property_name
        self.cluster_setting_updators = cluster_setting_updators
        self.params = params

    def update(self):
        change_settings = []
        for updator_class in self.cluster_setting_updators:
            updator = updator_class(
                item=self.item,
                rule=self.rule,
                show_diff_only=self.show_diff_only,
                sub_level=1,
                params=self.params,
            )
            change_setting = updator.update()
            if change_setting:
                change_settings.append(change_setting)
        if change_settings:
            return ClusterSetting(
                property_name=self.property_name,
                before=None,
                after=None,
                show_diff_only=self.show_diff_only,
                change_settings=change_settings,
            )
        return None


class PermissionsUpdator(LocalUpdator):
    permission_rule_name = None  # type: str

    def update(self):
        if "permissions" in self.rule and self.permission_rule_name in self.rule.permissions:
            self.filter_value(getattr(self.rule.permissions, self.permission_rule_name))
            change_setting = ChangeSetting(
                property_name=self.permission_rule_name,
                before=getattr(self.item, self.permission_rule_name),
                after=getattr(self.rule.permissions, self.permission_rule_name),
                show_diff_only=self.show_diff_only,
                sub_level=self.sub_level,
            )
            setattr(
                self.item,
                self.permission_rule_name,
                getattr(self.rule.permissions, self.permission_rule_name),
            )
            return change_setting
        return None

    def filter_value(self, _value):
        pass


class VisibilityUpdator(PermissionsUpdator):
    permission_rule_name = "visibility"

    def filter_value(self, value):
        if value not in VISIBILITY_VALUES:
            raise ValueError(
                f"the visibility value '{value}' is not acceptable, "
                f"the value should be in : {VISIBILITY_VALUES}."
            )

    def update(self):
        if "permissions" in self.rule and self.permission_rule_name in self.rule.permissions:
            self.filter_value(getattr(self.rule.permissions, self.permission_rule_name))
            change_setting = ChangeSetting(
                property_name=self.permission_rule_name,
                before=getattr(self.item, self.permission_rule_name),
                after=getattr(self.rule.permissions, self.permission_rule_name),
                show_diff_only=self.show_diff_only,
                sub_level=self.sub_level,
            )
            if (
                change_setting.before in ["internal", "private"]
                and change_setting.after == "public"
            ):
                change_setting.action = "error"
                item_type = "group" if isinstance(self.item, Group) else "project"
                click.secho(
                    "Access forbidden."
                    f" To update the permission on this {item_type}, your Gitlab token should"
                    f" be administrator of the {item_type}.",
                    fg="red",
                )
            setattr(
                self.item,
                self.permission_rule_name,
                getattr(self.rule.permissions, self.permission_rule_name),
            )
            return change_setting
        return None
