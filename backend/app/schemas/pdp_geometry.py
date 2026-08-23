from pydantic import BaseModel, ConfigDict


class BoundingBoxOverlay(BaseModel):
    label: str
    bbox: list[list[float]] | list[float]
    color: str = "#00FF00"


class PDPGeometryResponse(BaseModel):
    pdp_bbox: list[float] | None = None # [x1, y1, x2, y2]
    pdp_area_sq_cm: float | None = None
    net_qty_bbox: list[list[float]] | list[float] | None = None
    clearance_margin_mm: float | None = None
    overlays: list[BoundingBoxOverlay] = []

    model_config = ConfigDict(from_attributes=True)
