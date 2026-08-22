import cv2
import numpy as np
import pytest
from app.services.cv.quality_check_service import QualityCheckService


def create_test_image(width=800, height=800, blur=False, low_res=False, glare=False):
    if low_res:
        img = np.zeros((100, 100, 3), dtype=np.uint8)
    else:
        img = np.zeros((height, width, 3), dtype=np.uint8)
        # Add high contrast sharp text/lines for clear Laplacian variance
        cv2.putText(img, "LABELSETU TEST PACKET", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        cv2.putText(img, "NET WT. 500g MRP Rs 250", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
        cv2.rectangle(img, (50, 250), (700, 700), (255, 255, 255), 2)

    if blur:
        img = cv2.GaussianBlur(img, (55, 55), 0)

    if glare:
        # Fill > 20% of image with bright white glare pixels
        img[300:700, 300:700] = 255

    _, encoded = cv2.imencode(".jpg", img)
    return encoded.tobytes()


def test_quality_check_low_resolution():
    service = QualityCheckService()
    img_bytes = create_test_image(low_res=True)
    res = service.evaluate_image(img_bytes)
    assert res.is_usable is False
    assert res.status == "needs_recapture"
    assert res.reason == "low_resolution"


def test_quality_check_blur():
    service = QualityCheckService(blur_threshold=100.0)
    img_bytes = create_test_image(blur=True)
    res = service.evaluate_image(img_bytes)
    assert res.is_usable is False
    assert res.status == "needs_recapture"
    assert res.reason == "blur"


def test_quality_check_glare():
    service = QualityCheckService(glare_threshold=0.10)
    img_bytes = create_test_image(glare=True)
    res = service.evaluate_image(img_bytes)
    assert res.is_usable is False
    assert res.status == "needs_recapture"
    assert res.reason == "glare"


def test_quality_check_usable():
    service = QualityCheckService()
    img_bytes = create_test_image()
    res = service.evaluate_image(img_bytes)
    assert res.is_usable is True
    assert res.status == "complete"
    assert res.reason is None
