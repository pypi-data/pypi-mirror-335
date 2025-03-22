import logging
import re
from copy import (
    deepcopy,
)

from bs4 import (
    BeautifulSoup,
)
from packageurl import (
    PackageURL,
)
from pydantic import (
    ValidationError,
)

from sbom.artifact.relationship import (
    Relationship,
)
from sbom.file.dependency_type import (
    DependencyType,
)
from sbom.file.location_read_closer import (
    LocationReadCloser,
)
from sbom.file.resolver import (
    Resolver,
)
from sbom.model.core import (
    Language,
    Package,
    PackageType,
)
from sbom.pkg.cataloger.generic.parser import (
    Environment,
)
from sbom.utils.strings import format_exception

LOGGER = logging.getLogger(__name__)
PACKAGE = re.compile(r".+\\packages\\(?P<package_info>[^\s\\]*)\\.+")
DEP_INFO = re.compile(r"(?P<package_name>[^\d]*)\.(?P<version>[\d.]+)")


def _get_version(include_info: list[str]) -> str | None:
    return next(
        (
            pkg_info.lstrip("Version=")
            for pkg_info in include_info
            if pkg_info.startswith("Version=")
        ),
        None,
    )


def format_package(
    name: str,
    version: str,
    line: int,
    reader: LocationReadCloser,
) -> Package | None:
    location = deepcopy(reader.location)
    if location.coordinates:
        location.coordinates.line = line
        location.dependency_type = DependencyType.DIRECT

    try:
        return Package(
            name=name,
            version=version,
            locations=[location],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url=PackageURL(
                type="nuget",
                namespace="",
                name=name,
                version=version,
                qualifiers={},
                subpath="",
            ).to_string(),
        )
    except ValidationError as ex:
        LOGGER.warning(
            "Malformed package. Required fields are missing or data types are incorrect.",
            extra={
                "extra": {
                    "exception": format_exception(str(ex)),
                    "location": location.path(),
                },
            },
        )
    return None


def _format_csproj_reference_deps(root: BeautifulSoup, reader: LocationReadCloser) -> list[Package]:
    return [
        package
        for pkg in root.find_all("reference", recursive=True)
        if (
            (dll_path := pkg.find("hintpath"))
            and (raw_package := PACKAGE.match(dll_path.text))
            and (pkg_info := DEP_INFO.match(raw_package.group("package_info")))
            and (
                package := format_package(
                    str(pkg_info.group("package_name").lower()),
                    str(pkg_info.group("version")),
                    dll_path.sourceline,
                    reader,
                )
            )
        )
        or (
            (include := pkg.get("include"))
            and (include_info := include.replace(" ", "").split(","))
            and (version := _get_version(include_info))
            and (
                package := format_package(
                    str(include_info[0]).strip(),
                    str(version),
                    pkg.sourceline,
                    reader,
                )
            )
        )
    ]


def parse_csproj(
    _resolver: Resolver | None,
    _env: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    packages: list[Package] = []
    root = BeautifulSoup(reader.read_closer.read(), features="html.parser")
    for pkg in root.find_all("packagereference", recursive=True):
        name: str | None = pkg.get("include")
        version: str | None = pkg.get("version")
        if not name or not version:
            continue

        if package := format_package(name, version, pkg.sourceline, reader):
            packages.append(package)

    packages.extend(_format_csproj_reference_deps(root, reader))
    return packages, []
