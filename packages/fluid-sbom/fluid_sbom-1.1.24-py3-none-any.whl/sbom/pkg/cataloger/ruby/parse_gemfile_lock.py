import logging
import os
from copy import (
    deepcopy,
)
from ctypes import (
    c_void_p,
    cdll,
)

from pydantic import (
    ValidationError,
)
from tree_sitter import (
    Language as TLanguage,
)
from tree_sitter import (
    Node,
    Parser,
)

from sbom.artifact.relationship import (
    Relationship,
    RelationshipType,
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
from sbom.pkg.cataloger.ruby.package import (
    package_url,
)
from sbom.utils.env import (
    TREE_SITTER_PARSERS,
)
from sbom.utils.strings import format_exception

LOGGER = logging.getLogger(__name__)


def lang_from_so(path: str, name: str) -> TLanguage:
    lib = cdll.LoadLibrary(os.fspath(path))
    language_function = getattr(lib, f"tree_sitter_{name}")
    language_function.restype = c_void_p
    language_ptr = language_function()
    return TLanguage(language_ptr)


def collect_gem_entries(_content: str) -> tuple[list[Node], list[str]]:
    if TREE_SITTER_PARSERS is None:
        LOGGER.warning(
            (
                "Unable to parse gemfile.lock file because the binary file "
                "for the parser is not available in the environment."
            ),
        )
        return [], []
    so_library_path: str = os.path.join(TREE_SITTER_PARSERS, "gemfilelock.so")
    parser_language = lang_from_so(so_library_path, "gemfilelock")
    parser = Parser(parser_language)
    result = parser.parse(_content.encode("utf-8"))

    dependencies_node = next(
        (node for node in result.root_node.children if node.type == "dependencies"),
        None,
    )
    dependencies: list[str] = []
    if dependencies_node and dependencies_node.children:
        dependencies.extend(
            dependency.children[0].parent.named_children[0].text.decode("utf-8")
            for dependency in dependencies_node.children[1:]
            if (
                dependency.children
                and dependency.children[0].parent
                and dependency.children[0].parent.named_children
                and dependency.children[0].parent.named_children[0].text
            )
        )

    gem_section = next(
        (node for node in result.root_node.children if node.type == "gem_section"),
        None,
    )
    if gem_section and (
        specs := next(
            (x for x in gem_section.children[1].children if x.type == "specs"),
            None,
        )
    ):
        return [x.children[0] for x in specs.children[1:]], dependencies

    return [], dependencies


def parse_gemfile_lock(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    packages: list[Package] = []
    relationships: list[Relationship] = []
    gem_entries, dependencies = collect_gem_entries(reader.read_closer.read())

    packages = _process_packages(gem_entries, reader, dependencies)
    relationships = _process_dependencies(gem_entries, packages)

    return packages, relationships


def _process_packages(
    gem_entries: list,
    reader: LocationReadCloser,
    dependencies: list,
) -> list[Package]:
    packages = []

    for gem_entry in gem_entries:
        gem_name = gem_entry.named_children[0].text.decode("utf-8")
        gem_version = gem_entry.named_children[1].text.decode("utf-8")

        if not gem_name or not gem_version:
            continue

        location = deepcopy(reader.location)
        if location.coordinates:
            location.coordinates.line = gem_entry.start_point[0] + 1
            location.dependency_type = (
                DependencyType.DIRECT if gem_name in dependencies else DependencyType.TRANSITIVE
            )

        try:
            packages.append(
                Package(
                    name=gem_name,
                    version=gem_version,
                    locations=[location],
                    language=Language.RUBY,
                    licenses=[],
                    p_url=package_url(gem_name, gem_version),
                    type=PackageType.GemPkg,
                    metadata=None,
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


def _process_dependencies(
    gem_entries: list,
    packages: list[Package],
) -> list[Relationship]:
    relationships = []

    for gem_entry in gem_entries:
        gem_entry_name = gem_entry.named_children[0].text.decode("utf-8")
        _package = next(
            (pkg for pkg in packages if pkg.name == gem_entry_name),
            None,
        )

        if not _package or not gem_entry.parent:
            continue

        for dependency_node in (x for x in gem_entry.parent.children if x.type == "dependency"):
            dependency_name = dependency_node.named_children[0].text.decode(
                "utf-8",
            )

            dependency_package = next(
                (pkg for pkg in packages if pkg.name == dependency_name),
                None,
            )

            if dependency_package:
                relationships.append(
                    Relationship(
                        from_=_package,
                        to_=dependency_package,
                        type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
                    ),
                )

    return relationships
