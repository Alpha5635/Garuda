import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings
from app.models.base import Base
from app.models.user import User, UserRole
from app.models.organisation import Organisation
from app.models.rule_pack import RulePackVersion
from app.models.inspection import Inspection, InspectionStatus
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.repositories.organisation_repository import OrganisationRepository
from app.repositories.rule_pack_repository import RulePackRepository
from app.dependencies import AsyncSessionLocal


async def init_db():
    print("[InitDB] Initializing database tables & Stage 3 demo dataset...")
    engine = create_async_engine(settings.get_database_url())
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        org_repo = OrganisationRepository(session)
        rule_pack_repo = RulePackRepository(session)

        # 1. Seed demo Organisation
        demo_org = await org_repo.get_all(limit=1)
        org_id = None
        if not demo_org:
            org = Organisation(
                name="GlowSoft Pvt Ltd",
                type="Manufacturer",
                brand="GlowSoft",
                address="101 Marine Drive, Mumbai, Maharashtra 400021"
            )
            org = await org_repo.create(org)
            org_id = org.id
            print(f"[InitDB] Created demo organisation: {org.name}")
        else:
            org_id = demo_org[0].id

        # 2. Seed Default Demo Users
        demo_users = [
            ("officer@lm.gov.in", "Inspector Mumbai", UserRole.OFFICER, None),
            ("reviewer@lm.gov.in", "Controller Maharashtra", UserRole.REVIEWER, None),
            ("manufacturer@glowsoft.example", "GlowSoft Manufacturer", UserRole.MANUFACTURER, org_id),
            ("admin@doca.gov.in", "Admin DoCA", UserRole.SUPER_ADMIN, None),
            ("ruleadmin@doca.gov.in", "Rule Administrator", UserRole.RULE_ADMIN, None),
        ]

        for email, name, role, o_id in demo_users:
            existing = await user_repo.get_by_email(email)
            if not existing:
                pw_hash = AuthService.hash_password("Demo@2026")
                user = User(
                    email=email,
                    password_hash=pw_hash,
                    name=name,
                    role=role.value if isinstance(role, UserRole) else str(role),
                    organisation_id=o_id
                )
                await user_repo.create(user)
                print(f"[InitDB] Created demo user: {email} ({role.value})")

        # 3. Seed Rule Pack Version
        active_pack = await rule_pack_repo.get_by_version("rp-2026.03")
        if not active_pack:
            rp = RulePackVersion(
                version="rp-2026.03",
                name="LMPC 2011 Rule Pack (SIH 2026)",
                status="active",
                rules_json={"rulepack_version": "rp-2026.03"},
                is_active=True
            )
            await rule_pack_repo.create(rp)
            print("[InitDB] Created active rule pack: rp-2026.03")

        await session.commit()
    print("[InitDB] Database initialization completed successfully.")

if __name__ == "__main__":
    asyncio.run(init_db())
