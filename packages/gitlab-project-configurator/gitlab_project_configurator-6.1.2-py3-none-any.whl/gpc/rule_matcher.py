"""
Matches which rules should apply on which project.
"""

# Standard Library
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import List
from typing import Optional

# Third Party Libraries
from dictns import Namespace
from gitlab import Gitlab
from structlog import get_logger

# Gitlab-Project-Configurator Modules
from gpc.helpers.gitlab_helper import walk_gitlab_projects
from gpc.helpers.remerge import ListOverrideBehavior
from gpc.helpers.remerge import remerge
from gpc.helpers.types import GenGroupPathRules
from gpc.helpers.types import GenProjectPathRules
from gpc.helpers.types import GroupPathRule
from gpc.helpers.types import ProjectPathRule
from gpc.helpers.types import Rule
from gpc.helpers.types import listify


log = get_logger()

# pylint: disable=assignment-from-none, useless-return


@dataclass
class RuleMatcher(ABC):
    """
    I am responsible for associating projects with rules.

    I find in the configuration which policies should be applied on which projects.
    Note projects can be a simple group name, the unrolling of every project in this
    group is not under my responsibility.

    I support the rule override.
    """

    gitlab: Gitlab
    raw_config: Namespace
    list_update_behavior: ListOverrideBehavior = ListOverrideBehavior.REPLACE

    @property
    def rules(self):
        return []

    @abstractmethod
    def find_rules(self):
        raise NotImplementedError()

    def _get_rules(self, cfg) -> List[Rule]:
        rules_name = listify(cfg.get("rule_name", None))
        rules = []
        for rule_name in rules_name:
            rule = self.get_named_rule(rule_name)
            if not rule:
                raise ValueError(f"Cannot find rule name: {rule_name}")
            rules.append(rule)
        if not rules_name:
            rule = self._inject_profiles(
                {
                    "rule_name": "gpc_default_empty_rule",
                }
            )
            if rule:
                rules.append(rule)
        return rules

    def get_named_rule(self, rule_name: str) -> Optional[Rule]:
        log.debug("searching named rule", rule_name=rule_name)
        rule = self._get_rule(rule_name)
        return self._inject_profiles(rule) if rule else None

    def _get_rule(self, rule_name: str) -> Optional[Rule]:
        for item_rule in self.rules:
            if item_rule.rule_name == rule_name:
                return item_rule
        return None

    def _prepare_rule(self, rules: List[Rule], item_cfg: Namespace) -> Rule:
        if rules:
            merged_rule = self._handle_rule_inherits_from(rules[0])
            rules_applied = (
                merged_rule.rule_name
                if isinstance(merged_rule.rule_name, list)
                else [merged_rule.rule_name]
            )
            for rule in rules[1:]:
                rules_applied.append(rule.rule_name)
                cur_rule = self._handle_rule_inherits_from(rule)
                merged_rule = self.override_rule(merged_rule, cur_rule)
        else:
            rules_applied = []
            merged_rule = Namespace({})
        item_rule = self._handle_custom_rules(merged_rule, item_cfg)
        item_rule.rule_name = rules_applied
        return item_rule

    def _handle_rule_inherits_from(self, rule: Rule) -> Rule:
        if "inherits_from" not in rule:
            return Namespace(rule)
        irule = Namespace(rule.copy())

        # We merged first all inherited_rules
        merged_rule: Rule = {}
        irule.inherits_from = listify(irule.inherits_from).copy()
        for wanted_rule_name in irule.inherits_from:
            other_rule = self._get_rule(wanted_rule_name)
            if not other_rule:
                raise NotImplementedError(
                    "This case 'invalid inherits_from' should not happen, "
                    "the validator should have caught it"
                )
            log.debug(
                "Applying rule inheritance (inherits_from)",
                rule_name=irule.rule_name,
                other_rule_name=other_rule.rule_name,
            )
            other_rule = self._handle_rule_inherits_from(other_rule.copy())
            del other_rule["rule_name"]
            if merged_rule:
                merged_rule = self.override_rule(merged_rule, other_rule)
            else:
                merged_rule = other_rule
        # We override the merged_rule by current rule
        irule = self.override_rule(merged_rule, irule)
        log.debug(
            "Merged rule",
            merged_rule=irule,
        )
        return irule

    def _handle_custom_rules(self, rule: Rule, item_cfg: Namespace) -> Rule:
        if "custom_rules" not in item_cfg:
            return rule
        crule = Namespace(rule.copy())
        custom_rules = item_cfg["custom_rules"]
        if custom_rules:
            crule = self.override_rule(crule, custom_rules)
            crule["custom_rules"] = "yes"
            log.debug(
                "Applying custom rules",
                rule_name=rule.get("rule_name", "?"),
                custom_rules=custom_rules,
                overriden_rule=crule,
            )
        return crule

    def _inject_profiles(self, rule: Rule) -> Rule:
        cr = Namespace(rule.copy())
        for profiles in ["variable_profiles", "member_profiles", "label_profiles"]:
            if profiles not in self.raw_config:
                continue

            cr[profiles] = self.raw_config[profiles]
        return cr

    def override_rule(self, rule: Rule, other_rule: Rule) -> Rule:
        return Namespace(
            remerge(
                [rule, other_rule],
                list_update_behavior=self.list_update_behavior,
            )
        )


class GroupRuleMatcher(RuleMatcher):
    @property
    def rules(self):
        return self.raw_config.get("groups_rules")

    def find_rules(self) -> GenGroupPathRules:
        log.debug("Listing group from configuration")
        for group_cfg in self.raw_config.get("groups_configuration", []):
            log.debug("Evaluating group configuration", group_cfg=group_cfg)
            for grp_path in group_cfg.get("paths", []):
                rules = self._get_rules(group_cfg)
                log.debug("Found group path from configuration", path=grp_path)
                yield GroupPathRule(
                    group_path=grp_path,
                    rule=self._prepare_rule(rules=rules, item_cfg=group_cfg),
                )


class ProjectRuleMatcher(RuleMatcher):
    @property
    def rules(self):
        return self.raw_config.get("projects_rules")

    def find_rules(self) -> GenProjectPathRules:
        log.debug("Listing project from configuration")
        for project_cfg in self.raw_config.get("projects_configuration", []):
            log.debug("Evaluating group configuration", project_cfg=project_cfg)
            for path in project_cfg.get("paths", []):
                rules = self._get_rules(project_cfg)
                if "*" in path:
                    paths_from_regex = walk_gitlab_projects(self.gitlab, path)
                    for proj_path in paths_from_regex:
                        log.debug(
                            "Found project path from configur ation (from regex)", path=proj_path
                        )
                        yield ProjectPathRule(
                            project_path=proj_path,
                            rule=self._prepare_rule(rules=rules, item_cfg=project_cfg),
                            recursive=project_cfg.get("recursive", False),
                            excludes=project_cfg.get("excludes", None),
                            not_seen_yet_only=project_cfg.get("not_seen_yet_only", False),
                        )
                else:
                    log.debug("Found project path from configuration", path=path)
                    yield ProjectPathRule(
                        project_path=path,
                        rule=self._prepare_rule(rules=rules, item_cfg=project_cfg),
                        recursive=project_cfg.get("recursive", False),
                        excludes=project_cfg.get("excludes", None),
                        not_seen_yet_only=project_cfg.get("not_seen_yet_only", False),
                    )
