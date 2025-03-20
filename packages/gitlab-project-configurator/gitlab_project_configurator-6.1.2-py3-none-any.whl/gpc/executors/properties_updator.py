"""
Change executor abstract class.
"""

# Standard Library
from typing import Optional

# Third Party Libraries
import click

from gitlab import Gitlab
from gitlab.exceptions import GitlabCreateError
from gitlab.exceptions import GitlabDeleteError
from gitlab.exceptions import GitlabGetError
from gitlab.v4.objects import Project

# Gitlab-Project-Configurator Modules
from gpc.executors.change_executor import ChangeExecutor
from gpc.helpers.types import ProjectRule
from gpc.parameters import GpcParameters


# pylint: disable= abstract-method


class PropertyUpdatorMixin:
    def _save_properties(self, manager, change_properties, properties):
        for name in change_properties.remove:
            try:
                manager.rm_existing(name)
            except GitlabDeleteError as e:
                click.secho(f"ERROR: {str(e.error_message)}", fg="red")
        self._update_or_create(manager, change_properties, properties)

    def _update_or_create(self, manager, change_properties, properties):
        # target to update or create
        variables_to_cu = change_properties.update_or_create
        for variable in properties:
            if variable.name in variables_to_cu:
                try:
                    manager.create(variable, self.item_path)
                except GitlabCreateError as e:
                    click.secho(f"ERROR: {str(e.error_message)}", fg="red")


class ChangePropertyExecutor(ChangeExecutor, PropertyUpdatorMixin):
    pass


class CustomService:
    """Class to manage Service object returned by project.services.get

    to fix this issue: https://python-gitlab.readthedocs.io/en/stable/gl_objects/projects.html#id18
    """

    _class_attrs = [
        "_api_service",
        "is_lazy",
        "_exist",
        "_update_properties",
    ]

    def __init__(self, api_service, exist):
        self.__dict__.update(
            {
                "_api_service": api_service,
                "is_lazy": api_service._lazy,
                "_exist": exist,
                "_update_properties": {},
            }
        )

    def save(self, **kwargs):
        self._api_service.save(**kwargs)

    def delete(self, **kwargs):
        if not self._exist:
            return
        self._api_service.delete(**kwargs)

    def __getattr__(self, name: str):
        if name in self.__dict__:
            return self.__dict__[name]
        return getattr(self._api_service, name)

    def __setattr__(self, key, value):
        if key in self.__dict__:
            self.__dict__[key] = value
        else:
            setattr(self._api_service, key, value)


class ChangeServicePropertyExecutor(ChangePropertyExecutor):
    service_name = ""

    def __init__(
        self,
        gl: Gitlab,
        item_path: str,
        item: Project,
        rule: ProjectRule,
        gpc_params: GpcParameters,
    ):
        super().__init__(gl, item_path, item, rule, gpc_params)
        self._service: Optional[CustomService] = None

    @property
    def service(self) -> CustomService:
        if self._service is None:
            try:
                self._service = CustomService(
                    self.item.services.get(self.service_name, retry_transient_errors=True),
                    exist=True,
                )
            except GitlabGetError:
                self._service = CustomService(
                    self.item.services.get(self.service_name, lazy=True), exist=False
                )

        return self._service

    def _apply(self):
        if self.service_name.lower() in self.gpc_params.force:
            click.secho(f"'{self.service_name}': settings force updated!", fg="yellow")
            self.service.save(retry_transient_errors=True)
        elif self.changes:
            service_property = self.changes[0]
            if not service_property.has_diff():
                return
            if service_property.after.disabled:
                self.service.delete(retry_transient_errors=True)
            else:
                self.service.save(retry_transient_errors=True)
