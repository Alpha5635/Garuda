from app.services.auth_service import AuthService
from app.services.storage_service import storage_service, StorageService
from app.services.cv.quality_check_service import quality_check_service, QualityCheckService
from app.services.ocr.ocr_service import ocr_service, OcrService
from app.services.inspection.inspection_service import InspectionService

__all__ = [
    "AuthService",
    "storage_service",
    "StorageService",
    "quality_check_service",
    "QualityCheckService",
    "ocr_service",
    "OcrService",
    "InspectionService",
]
