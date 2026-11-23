import uuid

from pydantic import BaseModel, ConfigDict


class MeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str | None
    display_name: str | None
    timezone: str
