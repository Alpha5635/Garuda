from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.dependencies import get_db, get_current_user
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse, RefreshTokenRequest
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    session: AsyncSession = Depends(get_db)
):
    user_repo = UserRepository(session)
    user = await user_repo.get_by_email(credentials.email)

    if not user or not AuthService.verify_password(user.password_hash, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = AuthService.create_access_token(
        data={"sub": str(user.id), "role": user.role, "email": user.email}
    )
    refresh_token = AuthService.create_refresh_token(
        data={"sub": str(user.id)}
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    session: AsyncSession = Depends(get_db)
):
    payload = AuthService.decode_token(request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id_str = payload.get("sub")
    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(user_id_str)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    access_token = AuthService.create_access_token(
        data={"sub": str(user.id), "role": user.role, "email": user.email}
    )
    new_refresh_token = AuthService.create_refresh_token(
        data={"sub": str(user.id)}
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    session: AsyncSession = Depends(get_db)
):
    user_repo = UserRepository(session)
    existing = await user_repo.get_by_email(user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    hashed_pw = AuthService.hash_password(user_in.password)
    user = User(
        email=user_in.email.lower().strip(),
        password_hash=hashed_pw,
        name=user_in.name,
        role=user_in.role.value if isinstance(user_in.role, UserRole) else str(user_in.role),
        organisation_id=user_in.organisation_id
    )
    return await user_repo.create(user)
