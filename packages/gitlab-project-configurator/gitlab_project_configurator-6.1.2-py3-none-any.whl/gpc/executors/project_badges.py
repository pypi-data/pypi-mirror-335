# Standard Library
from collections import Counter
from typing import List  # pylint: disable=unused-import
from typing import Optional  # pylint: disable=unused-import

# Third Party Libraries
import attr
import click

from boltons.cacheutils import cachedproperty
from boltons.iterutils import unique
from dotmap import DotMap
from gitlab.exceptions import GitlabDeleteError
from structlog import get_logger

# Gitlab-Project-Configurator Modules
from gpc.change_setting import ChangeUnNamedPropertySetting
from gpc.executors.properties_updator import ChangePropertyExecutor
from gpc.parameters import RunMode
from gpc.property_manager import PropertyBean
from gpc.property_manager import PropertyManager


log = get_logger()

WARNING_MSG_GROUP_BADGE = (
    "/!\\ You try to edit or remove a group badge from a "
    "project. This operation can not be performed. "
    "badge link: {}, badge image : {}"
)


@attr.s(eq=False)
class ProjectBadge(PropertyBean):
    link_url = attr.ib()  # type: str
    image_url = attr.ib()  # type: str
    kind = attr.ib(default="project")  # type: Optional[str]
    badge_id = attr.ib(default=None)  # type: Optional[str]

    @property
    def is_group(self):
        return self.kind == "group"

    @staticmethod
    def to_project_badges(api_project_badges):
        project_badges = []  # type: List[ProjectBadge]
        for api_project_badge in api_project_badges:
            project_badges.append(ProjectBadge.to_project_badge(api_project_badge))
        log.debug("Project badges", project_badges=project_badges)
        return project_badges

    @staticmethod
    def to_project_badge(api_project_badge):
        name = str(api_project_badge.id)
        if api_project_badge.name:
            name = api_project_badge.name
        return ProjectBadge(
            name=name,
            link_url=api_project_badge.link_url,
            image_url=api_project_badge.image_url,
            kind=api_project_badge.kind,
            badge_id=api_project_badge.id,
        )

    def get_query(self):
        return {
            "name": self.name,
            "link_url": self.link_url,
            "image_url": self.image_url,
        }

    def to_dict(self):
        return {
            "name": self.name,
            "link_url": self.link_url,
            "image_url": self.image_url,
            "kind": self.kind,
        }

    def __eq__(self, other):
        if not isinstance(other, ProjectBadge):
            return False
        # Note name (badge_id) is not compared, since name cannot be set
        return self.link_url == other.link_url and self.image_url == other.image_url


class ChangeProjectBadge(ChangeUnNamedPropertySetting):
    sub_properties = ["link_url", "image_url"]
    status_to_process = ["removed", "updated", "kept", "added"]

    @cachedproperty
    def action(self):
        if {m["status"] for m in self.differences.values()} == {"kept"}:
            return "kept"
        if self.after and self.before is None:
            return "added"
        if self.after is None and self.before:
            return "removed"
        return "updated"


