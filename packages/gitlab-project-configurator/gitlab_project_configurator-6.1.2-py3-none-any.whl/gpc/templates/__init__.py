"""
A Jinja template loader using Importlib_resource.
"""

# Standard Library
import fnmatch
import importlib.resources
import os
import re
import types

from typing import Iterable
from typing import Union

# Third Party Libraries
import arrow

from jinja2 import Environment
from jinja2 import Template
from jinja2 import select_autoescape
from jinja2.exceptions import TemplateNotFound
from jinja2.loaders import BaseLoader
from jinja2.loaders import split_template_path

# Gitlab-Project-Configurator Modules
from gpc.config_validator import importlib_resources_contents
from gpc.config_validator import importlib_resources_is_resource
from gpc.config_validator import importlib_resources_read_binary


Char = str


def is_dir(templates_path: str, wanted_resource: str) -> bool:
    return wanted_resource in importlib_resources_contents(
        templates_path
    ) and not importlib_resources_is_resource(templates_path, wanted_resource)


def has_resource(resource_path: str) -> bool:
    dir_name, _, filename = resource_path.rpartition("/")
    return filename in importlib_resources_contents(dir_name)


def format_datetime(value, format="medium"):  # pylint: disable=redefined-builtin
    if format == "full":
        format = "YYYY MMMM DD, HH:mm:ss"
    elif format == "medium":  # pylint: disable=comparison-with-callable
        format = "YY.MM.DD HH:mm"
    return arrow.get(value).format(format)


def strip_str(s: str, c: Char) -> str:
    return s.strip(c)


def first_line(s: str) -> str:
    return s.partition("\n")[0]


def truncate_from_start(s: str, lenght, start="...") -> str:
    if len(s) <= lenght:
        return s
    return start + s[len(s) - lenght :]


class ImportLibResourceLoader(BaseLoader):
    # Adapted from PackageResource, using this migration guide:
    # https://importlib-resources.readthedocs.io/en/latest/migration.html#migration

    def __init__(self, templates_path, encoding="utf-8"):
        self.templates_path = templates_path
        self.encoding = encoding

    def get_source(self, environment, template):
        pieces = split_template_path(template)
        p = "/".join((self.templates_path,) + tuple(pieces))
        if not has_resource(p):
            raise TemplateNotFound(template)

        package_name, _, filename = p.rpartition("/")
        source = importlib_resources_read_binary(package_name, filename)

        def uptodate():
            return False

        return source.decode(self.encoding), filename, uptodate

    def list_templates(self):
        p = self.templates_path
        if p[:2] == "./":
            p = p[2:]
        elif p == ".":
            p = ""
        offset = len(p)
        results = []

        def _walk(p):
            try:
                for filename in importlib_resources_contents(p):
                    if fnmatch.fnmatch(filename, "*.py"):
                        pass
                    fullname = p + "/" + filename
                    if is_dir(p, filename):
                        _walk(fullname)
                    else:
                        results.append(fullname[offset:].lstrip("/"))
            except ImportError:
                pass

        _walk(p)
        results.sort()
        return results


def load_template(tpl_name: str) -> Template:
    autoescape = select_autoescape(
        default_for_string=True,
        enabled_extensions=("html", "htm", "xml"),
    )

    env = Environment(  # nosec
        autoescape=autoescape, loader=ImportLibResourceLoader("gpc.templates")
    )
    env.filters["datetime"] = format_datetime
    env.filters["strip"] = strip_str
    env.filters["first_line"] = first_line
    env.filters["truncate_from_start"] = truncate_from_start
    return env.get_template(tpl_name)
