import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1 import auth, inspections, images, jobs, calibration, rules, violations, reviews, reports, ecommerce, audit, search, dashboard, rule_admin, inspection_sessions

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    description="LabelSetu Backend - Legal Metrology Compliance Inspection Platform (SIH 2026 PS 26034)"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API V1 Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(inspections.router, prefix=settings.API_V1_STR)
app.include_router(inspection_sessions.router, prefix=settings.API_V1_STR)
app.include_router(images.router, prefix=settings.API_V1_STR)
app.include_router(jobs.router, prefix=settings.API_V1_STR)
app.include_router(calibration.router, prefix=settings.API_V1_STR)
app.include_router(rules.router, prefix=settings.API_V1_STR)
app.include_router(violations.router, prefix=settings.API_V1_STR)
app.include_router(reviews.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)
app.include_router(ecommerce.router, prefix=settings.API_V1_STR)
app.include_router(audit.router, prefix=settings.API_V1_STR)
app.include_router(search.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)
app.include_router(rule_admin.router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def on_startup():
    try:
        from app.models.base import Base
        from app.dependencies import async_engine, AsyncSessionLocal
        from app.models.user import User, UserRole
        from app.repositories.user_repository import UserRepository
        from app.services.auth_service import AuthService

        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with AsyncSessionLocal() as session:
            user_repo = UserRepository(session)
            demo_accounts = [
                ("officer@lm.gov.in", "Inspector Mumbai", UserRole.OFFICER),
                ("officer@labelsetu.gov.in", "Inspector Central", UserRole.OFFICER),
                ("admin@doca.gov.in", "Admin DoCA", UserRole.SUPER_ADMIN),
            ]
            for email, name, role in demo_accounts:
                existing = await user_repo.get_by_email(email)
                if not existing:
                    user = User(
                        email=email,
                        password_hash=AuthService.hash_password("Demo@2026"),
                        name=name,
                        role=role.value if isinstance(role, UserRole) else str(role)
                    )
                    await user_repo.create(user)
            await session.commit()
    except Exception as e:
        print(f"[Startup] Note on database table init/seed: {e}")


@app.get("/", tags=["Health"])
async def root():
    return {
        "app": settings.PROJECT_NAME,
        "status": "online",
        "version": "1.0.0-stage1",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
