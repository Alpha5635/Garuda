# LabelSetu Backend (SIH 2026 Problem Statement 26034)

Legal Metrology compliance checking backend foundation (STAGE 1) for the Department of Consumer Affairs, Government of India.

---

## Technical Stack
- **Framework**: Python 3.12+ / FastAPI
- **Database & ORM**: PostgreSQL / SQLAlchemy 2.0 (Async) + Alembic
- **Queue & Cache**: Celery 5.x + Redis
- **Storage**: MinIO / S3-compatible object storage
- **Computer Vision & OCR**: OpenCV (quality checks) & PaddleOCR (multi-lingual text extraction)
- **Security**: Argon2 password hashing (`argon2-cffi`) & PyJWT token authorization

---

## 1. Installation Commands

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment (Linux/macOS)
source venv/bin/activate

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt
```

---

## 2. Environment Setup

```bash
# Copy environment example
cp .env.example .env
```

Ensure environment variables in `.env` are set correctly according to your local services.

---

## 3. Docker Commands

```bash
# Start all services (PostgreSQL, Redis, MinIO, API, Worker)
docker-compose up -d

# Check status of containers
docker-compose ps

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

---

## 4. Database Migration Commands

```bash
# Run database migrations to current head
alembic upgrade head

# Create a new migration script
alembic revision --autogenerate -m "migration description"

# Seed default demo users and data
python -m scripts.init_db
```

---

## 5. Server Start Command

```bash
# Run FastAPI development server with auto-reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive OpenAPI documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 6. Worker Start Command

```bash
# Start Celery background task worker
celery -A app.workers.celery_app.celery_app worker --loglevel=info -c 2
```

---

## 7. Test Command

```bash
# Run pytest test suite
pytest -v
```

---

## API Pipeline Flow (STAGE 1 Goal)

```
Login (POST /api/v1/auth/login)
  ↓
Create Inspection (POST /api/v1/inspections)
  ↓
Upload Image (POST /api/v1/inspections/{id}/images/upload-url)
  ↓
Celery Job Enqueued (Job State: queued → processing)
  ↓
Quality Check (OpenCV: blur, glare, low-res, orientation check)
  ↓
PaddleOCR Parsing (Multi-lingual: English & Devanagari)
  ↓
Candidate Field Extraction (Manufacturer, Address, Net Qty, MRP, Mfg Date, etc.)
  ↓
Query Inspection/Job Results (GET /api/v1/jobs/{id})
```

### Pre-seeded Demo Accounts
- **Officer**: `officer@lm.gov.in` / `Demo@2026`
- **Reviewer**: `reviewer@lm.gov.in` / `Demo@2026`
- **Manufacturer**: `manufacturer@glowsoft.example` / `Demo@2026`
- **Admin**: `admin@doca.gov.in` / `Demo@2026`
