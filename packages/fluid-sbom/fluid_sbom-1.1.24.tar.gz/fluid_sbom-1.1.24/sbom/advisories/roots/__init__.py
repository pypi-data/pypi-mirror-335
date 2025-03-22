import atexit
import logging
import os
import sqlite3
import subprocess  # nosec
from pathlib import Path
from typing import (
    Literal,
    cast,
)

import boto3
from botocore import (
    UNSIGNED,
)
from botocore.config import (
    Config,
)
from platformdirs import (
    user_data_dir,
)

from sbom.model.core import (
    Advisory,
)

LOGGER = logging.getLogger(__name__)

BUCKET_NAME = "skims.sca"
DB_NAME = "skims_sca_advisories.db"
BUCKET_FILE_KEY = f"{DB_NAME}.zst"
CONFIG_DIRECTORY = user_data_dir(
    appname="fluid-sbom",
    appauthor="fluidattacks",
    ensure_exists=True,
)
DB_LOCAL_PATH = os.path.join(CONFIG_DIRECTORY, DB_NAME)
DB_LOCAL_COMPRESSED_PATH = f"{DB_LOCAL_PATH}.zst"
S3_SERVICE_NAME: Literal["s3"] = "s3"
S3_CLIENT = boto3.client(
    service_name=S3_SERVICE_NAME,
    config=Config(
        region_name="us-east-1",
        signature_version=UNSIGNED,
    ),
)

MAP_MANAGER_TO_LANG = {
    "composer": "php",
    "pip": "python",
    "gem": "ruby",
    "npm": "javascript",
    "cargo": "rust",
    "swift": "swift",
    "conan": "conan",
    "erlang": "erlang",
    "github_actions": "github_actions",
    "go": "go",
    "maven": "java",
    "nuget": "dotnet",
    "pub": "dart",
}


def get_package_advisories(
    package_manager: str,
    package_name: str,
) -> list[Advisory]:
    connection = DATABASE.get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT
            adv_id,
            source,
            vulnerable_version,
            severity,
            epss,
            details
        FROM advisories
        WHERE package_manager = ? AND package_name = ?;
        """,
        (package_manager, package_name),
    )
    return [
        Advisory(
            id=result[0],
            urls=[result[1]],
            version_constraint=result[2],
            severity=result[3],
            epss=result[4],
            description=result[5],
            cpes=[],
            namespace=f"github:language:{MAP_MANAGER_TO_LANG[package_manager]}",
            percentile=0.0,
        )
        for result in cursor.fetchall()
    ]


def _get_database_file() -> None:
    LOGGER.info("⬇️ Downloading advisories database")
    S3_CLIENT.download_file(
        Bucket=BUCKET_NAME,
        Key=BUCKET_FILE_KEY,
        Filename=DB_LOCAL_COMPRESSED_PATH,
    )
    LOGGER.info("🗜️ Decompressing advisories database")
    with subprocess.Popen(  # noqa: S603
        ["zstd", "-d", "-f", DB_LOCAL_COMPRESSED_PATH],  # noqa: S607
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as process:
        _, stderr = process.communicate()
        if cast(int, process.returncode) != 0:
            raise RuntimeError(stderr.decode())


def initialize_db() -> bool:
    local_database_exists = Path(DB_LOCAL_PATH).is_file()

    try:
        db_metadata = S3_CLIENT.head_object(Bucket=BUCKET_NAME, Key=BUCKET_FILE_KEY)
        up_to_date = (
            local_database_exists
            and Path(DB_LOCAL_PATH).stat().st_mtime >= db_metadata["LastModified"].timestamp()
        )

        if up_to_date:
            LOGGER.info("✅ Advisories database is up to date")
            return True
        _get_database_file()
        Path(DB_LOCAL_COMPRESSED_PATH).unlink()
    except Exception:
        if local_database_exists:
            LOGGER.warning(
                "⚠️ Advisories may be outdated, unable to update database",
            )
            return True

        LOGGER.exception(
            "❌ Advisories won't be included, unable to download database",
        )
        return False
    else:
        return True


class Database:
    def __init__(self) -> None:
        self.connection: sqlite3.Connection | None = None

    def initialize(self) -> None:
        if self.connection is None and initialize_db():
            self.connection = sqlite3.connect(
                DB_LOCAL_PATH,
                check_same_thread=False,
            )
            atexit.register(self.connection.close)

    def get_connection(self) -> sqlite3.Connection:
        if self.connection is not None:
            return self.connection
        self.connection = sqlite3.connect(
            DB_LOCAL_PATH,
            check_same_thread=False,
        )
        atexit.register(self.connection.close)
        return self.connection


DATABASE = Database()
