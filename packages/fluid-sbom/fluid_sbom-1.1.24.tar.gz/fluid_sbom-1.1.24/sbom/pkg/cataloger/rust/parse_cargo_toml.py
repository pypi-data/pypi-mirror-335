import logging
from typing import TYPE_CHECKING

from sbom.utils.strings import format_exception

if TYPE_CHECKING:
    from collections.abc import ItemsView

from pydantic import ValidationError

from sbom.artifact.relationship import Relationship
from sbom.file.dependency_type import DependencyType
from sbom.file.location import Location
from sbom.file.location_read_closer import LocationReadCloser
from sbom.file.resolver import Resolver
from sbom.file.scope import Scope
from sbom.internal.collection.toml import parse_toml_with_tree_sitter
from sbom.internal.collection.types import IndexedDict, ParsedValue
from sbom.model.core import Language, Package, PackageType
from sbom.pkg.cataloger.generic.parser import Environment
from sbom.pkg.cataloger.rust.package import package_url

LOGGER = logging.getLogger(__name__)


def _get_location(location: Location, sourceline: int) -> Location:
    if location.coordinates:
        c_upd = {"line": sourceline}
        l_upd = {"coordinates": location.coordinates.model_copy(update=c_upd)}
        location.dependency_type = DependencyType.DIRECT
        return location.model_copy(update=l_upd)
    return location


def _get_version(value: ParsedValue) -> str | None:
    if isinstance(value, str):
        return value
    if not isinstance(value, IndexedDict):
        return None
    if "git" in value:
        repo_url: str = str(value.get("git", ""))
        branch: str = str(value.get("branch", ""))
        if repo_url and branch:
            return f"{repo_url}@{branch}"
    version: str = str(value.get("version", ""))
    return version


def _get_packages(
    reader: LocationReadCloser,
    dependencies: ParsedValue,
    *,
    is_dev: bool,
) -> list[Package]:
    if dependencies is None or not isinstance(dependencies, IndexedDict):
        return []

    packages = []

    general_location = _get_location(
        reader.location,
        dependencies.position.start.line,
    )
    items: ItemsView[str, ParsedValue] = dependencies.items()

    for name, value in items:
        version = _get_version(value)
        if not name or not version:
            continue

        location = (
            _get_location(reader.location, value.position.start.line)
            if isinstance(value, IndexedDict)
            else general_location
        )
        location.scope = Scope.DEV if is_dev else Scope.PROD
        try:
            packages.append(
                Package(
                    name=name,
                    version=version,
                    locations=[location],
                    language=Language.RUST,
                    licenses=[],
                    p_url=package_url(name=name, version=version),
                    type=PackageType.RustPkg,
                ),
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
            continue

    return packages


def parse_cargo_toml(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    content: IndexedDict[
        str,
        ParsedValue,
    ] = parse_toml_with_tree_sitter(reader.read_closer.read())

    deps: ParsedValue = content.get(
        "dependencies",
    )
    dev_deps: ParsedValue = content.get(
        "dev-dependencies",
    )
    packages = [
        *_get_packages(reader, deps, is_dev=False),
        *_get_packages(reader, dev_deps, is_dev=True),
    ]
    return packages, []
