"""
Change executors factory class.

This class provides method to discover all class ChangeExecutor.
"""

# Standard Library
import importlib
import inspect
import os

from typing import TYPE_CHECKING
from typing import Union

# Third Party Libraries
import click

from boltons.cacheutils import cachedproperty
from gitlab import Gitlab
from gitlab.v4.objects import Group
from path import Path

# Gitlab-Project-Configurator Modules
from gpc.executors.change_executor import ChangeExecutor
from gpc.helpers.exceptions import GpcExecutorNotFound
from gpc.helpers.types import Rule
from gpc.parameters import GpcParameters


if TYPE_CHECKING:
    # Third Party Libraries
    from gitlab.v4.objects import Project


EXCLUDES = ["__init__.py"]
EXTENSION = ".py"


class ChangeExecutorsFactory:
    @cachedproperty
    def executors(self):
        dir_executors = Path(__file__).parent / "executors"
        self.load_module_form_dir(dir_executors)
        executors = []
        ChangeExecutorsFactory.get_executors(executors, ChangeExecutor)
        return sorted((c for c in executors), key=lambda x: x.order)

    def init_executors(
        self,
        gl: Gitlab,
        item_path: str,
        item: Union["Project", Group],
        rule: Rule,
        gpc_params: GpcParameters,
    ):
        item_type = "group" if isinstance(item, Group) else "project"
        if gpc_params.executor:
            executors = gpc_params.executor.split(",")
            executor_result = [
                executor(gl, item_path, item, rule, gpc_params)
                for executor in self.executors
                if item_type in executor.applicable_to and executor.name in executors
            ]
            if not executor_result:
                raise GpcExecutorNotFound(
                    f"{gpc_params.executor} is not a valid argument "
                    "(none of the given properties are valid)"
                )
            if len(executor_result) < len(executors):
                click.secho(
                    f"{len(executors)} properties set but only {len(executor_result)} will "
                    "be applied, please check if you misspelled some of them",
                    fg="yellow",
                )
            return executor_result
        return [
            executor(gl, item_path, item, rule, gpc_params)
            for executor in self.executors
            if item_type in executor.applicable_to
        ]

    @staticmethod
    def get_executors(executors, executor_class):
        for executor in executor_class.__subclasses__():
            if not inspect.isabstract(executor):
                executors.append(executor)
            ChangeExecutorsFactory.get_executors(executors, executor)

    @staticmethod
    def load_module_form_dir(dir_executors):
        files = os.listdir(dir_executors)
        for file_to_load in files:
            if file_to_load not in EXCLUDES and file_to_load.endswith(EXTENSION):
                module_to_load = file_to_load[: -len(EXTENSION)]
                importlib.import_module(f"gpc.executors.{module_to_load}", "*")
