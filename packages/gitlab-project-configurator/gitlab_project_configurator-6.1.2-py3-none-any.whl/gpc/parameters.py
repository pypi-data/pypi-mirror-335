"""
Command line parameters store.
"""

# Standard Library
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any  # pylint: disable=unused-import
from typing import List  # pylint: disable=unused-import
from typing import Optional  # pylint: disable=unused-import
from typing import Union  # pylint: disable=unused-import

# Third Party Libraries
from dictns import Namespace
from path import Path  # pylint: disable=unused-import


RawConfig = Namespace


class RunMode(Enum):
    DRY_RUN = "dry-run"
    APPLY = "apply"
    INTERACTIVE = "interactive"

    def __str__(self) -> str:
        return str(self.value)


@dataclass
class GpcParameters:  # pylint: disable=too-many-instance-attributes
    config: Path
    force: List[str] = field(default_factory=list)
    mode: RunMode = RunMode.DRY_RUN
    projects: List[str] = field(default_factory=list)
    report_file: Optional[str] = None
    report_html: Optional[str] = None
    diff: bool = False
    debug: bool = False
    config_project_url: Optional[str] = None
    gpc_enabled_badge_url: Optional[str] = None
    gpc_enabled_badge_name: Optional[str] = None
    gpc_accepted_external_badge_image_urls: Optional[str] = None
    smtp_server: Optional[str] = None
    smtp_port: Optional[str] = None
    email_author: Optional[str] = None
    watchers: List[str] = field(default_factory=list)
    executor: Optional[str] = None
    max_workers: int = 8
    dump_merged_config: Optional[str] = None
    preview: bool = False
