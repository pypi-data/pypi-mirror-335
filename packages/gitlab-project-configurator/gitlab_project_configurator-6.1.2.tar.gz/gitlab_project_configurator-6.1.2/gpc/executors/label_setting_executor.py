"""
Make the update of label.
"""

# Third Party Libraries
import attr

from gitlab.exceptions import GitlabDeleteError

# Gitlab-Project-Configurator Modules
from gpc.change_setting import ChangePropertySetting
from gpc.executors.profile_label_mixin import ProfileLabelMixin
from gpc.executors.properties_updator import ChangePropertyExecutor
from gpc.helpers.exceptions import GpcLabelError
from gpc.parameters import RunMode
from gpc.property_manager import PropertyBean
from gpc.property_manager import PropertyManager


class LabelManager(PropertyManager):
    def rm_existing(self, property_bean: str):
        try:
            self.manager.delete(property_bean, retry_transient_errors=True)
        except GitlabDeleteError:
            pass


@attr.s
class ProjectLabel(PropertyBean):
    color = attr.ib()  # type: str

    @staticmethod
    def to_project_labels(api_labels):
        project_labels = []
        for api_label in api_labels:
            project_labels.append(ProjectLabel.to_project_label(api_label))
        return project_labels

    @staticmethod
    def to_project_label(api_label):
        return ProjectLabel(name=api_label.name, color=api_label.color)

    def get_query(self):
        return {"name": self.name, "color": self.color}

    def to_dict(self):
        return self.get_query()


class ChangeLabels(ChangePropertySetting):
    sub_properties = ["color"]
    status_to_process = ["updated", "kept", "added"]

    def _is_kept(self, before_name, before, after_properties):
        if before_name in after_properties:
            after_prop = after_properties[before_name].to_dict()
        else:
            after_prop = before.to_dict()
        return {
            "status": "kept",
            "before": before.to_dict(),
            "after": after_prop,
        }


class LabelSettingExecutor(ChangePropertyExecutor, ProfileLabelMixin):
    order = 50
    name = "labels"
    sections = ["labels"]

    def _apply(self):
        if self.changes:
            labels = self.changes[0]
            self._save_properties(LabelManager(self.item.labels), labels, labels.after)

    def _update(self, mode: RunMode, members_user, members_group):
        if "labels" in self.rule and self.rule.labels is not None:
            labels = []
            for label in self._labels_to_update():
                labels.append(ProjectLabel(name=label.name, color=label.color))
            self.changes.append(
                ChangeLabels(
                    "labels",
                    ProjectLabel.to_project_labels(
                        self.item.labels.list(  # type: ignore
                            iterator=True, retry_transient_errors=True
                        )
                    ),
                    labels,
                    self.show_diff_only,
                )
            )

    def _labels_to_update(self):
        labels = {}
        for item in self.rule.labels:
            if item.get("profile"):
                profile = self.get_label_profile(item.get("profile"))
                for label in profile.labels:
                    if label.name not in labels:
                        # A label defined directly shall overwrite
                        # the ones defined in a profile
                        labels[label.name] = label
            elif item.get("name"):
                labels[item.get("name")] = item
            else:
                raise GpcLabelError(f"Impossible to handle label {item}.")
        return labels.values()
