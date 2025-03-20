# Standard Library
import importlib.resources
import os
import pathlib
import re
import types

from collections import Counter
from typing import Any
from typing import ContextManager
from typing import Iterable
from typing import Optional  # pylint: disable=unused-import
from typing import Tuple
from typing import Union

# Third Party Libraries
import anyconfig
import click
import jsonschema

from boltons.cacheutils import cachedproperty
from colorama import Fore
from dictns import Namespace
from jsonschema.exceptions import SchemaError
from jsonschema.exceptions import ValidationError
from path import Path
from structlog import get_logger

# Gitlab-Project-Configurator Modules
import gpc.schema

from gpc import version
from gpc.helpers.error_codes import GPC_ERR_CODE_SUCCESS
from gpc.helpers.exceptions import GpcDuplicateKey
from gpc.helpers.exceptions import GpcProfileError
from gpc.helpers.exceptions import GpcSchemaError
from gpc.helpers.exceptions import GpcValidationError
from gpc.helpers.types import listify
from gpc.parameters import GpcParameters
from gpc.parameters import RawConfig  # pylint: disable=unused-import


log = get_logger()


# https://github.com/python/importlib_resources/blob/66ea2dc7eb12b1be2322b7ad002cefb12d364dff/importlib_resources/_legacy.py
Package = Union[types.ModuleType, str]
Resource = Union[str, os.PathLike]


def importlib_resources_read_binary(package: Package, resource: Resource) -> bytes:
    """Return the binary contents of the resource."""
    return (importlib.resources.files(package) / normalize_path(resource)).read_bytes()


def normalize_path(path):
    str_path = str(path)
    parent, file_name = os.path.split(str_path)
    if parent:
        raise ValueError(f"{path!r} must be only a file name")
    return file_name


def importlib_resources_path(
    package: Package,
    resource: Resource,
) -> ContextManager[pathlib.Path]:
    return importlib.resources.as_file(
        importlib.resources.files(package) / normalize_path(resource)
    )


def importlib_resources_contents(package: Package) -> Iterable[str]:
    return [path.name for path in importlib.resources.files(package).iterdir()]


def importlib_resources_is_resource(package: Package, name: str) -> bool:
    resource = normalize_path(name)
    return any(
        traversable.name == resource and traversable.is_file()
        for traversable in importlib.resources.files(package).iterdir()
    )


