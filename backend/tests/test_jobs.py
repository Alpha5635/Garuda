import uuid
import pytest
from httpx import AsyncClient
from app.workers.tasks import process_inspection_image_task


@pytest.mark.asyncio
async def test_job_status_endpoint_not_found(async_client: AsyncClient, auth_headers: dict):
    random_job_id = uuid.uuid4()
    resp = await async_client.get(f"/api/v1/jobs/{random_job_id}", headers=auth_headers)
    assert resp.status_code == 404


def test_process_inspection_image_task_missing_job():
    fake_job_id = str(uuid.uuid4())
    res = process_inspection_image_task(fake_job_id)
    assert res["status"] == "failed"