class ProjectBadgeExecutor(ChangePropertyExecutor):
    order = 70
    name = "badges"
    sections = ["badges"]

    def _apply(self):
        if self.changes:
            project_badges = self.changes[0]
            self._save_properties(
                PropertyManager(self.item.badges),
                project_badges,
                project_badges.after,
            )

    def _save_properties(self, manager, change_properties, properties):
        for name in change_properties.remove:
            try:
                prop_dot_mat = DotMap(change_properties.differences.get(name, {}))
                if prop_dot_mat.before.kind == "group":
                    click.secho(
                        WARNING_MSG_GROUP_BADGE.format(
                            prop_dot_mat.before.link_url, prop_dot_mat.before.image_url
                        ),
                        fg="yellow",
                    )
                else:
                    badge_id = self._get_badge_to_rm(name, change_properties.before)
                    manager.rm_existing(badge_id)
            except GitlabDeleteError as e:
                click.secho(f"ERROR: {str(e.error_message)}", fg="red")
        self._update_or_create(manager, change_properties, properties)
        self._drop_duplicates(manager)

    def _drop_duplicates(self, manager):
        badge_names = [b.name for b in self.item.badges.list(all=True)]
        name_counter = Counter(badge_names)
        for name in set(badge_names):
            for _ in range(name_counter[name] - 1):
                badge_id = self._get_badge_to_rm_raw(name, self.item.badges.list(all=True))
                manager.rm_existing(badge_id)

    def _get_badge_to_rm(self, name, project_badges):
        for badge in project_badges:
            if name == badge.name:
                return badge.badge_id
        return None

    def _get_badge_to_rm_raw(self, name, project_badges):
        for badge in project_badges:
            if name == badge.name:
                return badge.id
        return None

    def _update(self, mode: RunMode, members_user, members_group):
        keep_existing_badges = self.rule.get("keep_existing_badges", True)
        wanted_badges = []
        existing_badges = ProjectBadge.to_project_badges(
            b
            for b in self.item.badges.list(  # type: ignore
                iterator=True, retry_transient_errors=True
            )
            if b.kind == "project"
        )

        # Add the mandatory "under GPC" badge
        if self.gpc_params.config_project_url:
            wanted_badges.append(
                ProjectBadge(
                    name=self.gpc_params.gpc_enabled_badge_name or "UNDER_GPC_BADGE",
                    link_url=self._resolve_variables(self.gpc_params.config_project_url),
                    image_url=self._resolve_variables(self.gpc_params.gpc_enabled_badge_url),
                )
            )
        self._inject_external_accepted_badges(existing_badges, wanted_badges)
        if "badges" in self.rule and self.rule.badges:
            for badge in self.rule.badges:
                name = self._resolve_variables(badge.link_url)
                if not name:
                    name = badge.link_url
                if "name" in badge and badge.name:
                    name = badge.name
                wanted_badges.append(
                    ProjectBadge(
                        name=name,
                        image_url=self._resolve_variables(badge.image_url),
                        link_url=self._resolve_variables(badge.link_url),
                    )
                )
        if keep_existing_badges:
            # replace all badges that do not have a name
            badges_to_replace = self._find_badge_without_name(existing_badges, wanted_badges)
            existing_badges = ProjectBadgeExecutor.prepare_to_keep_badges(
                existing_badges, wanted_badges
            )
            existing_badges.extend(badges_to_replace)
        else:
            # display warning if the user remove group badges
            ProjectBadgeExecutor.check_group_badges(existing_badges, wanted_badges)
        wanted_badges = unique(wanted_badges, key=lambda badge: badge.image_url)
        if wanted_badges:
            self.changes.append(
                ChangeProjectBadge(
                    "project_badges",
                    sorted(existing_badges, key=lambda x: x.name),
                    sorted(wanted_badges, key=lambda x: x.name),
                    self.show_diff_only,
                )
            )

    @staticmethod
    def check_group_badges(existing_badges, wanted_badges):
        for existing_badge in existing_badges:
            if existing_badge.is_group and existing_badge not in wanted_badges:
                click.secho(
                    WARNING_MSG_GROUP_BADGE.format(
                        existing_badge.link_url, existing_badge.image_url
                    ),
                    fg="yellow",
                )

    @staticmethod
    def prepare_to_keep_badges(existing_badges, wanted_badges):
        existing_badges_prepared = []
        for existing_badge in existing_badges:
            for wanted_badge in wanted_badges:
                if existing_badge.name == wanted_badge.name:
                    existing_badges_prepared.append(existing_badge)
                    break
        return existing_badges_prepared

    def _find_badge_without_name(
        self, existing_badges: List[ProjectBadge], wanted_badges: List[ProjectBadge]
    ):
        badges_found = []
        for wanted_project_badge in wanted_badges:
            for existing_badge in existing_badges:
                if (
                    existing_badge == wanted_project_badge
                    and wanted_project_badge.name != existing_badge.name
                ):
                    badges_found.append(existing_badge)
        return badges_found

    def _inject_external_accepted_badges(
        self, existing_badges: List[ProjectBadge], wanted_badges: List[ProjectBadge]
    ):
        if not self.gpc_params.gpc_accepted_external_badge_image_urls:
            return
        for existing_badge in existing_badges:
            if existing_badge.image_url in self.gpc_params.gpc_accepted_external_badge_image_urls:
                wanted_badges.append(existing_badge)

    def _resolve_variables(self, txt: Optional[str]) -> str:
        if not txt:
            return ""
        return txt.replace("%{gpc_gitlab_url}", self.gitlab.url.strip("/"))
