import logging
from fnmatch import (
    fnmatch,
)
from zipfile import (
    BadZipFile,
    ZipFile,
    ZipInfo,
)

LOGGER = logging.getLogger(__name__)


def normalize_zip_entry_name(entry: str, *, case_insensitive: bool) -> str:
    if case_insensitive:
        entry = entry.lower()
    if not entry.startswith("/"):
        entry = "/" + entry

    return entry


def new_zip_file_manifest(archive_path: str) -> list[ZipInfo]:
    try:
        with ZipFile(archive_path, "r") as myzip:
            return myzip.infolist()
    except BadZipFile:
        return []


def zip_glob_match(
    manifest: list[ZipInfo],
    *,
    case_sensitive: bool,
    patterns: tuple[str, ...],
) -> list[str]:
    result = []

    for pattern in patterns:
        for entry in manifest:
            normalized_entry = normalize_zip_entry_name(
                entry.filename,
                case_insensitive=case_sensitive,
            )
            if entry.filename.endswith(pattern):
                result.append(entry.filename)
            lower_pattern = pattern.lower() if case_sensitive else pattern
            if fnmatch(normalized_entry, lower_pattern):
                result.append(entry.filename)
    return result
