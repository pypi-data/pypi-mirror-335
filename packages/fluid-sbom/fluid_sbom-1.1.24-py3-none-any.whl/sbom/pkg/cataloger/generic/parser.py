from collections.abc import Callable

from pydantic import (
    BaseModel,
    ConfigDict,
)

from sbom.artifact.relationship import (
    Relationship,
)
from sbom.file.location_read_closer import (
    LocationReadCloser,
)
from sbom.file.resolver import (
    Resolver,
)
from sbom.linux.release import (
    Release,
)
from sbom.model.core import (
    Package,
)


class Environment(BaseModel):
    linux_release: Release | None
    model_config = ConfigDict(frozen=True)


Parser = Callable[
    [Resolver, Environment, LocationReadCloser],
    tuple[list[Package], list[Relationship]] | None,
]
