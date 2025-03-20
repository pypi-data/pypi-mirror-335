"""
Change executor abstract class.
"""

# Standard Library
import traceback

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING  # pylint: disable=unused-import
from typing import Dict
from typing import List  # pylint: disable=unused-import
from typing import Union

# Third Party Libraries
import click

from gitlab import Gitlab
from gitlab.exceptions import GitlabError
from structlog import getLogger

# Gitlab-Project-Configurator Modules
from gpc.change_setting import ChangeSetting  # pylint: disable=unused-import
from gpc.helpers.exceptions import GpcProfileError
from gpc.helpers.exceptions import GpcVariableError
from gpc.helpers.gitlab_helper import MAP_ACCESS
from gpc.parameters import GpcParameters
from gpc.parameters import RunMode


if TYPE_CHECKING:
    # Third Party Libraries
    from gitlab.v4.objects import Group
    from gitlab.v4.objects import Project

    # Gitlab-Project-Configurator Modules
    from gpc.helpers.types import Rule
log = getLogger()


class ChangeExecutor(ABC):
    applicable_to = ["project"]  # project by default but it can also be used for group
    sections = []  # type: List[str]

    def __init__(
        self,
        gl: Gitlab,
        item_path: str,
        item: Union["Project", "Group"],
        rule: "Rule",
        gpc_params: GpcParameters,
    ):
        self.gitlab = gl
        self.item = item
        self.item_path = item_path
        self.rule = rule
        self.gpc_params = gpc_params
        self.changes = []  # type: List[ChangeSetting]
        self.errors = []  # type: List[Dict]
        self.warnings = []  # type: List[str]
        self.error_message = ""
        self.success = True

    @staticmethod
    def _get_role_id(role_name):
        role_id = MAP_ACCESS.get(role_name.lower(), None)
        if role_id is None:
            raise GpcProfileError(
                f"The role '{role_name}' is not acceptable, "
                f"it should be {list(MAP_ACCESS.keys())}"
            )
        return role_id

    def apply(self):
        if self.success:
            try:
                self._apply()
            except BaseException as exc:
                self.error_message = str(exc)
                self.success = False
                self.errors.append(
                    {
                        "exception": self.error_message,
                        "trace": traceback.format_exc().splitlines(),
                    }
                )
                click.secho(
                    f"ERROR on sections {self.sections}"
                    f"\n{self.error_message}"
                    f" (Project path: {self.item_path})",
                    fg="red",
                )
        else:
            click.secho(
                f"Error: We don't apply the configuration for sections {self.sections} because an "
                f"error occurred previously: {self.error_message} (project: {self.item_path})",
                fg="red",
            )

    def update(self, mode: RunMode, members_user, members_group):
        try:
            self._update(mode, members_user, members_group)
        except BaseException as exc:
            self.error_message = str(exc)
            self.success = False
            # pylint: disable=no-member
            if isinstance(exc, GitlabError) and exc.response_code == 403:
                self.error_message = (
                    f"On project {self.item_path}: Access forbidden. "
                    "Please ensure your Gitlab token has 'owner' "
                    "membership to the projects"
                )
            # pylint: enable=no-member
            self.errors.append(
                {
                    "exception": self.error_message,
                    "trace": traceback.format_exc().splitlines(),
                }
            )
            log.exception("error during change executor update")
            click.secho(f"ERROR: {self.error_message}", fg="red")
            if isinstance(exc, GpcVariableError):
                click.secho(
                    "/!\\ Environment variables could not be updated, "
                    "but the others settings will by updated.",
                    fg="yellow",
                )

    @property
    def raise_errors(self):
        return False

    @abstractmethod
    def _update(self, mode: RunMode, members_user: List[int], members_group: List[str]):
        raise NotImplementedError()

    @abstractmethod
    def _apply(self):
        raise NotImplementedError()

    @property
    def show_diff_only(self):
        return self.gpc_params.diff
