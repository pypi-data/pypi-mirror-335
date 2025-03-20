"""
Up the jira services.
"""

# Standard Library
import os

from typing import Optional  # pylint: disable=unused-import
from typing import Union  # pylint: disable=unused-import

# Third Party Libraries
import attr
import click

from boltons.cacheutils import cachedproperty

# Gitlab-Project-Configurator Modules
from gpc.change_setting import ChangeSettingSubProperty
from gpc.executors.properties_updator import ChangeServicePropertyExecutor
from gpc.executors.properties_updator import CustomService
from gpc.helpers.hider import hide_value
from gpc.parameters import RunMode
from gpc.property_manager import PropertyBean


S_BASIC = "Basic"
S_JIRA_TOKEN = "Jira Access Token"


@attr.s(eq=False)
class JiraProperty(PropertyBean):
    url = attr.ib(default=None)  # type: str
    jira_issue_transition_id = attr.ib(default=None)  # type: int
    disabled = attr.ib(default=False)  # type: bool
    username = attr.ib(default=None)  # type: str
    password = attr.ib(default=None)  # type: str
    token = attr.ib(default=None)  # type: str
    authentication_method = attr.ib(default=None)  # type: Optional[str]
    trigger_on_commit = attr.ib(default=False)  # type: Optional[bool]
    trigger_on_mr = attr.ib(default=True)  # type: Optional[bool]
    comment_on_event_enabled = attr.ib(default=False)  # type: Optional[Union[bool, str]]
    warning_msg = attr.ib(default=None)  # type: str

    @staticmethod
    def to_jira_property(api_jira_setting: CustomService):
        jira_property = JiraProperty(name="jira")
        if api_jira_setting.is_lazy:
            return jira_property
        jira_property.url = api_jira_setting.properties.get("url", None)
        jira_property.username = api_jira_setting.properties.get("username", None)
        jira_property.password = api_jira_setting.properties.get("password", None)
        jira_property.token = api_jira_setting.properties.get("token", None)
        auth_met = None
        if api_jira_setting.properties.get("jira_auth_type", None) == 1:
            auth_met = S_JIRA_TOKEN
        elif api_jira_setting.properties.get("jira_auth_type", None) == 0:
            auth_met = S_BASIC
        jira_property.authentication_method = auth_met
        jira_property.jira_issue_transition_id = api_jira_setting.properties.get(
            "jira_issue_transition_id", None
        )
        jira_property.trigger_on_commit = api_jira_setting.commit_events
        jira_property.trigger_on_mr = api_jira_setting.merge_requests_events
        jira_property.comment_on_event_enabled = api_jira_setting.comment_on_event_enabled
        if hasattr(api_jira_setting, "active"):
            jira_property.disabled = not api_jira_setting.active
        return jira_property

    def get_query(self):
        pass

    def to_dict(self):
        to_dict = {
            "name": self.name,
            "url": self.url,
            "username": self.username,
            "jira_issue_transition_id": self.jira_issue_transition_id,
            "trigger_on_commit": self.trigger_on_commit,
            "trigger_on_mr": self.trigger_on_mr,
            "comment_on_event_enabled": self.comment_on_event_enabled,
            "authentication_method": self.authentication_method,
        }
        if self.warning_msg:
            to_dict["warning"] = self.warning_msg
        to_dict["password"] = hide_value(self.password)
        to_dict["token"] = hide_value(self.token)
        return to_dict

    def __eq__(self, other):
        if not isinstance(other, JiraProperty):
            return False
        eq = (
            self.name == other.name
            and self.url == other.url
            and self.username == other.username
            and self.jira_issue_transition_id == other.jira_issue_transition_id
            and self.disabled == other.disabled
            and self.trigger_on_commit == other.trigger_on_commit
            and self.trigger_on_mr == other.trigger_on_mr
            and self.comment_on_event_enabled == other.comment_on_event_enabled
            and self.authentication_method == other.authentication_method
        )
        return eq


@attr.s
class ChangeJiraProperty(ChangeSettingSubProperty):
    def to_dict(self):
        return {
            "property_name": self.property_name,
            "differences": {
                "jira": {
                    "before": self.before.to_dict(),
                    "after": self.after.to_dict(),
                    "action": self.action,
                }
            },
        }

    @cachedproperty
    def action(self):
        if self.after.disabled:
            return "removed"
        if self.after.warning_msg:
            return "warning"
        if self.after == self.before:
            return "kept"
        return "updated"