class GpcConfigValidator:
    """
    I am responsible for validating the user configuration file.

    I also support the file inclusion and default value loading.
    """

    include_sections = [
        "projects_rules",
        "groups_rules",
        "variable_profiles",
        "member_profiles",
        "label_profiles",
    ]
    sections_list = [
        "projects_rules",
        "groups_rules",
        "member_profiles",
        "label_profiles",
    ]
    check_duplicate_list = [
        "projects_configuration",
        "groups_configuration",
        "projects_rules",
        "member_profiles",
        "variable_profiles",
        "groups_rules",
        "label_profiles",
    ]
    schema_file = "config.schema.yaml"

    def __init__(self, parameters: GpcParameters):
        self.params = parameters

    @cachedproperty
    def _uninited_config(self) -> Optional[RawConfig]:
        try:
            self.check_duplicate_keys(self.params.config)
            return Namespace(anyconfig.load(self.params.config))
        finally:
            log.debug(
                "Raw configuration file",
                mode=str(self.params.mode),
                config_file=self.params.config,
            )

    @cachedproperty
    def raw_config(self) -> RawConfig:
        # import seep.core
        # inited_config =  seep.core.instantiate(self._uninited_config, self.schema)
        # log.debug("Setting default value in configuration",
        #           inited_config=inited_config,
        #           uninited_config=self._uninited_config)
        # return inited_config
        return self._uninited_config

    @cachedproperty
    def _schema_and_schemapath(self) -> Tuple[Any, Path]:
        with importlib_resources_path(gpc.schema, self.schema_file) as s:
            schema_path = Path(s)
            schema = anyconfig.load(s)
            return schema, schema_path

    @cachedproperty
    def schema(self) -> Any:
        return self._schema_and_schemapath[0]

    @cachedproperty
    def schema_path(self) -> Path:
        return self._schema_and_schemapath[1]

    def check_duplicate_keys(self, file):
        with open(file, encoding="utf-8") as f:
            lines = f.readlines()
        duplicates = {}
        for key in GpcConfigValidator.check_duplicate_list:
            count_key = [bool(re.match(f"^{key}:", line)) for line in lines]
            count_key = Counter(count_key)[True]

            if count_key > 1:
                duplicates[key] = count_key

        if duplicates:
            raise GpcDuplicateKey(file, duplicates)

    def run(self) -> int:
        v = version()

        click.echo(
            Fore.LIGHTGREEN_EX
            + "-" * 80
            + f"\nGitlab Project Configurator version {v!s}\n"
            + "-" * 80
            + Fore.RESET
        )
        log.debug("Gitlab Project Configuration started", parameters=self.params, version=v)

        # Load and validate includes
        self.load_includes()

        # Validate the whole configuration
        self.validate()

        self.check_rule_names()

        return GPC_ERR_CODE_SUCCESS

    def validate(self):
        if not self._uninited_config:
            raise ValueError("Empty configuration file")
        self._validate_config(self._uninited_config, self.params.config)
        return 0

    def load_includes(self):
        return self._load_include(self._uninited_config, Path(self.params.config).parent)

    def _load_include(self, config_file: Namespace, working_dir: Path):
        config_file.include = listify(config_file.get("include", None))
        includes = config_file.include
        log.debug("Found includes", include=includes)
        if not includes:
            return
        includes_path = self._get_include_path(includes, working_dir)
        projects_configuration = []
        groups_configuration = []
        for include in includes_path:
            log.debug(f"Injecting include file {include}")
            self.check_duplicate_keys(Path(include))
            incl_content = Namespace(anyconfig.load(Path(include)))
            self._validate_config(incl_content, include)
            for section in self.include_sections:
                self._merge_sections(section, incl_content)
            if "projects_configuration" in incl_content:
                projects_configuration.extend(incl_content.projects_configuration)
            if "groups_configuration" in incl_content:
                groups_configuration.extend(incl_content.groups_configuration)
            self._load_include(incl_content, include.parent)
        self._merge_projects_configuration(projects_configuration)
        self._merge_groups_configuration(groups_configuration)
        del config_file["include"]

    def _get_include_path(self, includes, working_dir: Path):
        includes_path = []
        for include in includes:
            log.debug(f"Injecting include file {include}")
            if include.startswith("/"):
                full_path = include  # type: str
            else:
                full_path = working_dir / include
            for unglobed in [
                Path(p2) for p2 in sorted(str(p1.absolute()) for p1 in Path().glob(full_path))
            ]:
                if unglobed not in includes_path:
                    includes_path.append(unglobed)
        return includes_path

    def _merge_projects_configuration(self, projects_configuration):
        if "projects_configuration" in self._uninited_config:
            projects_configuration.extend(self._uninited_config["projects_configuration"])
            self._uninited_config["projects_configuration"] = projects_configuration
        else:
            self._uninited_config["projects_configuration"] = projects_configuration

    def _merge_groups_configuration(self, groups_configuration):
        if "groups_configuration" in self._uninited_config:
            groups_configuration.extend(self._uninited_config["groups_configuration"])
            self._uninited_config["groups_configuration"] = groups_configuration
        else:
            self._uninited_config["groups_configuration"] = groups_configuration

    def _merge_sections(self, section, incl_content):
        if section in incl_content:
            if section in self._uninited_config:
                if section in self.sections_list:
                    self._uninited_config[section] += getattr(incl_content, section)
                else:
                    sub_sections = getattr(incl_content, section)
                    for sub_section in sub_sections:
                        self._uninited_config[section][sub_section] = getattr(
                            sub_sections, sub_section
                        )
            else:
                setattr(self._uninited_config, section, getattr(incl_content, section))

    def _validate_config(self, config_content, file_config):
        log.info(
            f"Validating configuration file: {file_config}",
            config=str(file_config),
        )
        try:
            jsonschema.validate(config_content, self.schema)
        except SchemaError as e:
            raise GpcSchemaError(self.schema_file, e) from e
        except ValidationError as e:
            raise GpcValidationError(file_config, self.schema_file, e) from e
        log.debug(
            "Configuration file is validated",
            config=str(file_config),
            schema=str(self.schema_path),
        )
        click.echo(
            Fore.LIGHTGREEN_EX
            + f"Data from {str(file_config)} is valid against schema {str(self.schema_path)}"
            + Fore.RESET
        )

    def check_rule_names(self):
        log.debug("checking rules consistency...")
        self._check_inheritance()
        self._check_project_config()

    def _check_inheritance(self):
        if "projects_rules" not in self.raw_config:
            return
        for rule in self.raw_config.get("projects_rules"):
            if "inherits_from" not in rule:
                continue
            wanted_rules_name = listify(rule.inherits_from).copy()
            existing_rules = []
            log.debug("checking inherits_from", wanted_rules_name=wanted_rules_name)
            for other_rule in self.raw_config.get("projects_rules", []):
                if not wanted_rules_name:
                    break
                existing_rules.append(other_rule.rule_name)
                if other_rule.rule_name in wanted_rules_name:
                    wanted_rules_name.remove(other_rule.rule_name)
            else:
                raise GpcProfileError(
                    f"In rule '{rule.rule_name}', inherits_from "
                    f"declares an invalid rule name: {wanted_rules_name}. "
                    f"Available: {existing_rules}"
                )

    def _check_project_config(self):
        if "projects_configuration" not in self.raw_config:
            return
        for project_cfg in self.raw_config.get("projects_configuration"):
            wanted_rule_name = listify(project_cfg.get("rule_name", None)).copy()
            if not wanted_rule_name:
                log.debug("no rule defined for config", project_cfg=project_cfg)
                continue
            existing_rules = []
            log.debug("checking rule_name", wanted_rule_name=wanted_rule_name)
            for rule in self.raw_config.get("projects_rules", []):
                existing_rules.append(rule.rule_name)
                if rule.rule_name in wanted_rule_name:
                    wanted_rule_name.remove(rule.rule_name)
                if not wanted_rule_name:
                    break
            else:
                raise GpcProfileError(
                    f"Project configuration in file '{Path(self.params.config).name}' "
                    f"declares an invalid rule name: '{wanted_rule_name}'. "
                    f"Available: {existing_rules}"
                )
