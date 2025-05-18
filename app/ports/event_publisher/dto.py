from pydantic import UUID4, BaseModel


class EventPayload(BaseModel):
    event_id: UUID4
    event_name: str
    data: dict
