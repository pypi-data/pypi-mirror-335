from sbom.advisories import images as advisories
from sbom.internal.package_information.dart import (
    PubPackage,
    PubPackageVersion,
    get_pub_package,
)
from sbom.model.core import (
    Artifact,
    Digest,
    HealthMetadata,
    Package,
)
from sbom.pkg.cataloger.common import (
    infer_algorithm,
)


def _get_current_package(pub_package: PubPackage, version: str) -> PubPackageVersion | None:
    return next((v for v in pub_package["versions"] if v["version"] == version), None)


def _get_authors(pub_package: PubPackage) -> str | None:
    return next(
        (
            version["pubspec"]["author"]
            for version in reversed(pub_package["versions"])
            if "author" in version["pubspec"]
        ),
        None,
    )


def _get_artifact(current_package: PubPackageVersion) -> Artifact:
    digest_value = current_package["archive_sha256"]
    return Artifact(
        url=current_package["archive_url"],
        integrity=Digest(
            value=digest_value,
            algorithm=infer_algorithm(digest_value),
        ),
    )


def _set_health_metadata(
    package: Package,
    pub_package: PubPackage,
    current_package: PubPackageVersion | None,
) -> None:
    package.health_metadata = HealthMetadata(
        latest_version=pub_package["latest"]["version"],
        latest_version_created_at=pub_package["latest"]["published"],
        authors=_get_authors(pub_package),
        artifact=_get_artifact(current_package) if current_package else None,
    )


def _update_advisories(package: Package) -> None:
    pkg_advisories = advisories.get_package_advisories(package)
    if pkg_advisories:
        package.advisories = pkg_advisories


def complete_package(package: Package) -> Package:
    _update_advisories(package)
    pub_package = get_pub_package(package.name)
    if not pub_package:
        return package

    current_package = _get_current_package(pub_package, package.version)

    _set_health_metadata(package, pub_package, current_package)

    return package
