"""
Make the update of label.
"""

# Standard Library
from typing import Dict  # pylint: disable=unused-import
from typing import Optional  # pylint: disable=unused-import

# Third Party Libraries
import attr

from boltons.cacheutils import cachedproperty
from dictns import Namespace

# Gitlab-Project-Configurator Modules
from gpc.change_setting import ChangePropertySetting
from gpc.executors.properties_updator import ChangePropertyExecutor
from gpc.executors.variables_setting_executor import ChangeVariables
from gpc.executors.variables_setting_executor import ItemVariable
from gpc.executors.variables_setting_executor import VariablesSettingPreparator
from gpc.parameters import RunMode
from gpc.property_manager import PropertyBean


@attr.s(eq=False)
class Scheduler(PropertyBean):
    branch = attr.ib()  # type: bool
    cron = attr.ib()  # type: bool
    enabled = attr.ib()  # type: bool
    tz = attr.ib()  # type: bool
    variables = attr.ib()  # type: Optional[Dict[str, ItemVariable]]
    api_id = attr.ib(default=None)  # type: int

    @staticmethod
    def to_schedulers(api_schedulers, project_api):
        schedulers = []
        for api_scheduler in api_schedulers:
            schedulers.append(
                Scheduler.to_scheduler(
                    project_api.pipelineschedules.get(api_scheduler.id, retry_transient_errors=True)
                )
            )
        return schedulers

    @staticmethod
    def to_scheduler(api_scheduler):
        variables = ItemVariable.to_item_variables(Namespace(api_scheduler.attributes["variables"]))
        dict_variables = {var.name: var for var in variables}
        return Scheduler(
            name=api_scheduler.description,
            branch=api_scheduler.ref,
            api_id=api_scheduler.id,
            cron=api_scheduler.cron,
            enabled=api_scheduler.active,
            tz=api_scheduler.cron_timezone,
            variables=dict_variables,
        )

    def get_query(self):
        return {
            "description": self.name,
            "ref": self.branch,
            "active": self.enabled,
            "cron_timezone": self.tz,
            "cron": self.cron,
        }

    def to_compare(self, as_dict=False):
        return self.to_dict() if as_dict else self.__to_diff()

    def to_dict(self):
        result = self.__to_diff()
        if self.variables:
            result["variables"] = {key: var.to_dict() for key, var in self.variables.items()}
        return result

    def __to_diff(self):
        return {
            "name": self.name,
            "branch": self.branch,
            "cron": self.cron,
            "tz": self.tz,
            "enabled": self.enabled,
            "variables": self.variables,
            "api_id": self.api_id,
        }

    def __eq__(self, other):
        if not isinstance(other, Scheduler):
            return False

        equal_variables = (not bool(self.variables) and not bool(other.variables)) or (
            self.variables == other.variables
        )

        return (
            self.name == other.name
            and self.branch == other.branch
            and self.cron == other.cron
            and self.tz == other.tz
            and self.enabled == other.enabled
            and equal_variables
        )


class ChangeSchedulers(ChangePropertySetting):
    sub_properties = ["branch", "cron", "tz", "enabled", "variables"]
    status_to_process = ["updated", "kept", "added", "removed", "warning"]

    def to_dict(self):
        return {
            "property_name": self.property_name,
            "differences": self.get_differences_as_dict(recursive=True),
        }

    def diff_to_dict(self):
        differences = {}
        if self.has_diff():
            for name, difference in self.get_differences_as_dict(recursive=True).items():
                if difference["status"] != "kept":
                    differences[name] = difference
            return {"property_name": self.property_name, "differences": differences}
        return None

    def get_differences_as_dict(self, recursive=False):
        before_properties = {prop.name: prop for prop in self.before}
        after_properties = {prop.name: prop for prop in self.after}
        differences = {}
        for name, prop in before_properties.items():
            status = "kept"
            after_prop = None
            if name in after_properties:
                # Check differences of schedulers variables
                change_variables = ChangeVariables(
                    "variables",
                    (prop.variables or {}).values(),
                    (after_properties[name].variables or {}).values(),
                    self.show_diff_only,
                )
                if change_variables.has_diff():
                    status = "updated"
                after_prop = after_properties[name].to_compare(as_dict=recursive)
                # check differences of schedulers
                if prop != after_properties[name]:
                    status = "updated"
            elif self.keep_existing:
                # Old variable but user wants to keep it
                status = "kept"
                after_prop = prop.to_compare(as_dict=recursive)
            else:
                status = "removed"
            differences[name] = {
                "status": status,
                "before": prop.to_compare(as_dict=recursive),
                "after": after_prop,
            }
        self._added_properties(differences, after_properties, recursive=recursive)
        return differences

    def _added(self, after_prop, recursive=False, **kwargs):
        return {
            "status": "added",
            "before": None,
            "after": after_prop.to_compare(as_dict=recursive),
        }

    @cachedproperty
    def differences(self):
        return self.get_differences_as_dict()

    def sub_property_to_str(self, after, before, sub_prop, to_str):
        if sub_prop == "variables":
            bef_var = (
                before.get("variables") if before and before.get("variables") is not None else {}
            )
            after_var = (
                after.get("variables") if after and after.get("variables") is not None else {}
            )
            if bef_var or after_var:
                change_variables = ChangeVariables(
                    "variables",
                    bef_var.values(),
                    after_var.values(),
                    self.show_diff_only,
                )
                change_variables.sub_level = 1
                change_variables.sub_properties = ["value", "variable_type"]
                to_str += change_variables.to_string()
        else:
            to_str = super().sub_property_to_str(after, before, sub_prop, to_str)
        return to_str


