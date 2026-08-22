import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.ecommerce import EcommerceListing
from app.schemas.ecommerce import EcommerceListingRequest, EcommerceListingResponse
from app.schemas.rule_engine import RuleEvaluationResult
from app.services.ecommerce_service import ecommerce_service
from app.repositories.ecommerce_repository import EcommerceRepository

router = APIRouter(prefix="/ecommerce", tags=["E-Commerce Compliance"])


@router.post("/listings", response_model=EcommerceListingResponse, status_code=status.HTTP_201_CREATED)
async def process_ecommerce_listing(
    data: EcommerceListingRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    res_dict = ecommerce_service.process_listing(data)

    repo = EcommerceRepository(session)
    listing = EcommerceListing(
        platform=data.platform,
        listing_id=data.listing_id,
        url=data.url,
        seller_name=data.seller_name,
        content_hash=res_dict["content_hash"],
        declarations_json=data.declarations or {}
    )
    listing = await repo.create(listing)
    await session.commit()

    rule_evals = [RuleEvaluationResult(**r) for r in res_dict["rule_evaluations"]]

    return EcommerceListingResponse(
        id=listing.id,
        platform=listing.platform,
        listing_id=listing.listing_id,
        url=listing.url,
        seller_name=listing.seller_name,
        content_hash=listing.content_hash,
        rule_evaluations=rule_evals,
        created_at=listing.created_at
    )
