from pydantic import (
    BaseModel,
)

from sbom.file.type import (
    Type,
)


class Metadata(BaseModel):
    path: str
    link_destination: str
    user_id: int
    group_id: int
    type: Type
    mime_type: str
