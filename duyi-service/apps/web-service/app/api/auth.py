from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.model.user import User
from app.schema.user import ChangePassword, UserLogin, UserRegister, TokenResponse, UserResponse
from app.service.user_service import UserService

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    data: UserRegister,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await UserService(db).register(data)


@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserLogin,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await UserService(db).login(data)


@router.get("/me", response_model=UserResponse)
async def profile(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await UserService(db).profile(current_user)


@router.put("/password", status_code=204)
async def change_password(
    data: ChangePassword,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await UserService(db).change_password(
        current_user, data.old_password, data.new_password
    )
