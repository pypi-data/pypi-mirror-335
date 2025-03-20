"""
Up the jira services.
"""

# Third Party Libraries
import attr

from boltons.cacheutils import cachedproperty
from gitlab.exceptions import GitlabParsingError

# Gitlab-Project-Configurator Modules
from gpc.change_setting import ChangeSettingSubProperty
from gpc.executors.properties_updator import ChangePropertyExecutor
from gpc.parameters import RunMode
from gpc.property_manager import PropertyBean


PROP_NAME = "push_rules"


@attr.s(eq=False)
class PushRulesProperty(PropertyBean):
    map_fields_api = {
        "dont_allow_users_to_remove_tags": "deny_delete_tag",
        "member_check": "member_check",
        "prevent_secrets": "prevent_secrets",
        "commit_message": "commit_message_regex",
        "commit_message_negative": "commit_message_negative_regex",
        "branch_name_regex": "branch_name_regex",
        "author_mail_regex": "author_email_regex",
        "prohibited_file_name_regex": "file_name_regex",
        "max_file_size": "max_file_size",
        "reject_unsigned_commits": "reject_unsigned_commits",
    }
    dont_allow_users_to_remove_tags = attr.ib(default=None)  # type: bool
    member_check = attr.ib(default=False)  # type: bool
    prevent_secrets = attr.ib(default=False)  # type: bool
    commit_message = attr.ib(default=None)  # type: str
    commit_message_negative = attr.ib(default=None)  # type: str
    branch_name_regex = attr.ib(default=None)  # type: str
    author_mail_regex = attr.ib(default=None)  # type: str
    prohibited_file_name_regex = attr.ib(default=None)  # type: str
    max_file_size = attr.ib(default=0)  # type: int
    reject_unsigned_commits = attr.ib(default=None)  # type: bool

    @staticmethod
    def to_push_rules_property(api_push_rules_setting):
        push_rules_property = PushRulesProperty(name=PROP_NAME)
        if api_push_rules_setting:
            for local_field, api_field in PushRulesProperty.map_fields_api.items():
                setattr(
                    push_rules_property,
                    local_field,
                    getattr(api_push_rules_setting, api_field),
                )
            # api_push_rules_setting.reject_unsigned_commits returns either None or
            # True we need to force a boolean to avoid updating to False each time
            push_rules_property.reject_unsigned_commits = bool(
                push_rules_property.reject_unsigned_commits
            )

        return push_rules_property

    def get_query(self):
        query = {}
        for local_field, api_field in PushRulesProperty.map_fields_api.items():
            if getattr(self, local_field) is not None:
                query[api_field] = getattr(self, local_field)
        return query

    def to_dict(self):
        return {
            "name": self.name,
            "dont_allow_users_to_remove_tags": self.dont_allow_users_to_remove_tags,
            "member_check": self.member_check,
            "prevent_secrets": self.prevent_secrets,
            "commit_message": self.commit_message,
            "commit_message_negative": self.commit_message_negative,
            "branch_name_regex": self.branch_name_regex,
            "author_mail_regex": self.author_mail_regex,
            "prohibited_file_name_regex": self.prohibited_file_name_regex,
            "max_file_size": self.max_file_size,
            "reject_unsigned_commits": self.reject_unsigned_commits,
        }

    def __eq__(self, other):
        if not isinstance(other, PushRulesProperty):
            return False
        return all(getattr(self, x) == getattr(other, x) for x in self.__dict__)


@attr.s
class PushRulesPropertyToSave(PushRulesProperty):
    remove = attr.ib(default=False)  # type: bool


@attr.s
class ChangePushRulesProperty(ChangeSettingSubProperty):
    apply_after_remove = attr.ib(default=False)

    @cachedproperty
    def action(self):
        if self.after == self.before:
            return "kept"
        if self.apply_after_remove:
            return "updated"
        if self.after.remove:
            return "removed"
        return "updated"


class PushRulesSettingExecutor(ChangePropertyExecutor):
    order = 80
    name = "push_rules"
    sections = ["push_rules"]

    @cachedproperty
    def push_rules(self):
        try:
            return self.item.pushrules.get(retry_transient_errors=True)
        except GitlabParsingError:
            return None

    def _apply(self):
        if self.changes:
            change_push_rules = self.changes[0]
            if self.push_rules:
                if change_push_rules.action != "kept":
                    self._execute_changes(change_push_rules)
            elif not change_push_rules.after.remove:
                self.item.pushrules.create(
                    change_push_rules.after.get_query(), retry_transient_errors=True
                )

    def _execute_changes(self, change_push_rules):
        if change_push_rules.apply_after_remove:
            self.push_rules.delete(retry_transient_errors=True)
            self.push_rules.save(retry_transient_errors=True)
            self.item.pushrules.create(
                change_push_rules.after.get_query(), retry_transient_errors=True
            )
        elif change_push_rules.after.remove:
            self.push_rules.delete(retry_transient_errors=True)
        else:
            for field, value in change_push_rules.after.get_query().items():
                setattr(self.push_rules, field, value)
            self.push_rules.save(retry_transient_errors=True)

    def _update(self, mode: RunMode, members_user, members_group):
        if "push_rules" in self.rule:
            push_rules_property = PushRulesSettingExecutor.to_push_rules(self.rule.push_rules)
            before_push_rules_property = PushRulesProperty.to_push_rules_property(self.push_rules)
            apply_after_remove = (
                self.rule.push_rules.get("remove", False) and len(self.rule.push_rules) > 1
            )
            # set value of (after) push_rules_property to value of before if it is None to prevent
            # false updated indications
            if not push_rules_property.remove:
                for field in push_rules_property.map_fields_api:
                    if getattr(push_rules_property, field) is None:
                        setattr(
                            push_rules_property, field, getattr(before_push_rules_property, field)
                        )
            self.changes.append(
                ChangePushRulesProperty(
                    property_name=PROP_NAME,
                    before=before_push_rules_property,
                    after=push_rules_property,
                    show_diff_only=self.show_diff_only,
                    apply_after_remove=apply_after_remove,
                )
            )

    @staticmethod
    def to_push_rules(config_push_rules: dict):
        push_rules_property = PushRulesPropertyToSave(name=PROP_NAME)
        push_rules_property.reject_unsigned_commits = bool(
            push_rules_property.reject_unsigned_commits
        )
        if config_push_rules.get("remove") and len(config_push_rules) == 1:
            push_rules_property.remove = config_push_rules.get("remove", False)
            return push_rules_property
        if config_push_rules.get("remove") and len(config_push_rules) > 1:
            push_rules_property.remove = config_push_rules.get("remove", False)
        for field in PushRulesProperty.map_fields_api:
            if config_push_rules.get(field, None) is not None:
                setattr(push_rules_property, field, config_push_rules.get(field, None))
        return push_rules_property
