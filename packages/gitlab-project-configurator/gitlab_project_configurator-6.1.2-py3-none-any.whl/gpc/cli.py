#!/usr/bin/env python
"""
GPC Command Line Interface module.

Please note the Click ``entrypoint`` method does not appear in the generated documentation.
"""

# Standard Library
import os
import sys

from logging import FATAL
from logging import INFO
from typing import Optional

# Third Party Libraries
import click
import click_config_file
import colorama
import gitlab as gl

from gitlab.config import GitlabConfigMissingError
from path import Path
from structlog import get_logger

# Gitlab-Project-Configurator Modules
from gpc import version as gpc_version
from gpc.config_validator import GpcConfigValidator
from gpc.general_executor import GpcGeneralExecutor
from gpc.helpers.click_mutually_excl_opt import MutuallyExclusiveOption
from gpc.helpers.session_helper import create_retry_request_session
from gpc.parameters import GpcParameters
from gpc.parameters import RunMode


# pylint: disable=no-value-for-parameter, too-many-arguments, too-many-locals
# pylint: disable=import-outside-toplevel

log = get_logger()


def configure_stdout_and_logs(
    debug: Optional[bool] = False,
    trace_filename: Optional[str] = None,
):
    # Standard Library
    import logging.config

    # Third Party Libraries
    import structlog

    timestamper = structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S")
    pre_chain = [
        # Add the log level and a timestamp to the event_dict if the log entry
        # is not from structlog.
        structlog.stdlib.add_log_level,
        timestamper,
    ]

    logcfg = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "plain": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(colors=False),
                "foreign_pre_chain": pre_chain,
            },
            "colored": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(colors=True),
                "foreign_pre_chain": pre_chain,
            },
        },
        "handlers": {
            "default": {
                "level": "DEBUG" if debug else "ERROR",
                "class": "logging.StreamHandler",
                "formatter": "colored",
            },
        },
        "loggers": {
            "": {
                "handlers": ["default"],
                "level": "DEBUG",
                "propagate": True,
            },
        },
    }
    if trace_filename:
        logcfg["handlers"]["file"] = {  # type: ignore
            "level": "DEBUG",
            "class": "logging.handlers.WatchedFileHandler",
            "filename": trace_filename,
            "formatter": "plain",
        }
        logcfg["loggers"][""]["handlers"].append("file")  # type: ignore

    logging.config.dictConfig(logcfg)

    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            timestamper,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def init_color(color: str):
    coloropt_to_stripcolor = {
        "force": False,
        "no": True,
        "auto": None,
    }
    color_choice = coloropt_to_stripcolor.get(color, None)
    if color_choice is not None:
        colorama.deinit()
        colorama.init(strip=coloropt_to_stripcolor.get(color, None), autoreset=True)


def sentry_before_send(event, _hint):
    try:
        event["gpc_version"] = gpc_version()
        environ = event.setdefault("environ", {})
        environ["CI_JOB_URL"] = os.getenv("CI_JOB_URL")
        environ["CI_PIPELINE_URL"] = os.getenv("CI_PIPELINE_URL")
        environ["GPC_CONFIG"] = os.getenv("GPC_CONFIG")
    except Exception:
        pass  # nosec B110
    return event


def configure_sentry(sentry_dsn: str):
    if not sentry_dsn:
        return
    try:
        # pylint: disable=import-outside-toplevel
        # Third Party Libraries
        import sentry_sdk

        from sentry_sdk.integrations.argv import ArgvIntegration
        from sentry_sdk.integrations.excepthook import ExcepthookIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
        from sentry_sdk.integrations.stdlib import StdlibIntegration

        # pylint: enable=import-outside-toplevel

        sentry_logging = LoggingIntegration(
            level=INFO,  # Capture info and above as breadcrumbs
            event_level=FATAL,  # Send errors as events
        )

        sentry_sdk.init(
            sentry_dsn,
            release=gpc_version(),
            before_send=sentry_before_send,
            integrations=[
                sentry_logging,
                ArgvIntegration(),
                StdlibIntegration(),
                ExcepthookIntegration(),
            ],
        )
    except ImportError:
        log.warn("cannot import sentry_sdk, ignoring Sentry configuration")


