from enum import (
    Enum,
)


class DependencyType(Enum):
    DIRECT = "DIRECT"
    TRANSITIVE = "TRANSITIVE"
    UNKNOWN = "UNKNOWN"
