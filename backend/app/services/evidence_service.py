import uuid
import cv2
import numpy as np
from app.services.storage_service import storage_service


class EvidenceService:
    def crop_and_store_evidence(
        self,
        original_image_bytes: bytes,
        inspection_id: uuid.UUID,
        rule_id: str,
        bbox: list[list[float]] | list[float] | None
    ) -> str:
        if not bbox or not original_image_bytes:
            return f"evidence/inspections/{inspection_id}/no_crop_{uuid.uuid4()}.jpg"

        nparr = np.frombuffer(original_image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return f"evidence/inspections/{inspection_id}/no_crop_{uuid.uuid4()}.jpg"

        h, w = img.shape[:2]

        if isinstance(bbox[0], list):
            pts = np.array(bbox, dtype=np.int32)
            min_x = max(0, int(np.min(pts[:, 0])))
            min_y = max(0, int(np.min(pts[:, 1])))
            max_x = min(w, int(np.max(pts[:, 0])))
            max_y = min(h, int(np.max(pts[:, 1])))
        else:
            min_x = max(0, int(bbox[0]))
            min_y = max(0, int(bbox[1]))
            max_x = min(w, int(bbox[0] + bbox[2]))
            max_y = min(h, int(bbox[1] + bbox[3]))

        # Add 10px padding if possible
        min_x = max(0, min_x - 10)
        min_y = max(0, min_y - 10)
        max_x = min(w, max_x + 10)
        max_y = min(h, max_y + 10)

        crop = img[min_y:max_y, min_x:max_x] if (max_x > min_x and max_y > min_y) else img

        _, crop_bytes = cv2.imencode(".jpg", crop)
        object_key = f"evidence/inspections/{inspection_id}/{rule_id}_{uuid.uuid4()}.jpg"

        storage_service.upload_file_bytes(object_key, crop_bytes.tobytes(), content_type="image/jpeg")
        return object_key


evidence_service = EvidenceService()
