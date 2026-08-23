import io
import cv2
import numpy as np
from pydantic import BaseModel
from PIL import Image as PILImage


class DetectionCandidate(BaseModel):
    bbox_x: float
    bbox_y: float
    bbox_width: float
    bbox_height: float
    confidence: float


class ProductDetectionService:
    def __init__(self, min_confidence: float = 0.50):
        self.min_confidence = min_confidence

    def detect_products(self, image_bytes: bytes) -> list[DetectionCandidate]:
        """
        Detects individual packaged products on a retail shelf or display image.
        Uses multi-scale edge filtering, adaptive morphological thresholding,
        shelf-line suppression, and Non-Maximum Suppression (NMS).
        """
        if not image_bytes:
            return []

        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                return []
        except Exception:
            return []

        img_h, img_w = img.shape[:2]
        if img_h < 40 or img_w < 40:
            return []

        total_area = float(img_w * img_h)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Contrast Limited Adaptive Histogram Equalization (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # Shelf / plank suppression: detect long continuous horizontal lines (> 30% image width)
        h_len = max(40, int(img_w * 0.30))
        h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (h_len, 1))
        shelf_lines = cv2.morphologyEx(enhanced, cv2.MORPH_OPEN, h_kernel)
        cleaned = cv2.subtract(enhanced, shelf_lines)

        candidates: list[tuple[int, int, int, int, float]] = []

        # Pass 1: Adaptive Thresholding with small structuring element
        thresh1 = cv2.adaptiveThreshold(
            cleaned, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 3
        )
        kernel1 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        closed1 = cv2.morphologyEx(thresh1, cv2.MORPH_CLOSE, kernel1, iterations=1)

        # Pass 2: Otsu thresholding on blurred cleaned image
        blurred = cv2.GaussianBlur(cleaned, (5, 5), 0)
        _, thresh2 = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        closed2 = cv2.morphologyEx(thresh2, cv2.MORPH_CLOSE, kernel2, iterations=1)

        # Pass 3: Canny edges + light dilation
        edges = cv2.Canny(cleaned, 30, 120)
        kernel3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        closed3 = cv2.dilate(edges, kernel3, iterations=1)

        # Pass 4: Color gradient magnitude
        grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        mag = cv2.magnitude(grad_x, grad_y)
        mag_max = float(mag.max())
        closed_maps = [closed1, closed2, closed3]
        if mag_max > 0:
            mag_norm = np.uint8(np.clip(mag / mag_max * 255, 0, 255))
            _, grad_thresh = cv2.threshold(mag_norm, 30, 255, cv2.THRESH_BINARY)
            closed4 = cv2.morphologyEx(grad_thresh, cv2.MORPH_CLOSE, kernel2, iterations=1)
            closed_maps.append(closed4)

        for closed_map in closed_maps:
            contours, _ = cv2.findContours(closed_map, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                area = w * h
                area_ratio = area / total_area

                # Filter out background planks and microscopic noise
                if area_ratio > 0.60 or area_ratio < 0.003:
                    continue
                if w < 25 or h < 25:
                    continue
                if w > 0.75 * img_w or h > 0.85 * img_h:
                    continue

                aspect_ratio = float(w) / float(h)
                # Packaged products aspect ratio typically between 0.15 and 4.0
                if aspect_ratio < 0.15 or aspect_ratio > 4.5:
                    continue

                # Calculate confidence score based on contour properties
                cnt_area = cv2.contourArea(cnt)
                solidity = float(cnt_area) / float(area) if area > 0 else 0.0

                roi_gray = gray[y:y+h, x:x+w]
                if roi_gray.size == 0:
                    continue
                std_dev = float(np.std(roi_gray))
                contrast_score = min(1.0, std_dev / 40.0)

                ar_score = 1.0 - min(1.0, abs(aspect_ratio - 1.0) / 3.0)

                confidence = (solidity * 0.35) + (contrast_score * 0.45) + (ar_score * 0.20)
                confidence = float(np.clip(confidence, 0.0, 0.99))

                if confidence >= self.min_confidence:
                    candidates.append((x, y, w, h, confidence))

        if not candidates:
            return []

        # Apply Non-Maximum Suppression (NMS)
        nms_boxes = self._apply_nms(candidates, iou_threshold=0.30)

        # Sort spatially: top-to-bottom, left-to-right
        nms_boxes.sort(key=lambda b: (b[1] // 80, b[0]))

        return [
            DetectionCandidate(
                bbox_x=float(box[0]),
                bbox_y=float(box[1]),
                bbox_width=float(box[2]),
                bbox_height=float(box[3]),
                confidence=round(float(box[4]), 3)
            )
            for box in nms_boxes
        ]

    def _apply_nms(self, boxes: list[tuple[int, int, int, int, float]], iou_threshold: float = 0.30) -> list[tuple[int, int, int, int, float]]:
        if not boxes:
            return []

        boxes_sorted = sorted(boxes, key=lambda b: b[4], reverse=True)
        selected: list[tuple[int, int, int, int, float]] = []

        for b in boxes_sorted:
            bx, by, bw, bh, bconf = b
            b_x2, b_y2 = bx + bw, by + bh
            b_area = bw * bh

            keep = True
            for s in selected:
                sx, sy, sw, sh, _ = s
                s_x2, s_y2 = sx + sw, sy + sh
                s_area = sw * sh

                # Intersection
                ix1 = max(bx, sx)
                iy1 = max(by, sy)
                ix2 = min(b_x2, s_x2)
                iy2 = min(b_y2, s_y2)

                inter_w = max(0, ix2 - ix1)
                inter_h = max(0, iy2 - iy1)
                inter_area = inter_w * inter_h

                if inter_area > 0:
                    union_area = b_area + s_area - inter_area
                    iou = inter_area / union_area if union_area > 0 else 0.0
                    overlap_ratio = inter_area / min(b_area, s_area)
                    if iou > iou_threshold or overlap_ratio > 0.60:
                        keep = False
                        break

            if keep:
                selected.append(b)

        return selected

    def crop_product(
        self,
        image_bytes: bytes,
        bbox_x: float,
        bbox_y: float,
        bbox_width: float,
        bbox_height: float,
        padding_ratio: float = 0.03
    ) -> bytes:
        """
        Crops an individual product from original image bytes.
        Adds safe padding and boundary clipping.
        Never modifies the original evidence image.
        """
        pil_img = PILImage.open(io.BytesIO(image_bytes))
        img_w, img_h = pil_img.size

        if bbox_width <= 1.0 and bbox_height <= 1.0 and img_w > 1 and img_h > 1:
            bx = bbox_x * img_w
            by = bbox_y * img_h
            bw = bbox_width * img_w
            bh = bbox_height * img_h
        else:
            bx, by, bw, bh = bbox_x, bbox_y, bbox_width, bbox_height

        pad_x = bw * padding_ratio
        pad_y = bh * padding_ratio

        x1 = max(0, int(bx - pad_x))
        y1 = max(0, int(by - pad_y))
        x2 = min(img_w, int(bx + bw + pad_x))
        y2 = min(img_h, int(by + bh + pad_y))

        if x2 <= x1:
            x2 = min(img_w, x1 + 10)
        if y2 <= y1:
            y2 = min(img_h, y1 + 10)

        crop = pil_img.crop((x1, y1, x2, y2))

        if crop.mode in ("RGBA", "P"):
            crop = crop.convert("RGB")

        out_io = io.BytesIO()
        crop.save(out_io, format="JPEG", quality=95)
        return out_io.getvalue()


product_detection_service = ProductDetectionService()