class SchedulersSettingExecutor(ChangePropertyExecutor):
    order = 100
    name = "schedulers"
    sections = ["schedulers"]

    def _apply(self):
        if self.changes:
            change_schedulers = self.changes[0]  # type: ChangeSchedulers
            after = {sched.name: sched for sched in change_schedulers.after}
            before = {sched.name: sched for sched in change_schedulers.before}
            ns_differences = Namespace(change_schedulers.differences)
            for sched_name, difference in ns_differences.items():
                if difference["status"] == "removed":
                    self._remove_scheduler(difference.before.api_id)
                elif difference["status"] == "updated":
                    self._update_schedulers(before[sched_name], after[sched_name])
                elif difference["status"] == "added":
                    self._add_scheduler(after[sched_name])

    def _remove_scheduler(self, scheduler_id):
        scheduler = self.item.pipelineschedules.get(scheduler_id, retry_transient_errors=True)
        scheduler.delete(retry_transient_errors=True)

    def _add_scheduler(self, scheduler):
        scheduler_created = self.item.pipelineschedules.create(
            scheduler.get_query(), retry_transient_errors=True
        )
        if scheduler.variables:
            for _, variable in scheduler.variables.items():  # type: ItemVariable
                scheduler_created.variables.create(
                    {"key": variable.name, "value": variable.value}, retry_transient_errors=True
                )

    def _update_schedulers(self, sched_before, sched_after):
        scheduler = self.item.pipelineschedules.get(
            sched_before.api_id, retry_transient_errors=True
        )
        for field, value in sched_after.get_query().items():
            setattr(scheduler, field, value)
        scheduler.save(retry_transient_errors=True)
        self._save_variables(sched_after, scheduler)

    def _save_variables(self, sched_after, scheduler):
        scheduler_variables = {var.get("key"): var for var in scheduler.attributes["variables"]}
        variables_used = []
        for var_name, var_value in scheduler_variables.items():
            if var_name in sched_after.variables:
                new_value = sched_after.variables[var_name].value
                new_var_type = sched_after.variables[var_name].variable_type
                if (
                    var_value.get("value") != new_value
                    or var_value.get("variable_type") != new_var_type
                ):
                    scheduler.variables.update(
                        var_name,
                        new_data={
                            "key": var_name,
                            "value": new_value,
                            "variable_type": new_var_type,
                        },
                        retry_transient_errors=True,
                    )
                variables_used.append(var_name)
            else:
                variables_used.append(var_name)
                scheduler.variables.delete(var_name, retry_transient_errors=True)
        for var_name, variable in sched_after.variables.items():
            if var_name not in variables_used:
                scheduler.variables.create(
                    {
                        "key": variable.name,
                        "value": variable.value,
                        "variable_type": variable.variable_type,
                    },
                    retry_transient_errors=True,
                )

    def _update(self, mode: RunMode, members_user, members_group):
        if "schedulers" in self.rule and self.rule.schedulers is not None:
            schedulers = []
            keep_existing_schedulers = self.rule.get("keep_existing_schedulers", False)
            for scheduler in self.rule.schedulers:
                dict_variables = None
                if "variables" in scheduler:
                    preparator = ScheduleVariablesSettingPreparator(
                        self.item_path, self.rule, scheduler.variables, self.warnings
                    )
                    variables = preparator.prepare_variables(mode)
                    dict_variables = {var.name: var for var in variables}

                before_schedule = self.item.pipelineschedules.list(
                    name=scheduler.name, all=False
                )  # type: ignore

                if "enabled" not in scheduler and before_schedule:
                    scheduler_enable = before_schedule[0].attributes["active"] or False  # type: ignore # pylint: disable=line-too-long
                else:
                    scheduler_enable = scheduler.enabled if hasattr(scheduler, "enabled") else False

                schedulers.append(
                    Scheduler(
                        name=scheduler.name,
                        branch=scheduler.branch,
                        cron=scheduler.cron,
                        enabled=scheduler_enable,
                        tz=scheduler.tz,
                        variables=dict_variables,
                    )
                )

            self.changes.append(
                ChangeSchedulers(
                    property_name="schedulers",
                    before=Scheduler.to_schedulers(
                        self.item.pipelineschedules.list(  # type: ignore
                            iterator=True, retry_transient_errors=True
                        ),
                        self.item,
                    ),
                    after=schedulers,
                    show_diff_only=self.show_diff_only,
                    keep_existing=keep_existing_schedulers,
                )
            )


class ScheduleVariablesSettingPreparator(VariablesSettingPreparator):
    def is_protected_variable(self, env_variable):
        return False
