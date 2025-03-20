"""
Mixin to extract label profiles from label section.
"""

# Third Party Libraries
from structlog import get_logger

# Gitlab-Project-Configurator Modules
from gpc.helpers.exceptions import GpcLabelError


log = get_logger()


class ProfileLabelMixin:
    def get_label_profile(self, profile_name):
        if not self.rule.get("label_profiles"):
            raise GpcLabelError(
                f"ERROR on project {self.item_path}: "
                f"The import of label_profiles profile {profile_name} is impossible, because"
                "the section 'label_profiles' does not exist."
            )
        for label_profile in self.rule.get("label_profiles"):
            if label_profile.name == profile_name:
                return label_profile
        raise GpcLabelError(
            f"ERROR on project {self.item_path}: "
            f"The import of label_profiles profile {profile_name} is impossible, because"
            "this profile name is not found in the 'label_profiles' "
            "section."
        )
