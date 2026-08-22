import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.rule_pack import RulePackVersion
from app.repositories.rule_pack_repository import RulePackRepository
from app.schemas.rule_pack import RulePackVersionRequest


class RuleAdminService:
    async def create_staged_rule_pack(
        self,
        session: AsyncSession,
        data: RulePackVersionRequest
    ) -> RulePackVersion:
        repo = RulePackRepository(session)
        version_pack = RulePackVersion(
            version=data.version,
            name=data.name,
            status="staged",
            rules_json=data.rules_json,
            is_active=False
        )
        return await repo.create(version_pack)

    async def approve_rule_pack(
        self,
        session: AsyncSession,
        version_id: uuid.UUID
    ) -> RulePackVersion:
        repo = RulePackRepository(session)
        pack = await repo.get_by_id(version_id)
        if pack:
            pack.status = "active"
            pack.is_active = True
            await repo.update(pack)
        return pack


rule_admin_service = RuleAdminService()
