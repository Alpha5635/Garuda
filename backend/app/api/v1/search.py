from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.search import SearchQuery, SearchResultResponse
from app.schemas.inspection import InspectionResponse
from app.services.search_service import search_service

router = APIRouter(tags=["Search"])


@router.get("/search", response_model=SearchResultResponse)
async def search_inspections(
    q: str | None = Query(None, description="General search query"),
    product_name: str | None = Query(None),
    district: str | None = Query(None),
    status: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    query_obj = SearchQuery(
        query=q,
        product_name=product_name,
        district=district,
        status=status,
        skip=skip,
        limit=limit
    )

    results = await search_service.search_inspections(session, current_user, query_obj)
    resp_list = [InspectionResponse.model_validate(i) for i in results]

    return SearchResultResponse(
        total_results=len(resp_list),
        results=resp_list
    )
