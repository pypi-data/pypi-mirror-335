"""
Main process.
"""

# Standard Library
import os
import re
import sys
import traceback

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from typing import Any  # pylint: disable=unused-import
from typing import Dict  # pylint: disable=unused-import
from typing import List  # pylint: disable=unused-import
from typing import Pattern

# Third Party Libraries
import anyconfig
import click

from boltons.cacheutils import LRI
from boltons.cacheutils import cachedmethod
from boltons.cacheutils import cachedproperty
from dictns import Namespace
from gitlab import Gitlab
from gitlab import exceptions as gl_exceptions
from gitlab.v4.objects import Group as GitlabGroup
from path import Path
from structlog import get_logger

# Gitlab-Project-Configurator Modules
from gpc import version
from gpc.changes_converter import ConverterFactory
from gpc.config_validator import GpcConfigValidator
from gpc.helpers.error_codes import GPC_ERR_CODE_PROJECT_FAILURE
from gpc.helpers.error_codes import GPC_ERR_CODE_SUCCESS
from gpc.helpers.exceptions import GpcProfileError
from gpc.helpers.exceptions import GpcSchemaError
from gpc.helpers.exceptions import GpcValidationError
from gpc.helpers.gitlab_helper import clean_gitlab_project_name
from gpc.helpers.gitlab_helper import get_group
from gpc.helpers.gitlab_helper import is_archived_project
from gpc.helpers.gitlab_helper import is_existing_group
from gpc.helpers.gitlab_helper import is_existing_project
from gpc.helpers.gitlab_helper import is_shared_project
from gpc.helpers.mail_reporter import send_change_event_email
from gpc.helpers.remerge import ListOverrideBehavior
from gpc.helpers.types import GenProjectPathRules
from gpc.helpers.types import GroupRule  # pylint: disable=unused-import
from gpc.helpers.types import ProjectPathRule
from gpc.helpers.types import ProjectRule  # pylint: disable=unused-import
from gpc.parameters import GpcParameters
from gpc.parameters import RawConfig  # pylint: disable=unused-import
from gpc.parameters import RunMode
from gpc.project_rule_executor import GroupRuleExecutor
from gpc.project_rule_executor import ProjectRuleExecutor
from gpc.rule_matcher import GroupRuleMatcher
from gpc.rule_matcher import ProjectRuleMatcher
from gpc.templates import load_template


log = get_logger()

MAX_CHANGES_TO_DISPLAY = 10


def generate_event(changes):
    changes_event = {}
    all_changes = False
    nbr_changes = 0
    if not changes:
        return all_changes, changes_event

    for item, item_diff in changes.items():
        if nbr_changes >= MAX_CHANGES_TO_DISPLAY:
            break
        converted_changes = []
        nbr_changes += 1
        for prop, item_changes in item_diff.items():
            converter = ConverterFactory.init_converter(prop, Namespace(item_changes))
            converted_changes.append(converter.execute())
        changes_event[item] = converted_changes
    else:
        all_changes = True
    return all_changes, changes_event


def process_json_for_report(obj):
    if isinstance(obj, dict):
        if ("masked" in obj and obj["masked"] is True) and "value" in obj:
            obj["value"] = "[MASKED]"
        for key in obj:
            process_json_for_report(obj[key])
    elif isinstance(obj, list):
        for item in obj:
            process_json_for_report(item)
    return obj


