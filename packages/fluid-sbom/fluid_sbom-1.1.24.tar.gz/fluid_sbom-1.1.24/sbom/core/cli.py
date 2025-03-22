import logging
import os
import textwrap
from concurrent.futures import ThreadPoolExecutor
from typing import Unpack

import click

from sbom.advisories.images.database import DATABASE
from sbom.config.bugsnag import initialize_bugsnag
from sbom.config.logger import configure_logger, modify_logger_level
from sbom.core.options import MutuallyExclusiveOption, RequiredAnyCommand
from sbom.core.sbom_configurator import ScanArgs, build_sbom_config
from sbom.core.source_dispatcher import resolve_sbom_source
from sbom.format import format_sbom
from sbom.pkg.cataloger.complete import complete_package
from sbom.pkg.operations.package_operation import package_operations_factory

LOGGER = logging.getLogger(__name__)


def show_banner() -> None:
    logo = textwrap.dedent(
        """
         ───── ⌝
        |    ⌝|  Fluid Attacks
        |  ⌝  |  We hack your software.
         ─────
        """,
    )
    click.secho(logo, fg="red")


@click.command(cls=RequiredAnyCommand, required_any=["o_from", "config"])
@click.argument("arg")
@click.option(
    "--from",
    "o_from",
    type=click.Choice(
        ["docker", "dir", "docker-daemon", "ecr"],
        case_sensitive=False,
    ),
    help=(
        "Source of the scan: 'docker' for scanning Docker images or 'dir' for scanning directories."
    ),
    cls=MutuallyExclusiveOption,
    mutually_exclusive=["config"],
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(
        [
            "fluid-json",
            "cyclonedx-json",
            "spdx-json",
            "cyclonedx-xml",
            "spdx-xml",
        ],
        case_sensitive=False,
    ),
    default="fluid-json",
    help="Output format for the scanned data.",
    cls=MutuallyExclusiveOption,
    mutually_exclusive=["config"],
)
@click.option(
    "--output",
    "-o",
    help="Output filename.",
    default="sbom",
    cls=MutuallyExclusiveOption,
    mutually_exclusive=["config"],
)
@click.option(
    "--docker-user",
    default=None,
    help="Docker registry username.",
    cls=MutuallyExclusiveOption,
    mutually_exclusive=["config"],
)
@click.option(
    "--docker-password",
    default=None,
    help="Docker registry password.",
    cls=MutuallyExclusiveOption,
    mutually_exclusive=["config"],
)
@click.option(
    "--aws-external-id",
    default=None,
    help="Docker registry username.",
    cls=MutuallyExclusiveOption,
    mutually_exclusive=["config"],
)
@click.option(
    "--aws-role",
    default=None,
    help="Docker registry password.",
    cls=MutuallyExclusiveOption,
    mutually_exclusive=["config"],
)
@click.option(
    "--config",
    "-c",
    is_flag=True,
    default=False,
    cls=MutuallyExclusiveOption,
    help="Path to an advanced configuration file with additional settings.",
    mutually_exclusive=[
        "aws-role",
        "aws-external-id",
        "docker-user",
        "docker-password",
        "output_format",
        "output",
        "o_from",
    ],
)
@click.option(
    "--debug",
    help="Run the application on debug mode",
    is_flag=True,
)
def scan(arg: str, **kwargs: Unpack[ScanArgs]) -> None:
    configure_logger()
    initialize_bugsnag()
    show_banner()

    sbom_config = build_sbom_config(arg, **kwargs)

    if sbom_config.debug or kwargs["debug"]:
        modify_logger_level()

    main_sbom_resolver = resolve_sbom_source(sbom_config)

    DATABASE.initialize()

    LOGGER.info("📦 Generating SBOM from %s: %s", sbom_config.source_type.value, sbom_config.source)
    packages, relationships = package_operations_factory(main_sbom_resolver)

    with ThreadPoolExecutor(
        max_workers=min(32, (os.cpu_count() or 1) * 5 if os.cpu_count() is not None else 32),
    ) as executor:
        LOGGER.info("📦 Gathering additional package information")
        packages = list(filter(None, executor.map(complete_package, packages)))

    LOGGER.info("📦 Preparing %s report", sbom_config.output_format)
    format_sbom(
        packages=packages,
        relationships=relationships,
        config=sbom_config,
        resolver=main_sbom_resolver,
    )


if __name__ == "__main__":
    scan(prog_name="sbom")