class JiraSettingExecutor(ChangeServicePropertyExecutor):
    order = 70
    name = "jira"
    sections = ["integrations"]
    service_name = "jira"

    def _update(self, mode: RunMode, members_user, members_group):
        if "integrations" not in self.rule or "jira" not in self.rule.integrations:
            return
        setting = self.rule.integrations.jira
        jira_property = JiraProperty(name="jira")
        disabled = setting.get("disabled", False)
        before_settings = JiraProperty.to_jira_property(self.service)
        jira_property.disabled = disabled
        if not disabled:
            jira_property.url = setting.get("url")
            transition_ids = setting.get("jira_issue_transition_id", None)
            if transition_ids == "":
                # If the config value is an empty string, we want to remove the
                # jira_issue_transition_id on server.
                transition_ids = None
            elif transition_ids is not None:
                transition_ids = str(transition_ids)
            else:
                # If None we want to keep the existing value.
                transition_ids = before_settings.jira_issue_transition_id
            jira_property.jira_issue_transition_id = transition_ids
            jira_property.username = (
                os.getenv(setting.get("username_from_envvar"))  # type: ignore
                if "username_from_envvar" in setting
                else setting.get("username")
            )
            jira_property.trigger_on_commit = setting.get("trigger_on_commit", False)
            jira_property.comment_on_event_enabled = setting.get("comment_on_event_enabled", False)
            jira_property.trigger_on_mr = setting.get("trigger_on_mr", True)

            if (
                self.gpc_params.mode == RunMode.APPLY
                and hasattr(self.service, "inherited")
                and self.service.inherited
            ):
                jira_settings = {
                    "url": before_settings.url,
                    "username": before_settings.username,
                    "password": "x",
                    "use_inherited_settings": False,
                }
                item_id = self.item.id
                headers = {
                    "PRIVATE-TOKEN": self.gitlab.private_token,
                    "Content-Type": "application/json",
                }
                api_endpoint = f"{self.gitlab.url}/api/v4/projects/{item_id}/services/jira"
                self.gitlab.session.put(api_endpoint, headers=headers, json=jira_settings)

            self._set_password(jira_property, setting, mode)
        self.changes.append(
            ChangeJiraProperty(
                property_name="jira",
                before=before_settings,
                after=jira_property,
                show_diff_only=self.show_diff_only,
            )
        )
        self.service.url = jira_property.url
        self.service.username = jira_property.username
        if jira_property.token:
            self.service.password = jira_property.token
            self.service.jira_auth_type = 1
        else:
            self.service.password = jira_property.password
            self.service.jira_auth_type = 0
        self.service.jira_issue_transition_id = jira_property.jira_issue_transition_id
        self.service.commit_events = jira_property.trigger_on_commit
        self.service.comment_on_event_enabled = jira_property.comment_on_event_enabled
        self.service.merge_requests_events = jira_property.trigger_on_mr

    def _set_password(self, jira_property: JiraProperty, setting, mode: RunMode):
        if "password_from_envvar" in setting:
            jira_property.authentication_method = S_BASIC
            self._set_pwd(jira_property, setting, "password", "password_from_envvar", mode)
        elif "token_from_envvar" in setting:
            jira_property.authentication_method = S_JIRA_TOKEN
            self._set_pwd(jira_property, setting, "token", "token_from_envvar", mode)

    def _set_pwd(self, jira_property, setting, attr_name, envvar, mode: RunMode):
        if os.getenv(setting.get(envvar)) is not None:
            setattr(jira_property, attr_name, os.getenv(setting.get(envvar), ""))
        else:
            warning_msg = f"/!\\ Environment variable {setting.get(envvar)} not found."
            click.secho(warning_msg, fg="red")
            if mode is RunMode.DRY_RUN:
                self.warnings.append(warning_msg)
                click.secho(
                    "/!\\ In Apply or Interactive mode your configuration will fail.",
                    fg="yellow",
                )
                setattr(jira_property, attr_name, "")
                jira_property.warning_msg = warning_msg
            else:
                raise ValueError(warning_msg)

    def _apply(self):
        if self.service_name.lower() in self.gpc_params.force:
            click.secho(f"'{self.service_name}': settings force updated!", fg="yellow")
            self.service.save(retry_transient_errors=True)
        elif self.changes:
            service_property = self.changes[0]

            if service_property.after.disabled:
                self.service.delete(retry_transient_errors=True)
            else:
                self.service.save(retry_transient_errors=True)
