import logging
from copy import (
    deepcopy,
)
from typing import (
    TypedDict,
    cast,
)

from pydantic import (
    BaseModel,
    ValidationError,
)

from sbom.artifact.relationship import (
    Relationship,
    RelationshipType,
)
from sbom.file.location import (
    Location,
)
from sbom.file.location_read_closer import (
    LocationReadCloser,
)
from sbom.file.resolver import (
    Resolver,
)
from sbom.internal.collection.toml import (
    parse_toml_with_tree_sitter,
)
from sbom.internal.collection.types import (
    IndexedDict,
    IndexedList,
    ParsedValue,
)
from sbom.model.core import (
    Language,
    Package,
    PackageType,
)
from sbom.pkg.cataloger.generic.parser import (
    Environment,
)
from sbom.pkg.cataloger.rust.package import (
    package_url,
)
from sbom.utils.strings import format_exception

LOGGER = logging.getLogger(__name__)


class RustCargoLockEntry(BaseModel):
    name: str
    version: str
    source: str | None
    checksum: str | None
    dependencies: list[str]


class CargoLockEntry(TypedDict):
    name: str
    version: str
    source: str | None
    checksum: str | None
    dependencies: list[str]


class CargoLock(TypedDict):
    package: IndexedList[CargoLockEntry]


def _create_package(pkg: ParsedValue, location: Location) -> Package | None:
    if not isinstance(pkg, IndexedDict):
        return None
    name = str(pkg.get("name", ""))
    version = str(pkg.get("version", ""))

    if not name or not version:
        return None

    source = str(pkg.get("source", ""))
    dependencies: IndexedList[str] | None = cast(IndexedList[str] | None, pkg.get("dependencies"))
    checksum = str(pkg.get("checksum", ""))

    current_location = deepcopy(location)
    if current_location.coordinates and hasattr(pkg, "position"):
        current_location.coordinates.line = pkg.position.start.line

    try:
        return Package(
            name=name,
            version=version,
            locations=[current_location],
            language=Language.RUST,
            licenses=[],
            p_url=package_url(name, version),
            type=PackageType.RustPkg,
            metadata=RustCargoLockEntry(
                name=name,
                version=version,
                source=source,
                dependencies=list(dependencies or []),
                checksum=checksum,
            ),
        )
    except ValidationError as ex:
        LOGGER.warning(
            "Malformed package. Required fields are missing or data types are incorrect.",
            extra={
                "extra": {
                    "exception": format_exception(str(ex)),
                    "location": current_location.path(),
                },
            },
        )
        return None


def _create_relationships(packages: list[Package]) -> list[Relationship]:
    relationships: list[Relationship] = []
    for pkg in packages:
        if isinstance(pkg.metadata, RustCargoLockEntry):
            relationships.extend(
                Relationship(
                    from_=pkg,
                    to_=dep,
                    type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
                )
                for dep_name in pkg.metadata.dependencies
                if (dep := next((x for x in packages if x.name == dep_name), None))
            )
    return relationships


def parse_cargo_lock(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    packages: list[Package] = []

    if not reader.location.coordinates:
        return packages, []

    _content = reader.read_closer.read()
    toml: IndexedDict[str, ParsedValue] = parse_toml_with_tree_sitter(
        _content,
    )

    toml_pkgs: ParsedValue = toml.get("package")
    if not isinstance(toml_pkgs, IndexedList):
        return [], []

    packages.extend(
        package
        for package in (_create_package(pkg, reader.location) for pkg in toml_pkgs)
        if package
    )

    relationships = _create_relationships(packages)

    return packages, relationships
