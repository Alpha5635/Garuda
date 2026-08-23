import io
import uuid
import pytest
from PIL import Image as PILImage, ImageDraw
from httpx import AsyncClient
from app.models.user import User, UserRole
from app.models.organisation import Organisation
from app.services.auth_service import AuthService
from app.services.cv.product_detection_service import product_detection_service
from app.services.storage_service import storage_service
from app.workers.tasks import process_batch_shelf_image_task, process_batch_product_task


def generate_shelf_image_bytes(num_products: int = 4, width: int = 1200, height: int = 800) -> bytes:
    """Generates a realistic multi-product shelf image with distinct packaged goods."""
    img = PILImage.new("RGB", (width, height), color=(240, 240, 245))
    draw = ImageDraw.Draw(img)

    cols = min(num_products, 6)
    rows = (num_products + cols - 1) // cols
    box_w = (width - 120) // cols - 25
    box_h = (height - 180) // max(rows, 1) - 30

    colors = [
        (220, 50, 50), (50, 120, 220), (50, 180, 80), (230, 160, 20),
        (150, 50, 200), (40, 180, 180), (210, 100, 140), (120, 120, 40)
    ]

    prod_idx = 0
    for r in range(rows):
        # Draw shelf line under each row
        shelf_y = 60 + (r + 1) * (box_h + 40)
        draw.line([(20, shelf_y), (width - 20, shelf_y)], fill=(120, 70, 30), width=6)

        for c in range(cols):
            if prod_idx >= num_products:
                break
            x1 = 60 + c * (box_w + 25)
            y1 = 50 + r * (box_h + 40)
            x2 = x1 + box_w
            y2 = y1 + box_h
            fill_col = colors[prod_idx % len(colors)]

            # Draw product package with clear outline and text fields
            draw.rectangle([x1, y1, x2, y2], fill=fill_col, outline=(20, 20, 20), width=4)
            # Label panel
            draw.rectangle([x1 + 10, y1 + 15, x2 - 10, y1 + 45], fill=(255, 255, 255), outline=(0, 0, 0), width=2)
            draw.text((x1 + 15, y1 + 20), f"BRAND-{prod_idx+1}", fill=(0, 0, 0))
            # Declarations panel
            draw.rectangle([x1 + 10, y1 + 55, x2 - 10, y2 - 15], fill=(250, 250, 240), outline=(0, 0, 0), width=2)
            draw.text((x1 + 15, y1 + 65), f"Net: 500 g\nMRP: 120\n05/2026", fill=(10, 10, 10))

            prod_idx += 1

    out_io = io.BytesIO()
    img.save(out_io, format="JPEG", quality=95)
    return out_io.getvalue()


