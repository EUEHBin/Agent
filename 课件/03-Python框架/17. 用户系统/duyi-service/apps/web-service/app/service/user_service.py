from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.config import web_settings
from app.exception.auth import AuthException
from app.exception.database import DatabaseException
from app.model.setting import Setting
from app.model.user import User
from app.schema.user import UserLogin, UserRegister, TokenResponse, UserResponse
from app.service.base import BaseService
from duyi_utils.auth.jwt_util import create_token
from duyi_utils.auth.password import hash_password, verify_password


class UserService(BaseService):
    async def register(self, data: UserRegister) -> UserResponse:
        existing = await self.db.scalar(
            select(User).where(User.username == data.username)
        )
        if existing is not None:
            raise DatabaseException(message="注册失败：用户名已存在")

        user = User(
            username=data.username,
            password_hash=hash_password(data.password),
        )
        try:
            self.db.add(user)
            await self.db.flush()
        except IntegrityError as e:
            raise DatabaseException(
                message="注册失败：用户名已存在",
                detail=str(e),
                original_exception=e,
            ) from e

        return UserResponse(id=user.id, username=user.username)

    async def login(self, data: UserLogin) -> TokenResponse:
        user = await self.db.scalar(select(User).where(User.username == data.username))
        if user is None or not verify_password(data.password, user.password_hash):
            raise AuthException(message="登录失败：用户名或密码错误")

        expire_setting = await self.db.scalar(
            select(Setting.value).where(Setting.key == "jwt_expire_minutes")
        )
        expire_minutes = int(expire_setting) if expire_setting else 120

        token = create_token(
            {"sub": user.id},
            web_settings.jwt_secret_key,
            expires_delta=timedelta(minutes=expire_minutes),
        )
        return TokenResponse(access_token=token)

    async def profile(self, user: User) -> UserResponse:
        return UserResponse(id=user.id, username=user.username)

    async def change_password(
        self, user: User, old_password: str, new_password: str
    ) -> None:
        if not verify_password(old_password, user.password_hash):
            raise AuthException(message="修改密码失败：原密码错误")

        user.password_hash = hash_password(new_password)
        await self.db.flush()
