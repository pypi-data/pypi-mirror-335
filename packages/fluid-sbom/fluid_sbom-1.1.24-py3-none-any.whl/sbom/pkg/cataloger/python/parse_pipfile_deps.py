import logging
from copy import (
    deepcopy,
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
from sbom.file.location import (
    Location,
)
from sbom.file.location_read_closer import (
    LocationReadCloser,
)
from sbom.file.resolver import (
    Resolver,
)
from sbom.file.scope import Scope
from sbom.internal.collection import (
    toml,
)
from sbom.internal.collection.types import (
    IndexedDict,
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
from sbom.pkg.cataloger.python.model import (
    PythonPackage,
)
from sbom.pkg.cataloger.python.package import (
    package_url,
)
from sbom.utils.strings import format_exception

LOGGER = logging.getLogger(__name__)


def _get_location(location: Location, sourceline: int, scope: Scope) -> Location:
    location.scope = scope
    location.dependency_type = DependencyType.DIRECT
    if location.coordinates:
        c_upd = {"line": sourceline}
        l_upd = {"coordinates": location.coordinates.model_copy(update=c_upd)}
        return location.model_copy(update=l_upd)
    return location


def _get_location_alt(location: Location, scope: Scope) -> Location:
    location.scope = scope
    location.dependency_type = DependencyType.DIRECT
    return location


def _get_packages(
    reader: LocationReadCloser,
    toml_packages: IndexedDict[str, ParsedValue],
    *,
    is_dev: bool = False,
) -> list[Package]:
    result = []
    scope = Scope.DEV if is_dev else Scope.PROD
    for package, version_data in toml_packages.items():
        version: str = ""
        if isinstance(version_data, str):
            version = version_data.strip("=<>~^ ")
        if isinstance(version_data, IndexedDict):
            version = str(version_data.get("version", "*")).strip("=<>~^ ")

        if not package or not version or "*" in version:
            continue
        current_location = deepcopy(reader.location)
        try:
            result.append(
                Package(
                    name=package,
                    version=version,
                    locations=[
                        (
                            _get_location(
                                current_location,
                                package.position.start.line,
                                scope,
                            )
                            if isinstance(package, IndexedDict)
                            else _get_location_alt(current_location, scope)
                        ),
                    ],
                    language=Language.PYTHON,
                    type=PackageType.PythonPkg,
                    metadata=PythonPackage(
                        name=package,
                        version=version,
                    ),
                    p_url=package_url(
                        name=package,
                        version=version,
                        package=None,
                    ),
                    licenses=[],
                    is_dev=is_dev,
                ),
            )
        except ValidationError as ex:
            LOGGER.warning(
                "Malformed package. Required fields are missing or data types are incorrect.",
                extra={
                    "extra": {
                        "exception": format_exception(str(ex)),
                        "location": reader.location.path(),
                    },
                },
            )
            continue
    return result


def parse_pipfile_deps(
    _resolver: Resolver | None,
    _env: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    packages = []
    file_content = reader.read_closer.read()
    toml_content: IndexedDict[str, ParsedValue] = toml.parse_toml_with_tree_sitter(file_content)
    toml_packages = toml_content.get("packages")
    if not isinstance(toml_packages, IndexedDict):
        return [], []
    packages = _get_packages(reader, toml_packages)
    dev_deps = toml_content.get("dev-packages")
    if isinstance(dev_deps, IndexedDict):
        dev_pkgs = _get_packages(reader, dev_deps, is_dev=True)
        packages.extend(dev_pkgs)
    return packages, []
