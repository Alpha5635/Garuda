from app.schemas.ocr import OcrItemSchema
from app.schemas.normalization import NormalizedFieldSchema
from app.schemas.pdp_geometry import PDPGeometryResponse, BoundingBoxOverlay
from app.services.cv.calibration_service import CalibrationResult


class PDPGeometryService:
    def calculate_geometry(
        self,
        ocr_items: list[OcrItemSchema],
        normalized_fields: list[NormalizedFieldSchema],
        calibration_result: CalibrationResult,
        image_width: int = 1920,
        image_height: int = 1080
    ) -> PDPGeometryResponse:
        overlays: list[BoundingBoxOverlay] = []
        field_map = {f.field_name: f for f in normalized_fields}

        # 1. Estimate PDP Bounding Box as bounding container around all detected OCR text
        min_x, min_y = float(image_width), float(image_height)
        max_x, max_y = 0.0, 0.0

        for item in ocr_items:
            bbox = item.bbox
            if bbox:
                if isinstance(bbox[0], list):
                    for pt in bbox:
                        min_x = min(min_x, pt[0])
                        min_y = min(min_y, pt[1])
                        max_x = max(max_x, pt[0])
                        max_y = max(max_y, pt[1])
                elif isinstance(bbox, list) and len(bbox) >= 4:
                    min_x = min(min_x, bbox[0])
                    min_y = min(min_y, bbox[1])
                    max_x = max(max_x, bbox[0] + bbox[2])
                    max_y = max(max_y, bbox[1] + bbox[3])

        pdp_bbox = [round(min_x, 1), round(min_y, 1), round(max_x, 1), round(max_y, 1)] if max_x > min_x else [0, 0, image_width, image_height]
        
        pdp_area_sq_cm = None
        if calibration_result.is_valid and calibration_result.pixels_per_mm > 0:
            px_per_mm = calibration_result.pixels_per_mm
            w_mm = (max_x - min_x) / px_per_mm
            h_mm = (max_y - min_y) / px_per_mm
            pdp_area_sq_cm = round((w_mm * h_mm) / 100.0, 2)

        # 2. Net Quantity Bounding Box & Overlays
        net_qty_bbox = None
        clearance_margin_mm = None

        net_field = field_map.get("net_quantity")
        if net_field and net_field.bounding_box:
            net_qty_bbox = net_field.bounding_box
            overlays.append(
                BoundingBoxOverlay(
                    label="Net Quantity (Rule 7)",
                    bbox=net_field.bounding_box,
                    color="#00FF00"
                )
            )

        # Add overlays for other key declarations
        if field_map.get("mrp") and field_map["mrp"].bounding_box:
            overlays.append(BoundingBoxOverlay(label="MRP", bbox=field_map["mrp"].bounding_box, color="#FF9900"))

        if field_map.get("manufacturer") and field_map["manufacturer"].bounding_box:
            overlays.append(BoundingBoxOverlay(label="Manufacturer", bbox=field_map["manufacturer"].bounding_box, color="#0099FF"))

        return PDPGeometryResponse(
            pdp_bbox=pdp_bbox,
            pdp_area_sq_cm=pdp_area_sq_cm,
            net_qty_bbox=net_qty_bbox,
            clearance_margin_mm=5.0, # default 5 mm clearance
            overlays=overlays
        )


pdp_geometry_service = PDPGeometryService()
