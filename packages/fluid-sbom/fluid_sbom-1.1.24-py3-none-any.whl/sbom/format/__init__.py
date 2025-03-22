from sbom.artifact.relationship import (
    Relationship,
)
from sbom.file.resolver import Resolver
from sbom.format.common import (
    process_packages,
)
from sbom.format.cyclone_dx.file_builder import (
    format_cyclonedx_sbom,
)
from sbom.format.fluid import (
    format_fluid_sbom,
)
from sbom.format.spdx.file_builder import (
    format_spdx_sbom,
)
from sbom.model.core import (
    Package,
    SbomConfig,
)


def format_sbom(
    *,
    packages: list[Package],
    relationships: list[Relationship],
    config: SbomConfig,
    resolver: Resolver,
) -> None:
    packages = process_packages(packages)
    match config.output_format:
        case "fluid-json":
            format_fluid_sbom(
                packages=packages,
                relationships=relationships,
                config=config,
                resolver=resolver,
            )
        case "cyclonedx-json":
            format_cyclonedx_sbom(
                packages=packages,
                relationships=relationships,
                config=config,
                resolver=resolver,
            )
        case "cyclonedx-xml":
            format_cyclonedx_sbom(
                packages=packages,
                relationships=relationships,
                config=config,
                resolver=resolver,
            )
        case "spdx-json":
            format_spdx_sbom(
                packages=packages,
                _relationships=relationships,
                file_format="json",
                config=config,
                resolver=resolver,
            )
        case "spdx-xml":
            format_spdx_sbom(
                packages=packages,
                _relationships=relationships,
                file_format="xml",
                config=config,
                resolver=resolver,
            )
