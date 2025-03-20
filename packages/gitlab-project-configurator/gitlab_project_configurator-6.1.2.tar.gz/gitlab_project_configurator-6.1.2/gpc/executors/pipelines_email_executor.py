"""
Manage pipelines email service.
"""

# Standard Library
from typing import List

# Third Party Libraries
import attr

from boltons.cacheutils import cachedproperty

# Gitlab-Project-Configurator Modules
from gpc.change_setting import ChangeSettingSubProperty
from gpc.executors.properties_updator import ChangeServicePropertyExecutor
from gpc.executors.properties_updator import CustomService
from gpc.parameters import RunMode
from gpc.property_manager import PropertyBean


@attr.s(eq=False)
class PipelinesEmailProperty(PropertyBean):
    recipients = attr.ib(factory=list)  # type: List[str]
    notify_only_broken_pipelines = attr.ib(default=None)  # type: bool
    notify_only_default_branch = attr.ib(default=None)  # type: bool
    pipeline_events = attr.ib(default=None)  # type: bool
    disabled = attr.ib(default=False)  # type: bool

    @staticmethod
    def parse_recipients(recipients: str):
        # Recipients shall be a comma-separated list
        if recipients:
            return recipients.split(",")
        return []

    @staticmethod
    def to_pipelines_email_property(api_pipelines_email_setting: CustomService):
        prop = PipelinesEmailProperty(name="pipelines_email")
        if api_pipelines_email_setting.is_lazy:
            return prop
        if hasattr(api_pipelines_email_setting, "active"):
            prop.disabled = not api_pipelines_email_setting.active
        if prop.disabled:
            return prop
        prop.recipients = PipelinesEmailProperty.parse_recipients(
            api_pipelines_email_setting.properties.get("recipients", None)
        )
        prop.notify_only_broken_pipelines = api_pipelines_email_setting.properties.get(
            "notify_only_broken_pipelines", None
        )
        prop.notify_only_default_branch = api_pipelines_email_setting.properties.get(
            "notify_only_default_branch", None
        )
        prop.pipeline_events = api_pipelines_email_setting.properties.get("pipeline_events", None)
        return prop

    def get_query(self):
        pass

    def to_dict(self):
        to_dict = {
            "name": self.name,
            "recipients": self.recipients,
            "notify_only_broken_pipelines": self.notify_only_broken_pipelines,
            "notify_only_default_branch": self.notify_only_default_branch,
            "pipeline_events": self.pipeline_events,
        }
        return to_dict

    def __eq__(self, other):
        if not isinstance(other, PipelinesEmailProperty):
            return False
        return (
            self.name == other.name
            and self.disabled == other.disabled
            and self.recipients.sort() == other.recipients.sort()
            and self.notify_only_broken_pipelines == other.notify_only_broken_pipelines
            and self.notify_only_default_branch == other.notify_only_default_branch
            and self.pipeline_events == other.pipeline_events
        )


@attr.s
class ChangePipelinesEmailProperty(ChangeSettingSubProperty):
    def to_dict(self):
        return {
            "property_name": self.property_name,
            "differences": {
                "pipelines_email": {
                    "before": self.before.to_dict(),
                    "after": self.after.to_dict(),
                    "action": self.action,
                }
            },
        }

    @cachedproperty
    def action(self):
        if self.after == self.before:
            return "kept"
        if self.after.disabled:
            return "removed"
        return "updated"


class PipelinesEmailSettingExecutor(ChangeServicePropertyExecutor):
    order = 71
    name = "pipelines_email"
    sections = ["integrations"]
    service_name = "pipelines-email"

    def _set_recipients(self, recipients):
        if isinstance(recipients, list):
            recipients = ",".join(recipients)
        self.service.recipients = recipients

    def _update(self, mode: RunMode, members_user, members_group):
        if "integrations" in self.rule and "pipelines_email" in self.rule.integrations:
            setting = self.rule.integrations.pipelines_email
            disabled = setting.get("disabled", False)
            pipelines_email_property = PipelinesEmailProperty(name="pipelines_email")
            pipelines_email_property.disabled = disabled
            if not disabled:
                pipelines_email_property.recipients = setting.get("recipients")
                pipelines_email_property.notify_only_broken_pipelines = setting.get(
                    "notify_only_broken_pipelines"
                )
                pipelines_email_property.notify_only_default_branch = setting.get(
                    "notify_only_default_branch"
                )
                pipelines_email_property.pipeline_events = setting.get("pipeline_events")
            self.changes.append(
                ChangePipelinesEmailProperty(
                    property_name="pipelines_email",
                    before=PipelinesEmailProperty.to_pipelines_email_property(self.service),
                    after=pipelines_email_property,
                    show_diff_only=self.show_diff_only,
                )
            )
            self._set_recipients(pipelines_email_property.recipients)
            self.service.notify_only_broken_pipelines = (
                pipelines_email_property.notify_only_broken_pipelines
            )
            self.service.notify_only_default_branch = (
                pipelines_email_property.notify_only_default_branch
            )
            self.service.pipeline_events = pipelines_email_property.pipeline_events