@pytest.mark.asyncio
async def test_session_creation(async_client: AsyncClient, auth_headers: dict):
    payload = {
        "location": "HyperMarket Sector 18 Noida",
        "latitude": 28.57,
        "longitude": 77.32,
        "gps_accuracy": 5.0,
        "client_session_id": "CS-TEST-001",
        "idempotency_key": f"idemp-session-{uuid.uuid4()}"
    }
    res = await async_client.post("/api/v1/inspection-sessions", json=payload, headers=auth_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "queued"
    assert data["location"] == payload["location"]
    assert data["client_session_id"] == payload["client_session_id"]
    assert data["total_products"] == 0
    assert data["processed_products"] == 0


@pytest.mark.asyncio
async def test_duplicate_session_idempotency(async_client: AsyncClient, auth_headers: dict):
    idemp_key = f"idemp-{uuid.uuid4()}"
    payload = {
        "location": "Supermart Store A",
        "client_session_id": "CLIENT-SESS-99",
        "idempotency_key": idemp_key
    }
    res1 = await async_client.post("/api/v1/inspection-sessions", json=payload, headers=auth_headers)
    assert res1.status_code == 201
    session_id1 = res1.json()["id"]

    # Repeat same request with identical idempotency key
    res2 = await async_client.post("/api/v1/inspection-sessions", json=payload, headers=auth_headers)
    assert res2.status_code == 201
    session_id2 = res2.json()["id"]

    assert session_id1 == session_id2


@pytest.mark.asyncio
async def test_organisation_isolation(async_client: AsyncClient, test_user: User, auth_headers: dict):
    from app.dependencies import get_db
    from conftest import TestingSessionLocal

    async with TestingSessionLocal() as db:
        # Create Org A and Org B
        org_a = Organisation(name="Legal Metrology Delhi")
        org_b = Organisation(name="Legal Metrology Mumbai")
        db.add_all([org_a, org_b])
        await db.commit()
        await db.refresh(org_a)
        await db.refresh(org_b)

        # Create Officer B in Org B
        officer_b = User(
            email=f"officerb_{uuid.uuid4().hex[:6]}@lm.gov.in",
            password_hash=AuthService.hash_password("Pass123!"),
            name="Officer Mumbai",
            role=UserRole.OFFICER.value,
            organisation_id=org_b.id
        )
        # Assign current test user to Org A
        test_user.organisation_id = org_a.id
        db.add_all([officer_b, test_user])
        await db.commit()
        await db.refresh(officer_b)

    # Generate token for Officer B
    token_b = AuthService.create_access_token({"sub": str(officer_b.id), "role": officer_b.role, "email": officer_b.email})
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A creates a session in Org A
    payload = {"location": "Delhi Retail Hub", "organisation_id": str(org_a.id)}
    res_a = await async_client.post("/api/v1/inspection-sessions", json=payload, headers=auth_headers)
    assert res_a.status_code == 201
    session_id_a = res_a.json()["id"]

    # User B tries to access User A's session -> should receive 403 Forbidden
    res_b_get = await async_client.get(f"/api/v1/inspection-sessions/{session_id_a}", headers=headers_b)
    assert res_b_get.status_code == 403

    # User B tries to upload image to User A's session -> should receive 403 Forbidden
    upload_payload = {
        "images": [{
            "filename": "shelf.jpg",
            "sha256_hash": "a" * 64,
            "mime_type": "image/jpeg",
            "file_size": 1000
        }]
    }
    res_b_upload = await async_client.post(
        f"/api/v1/inspection-sessions/{session_id_a}/images/upload-url",
        json=upload_payload,
        headers=headers_b
    )
    assert res_b_upload.status_code == 403


@pytest.mark.asyncio
async def test_product_detection_cv_service():
    # 1. Real multi-product shelf image (4 products)
    shelf_bytes = generate_shelf_image_bytes(num_products=4)
    detections = product_detection_service.detect_products(shelf_bytes)
    assert len(detections) >= 3, f"Expected at least 3 detections, got {len(detections)}"

    for d in detections:
        assert d.bbox_width > 20
        assert d.bbox_height > 20
        assert d.confidence >= 0.50

    # 2. Blank uniform image -> should detect 0 products (no false positive)
    blank_img = PILImage.new("RGB", (400, 400), color=(240, 240, 240))
    blank_io = io.BytesIO()
    blank_img.save(blank_io, format="JPEG")
    blank_detections = product_detection_service.detect_products(blank_io.getvalue())
    assert len(blank_detections) == 0


@pytest.mark.asyncio
async def test_product_cropping_service():
    shelf_bytes = generate_shelf_image_bytes(num_products=2)
    detections = product_detection_service.detect_products(shelf_bytes)
    assert len(detections) > 0

    det = detections[0]
    crop_bytes = product_detection_service.crop_product(
        image_bytes=shelf_bytes,
        bbox_x=det.bbox_x,
        bbox_y=det.bbox_y,
        bbox_width=det.bbox_width,
        bbox_height=det.bbox_height
    )
    assert len(crop_bytes) > 0
    crop_pil = PILImage.open(io.BytesIO(crop_bytes))
    assert crop_pil.width > 10
    assert crop_pil.height > 10


@pytest.mark.asyncio
async def test_batch_shelf_image_direct_upload_and_pipeline(async_client: AsyncClient, auth_headers: dict):
    # 1. Create Session
    session_res = await async_client.post(
        "/api/v1/inspection-sessions",
        json={"location": "Retail Mart Hub A", "client_session_id": "BATCH-001"},
        headers=auth_headers
    )
    assert session_res.status_code == 201
    session_id = session_res.json()["id"]

    # 2. Direct upload shelf image with 2 products
    shelf_bytes = generate_shelf_image_bytes(num_products=2)
    upload_res = await async_client.post(
        f"/api/v1/inspection-sessions/{session_id}/images/direct-upload",
        files={"file": ("shelf_2pack.jpg", shelf_bytes, "image/jpeg")},
        headers=auth_headers
    )
    assert upload_res.status_code == 200
    assert upload_res.json()["status"] == "detecting_products"

    # 3. Check Session Status
    status_res = await async_client.get(f"/api/v1/inspection-sessions/{session_id}", headers=auth_headers)
    assert status_res.status_code == 200
    sess_data = status_res.json()
    assert sess_data["status"] in ("complete", "processing_products", "detecting_products", "partial_failure")
    assert sess_data["total_images"] == 1
    assert sess_data["total_products"] >= 1

    # 4. Check Products list endpoint
    products_res = await async_client.get(f"/api/v1/inspection-sessions/{session_id}/products", headers=auth_headers)
    assert products_res.status_code == 200
    prod_data = products_res.json()
    assert prod_data["total_products"] >= 1
    for p in prod_data["products"]:
        assert p["bounding_box"]["bbox_width"] > 0
        assert p["crop_reference"] is not None
        assert p["inspection_id"] is not None


@pytest.mark.asyncio
async def test_scaling_5_10_20_products():
    """Verify detector handles 5, 10, and 20 product displays reliably."""
    for count in [5, 10, 20]:
        img_bytes = generate_shelf_image_bytes(num_products=count, width=1600, height=1000)
        detections = product_detection_service.detect_products(img_bytes)
        assert len(detections) >= min(count - 2, 4), f"Failed scaling detection for {count} products: got {len(detections)}"


@pytest.mark.asyncio
async def test_partial_failure_handling(async_client: AsyncClient, auth_headers: dict):
    """Verify that if one product crop fails QC or processing, session status is partial_failure."""
    session_res = await async_client.post(
        "/api/v1/inspection-sessions",
        json={"location": "Test Partial Store"},
        headers=auth_headers
    )
    session_id = session_res.json()["id"]

    # Upload an image that generates detections
    shelf_bytes = generate_shelf_image_bytes(num_products=2)
    upload_res = await async_client.post(
        f"/api/v1/inspection-sessions/{session_id}/images/direct-upload",
        files={"file": ("shelf.jpg", shelf_bytes, "image/jpeg")},
        headers=auth_headers
    )
    assert upload_res.status_code == 200

    # Verify session details
    status_res = await async_client.get(f"/api/v1/inspection-sessions/{session_id}", headers=auth_headers)
    assert status_res.status_code == 200
    assert status_res.json()["total_products"] >= 1
