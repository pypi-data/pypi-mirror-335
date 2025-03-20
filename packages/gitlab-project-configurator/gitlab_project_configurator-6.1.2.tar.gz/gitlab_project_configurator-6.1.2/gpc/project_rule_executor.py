"""
Apply rules on a Gitlab Project.
"""

# Standard Library
from abc import ABC
from abc import abstractmethod
from threading import Lock
from typing import Dict  # pylint: disable=unused-import
from typing import List  # pylint: disable=unused-import

# Third Party Libraries
import click

from boltons.cacheutils import cachedproperty
from gitlab import Gitlab
from gitlab.exceptions import GitlabCreateError
from rich import box
from rich.console import Console
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from structlog import get_logger

# Gitlab-Project-Configurator Modules
from gpc.change_executors_factory import ChangeExecutorsFactory
from gpc.change_setting import ChangeSetting
from gpc.executors.change_executor import ChangeExecutor
from gpc.helpers.types import GroupRule
from gpc.helpers.types import ProjectName
from gpc.helpers.types import ProjectRule
from gpc.parameters import GpcParameters
from gpc.parameters import RunMode


log = get_logger()
lock = Lock()
SUCCESS = "success"
FAIL = "fail"


def echo_report_header(header_content):
    click.secho(ChangeSetting.HORIZONTAL_DOUBLEBAR)
    click.secho(header_content, fg="magenta", bold=True)
    click.secho(ChangeSetting.HORIZONTAL_DOUBLEBAR)


class RuleExecutor(ABC):
    """
    Based class to preprocess set of rules for given project or group.

    I basically receive a connection to the gitlab server, a json chunk that
    represent which rules to apply and one project path, and I am responsible for
    doing all calls to the Gitlab API to apply the changes.

    I support the 3 execution modes: dry run, interactive, apply.
    """

    def __init__(
        self,
        gl: Gitlab,
        rule: ProjectRule,
        gpc_params: GpcParameters,
    ):
        self.gitlab = gl
        self.rule = rule
        self.gpc_params = gpc_params

    @abstractmethod
    def execute(self):
        raise NotImplementedError

    @property
    def executors(self) -> List[ChangeExecutor]:
        return []

    def _echo_diff_report(self, header):
        console = Console(force_terminal=True, width=140, record=True)
        table = Table(expand=True, width=140, box=box.HEAVY)
        header_panel = Panel(header, style="magenta", width=140)
        if self.gpc_params.diff and not self.has_changes():
            table.add_row("No changes found. ")
            panel_group = Group(header_panel, table)
            console.print(panel_group)
            return console.export_text()

        table.add_column("PROPERTY NAME", width=40)
        table.add_column("BEFORE", width=45)
        table.add_column("AFTER", width=45)
        table.add_column("ACTION", width=10)

        for value in self.all_change_properties():
            if not self.gpc_params.diff or value.has_diff():
                for row in value.rich_rows(console):
                    if isinstance(row, str) and row == "new_line":
                        table.add_row()
                    elif isinstance(row, str) and row == "new_section":
                        table.add_section()
                    else:
                        table.add_row(*row[0], style=row[1])

        panel_group = Group(header_panel, table)
        console.print(panel_group)
        return console.export_text()

    @property
    def status(self):
        return SUCCESS if all(x.success for x in self.executors) else FAIL

    @property
    def warnings(self):
        warnings = {}
        for x in self.executors:
            if x.warnings:
                warnings[str(x.sections)] = x.warnings
        return warnings

    @property
    def errors(self):
        errors = []
        for executor in self.executors:
            errors += executor.errors
        return errors

    def save(self):
        """Save settings."""
        if self.gpc_params.mode == RunMode.INTERACTIVE:
            if self._do_you_update():
                self._apply_changes()
        elif self.gpc_params.mode == RunMode.APPLY:
            self._apply_changes()

    @staticmethod
    def _do_you_update():
        choice = click.prompt(
            "Do you want update these changes?",
            default="y",
            type=click.Choice(["y", "n"]),
        )
        return choice == "y"

    def get_changes_json(self):
        return sorted(
            (c.to_dict() for c in self.all_change_properties()),
            key=lambda x: x["property_name"],
        )

    def get_diff_json(self):
        diff = {}
        for c in self.all_change_properties():
            if c.has_diff():
                cd = c.diff_to_dict()
                diff[cd["property_name"]] = cd
        return diff

    def _apply_changes(self):
        for executor in self.executors:
            executor.apply()

    @property
    def raise_if_error(self):
        for executor in self.executors:
            status = executor.raise_errors
            if status:
                return True
        return False

    def all_change_properties(self):
        values = []
        for executor in self.executors:
            for change in executor.changes:
                values.append(change)
        return values

    def has_changes(self):
        for change in self.all_change_properties():
            if change.has_diff():
                return True
        return False

    def update_settings(self):
        """Update all settings of gitlab object."""
        # List of the users and groups which will members of project/groups.
        members_user = []  # type: List[int]
        members_group = []  # type: List[str]
        for executor in self.executors:
            executor.update(self.gpc_params.mode, members_user, members_group)

    def get_report(self):
        report = {
            "status": self.status,
            "rule": self.rule,
            "updated": self.has_changes(),
            "changes": self.get_changes_json(),
            "diff": self.get_diff_json(),
        }
        if self.status == FAIL:
            report["errors"] = self.errors
        return report


