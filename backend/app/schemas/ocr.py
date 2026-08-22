from typing import Any
from pydantic import BaseModel, ConfigDict


class BoundingBox(BaseModel):
    points: list[list[float]] # [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]


class OcrItemSchema(BaseModel):
    raw_text: str
    confidence: float
    bbox: list[list[float]] | list[float]
    language: str = "en"
    ocr_model: str = "PaddleOCR-v4"


class OcrResultContainer(BaseModel):
    items: list[OcrItemSchema] = []
    text: list[str] = []
    confidence: float = 0.0


class ExtractedFieldCandidate(BaseModel):
    field_name: str
    value: str
    confidence: float
    raw_snippet: str | None = None


class InspectionAnalysisResponse(BaseModel):
    inspection_id: str
    status: str
    ocr: OcrResultContainer
    fields: list[ExtractedFieldCandidate] = []
    job_id: str | None = None
    error_reason: str | None = None

    model_config = ConfigDict(from_attributes=True)
