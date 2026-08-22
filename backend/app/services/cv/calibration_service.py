from dataclasses import dataclass
import cv2
import numpy as np
from app.schemas.calibration import CalibrationRequest, CalibrationResponse


@dataclass
class CalibrationResult:
    is_valid: bool
    calibration_type: str
    reference_width_mm: float
    reference_width_px: float
    pixels_per_mm: float
    measurement_error: float # +/- mm
    calibration_confidence: float
    perspective_matrix: list | None = None
    status: str = "complete" # "complete" or "not_evaluable"


class CalibrationService:
    def calibrate_image(
        self,
        image_bytes: bytes,
        request: CalibrationRequest | None = None
    ) -> CalibrationResult:
        # 1. Manual or Provided Request Parameters
        if request and request.reference_width_mm > 0 and request.reference_width_px and request.reference_width_px > 0:
            px_per_mm = request.reference_width_px / request.reference_width_mm
            return CalibrationResult(
                is_valid=True,
                calibration_type=request.calibration_type,
                reference_width_mm=request.reference_width_mm,
                reference_width_px=request.reference_width_px,
                pixels_per_mm=round(px_per_mm, 4),
                measurement_error=round(1.0 / px_per_mm, 3), # 1 pixel measurement uncertainty
                calibration_confidence=0.95,
                status="complete"
            )

        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return CalibrationResult(
                is_valid=False,
                calibration_type="uncalibrated",
                reference_width_mm=0.0,
                reference_width_px=0.0,
                pixels_per_mm=0.0,
                measurement_error=0.0,
                calibration_confidence=0.0,
                status="not_evaluable"
            )

        # 2. ArUco Marker Detection (50 mm reference target)
        try:
            dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
            parameters = cv2.aruco.DetectorParameters()
            detector = cv2.aruco.ArucoDetector(dictionary, parameters)
            corners, ids, _ = detector.detectMarkers(img)

            if ids is not None and len(corners) > 0:
                c = corners[0][0] # 4 corners
                # calculate side width in pixels
                w1 = np.linalg.norm(c[0] - c[1])
                w2 = np.linalg.norm(c[2] - c[3])
                ref_px = float((w1 + w2) / 2.0)
                ref_mm = 50.0 # 50 mm standard target
                px_per_mm = ref_px / ref_mm

                return CalibrationResult(
                    is_valid=True,
                    calibration_type="aruco_50mm",
                    reference_width_mm=ref_mm,
                    reference_width_px=round(ref_px, 2),
                    pixels_per_mm=round(px_per_mm, 4),
                    measurement_error=round(1.0 / px_per_mm, 3),
                    calibration_confidence=0.98,
                    status="complete"
                )
        except Exception as e:
            print(f"[CalibrationService] ArUco detection fallback: {e}")

        # 3. QR Code Detection
        try:
            qr_detector = cv2.QRCodeDetector()
            val, points, _ = qr_detector.detectAndDecode(img)
            if points is not None and len(points) > 0:
                pts = points[0]
                w = np.linalg.norm(pts[0] - pts[1])
                ref_mm = 25.0 # standard QR target width in mm
                ref_px = float(w)
                px_per_mm = ref_px / ref_mm

                return CalibrationResult(
                    is_valid=True,
                    calibration_type="qr_code",
                    reference_width_mm=ref_mm,
                    reference_width_px=round(ref_px, 2),
                    pixels_per_mm=round(px_per_mm, 4),
                    measurement_error=round(1.0 / px_per_mm, 3),
                    calibration_confidence=0.90,
                    status="complete"
                )
        except Exception as e:
            print(f"[CalibrationService] QR detection fallback: {e}")

        # 4. Fallback / Uncalibrated -> NOT EVALUABLE
        return CalibrationResult(
            is_valid=False,
            calibration_type="uncalibrated",
            reference_width_mm=0.0,
            reference_width_px=0.0,
            pixels_per_mm=0.0,
            measurement_error=0.0,
            calibration_confidence=0.0,
            status="not_evaluable"
        )

    def measure_numeral_height_mm(
        self,
        bbox: list[list[float]] | list[float],
        pixels_per_mm: float
    ) -> float | None:
        if not pixels_per_mm or pixels_per_mm <= 0:
            return None

        # Bounding box is either polygon [[x1,y1],[x2,y2],[x3,y3],[x4,y4]] or rect [x,y,w,h]
        if isinstance(bbox[0], list):
            # Polygon: compute vertical height
            pts = np.array(bbox, dtype=np.float32)
            h1 = np.linalg.norm(pts[3] - pts[0])
            h2 = np.linalg.norm(pts[2] - pts[1])
            height_px = float((h1 + h2) / 2.0)
        else:
            # Rect [x, y, width, height]
            height_px = float(bbox[3])

        height_mm = height_px / pixels_per_mm
        return round(height_mm, 2)


calibration_service = CalibrationService()
