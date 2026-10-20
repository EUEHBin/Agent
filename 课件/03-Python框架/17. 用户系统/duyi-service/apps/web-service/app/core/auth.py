from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import web_settings
from app.core.database import get_db
from app.exception.auth import AuthException
from app.model.user import User
from duyi_utils.auth.jwt_util import decode_token

security_scheme = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    try:
        payload = decode_token(
            credentials.credentials,
            web_settings.jwt_secret_key,
        )
    except jwt.InvalidTokenError as e:
        raise AuthException(message="token 无效：token无效或已过期") from e

    sub: str | None = payload.get("sub")
    if sub is None:
        raise AuthException(message="token 无效：token无效或已过期")
    user_id = int(sub)

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise AuthException(message="token 无效：token无效或已过期")

    return user
