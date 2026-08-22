import uuid
from pydantic import BaseModel, ConfigDict


class NormalizedFieldSchema(BaseModel):
    field_name: str
    raw_value: str
    normalized_value: str | None = None
    numeric_value: float | None = None
    unit: str | None = None
    confidence: float
    bounding_box: list | None = None

    model_config = ConfigDict(from_attributes=True)
