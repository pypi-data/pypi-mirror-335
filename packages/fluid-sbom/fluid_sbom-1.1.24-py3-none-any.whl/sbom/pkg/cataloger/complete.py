import logging
from typing import TYPE_CHECKING, cast

from pydantic import (
    ValidationError,
)

from sbom.file.location import Location
from sbom.model.core import (
    Advisory,
    HealthMetadata,
    Language,
    Package,
    PackageType,
)
from sbom.pkg.cataloger.alpine import (
    package as package_alpine,
)
from sbom.pkg.cataloger.dart import (
    package as package_dart,
)
from sbom.pkg.cataloger.debian import (
    package as package_debian,
)
from sbom.pkg.cataloger.dotnet import (
    package as package_dotnet,
)
from sbom.pkg.cataloger.golang import (
    package as package_go,
)
from sbom.pkg.cataloger.java import (
    package as package_java,
)
from sbom.pkg.cataloger.javascript import (
    package as package_js,
)
from sbom.pkg.cataloger.php import (
    package as package_php,
)
from sbom.pkg.cataloger.python import (
    package as package_python,
)
from sbom.pkg.cataloger.ruby import (
    package as package_ruby,
)
from sbom.pkg.cataloger.rust import (
    package as package_rust,
)
from sbom.utils.strings import format_exception

if TYPE_CHECKING:
    from collections.abc import Callable

LOGGER = logging.getLogger(__name__)


def complete_package(package: Package) -> Package | None:
    completion_map: dict[PackageType, Callable[[Package], Package]] = {
        PackageType.NpmPkg: package_js.complete_package,
        PackageType.DartPubPkg: package_dart.complete_package,
        PackageType.DotnetPkg: package_dotnet.complete_package,
        PackageType.JavaPkg: package_java.complete_package,
        PackageType.PhpComposerPkg: package_php.complete_package,
        PackageType.PythonPkg: package_python.complete_package,
        PackageType.GemPkg: package_ruby.complete_package,
        PackageType.RustPkg: package_rust.complete_package,
        PackageType.DebPkg: package_debian.complete_package,
        PackageType.ApkPkg: package_alpine.complete_package,
        PackageType.GoModulePkg: package_go.complete_package,
    }

    try:
        if package.type in completion_map:
            package = completion_map[package.type](package)
            package.model_validate(
                cast(
                    dict[
                        str,
                        str
                        | Language
                        | list[str]
                        | list[Location]
                        | PackageType
                        | list[Advisory]
                        | list[Package]
                        | HealthMetadata
                        | bool
                        | object
                        | None,
                    ],
                    package.__dict__,
                ),
            )
    except ValidationError as ex:
        LOGGER.warning(
            "Malformed package completion. Required fields are missing "
            "or data types are incorrect.",
            extra={
                "extra": {
                    "exception": format_exception(str(ex)),
                    "location": package.locations,
                    "package_type": package.type,
                },
            },
        )
        return None

    return package