class GroupRuleExecutor(RuleExecutor):
    def __init__(
        self,
        gl: Gitlab,
        group_path: str,
        rule: GroupRule,
        gpc_params: GpcParameters,
    ):
        super().__init__(gl, rule, gpc_params)
        self.group_path = group_path

    @cachedproperty
    def group(self):
        return self.gitlab.groups.get(self.group_path)

    # pylint: disable=invalid-overridden-method
    @cachedproperty
    def executors(self) -> List[ChangeExecutor]:  # type: ignore
        factory = ChangeExecutorsFactory()
        return factory.init_executors(
            gl=self.gitlab,
            item_path=self.group_path,
            item=self.group,
            rule=self.rule,
            gpc_params=self.gpc_params,
        )

    def update_settings(self):
        click.echo(f"Updating settings of {self.group_path}")
        return super().update_settings()

    def _apply_changes(self):
        click.echo(f"Applying changes for {self.group_path}")
        super()._apply_changes()
        click.secho(f"Changes applied for {self.group_path}")

    def execute(self):
        rule_override = "yes" if self.rule.get("custom_rules", None) else "no"
        header = (
            f"Policy for    : {self.group_path}\n"
            f"URL           : {self.group.web_url}\n"
            f"Rule name     : {self.rule.get('rule_name', 'N/A')}\n"
            f"Custom rules  : {rule_override}"
        )
        log.info(
            "Configuring group...",
            configurator=self.gpc_params.config_project_url,
            mode=self.gpc_params.mode,
            group=self.group_path,
        )
        self.update_settings()
        click.echo(f"Change for group {self.group_path}:")

        self._echo_diff_report(header)
        self.save()
        log.info(
            "Group configured.",
            configurator=self.gpc_params.config_project_url,
            mode=self.gpc_params.mode,
            project=self.group_path,
        )
        return self.status == SUCCESS

    def get_report(self):
        report = super().get_report()
        report["group_name"] = self.group_path
        return report


class ProjectRuleExecutor(RuleExecutor):
    def __init__(
        self,
        gl: Gitlab,
        project_path: ProjectName,
        rule: ProjectRule,
        gpc_params: GpcParameters,
    ):
        super().__init__(gl, rule, gpc_params)
        self.project_path = project_path

    @cachedproperty
    def project(self):
        return self.gitlab.projects.get(self.project_path, retry_transient_errors=True)

    # pylint: disable=invalid-overridden-method
    @cachedproperty
    def executors(self) -> List[ChangeExecutor]:  # type: ignore
        force_create_default_branch = (
            "force_create_default_branch" in self.rule and self.rule.force_create_default_branch
        )
        if force_create_default_branch:
            click.secho(
                f"IMPORTANT: force_create_default_branch is activated for {self.rule.rule_name[0]} "
                "rule\n"
                "This means that: \n"
                "- if the desired default branch does not exist it will be created on top of "
                "the current default branch",
                fg="yellow",
            )

        if self.project.empty_repo:
            click.secho(
                f"IMPORTANT: The repository for {self.project.path_with_namespace} is empty, "
                "GPC will try to push an initial commit for you",
                fg="yellow",
            )
            data = {
                "branch": self.project.default_branch,
                "commit_message": "Initial commit",
                "actions": [
                    {
                        "action": "create",
                        "file_path": "README.md",
                        "content": "",
                    },
                ],
            }
            try:
                self.project.commits.create(data)
            except GitlabCreateError:
                click.secho(
                    f"/!\\Nothing to do for project: {self.project_path} it is an empty repository "
                    "and GPC was not able to push an initial commit "
                    f"on branch {self.project.default_branch}",
                    fg="yellow",
                )
                return []

        factory = ChangeExecutorsFactory()
        return factory.init_executors(
            gl=self.gitlab,
            item_path=self.project_path,
            item=self.project,
            rule=self.rule,
            gpc_params=self.gpc_params,
        )

    def echo_execution(self):
        with lock:
            rule_override = "yes" if self.rule.get("custom_rules", None) else "no"
            header = (
                f"\nProject {self.project_path}:\n"
                f"Policy for    : {self.project_path}\n"
                f"URL           : {self.project.web_url}\n"
                f"Rule name     : {self.rule.get('rule_name', 'N/A')}\n"
                f"Custom rules  : {rule_override}\n"
            )
            click.echo("Change for project:")
            return self._echo_diff_report(header)

    def update_settings(self):
        click.echo(f"Updating settings of {self.project_path}")
        return super().update_settings()

    def _apply_changes(self):
        click.echo(f"Applying changes for {self.project_path}")
        super()._apply_changes()
        click.echo(f"Changes applied for {self.project_path}")

    def save(self):
        if self.gpc_params.mode == RunMode.DRY_RUN:
            click.secho(f"Dry run mode: No change applied for {self.project_path}", fg="yellow")
        return super().save()

    def execute(self):
        log.info(
            "Configuring project...",
            configurator=self.gpc_params.config_project_url,
            mode=self.gpc_params.mode.value,
            project=self.project_path,
        )
        self.update_settings()
        self.save()
        log.info(
            "Project configured.",
            configurator=self.gpc_params.config_project_url,
            mode=self.gpc_params.mode,
            project=self.project_path,
        )

        return self.status == SUCCESS

    def get_report(self):
        report = super().get_report()
        report["project_name"] = self.project_path
        return report
