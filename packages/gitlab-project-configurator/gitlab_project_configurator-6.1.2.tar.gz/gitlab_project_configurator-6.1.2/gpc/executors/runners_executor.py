"""
Make the update of label.
"""

# Standard Library
import os

from typing import Dict

# Third Party Libraries
import attr
import click

from gitlab.exceptions import GitlabCreateError
from gitlab.exceptions import GitlabDeleteError
from gitlab.exceptions import GitlabGetError

# Gitlab-Project-Configurator Modules
from gpc.change_setting import ChangePropertySetting
from gpc.executors.properties_updator import ChangePropertyExecutor
from gpc.parameters import RunMode
from gpc.property_manager import PropertyBean


@attr.s
class ProjectRunner(PropertyBean):
    enabled = attr.ib()  # type: bool

    def get_query(self):
        return {"runner_id": self.name}

    def to_dict(self):
        return {"runner_id": self.name, "enabled": self.enabled}


class ChangeRunners(ChangePropertySetting):
    sub_properties = ["enabled"]
    status_to_process = ["updated", "kept"]

    def _is_updated(self, before_name, before, after_properties):
        result = {}
        if before != after_properties[before_name]:
            after_prop = after_properties[before_name].to_dict()
            result = {
                "status": "updated",
                "before": before.to_dict(),
                "after": after_prop,
            }
        return result

    def _is_kept(self, before_name, before, after_properties):
        return {
            "status": "kept",
            "before": before.to_dict(),
            "after": after_properties[before_name].to_dict(),
        }

    def _added_properties(self, differences: Dict, after_properties: Dict, **kwargs):
        # no added properties for runner.
        pass


class RunnersSettingExecutor(ChangePropertyExecutor):
    order = 90
    name = "runners"
    sections = ["runners"]

    def _apply(self):
        if self.changes:
            change_runners = self.changes[0]
            for project_runner in change_runners.after:
                if project_runner.name not in change_runners.update_or_create:
                    continue
                if project_runner.enabled:
                    try:
                        self.item.runners.create(
                            project_runner.get_query(), retry_transient_errors=True
                        )
                    except GitlabCreateError:
                        click.secho(
                            f"/!\\ The runner {project_runner.name} "
                            f"is already enabled for the project {self.item_path}."
                        )
                else:
                    try:
                        self.item.runners.delete(project_runner.name, retry_transient_errors=True)
                    except GitlabDeleteError:
                        click.secho(
                            f"/!\\ The runner {project_runner.name} is already "
                            f"disabled for the project {self.item_path}."
                        )

    def _update(self, mode: RunMode, members_user, members_group):
        if "runners" in self.rule and self.rule.runners is not None:
            new_project_runners = []
            old_project_runners = []
            current_project_runners = {
                x.id: x.is_shared
                for x in self.item.runners.list(  # type: ignore
                    iterator=True, retry_transient_errors=True
                )
            }
            for runner in self.rule.runners:
                new_project_runner, old_project_runner = self.check_runner(
                    mode, runner, current_project_runners
                )
                if new_project_runner and old_project_runner:
                    new_project_runners.append(new_project_runner)
                    old_project_runners.append(old_project_runner)
            self.changes.append(
                ChangeRunners(
                    "runners",
                    old_project_runners,
                    new_project_runners,
                    self.show_diff_only,
                )
            )

    def check_runner(self, mode, runner, current_project_runners):
        new_project_runner = None
        old_project_runner = None
        runner_id = self._get_runner_id(mode, runner)
        if runner_id in current_project_runners and current_project_runners[runner_id]:
            click.secho(
                f"/!\\ We can not update the runner {runner_id} for the project"
                f" {self.item_path} because it is a shared runner.",
                color="yellow",
            )
        elif self.exist_runner(runner_id):
            new_project_runner = ProjectRunner(name=str(runner_id), enabled=runner.enabled)
            if runner_id in current_project_runners:
                old_project_runner = ProjectRunner(name=str(runner_id), enabled=True)
            else:
                old_project_runner = ProjectRunner(name=str(runner_id), enabled=False)
        else:
            click.secho(f"/!\\ The runner {runner_id} does not exist.", color="yellow")
        return new_project_runner, old_project_runner

    def _get_runner_id(self, mode, runner):
        runner_id = runner.get("runner_id", None)
        if runner_id:
            return runner_id
        runner_id_from_envvar = runner.get("runner_id_from_envvar", None)
        if runner_id_from_envvar:
            runner_id = os.getenv(runner_id_from_envvar)
            if runner_id:
                return int(runner_id)
            warning_msg = f"/!\\ Environment variable {runner_id_from_envvar} not set."
            self.warnings.append(warning_msg)
            RunnersSettingExecutor._send_warning_msg(mode, warning_msg)
        else:
            warning_msg = (
                "/!\\ Neither runner_id or runner_id_from_envvar "
                "are not set in your configuration."
            )
            self.warnings.append(warning_msg)
            RunnersSettingExecutor._send_warning_msg(mode, warning_msg)
        return None

    @staticmethod
    def _send_warning_msg(mode, msg):
        click.secho(msg, fg="red")
        if mode is RunMode.DRY_RUN:
            click.secho(
                "/!\\ In Apply or Interactive mode your configuration will fail.",
                fg="yellow",
            )
        else:
            raise ValueError(msg)

    def exist_runner(self, runner_id):
        try:
            self.gitlab.runners.get(runner_id, retry_transient_errors=True)
            return True
        except GitlabGetError:
            return False
