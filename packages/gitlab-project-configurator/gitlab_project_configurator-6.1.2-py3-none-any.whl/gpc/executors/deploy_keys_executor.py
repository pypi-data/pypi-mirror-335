# Third Party Libraries
import attr

# Gitlab-Project-Configurator Modules
from gpc.change_setting import ChangePropertySetting
from gpc.executors.properties_updator import ChangePropertyExecutor
from gpc.parameters import RunMode
from gpc.property_manager import PropertyBean


@attr.s(eq=False)
class DeployKey(PropertyBean):
    can_push = attr.ib()  # type: bool
    id = attr.ib()  # type: int

    def get_query(self):
        return {"id": self.id, "can_push": self.can_push}

    def to_dict(self):
        return {"id": self.id, "can_push": self.can_push}

    def __eq__(self, other):
        if not isinstance(other, DeployKey):
            return False
        return self.id == other.id and self.can_push == other.can_push


class ChangeDeployKey(ChangePropertySetting):
    sub_properties = ["can_push"]
    status_to_process = ["removed", "updated", "kept", "added"]


class DeployKeysExecutor(ChangePropertyExecutor):
    order = 110
    name = "deploy_keys"

    def _apply(self):
        if self.changes:
            for difference in self.changes[0].differences.values():
                if difference["status"] == "updated":
                    key = self.item.keys.get(difference["after"]["id"], retry_transient_errors=True)
                    key.can_push = difference["after"]["can_push"]
                    key.save(retry_transient_errors=True)
                elif difference["status"] == "removed":
                    self.item.keys.delete(difference["before"]["id"], retry_transient_errors=True)
                elif difference["status"] == "added":
                    self.item.keys.enable(difference["after"]["id"], retry_transient_errors=True)
                    key = self.item.keys.get(difference["after"]["id"], retry_transient_errors=True)
                    key.can_push = difference["after"]["can_push"]
                    key.save(retry_transient_errors=True)

    def _update(self, mode: RunMode, members_user, members_group):
        if "deploy_keys" in self.rule and self.rule.deploy_keys is not None:
            after_keys = []
            for key in self.rule.deploy_keys:
                after_keys.append(DeployKey(name=str(key.id), id=key.id, can_push=key.can_push))
            before_keys = []
            for key in self.item.keys.list(retry_transient_errors=True):  # type: ignore
                before_keys.append(DeployKey(name=str(key.id), id=key.id, can_push=key.can_push))
            self.changes.append(
                ChangeDeployKey(
                    property_name="deploy_keys",
                    before=before_keys,
                    after=after_keys,
                    show_diff_only=self.show_diff_only,
                )
            )