class GpcGeneralExecutor(GpcConfigValidator):
    """
    I am the main execution loop of GPC.

    I handle the project validation (through inheritance from GpcConfigValidator)
    and discovering dynamically all projects in a given group if the user has set
    group name in its configuration. I also apply exclusion and inclusion mecanism.

    I can also generate a report (JSON) at the end of execution.

    """

    def __init__(self, parameters: GpcParameters, gitlab: Gitlab):
        super().__init__(parameters=parameters)
        self.gitlab = gitlab  # type: Gitlab
        self.secrets = {}  # type: Dict[str, str]
        self.project_rules = {}  # type: Dict[str, ProjectRule]
        self.group_rules = {}  # type: Dict[str, GroupRule]
        self._group_cache = {}  # type: Dict[str, GitlabGroup]
        self._project_report = []  # type: List[Dict[str, Any]]
        self._group_report = []  # type: List[Dict[str, Any]]
        self._report = {}  # type: Dict[str, Any]
        self._excluded_projects = []  # type: List[Dict[str, Any]]
        self._rules_used = []  # type: List[str]
        self._cache = LRI(10000)
        self._warnings = {}  # type: Dict[str, Dict[str,Any]]

    @cachedproperty
    def rules(self):
        rules = [
            project_rule.rule_name for project_rule in self.raw_config.get("projects_rules", [])
        ]

        rules += [group_rule.rule_name for group_rule in self.raw_config.get("groups_rules", [])]
        return rules

    def run(self) -> int:
        try:
            log.info(
                "GPC Execution.",
                configurator=self.params.config_project_url,
                mode=self.params.mode,
            )
            super().run()
        except (GpcValidationError, GpcSchemaError, GpcProfileError) as e:
            click.secho("-" * 80, fg="red")
            e.echo()
            click.secho("-" * 80, fg="red")
            return e.error_code

        if self.params.preview:
            click.secho(
                "Preview mode enabled: list will be merged during rules inheritance",
                fg="magenta",
                bold=True,
            )
        self._print_merged_config()
        # Load rules accessors
        self.load_rules()

        # Find groups/projects and matching rules
        changes = {}  # type: Dict[Any, Any]
        succeed = all(
            [
                self.apply_for_groups(changes),
                self.apply_for_projects(changes),
            ]
        )

        self._check_warnings()
        self.notify_changes(changes)
        self.__generate_report_file()
        self.__generate_report_html()

        return GPC_ERR_CODE_SUCCESS if succeed else GPC_ERR_CODE_PROJECT_FAILURE

    def _print_merged_config(self):
        if not self.params.dump_merged_config:
            return

        click.secho(f"Generating Merged Config: {self.params.dump_merged_config}", fg="cyan")

        with open(self.params.dump_merged_config, "w", encoding="utf-8") as f:
            anyconfig.dump(self.raw_config, f, ac_parser="json", indent=2)

    def _check_warnings(self):
        if self._warnings and self.params.mode == RunMode.DRY_RUN:
            click.secho(
                "/!\\ The following warnings occurred during dry-run execution. "
                "If you try it in apply mode the execution might fail.",
                fg="red",
            )
            for project_url, warnings in self._warnings.items():
                click.secho(f"  >> Configuration for project {project_url} has warnings.", fg="red")
                for sections, warn_messages in warnings.items():
                    click.secho(
                        "    >>> Error for sections {}:\n       >>> {}".format(
                            sections, "\n      >>> ".join(warn_messages)
                        ),
                        fg="red",
                    )

    def apply_for_groups(self, changed_groups) -> bool:
        matcher = GroupRuleMatcher(
            gitlab=self.gitlab,
            raw_config=self.raw_config,
            list_update_behavior=self.get_list_update_behavior(),
        )
        succeed = True
        nbr_executions = 0
        for group_rule in matcher.find_rules():
            group = group_rule.group_path.rstrip("/")
            rule = group_rule.rule
            self._rules_used.extend(rule.rule_name)
            click.secho(f"\n\nRule for group {group}:")
            if not is_existing_group(self.gitlab, group):
                click.secho(
                    "/!\\ Error: "
                    f"The group {group} does not exist. Check the group name, "
                    "and the rights of your token.",
                    fg="red",
                )
                succeed = False
                continue
            try:
                rule_exec = GroupRuleExecutor(
                    gl=self.gitlab,
                    group_path=group,
                    rule=rule,
                    gpc_params=self.params,
                )
                nbr_executions += 1
                succeed = rule_exec.execute() and succeed
                if rule_exec.warnings:
                    self._warnings[rule_exec.group.web_url] = rule_exec.warnings
                if rule_exec.has_changes():
                    changed_groups[group] = rule_exec.get_diff_json()
            except Exception as e:
                self._group_report.append(
                    {
                        "exception": str(e),
                        "trace": traceback.format_exc().splitlines(),
                        "group_name": group,
                        "rule": rule,
                    }
                )
                click.secho(f"ERROR on group {group}: {str(e)}", fg="red")
                succeed = False
                if self.params.debug:
                    click.echo("--debug mode: stopping")
                    raise
                click.secho(
                    "More information about the error are written in the report.",
                    fg="red",
                )
                click.echo("Continuing with next job...")
            else:
                self._group_report.append(rule_exec.get_report())

        log.info(
            "GPC configured groups.",
            configurator=self.params.config_project_url,
            mode=self.params.mode,
            number_executions=int(nbr_executions),
        )
        return succeed

    def project_executor(
        self,
        project_rule,
    ):
        project = project_rule.project_path
        rule = project_rule.rule
        self._rules_used.extend(rule.rule_name)
        if not is_existing_project(self.gitlab, project):
            click.secho(
                "/!\\ Error: "
                f"The project {project} does not exist. Check the project name, "
                "and the rights of your token.",
                fg="red",
            )
            succeed = False
            return None, succeed, project
        if is_archived_project(self.gitlab, project):
            click.secho(f"The project {project} is archived, we can not update id")
            return None, True, project
        try:
            rule_exec = ProjectRuleExecutor(
                gl=self.gitlab,
                project_path=project,
                rule=rule,
                gpc_params=self.params,
            )
            succeed = rule_exec.execute()
            if rule_exec.warnings:
                self._warnings[rule_exec.project.web_url] = rule_exec.warnings
        except Exception as e:
            self._project_report.append(
                {
                    "exception": str(e),
                    "trace": traceback.format_exc().splitlines(),
                    "project_name": project,
                    "rule": rule,
                }
            )
            click.secho(f"ERROR on project {project}: {str(e)}", fg="red")
            succeed = False
            if self.params.debug:
                click.echo("--debug mode: stopping")
                raise
            click.secho(
                "More information about the error are written in the report.",
                fg="red",
            )
            click.echo("Continuing with next job...")
            return None, succeed, project
        self._project_report.append(rule_exec.get_report())
        return rule_exec, succeed, project

    def apply_for_projects(self, changed_projects) -> bool:
        matcher = ProjectRuleMatcher(
            gitlab=self.gitlab,
            raw_config=self.raw_config,
            list_update_behavior=self.get_list_update_behavior(),
        )

        succeed = True
        nbr_executions = 0
        click.secho(f"Using {self.params.max_workers} workers for threadpool", fg="cyan")
        with ThreadPoolExecutor(max_workers=self.params.max_workers) as thread_executor:
            futures = []
            for project_rule in self.iter_on_projets_with_rules(matcher):
                futures.append(
                    thread_executor.submit(
                        self.project_executor,
                        project_rule,
                    )
                )
            for future in as_completed(futures):
                result, status, project = future.result()
                succeed = succeed and status
                nbr_executions += 1
                if result:
                    result.echo_execution()
                    if result.has_changes():
                        changed_projects[project] = result.get_diff_json()
                    raise_errors = result.raise_if_error
                    if raise_errors:
                        succeed = False

        log.info(
            "GPC configured projects.",
            configurator=self.params.config_project_url,
            mode=self.params.mode,
            number_executions=int(nbr_executions),
        )

        return succeed

    def __generate_report_html(self):
        if self.params.report_html:
            self.format_report()
            self._generate_html_report()

    def __generate_report_file(self):
        if self.params.report_file:
            self.format_report()
            json_report = process_json_for_report(self._report)
            click.secho(f"Generating JSON report: {self.params.report_file}", fg="cyan")
            output_json_file = Path(self.params.report_file).absolute()
            dir_output = Path.dirname(output_json_file)
            dir_output.makedirs_p()
            with open(output_json_file, "w", encoding="utf-8") as f:
                anyconfig.dump(json_report, f, ac_parser="json", indent=2)

    def load_rules(self):
        for project_rule in self.raw_config.get("projects_rules", []):
            self.project_rules[project_rule.rule_name] = project_rule
        log.debug("Found project rules", project_rules_name=list(self.project_rules.keys()))

        for group_rule in self.raw_config.get("groups_rules", []):
            self.group_rules[group_rule.rule_name] = group_rule
        log.debug("Found group rules", group_rules_name=list(self.group_rules.keys()))

    def iter_on_projets_with_rules(self, matcher: ProjectRuleMatcher) -> GenProjectPathRules:
        """Deglob the project name and uniquify it."""
        return self._handle_project_exclusion(
            self._iter_list_project_from_path(matcher.find_rules())
        )

    def _iter_list_project_from_path(
        self, iter_prog_rule: GenProjectPathRules
    ) -> GenProjectPathRules:
        for ppr in iter_prog_rule:
            yield from self._generates_project_from_path(ppr)

    def _generates_project_from_path(self, ppr: ProjectPathRule) -> GenProjectPathRules:
        if ppr.is_root_path():
            for p in self.gitlab.projects.list(all=True, archived=False, iterator=True, lazy=True):
                yield ProjectPathRule(
                    project_path=p.path_with_namespace,
                    rule=ppr.rule,
                    recursive=ppr.recursive,
                    excludes=ppr.excludes,
                    not_seen_yet_only=ppr.not_seen_yet_only,
                )
        elif self.is_path_a_group(ppr.project_path):
            g = self.get_group(ppr.project_path)
            for p in g.projects.list(all=True, iterator=True, lazy=True):
                # The shared projects of a group are excluded
                if is_shared_project(p, g):
                    continue
                log.debug("Found project from group", path=p.path_with_namespace)
                yield ProjectPathRule(
                    project_path=p.path_with_namespace,
                    rule=ppr.rule,
                    recursive=ppr.recursive,
                    excludes=ppr.excludes,
                    not_seen_yet_only=ppr.not_seen_yet_only,
                )
            if not ppr.recursive:
                return
            sg = g.subgroups.list(all=True, lazy=True, iterator=True)
            for subgrp in sg:
                pppr = ProjectPathRule(
                    project_path=subgrp.full_path,
                    rule=ppr.rule,
                    recursive=ppr.recursive,
                    excludes=ppr.excludes,
                    not_seen_yet_only=ppr.not_seen_yet_only,
                )
                yield from self._generates_project_from_path(pppr)
        else:
            # It is a project, simply return it
            yield ProjectPathRule(
                project_path=ppr.project_path,
                rule=ppr.rule,
                recursive=ppr.recursive,
                excludes=ppr.excludes,
                not_seen_yet_only=ppr.not_seen_yet_only,
            )

    def is_path_a_group(self, project_glob: str) -> bool:
        return self._is_path_a_group(project_glob.strip("/"))

    @cachedmethod("_cache")
    def _is_path_a_group(self, project_glob: str) -> bool:
        try:
            get_group(self.gitlab, project_glob)
            return True
        except gl_exceptions.GitlabGetError:
            return False
        except gl_exceptions.GitlabAuthenticationError:
            click.secho(
                f"ERROR: Cannot Authenticate {project_glob}. " "Do you have enough permission ?",
                fg="white",
                bg="red",
            )
            sys.exit(GPC_ERR_CODE_PROJECT_FAILURE)

    def get_group(self, path_with_namespace: str) -> GitlabGroup:
        g = get_group(self.gitlab, path_with_namespace.strip("/"))
        return g

    def _handle_project_exclusion(self, iter_prog_rule: GenProjectPathRules) -> GenProjectPathRules:
        projects_configured = []  # type: List[str]
        for ppr in iter_prog_rule:
            if ppr.not_seen_yet_only and ppr.project_path in projects_configured:
                log.info(f"Skipping reapply on project {ppr.project_path}, already done earlier")
                continue
            if self.params.projects and ppr.project_path not in self.params.projects:
                log.info(f"Skipping project {ppr.project_path}")
                continue
            projects_configured.append(ppr.project_path)
            if not ppr.excludes:
                yield ppr
                continue
            for excl in ppr.excludes:
                if excl.startswith("^"):
                    if self._compiled_re(excl).match(ppr.project_path):
                        log.debug(
                            f"Excluding project {ppr.project_path} because of regular expression "
                            f"exclusion rule: {excl}"
                        )
                        self._excluded_projects.append(
                            {"project": ppr.project_path, "exclusion_rule": excl}
                        )
                        break
                else:
                    if self.exclude_project(excl, ppr.project_path):
                        log.debug(
                            f"Excluding project {ppr.project_path} because exclusion rule: {excl}"
                        )
                        self._excluded_projects.append(
                            {"project": ppr.project_path, "exclusion_rule": excl}
                        )
                        break
            else:
                yield ppr

    @staticmethod
    def exclude_project(exclusion, project_path):
        exclusion_clean = clean_gitlab_project_name(exclusion)
        project_path_clean = clean_gitlab_project_name(project_path)
        if exclusion_clean == project_path_clean:
            return True
        # exclude subprojects
        if project_path_clean.startswith(exclusion_clean):
            return project_path_clean[len(exclusion_clean) :][0] == "/"
        return False

    @cachedmethod("_cache")
    def _compiled_re(self, re_pattern: str) -> Pattern:
        return re.compile(re_pattern)

    def format_report(self):
        self._report = {
            "excluded": self._excluded_projects,
            "projects_report": self._project_report,
            "groups_report": self._group_report,
        }
        no_used_rules = list(set(self.rules) - set(self._rules_used))
        if no_used_rules:
            self._report["rules_not_used"] = no_used_rules

    def _generate_html_report(self):
        json_report = process_json_for_report(self._report)
        tpl = load_template("report.html.j2")
        click.secho(f"Generating HTML report: {self.params.report_html}", fg="cyan")
        output_html_file = Path(self.params.report_html).absolute()
        dir_output = Path.dirname(output_html_file)
        dir_output.makedirs_p()
        try:
            with output_html_file.open("w") as f:
                groups = [
                    {
                        "id": x["group_name"].replace("/", ""),
                        "category": x["group_name"].rpartition("/")[0],
                        "title": x["group_name"],
                    }
                    for x in json_report.get("groups_report", [])
                ]
                projects = [
                    {
                        "id": x["project_name"].replace("/", ""),
                        "category": x["project_name"].rpartition("/")[0],
                        "title": x["project_name"],
                    }
                    for x in json_report.get("projects_report", [])
                ]
                f.write(
                    tpl.render(
                        groups=groups,
                        projects=projects,
                        report=json_report,
                        gpc_version=version(),
                    )
                )
        except:  # pylint: disable=bare-except
            log.error("HTML generation failed, exiting without change error code")

    def get_errors(self):
        group_project_reports = self._group_report + self._project_report
        return [r for r in group_project_reports if "errors" in r or "exception" in r]

    def notify_changes(self, changes):
        watchers = self.get_watchers()
        errors_event = self.get_errors()
        do_notify = errors_event or changes
        if self.params.mode == RunMode.APPLY and do_notify and watchers:
            all_changes, changes_event = generate_event(changes)
            send_change_event_email(
                self.gitlab,
                changes_event,
                errors_event,
                watchers,
                all_changes=all_changes,
                smtp_server=self.params.smtp_server,
                smtp_port=self.params.smtp_port,
                email_author=self.params.email_author,
            )

    def get_watchers(self):
        watchers = self.params.watchers if self.params.watchers else os.getenv("GPC_WATCHERS")
        if watchers:
            watchers = watchers.replace(";", "\n")
            return [w.strip() for w in watchers.split("\n")]
        return None

    def get_list_update_behavior(self) -> ListOverrideBehavior:
        if self.params.preview:
            return ListOverrideBehavior.APPEND
        return ListOverrideBehavior.REPLACE