def print_version(ctx, _param, value):
    """Print the version string on ``gpc --version``."""
    if not value or ctx.resilient_parsing:
        return
    click.echo(f"Gitlab Project Configurator version: {gpc_version()}")
    ctx.exit()


def init_gitlab(
    gitlab_cfg: str,
    gitlab_profile: str,
    gitlab_url: str,
    gitlab_token: str,
) -> gl.Gitlab:
    if gitlab_url and gitlab_token:
        log.debug(
            "Using Gitlab information provided by argument\n"
            f"Gitlab URL: {gitlab_url}\nToken: {gitlab_token[:2] + '***'}",
            gitlab_url=gitlab_url,
            gitlab_safe_token=gitlab_token[:2] + "***",
        )
        gitlab_obj = gl.Gitlab(
            gitlab_url,
            private_token=gitlab_token,
            timeout=60,
            # retry_transient_errors=True,  # requires python-gitlab >=3
            session=create_retry_request_session(),
        )
    else:
        try:
            gitlab_obj = gl.Gitlab.from_config(
                gitlab_profile,
                [Path(gitlab_cfg).expand()],
            )
            gitlab_obj.session = create_retry_request_session()
        except GitlabConfigMissingError:
            click.secho(
                f"ERROR: Configuration file '{gitlab_cfg}' not found. "
                "If you are in a CI, "
                "please define GPC_GITLAB_URL and GPC_GITLAB_TOKEN.",
                fg="red",
            )
            sys.exit(1)
        log.debug(
            f"Using Gitlab information from '{gitlab_cfg}'\n"
            "Gitlab URL: {}\nToken: {}".format(
                gitlab_obj.url,
                gitlab_obj.private_token[:2] + "***" if gitlab_obj.private_token else "",
            ),
            gitlab_url=gitlab_obj.url,
            gitlab_safe_token=(
                gitlab_obj.private_token[:2] + "***" if gitlab_obj.private_token else ""
            ),
        )
    return gitlab_obj


