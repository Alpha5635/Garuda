from dataclasses import dataclass
import cv2
import numpy as np
from app.config import settings


@dataclass
class QualityCheckResult:
    is_usable: bool
    status: str # "complete" or "needs_recapture"
    reason: str | None # "blur", "glare", "low_resolution", "bad_orientation", None
    metrics: dict


class QualityCheckService:
    def __init__(
        self,
        blur_threshold: float = settings.BLUR_THRESHOLD,
        glare_threshold: float = settings.GLARE_THRESHOLD,
        min_width: int = settings.MIN_IMAGE_WIDTH,
        min_height: int = settings.MIN_IMAGE_HEIGHT,
    ):
        self.blur_threshold = blur_threshold
        self.glare_threshold = glare_threshold
        self.min_width = min_width
        self.min_height = min_height

    def evaluate_image(self, image_bytes: bytes, is_crop: bool = False) -> QualityCheckResult:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return QualityCheckResult(
                is_usable=False,
                status="needs_recapture",
                reason="unusable_image",
                metrics={"error": "Failed to decode image bytes"}
            )

        height, width = img.shape[:2]
        effective_min_w = 40 if is_crop else self.min_width
        effective_min_h = 40 if is_crop else self.min_height

        # 1. Resolution Check
        if width < effective_min_w or height < effective_min_h:
            return QualityCheckResult(
                is_usable=False,
                status="needs_recapture",
                reason="low_resolution",
                metrics={"width": width, "height": height, "min_width": effective_min_w, "min_height": effective_min_h}
            )

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 2. Blur Detection (Laplacian Variance)
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        effective_blur_thresh = 10.0 if is_crop else self.blur_threshold
        if laplacian_var < effective_blur_thresh:
            return QualityCheckResult(
                is_usable=False,
                status="needs_recapture",
                reason="blur",
                metrics={
                    "laplacian_variance": laplacian_var,
                    "blur_threshold": effective_blur_thresh,
                    "width": width,
                    "height": height
                }
            )

        # 3. Glare Detection (Excessive Bright Highlights)
        glare_pixels = np.sum(gray >= 240)
        total_pixels = width * height
        glare_ratio = float(glare_pixels / total_pixels)
        effective_glare_thresh = 0.98 if is_crop else self.glare_threshold

        if glare_ratio > effective_glare_thresh:
            return QualityCheckResult(
                is_usable=False,
                status="needs_recapture",
                reason="glare",
                metrics={
                    "glare_ratio": glare_ratio,
                    "glare_threshold": effective_glare_thresh,
                    "laplacian_variance": laplacian_var
                }
            )

        # 4. Severe Skew / Bad Orientation Check
        # Check aspect ratio extreme skew (e.g. ratio > 10 or < 0.1)
        aspect_ratio = float(width / height)
        if aspect_ratio > 10.0 or aspect_ratio < 0.1:
            return QualityCheckResult(
                is_usable=False,
                status="needs_recapture",
                reason="bad_orientation",
                metrics={"aspect_ratio": aspect_ratio}
            )

        return QualityCheckResult(
            is_usable=True,
            status="complete",
            reason=None,
            metrics={
                "laplacian_variance": laplacian_var,
                "glare_ratio": glare_ratio,
                "width": width,
                "height": height,
                "aspect_ratio": aspect_ratio
            }
        )


quality_check_service = QualityCheckService()
