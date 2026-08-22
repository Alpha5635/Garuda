from app.workers.celery_app import celery_app
from app.workers.tasks import process_inspection_image_task

__all__ = ["celery_app", "process_inspection_image_task"]
