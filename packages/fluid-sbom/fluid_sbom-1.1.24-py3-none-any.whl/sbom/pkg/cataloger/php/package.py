import logging
from copy import (
    deepcopy,
)
from typing import (
    cast,
)

from packageurl import (
    PackageURL,
)
from pydantic import (
    ValidationError,
)

from sbom.advisories import (
    images as advisories,
)
from sbom.file.dependency_type import (
    DependencyType,
)
from sbom.file.location import (
    Location,
)
from sbom.file.scope import (
    Scope,
)
from sbom.internal.collection.types import (
    IndexedDict,
    IndexedList,
    ParsedValue,
)
from sbom.internal.package_information.php import (
    PackagistPackageInfo,
    get_composer_package,
)
from sbom.model.core import (
    Artifact,
    Digest,
    HealthMetadata,
    Language,
    Package,
    PackageType,
)
from sbom.pkg.cataloger.common import (
    infer_algorithm,
)
from sbom.pkg.cataloger.php.model import (
    PhpComposerAuthors,
    PhpComposerExternalReference,
    PhpComposerInstalledEntry,
)
from sbom.utils.licenses.validation import (
    validate_licenses,
)
from sbom.utils.strings import format_exception

LOGGER = logging.getLogger(__name__)

EMPTY_LIST: IndexedList[str] = IndexedList()


def package_url(name: str, version: str) -> str:
    fields = name.split("/")

    vendor = ""
    if len(fields) == 1:
        name = fields[0]
    elif len(fields) >= 2:
        vendor = fields[0]
        name = "-".join(fields[1:])

    return PackageURL(  # type: ignore
        type="composer",
        namespace=vendor,
        name=name,
        version=version,
        qualifiers=None,
        subpath="",
    ).to_string()


def new_package_from_composer(
    package: IndexedDict[str, ParsedValue],
    location: Location,
    *,
    is_dev: bool = False,
) -> Package | None:
    empty_list_dict: IndexedList[IndexedDict[str, str]] = IndexedList()
    new_location = deepcopy(location)
    new_location.scope = Scope.DEV if is_dev else Scope.PROD
    if new_location.coordinates:
        new_location.coordinates.line = package.position.start.line
        new_location.dependency_type = DependencyType.DIRECT

    try:
        source = cast(IndexedDict[str, str], package.get("source"))
        dist = cast(IndexedDict[str, str], package.get("dist"))
        name = cast(str, package.get("name"))
        version = cast(str, package.get("version"))

        if not name or not version:
            return None

        return Package(
            name=name,
            version=version,
            locations=[new_location],
            language=Language.PHP,
            licenses=list(cast(IndexedList[str], package.get("license", EMPTY_LIST))),
            type=PackageType.PhpComposerPkg,
            p_url=package_url(name, version),
            metadata=PhpComposerInstalledEntry(
                name=name,
                version=version,
                source=PhpComposerExternalReference(
                    type=source.get("type"),
                    url=source.get("url"),
                    reference=source.get("reference"),
                    shasum=source.get("shasum"),
                )
                if source
                else None,
                dist=PhpComposerExternalReference(
                    type=dist.get("type"),
                    url=dist.get("url"),
                    reference=dist.get("reference"),
                    shasum=dist.get("shasum"),
                )
                if dist
                else None,
                require=cast(dict[str, str], package.get("require"))
                if isinstance(package.get("require"), IndexedDict)
                else None,
                provide=cast(dict[str, str], package.get("provide"))
                if isinstance(package.get("provide"), IndexedDict)
                else None,
                require_dev=cast(dict[str, str], package.get("require-dev"))
                if isinstance(package.get("require-dev"), IndexedDict)
                else None,
                suggest=cast(dict[str, str], package.get("suggest"))
                if isinstance(package.get("suggest"), IndexedDict)
                else None,
                license=cast(list[str], package.get("license"))
                if isinstance(package.get("license"), IndexedList)
                else None,
                type=cast(str, package.get("type"))
                if isinstance(package.get("type"), str)
                else None,
                notification_url=cast(str, package.get("notification-url"))
                if isinstance(package.get("notification-url"), str)
                else None,
                bin=cast(list[str], package.get("bin"))
                if isinstance(package.get("bin"), IndexedList)
                else None,
                authors=[
                    PhpComposerAuthors(
                        name=cast(str, x.get("name")),
                        email=x.get("email"),
                        homepage=x.get("homepage"),
                    )
                    for x in cast(
                        list[IndexedDict[str, str]],
                        package.get("authors", empty_list_dict),
                    )
                ],
                description=cast(str, package.get("description"))
                if isinstance(package.get("description"), str)
                else None,
                homepage=cast(str, package.get("homepage"))
                if isinstance(package.get("homepage"), str)
                else None,
                keywords=cast(list[str], package.get("keywords"))
                if isinstance(package.get("keywords"), IndexedDict)
                else None,
                time=cast(str, package.get("time"))
                if isinstance(package.get("time"), str)
                else None,
            ),
            is_dev=is_dev,
        )
    except ValidationError as ex:
        LOGGER.warning(
            "Malformed package. Required fields are missing or data types are incorrect.",
            extra={
                "extra": {
                    "exception": format_exception(str(ex)),
                    "location": new_location.path(),
                },
            },
        )
        return None


def package_url_from_pecl(pkg_name: str, version: str) -> str:
    return PackageURL(  # type: ignore
        type="pecl",
        namespace="",
        name=pkg_name,
        version=version,
        qualifiers=None,
        subpath="",
    ).to_string()


def _get_author(composer_package: PackagistPackageInfo) -> str | None:
    if not composer_package.get("authors"):
        return None

    authors: list[str] = []
    authors_dict = composer_package["authors"]
    for author_item in authors_dict:
        author: str = author_item["name"]
        if "email" in author_item:
            author_email = author_item["email"]
            author += f" <{author_email}>"
        authors.append(author)

    return ", ".join(authors)


def _set_health_metadata(
    package: Package,
    composer_package: PackagistPackageInfo,
    current_package: PackagistPackageInfo | None,
) -> None:
    package.health_metadata = HealthMetadata(
        latest_version=composer_package["version"],
        latest_version_created_at=composer_package["time"],
        artifact=_get_artifact_metadata(current_package) if current_package else None,
        authors=_get_author(composer_package),
    )


def _get_artifact_metadata(
    current_package: PackagistPackageInfo | None,
) -> Artifact | None:
    if current_package:
        dist_info = current_package.get("dist")
        if isinstance(dist_info, dict) and isinstance(dist_info.get("url"), str):
            digest_value = dist_info.get("shasum") or None
            return Artifact(
                url=dist_info["url"],
                integrity=Digest(
                    algorithm=infer_algorithm(digest_value),
                    value=digest_value,
                ),
            )
    return None


def _update_advisories(package: Package) -> None:
    pkg_advisories = advisories.get_package_advisories(package)
    if pkg_advisories:
        package.advisories = pkg_advisories


def complete_package(package: Package) -> Package:
    _update_advisories(package)
    current_package = get_composer_package(package.name, package.version)
    composer_package = get_composer_package(package.name)

    if not composer_package:
        return package

    _set_health_metadata(package, composer_package, current_package)

    package.licenses = validate_licenses(composer_package["license"])

    return package
