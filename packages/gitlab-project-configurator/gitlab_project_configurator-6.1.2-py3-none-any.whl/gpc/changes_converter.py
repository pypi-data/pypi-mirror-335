"""
Classes which convert the differences of a ProjectRuleExecutor to a RowPropertyBean.

"""

# Standard Library
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from typing import List  # pylint: disable=unused-import
from typing import Optional  # pylint: disable=unused-import
from typing import Union  # pylint: disable=unused-import

# Third Party Libraries
from sortedcontainers import SortedList

# Gitlab-Project-Configurator Modules
from gpc.executors.project_setting_executor import ProjectSettingExecutor


class ConverterFactory:
    @staticmethod
    def init_converter(property_name, changes):
        if property_name in ["jira", "pipelines_email"]:
            return RowConverterFieldSubLevel(changes, property_name)
        if property_name in ProjectSettingExecutor.project_properties:
            return RowProjectPropConverter(changes, property_name)
        if (
            changes.get("differences", {}).get("after") is not None
            or changes.get("differences", {}).get("before") is not None
        ):
            return RowConverter(changes, property_name)
        return RowConverterSubLevel(changes, property_name)


@dataclass
class PropertyBean:
    name: str
    # We do default_factory=lambda: SortedList(key=lambda x: x.name)
    # Because default_factory must be a zero-argument callable.
    # And we need to instantiate a SortedList, with the key of sort.
    before: SortedList = dataclass_field(default_factory=lambda: SortedList(key=lambda x: x.name))
    after: SortedList = dataclass_field(default_factory=lambda: SortedList(key=lambda x: x.name))

    def __str__(self):
        return self.name


@dataclass
class FieldBean(PropertyBean):
    value: Optional[Union[List, str]] = dataclass_field(default=None)

    def __str__(self):
        return super().__str__() + f": {self.value}"


class RowConverter:
    def __init__(self, changes, property_name) -> None:
        self.changes = changes
        self.property_name = property_name

    def execute(self):
        change_bean = PropertyBean(self.property_name)
        self.changes_to_list(self.changes.differences, change_bean)
        return change_bean

    def changes_to_list(self, differences, parent):
        before = differences.before
        after = differences.after
        self.to_diff_beans(before, after, parent)

    def to_diff_beans(self, before, after, parent):
        fields_used = []
        if before:
            for field, value in before.items():
                fields_used.append(field)
                self.diff_before_after(after, field, parent, value)
        if after:
            for field, value in after.items():
                self.diff_after(field, fields_used, parent, value)

    @staticmethod
    def diff_after(field, fields_used, parent, value):
        if field != "name" and field not in fields_used:
            parent.after.add(FieldBean(field, value=value))

    def diff_before_after(self, after, field, parent, value):
        if field != "name" and after and not self.eq_values(after.get(field), value):
            parent.before.add(FieldBean(field, value=value))
            parent.after.add(FieldBean(field, value=after.get(field)))

    @staticmethod
    def eq_values(val1, val2):
        if not isinstance(val1, type(val2)):
            return False
        if isinstance(val1, list):
            return sorted(val1) == sorted(val2)
        return val1 == val2


class RowProjectPropConverter(RowConverter):
    def to_diff_beans(self, before, after, parent):
        if before:
            parent.before = [before]
        if after:
            parent.after = [after]


class RowConverterSubLevel(RowConverter):
    def execute(self):
        change_bean = PropertyBean(self.property_name)
        if self.changes.differences:
            for sub_parameter, sub_changes in self.changes.differences.items():
                self.sub_changes_to_list(sub_parameter, sub_changes, change_bean)
        return change_bean

    def sub_changes_to_list(self, property_name, differences, parent):
        if differences.status == "removed":
            parent.before.add(PropertyBean(property_name))
        elif differences.status == "added":
            child = PropertyBean(property_name)
            parent.after.add(child)
        elif differences.status == "updated":
            child_after = PropertyBean(property_name)
            child_before = PropertyBean(property_name)
            parent.after.add(child_after)
            parent.before.add(child_before)


class RowConverterFieldSubLevel(RowConverterSubLevel):
    def sub_changes_to_list(self, property_name, differences, parent):
        if differences.action == "removed":
            RowConverterFieldSubLevel.add_field(parent.before, differences.before)
        elif differences.action == "added":
            RowConverterFieldSubLevel.add_field(parent.after, differences.after)
        elif differences.action == "updated":
            RowConverterFieldSubLevel.add_field(parent.after, differences.after)
            RowConverterFieldSubLevel.add_field(parent.before, differences.before)

    @staticmethod
    def add_field(fields_list, ns_props):
        for key, value in ns_props.items():
            # ignore the 'name' key as it shall be the name of the property
            if key == "name":
                continue
            fields_list.add(FieldBean(name=key, value=value))
