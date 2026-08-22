import uuid
from pydantic import BaseModel, ConfigDict


class CalibrationRequest(BaseModel):
    calibration_type: str # aruco, qr, credit_card, coin, manual
    reference_width_mm: float
    reference_width_px: float | None = None
    known_package_width_mm: float | None = None
    known_package_width_px: float | None = None


class CalibrationResponse(BaseModel):
    id: uuid.UUID
    inspection_id: uuid.UUID
    image_id: uuid.UUID | None = None
    calibration_type: str
    reference_width_mm: float
    reference_width_px: float
    pixels_per_mm: float
    measurement_error: float
    calibration_confidence: float
    perspective_transform: list | None = None

    model_config = ConfigDict(from_attributes=True)
