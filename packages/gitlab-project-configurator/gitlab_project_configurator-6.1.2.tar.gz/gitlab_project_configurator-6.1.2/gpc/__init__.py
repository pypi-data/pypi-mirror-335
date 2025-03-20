"""
Gitlab Project Configurator main module.

The entry point of the command line tools is :py:func:`gpc.cli.main`.
"""


def version():
    # Standard Library
    from importlib.metadata import version as importlib_version

    return importlib_version("gitlab-project-configurator")


__version__ = version()