@click.command(help="Gitlab Project Configurator")
@click.option(
    "--mode",
    "-m",
    type=click.Choice(["dry-run", "apply", "interactive"]),
    default="dry-run",
    help=(
        "- ``dry-run``: only evaluate the execution without modifying anything (default),\n"
        "- ``apply``: do all modifications without confirmation,\n"
        "- ``interactive``: require confirmation for each changed project"
    ),
    show_envvar=True,
)
@click.option(
    "--config",
    "-c",
    required=True,
    help="Projects Configuration file(s) (JSON or YAML) to apply",
    metavar="CONFIG_FILE",
    show_envvar=True,
)
@click.option(
    "--gitlab-cfg",
    help=(
        "Gitlab file reading the Python-Gitlab settings if using ``--gitlab`` option. "
        "Default to ``~/.gitlab.cfg``. Exclusive with ``--gitlab-token``/``--gitlab-url``"
    ),
    metavar="FILENAME",
    cls=MutuallyExclusiveOption,
    mutually_exclusive=["gitlab_token", "gitlab_url"],
    default="~/.gitlab.cfg",
    show_envvar=True,
)
@click.option(
    "--gitlab",
    "-g",
    help=(
        "Gitlab profile to use from ``~/.gitlab.cfg``. "
        "Exclusive with ``--gitlab-token/--gitlab-url``"
    ),
    metavar="GITLAB_ALIAS",
    cls=MutuallyExclusiveOption,
    mutually_exclusive=["gitlab_token", "gitlab_url"],
    show_envvar=True,
)
@click.option(
    "--gitlab-url",
    help="Override Gitlab URL",
    required=False,
    default=None,
    metavar="GITLAB_URL",
    cls=MutuallyExclusiveOption,
    mutually_exclusive=["gitlab"],
    show_envvar=True,
)
@click.option(
    "--gitlab-token",
    help=(
        "Override Gitlab Personal Access Token. "
        "It is advised to set the environment variable ``GPC_GITLAB_TOKEN`` instead "
        "of this argument"
    ),
    required=False,
    metavar="GITLAB_TOKEN",
    cls=MutuallyExclusiveOption,
    mutually_exclusive=["gitlab"],
    show_envvar=True,
)
@click.option(
    "--projects",
    "-p",
    multiple=True,
    metavar="PROJECT_PATH [PROJECT_PATH [PROJECT_PATH] ...]",
    help=("restrict to one or several projects " "(wildcard accepted)"),
    show_envvar=True,
)
@click.option("--verbose", "-v", count=True, help="Verbose outputs")
@click.option(
    "--validate",
    is_flag=True,
    default=False,
    help="Only perform configuration file validatation",
    show_envvar=True,
)
@click.option("--version", is_flag=True, callback=print_version, expose_value=False, is_eager=True)
@click.option(
    "--color",
    required=False,
    type=click.Choice(["auto", "force", "no"]),
    default="auto",
    help="Enable color output. Default: auto",
    show_envvar=True,
)
@click.option("--report-file", help="Dump report to a file", required=False)
@click.option("--diff", is_flag=True, default=False, help="Display only difference of update.")
@click.option("--debug", is_flag=True, default=False, help="Fails at first error")
@click.option(
    "--config-project-url",
    default=os.getenv("CI_PROJECT_URL"),
    help=(
        "Set the URL of the configuration project. "
        "Default: read from ``CI_PROJECT_URL`` environment variable"
    ),
    show_envvar=True,
)
@click.option(
    "--configured-by-gpc-badge-url",
    default=os.getenv("GPC_BADGE_URL"),
    help=("Set the URL of the 'Configured by GPC' badge"),
    show_envvar=True,
)
@click.option(
    "--configured-by-gpc-badge-name",
    default=os.getenv("GPC_BADGE_NAME"),
    help=("Set the NAME of the 'Configured by GPC' badge"),
    show_envvar=True,
)
@click.option(
    "--accepted-external-badge-image-urls",
    multiple=True,
    default=None,
    help=("List of Project's Badge image URL to keep on project"),
    show_envvar=True,
)
@click.option(
    "--report-html",
    default="report-gpc.html",
    help="Generate an HTML report",
    show_envvar=True,
)
@click.option(
    "--smtp-server",
    default=None,
    help="smtp server to send mail notification",
    show_envvar=True,
)
@click.option(
    "--smtp-port",
    default=None,
    help="smtp port to send mail notification",
    show_envvar=True,
)
@click.option(
    "--email-author",
    default=None,
    help=(
        "Email author of the report email "
        "(should follow the structure 'full name <full.name@server.com>')"
    ),
    show_envvar=True,
)
@click.option(
    "--watchers",
    default="",
    help=("Watchers who are notified when changes occurred. " "(mail address separated by ;)"),
    show_envvar=True,
)
@click.option(
    "--sentry-dsn",
    default=None,
    help="Set the project DSN where to send your sentry events",
    show_envvar=True,
)
@click.option(
    "--trace-filename",
    default=None,
    help="Output debug traces to this log file.",
    show_envvar=True,
)
@click.option(
    "--force",
    default=os.getenv("GPC_FORCE_UPDATE", ""),
    help=(
        "Force sections of project settings update: "
        "(supported sections:'jira', 'pipelines-email') "
        "(settings section separated by ;)"
    ),
    show_envvar=True,
)
@click.option(
    "--preview",
    help=(
        "Set GPC in preview mode. "
        "It changes the following internal behaviors of GPC: "
        "list are extended instead of replaced during rules inheritance."
    ),
    show_envvar=True,
    is_flag=True,
)
@click.option(
    "--executor",
    "-e",
    help=(
        "Apply a subset of properties in your schema "
        "(supported properties: global_settings,members,protected_branches,protected_tags,"
        "variables,labels,approval_rules,mergerequests,approval_settings,jira,badges,"
        "pipelines_email,push_rules,runners,schedulers,deploy_keys) "
        "(properties separated by ,)"
    ),
    show_envvar=True,
)
@click.option(
    "--max-workers",
    default=8,
    help=("workers for threadpool execution "),
    show_envvar=True,
)
@click_config_file.configuration_option(
    "--defaults-file",
    config_file_name="gpc.cfg",
    implicit=True,
    help="Read defaults settings from (default: ``gpc.cfg``).",
    show_envvar=True,
)
@click.option(
    "--dump-merged-config",
    required=False,
    help=("Name of the report file to generate the merged config file "),
    show_envvar=True,
)
@click.pass_context
def entrypoint(
    ctx,
    accepted_external_badge_image_urls,
    color,
    config_project_url,
    config,
    configured_by_gpc_badge_url,
    configured_by_gpc_badge_name,
    debug,
    diff,
    force,
    gitlab_cfg,
    gitlab_token,
    gitlab_url,
    gitlab,
    mode,
    projects,
    report_file,
    report_html,
    sentry_dsn,
    smtp_port,
    smtp_server,
    email_author,
    trace_filename,
    validate,
    verbose,
    watchers,
    executor,
    max_workers,
    dump_merged_config,
    preview,
):
    """
    Execute the GPC command.

    This function uses Click to define all the parameters of the CLI.

    Please note this function does not appear in the auto-generated Sphinx
    documentation.
    """

    if color == "force":
        # Hack to force color inside CI: https://github.com/pallets/click/issues/1090
        ctx.color = True
    # Fix accepted_external_badge_image_urls explosion (env var)
    configure_stdout_and_logs(debug=verbose, trace_filename=trace_filename)
    if all(len(x) == 1 for x in accepted_external_badge_image_urls):
        accepted_external_badge_image_urls = "".join(accepted_external_badge_image_urls).split(" ")
    init_color(color)
    if sentry_dsn:
        configure_sentry(sentry_dsn)
    if not gitlab_url:
        log.error(
            "No Gitlab URL set. Please set GPC_GITLAB_URL or "
            "set 'gitlab_url' in your gpc.cfg file."
        )
        sys.exit(1)
    if force:
        # Retrieve service list to force update
        force = [x.strip().lower() for x in force.split(";")]
        # Exclude empty element
        force = list(filter(None, force))

    gpc_params = GpcParameters(
        mode=RunMode(mode),
        config=Path(config),
        # only=only,
        projects=projects,
        report_file=report_file,
        report_html=report_html,
        diff=diff,
        debug=debug,
        force=force,
        config_project_url=config_project_url,
        # gpc_enabled_badge_url=configured_by_gpc_badge_url,
        gpc_enabled_badge_url=os.getenv("GPC_BADGE_URL") or configured_by_gpc_badge_url,
        gpc_enabled_badge_name=configured_by_gpc_badge_name,
        gpc_accepted_external_badge_image_urls=accepted_external_badge_image_urls,
        smtp_server=smtp_server,
        smtp_port=smtp_port,
        email_author=email_author,
        watchers=watchers,
        executor=executor,
        max_workers=max_workers,
        dump_merged_config=dump_merged_config,
        preview=preview,
    )
    log.debug("Initializing parameters", gpc_params=gpc_params)
    if projects:
        log.debug("Force projects: %s", projects)
    if validate:
        return GpcConfigValidator(parameters=gpc_params).validate()
    gitlab_obj = init_gitlab(gitlab_cfg, gitlab, gitlab_url, gitlab_token)
    sys.exit(GpcGeneralExecutor(parameters=gpc_params, gitlab=gitlab_obj).run())


def main():
    """Define the main entry point for GPC."""
    entrypoint(auto_envvar_prefix="GPC")  # pylint: disable=unexpected-keyword-arg


if __name__ == "__main__":
    main()
