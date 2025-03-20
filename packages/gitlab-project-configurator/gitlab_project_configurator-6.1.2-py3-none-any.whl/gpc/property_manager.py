"""
Manager of property bean.
"""

# Standard Library
from abc import ABC
from abc import abstractmethod

# Third Party Libraries
import attr
import click

from gitlab.exceptions import GitlabCreateError
from gitlab.exceptions import GitlabGetError
from gitlab.exceptions import GitlabUpdateError
from structlog import get_logger


log = get_logger()


@attr.s
class PropertyBean(ABC):
    name = attr.ib()  # type: str

    @abstractmethod
    def get_query(self):
        raise NotImplementedError()

    @abstractmethod
    def to_dict(self):
        raise NotImplementedError()


class PropertyManager:
    def __init__(self, manager):
        self.manager = manager

    def create(self, property_bean: PropertyBean, project_path):
        try:
            self.rm_existing(property_bean.name)
            obj_create = property_bean.get_query()
            self.manager.create(obj_create, retry_transient_errors=True)
        except GitlabCreateError as e:
            click.secho(str(e.error_message), fg="red")
            if e.response_code == 403:
                click.secho(
                    f"On project {project_path}: Access forbidden. "
                    "Please ensure your Gitlab token has "
                    "'owner' membership to the projects",
                    fg="red",
                )
            else:
                raise e

    def update(self, property_bean: PropertyBean, project_path):
        try:
            obj_create = property_bean.get_query()
            self.manager.update(property_bean.name, obj_create, retry_transient_errors=True)
        except GitlabUpdateError as e:
            click.secho(
                f"Error updating property on {project_path}: {e.error_message}",
                fg="red",
            )
            raise e

    def rm_existing(self, property_bean: str):
        try:
            self.manager.get(property_bean, retry_transient_errors=True).delete(
                retry_transient_errors=True
            )
        except GitlabGetError:
            pass
