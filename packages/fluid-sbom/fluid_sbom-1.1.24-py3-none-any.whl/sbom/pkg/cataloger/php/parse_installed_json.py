import logging
from copy import (
    deepcopy,
)
from typing import (
    cast,
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
from sbom.internal.collection.json import (
    parse_json_with_tree_sitter,
)
from sbom.internal.collection.types import (
    IndexedDict,
    IndexedList,
    ParsedValue,
)
from sbom.model.core import (
    Package,
)
from sbom.pkg.cataloger.generic.parser import (
    Environment,
)
from sbom.pkg.cataloger.php.model import PhpComposerInstalledEntry, PhpComposerLockEntry
from sbom.pkg.cataloger.php.package import (
    new_package_from_composer,
)

LOGGER = logging.getLogger(__name__)
EMPTY_LIST: IndexedList[ParsedValue] = IndexedList()


def _extract_packages(
    package_json: IndexedDict[str, ParsedValue],
    location: Location,
) -> list[Package]:
    packages = []
    if isinstance(package_json, IndexedDict) and "dev-package-names" in package_json:
        dev_packages = cast(IndexedList[ParsedValue], package_json["dev-package-names"])
    else:
        dev_packages = EMPTY_LIST

    packages_list = (
        package_json["packages"] if isinstance(package_json, IndexedDict) else package_json
    )

    for package in packages_list if isinstance(packages_list, IndexedList) else EMPTY_LIST:
        if not isinstance(package, IndexedDict):
            continue
        pkg_item = new_package_from_composer(package, deepcopy(location), is_dev=False)
        if pkg_item:
            pkg_item.is_dev = pkg_item.name in dev_packages
            packages.append(pkg_item)

    return packages


def _extract_relationships(packages: list[Package]) -> list[Relationship]:
    relationships = []
    for package in packages:
        if not isinstance(package.metadata, PhpComposerInstalledEntry | PhpComposerLockEntry):
            continue
        package_metadata = package.metadata.require
        dependencies = list(package_metadata.keys()) if package_metadata else []
        for dep_name in dependencies:
            package_dep = next((x for x in packages if x.name == dep_name), None)
            if package_dep:
                relationships.append(
                    Relationship(
                        from_=package,
                        to_=package_dep,
                        type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
                    ),
                )

    return relationships


def parse_installed_json(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    package_json = cast(
        IndexedDict[str, ParsedValue],
        parse_json_with_tree_sitter(reader.read_closer.read()),
    )

    packages = _extract_packages(package_json, reader.location)
    relationships = _extract_relationships(packages)

    return packages, relationships
