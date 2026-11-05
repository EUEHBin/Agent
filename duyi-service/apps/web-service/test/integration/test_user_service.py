import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exception.auth import AuthException
from app.exception.database import DatabaseException
from app.model.user import User
from app.schema.user import ChangePassword, UserLogin, UserRegister
from app.service.user_service import UserService


async def _get_user(db_session: AsyncSession, user_id: int) -> User:
    result = await db_session.execute(select(User).where(User.id == user_id))
    return result.scalar_one()


class TestRegister:
    @pytest.mark.smoke
    async def test_register_success(self, db_session: AsyncSession):
        svc = UserService(db_session)
        result = await svc.register(UserRegister(username="newuser", password="test123456"))
        assert result.id is not None
        assert result.username == "newuser"

    async def test_register_duplicate_username(self, db_session: AsyncSession):
        svc = UserService(db_session)
        await svc.register(UserRegister(username="dupuser", password="test123456"))
        with pytest.raises(DatabaseException) as exc:
            await svc.register(UserRegister(username="dupuser", password="test123456"))
        assert "用户名已存在" in str(exc.value.message)


class TestLogin:
    async def _register(self, db_session: AsyncSession) -> int:
        svc = UserService(db_session)
        result = await svc.register(UserRegister(username="loginuser", password="test123456"))
        return result.id

    @pytest.mark.smoke
    async def test_login_success(self, db_session: AsyncSession):
        await self._register(db_session)
        svc = UserService(db_session)
        result = await svc.login(UserLogin(username="loginuser", password="test123456"))
        assert result.access_token
        assert result.token_type == "bearer"

    async def test_login_wrong_password(self, db_session: AsyncSession):
        await self._register(db_session)
        svc = UserService(db_session)
        with pytest.raises(AuthException) as exc:
            await svc.login(UserLogin(username="loginuser", password="wrongpassword"))
        assert "用户名或密码错误" in str(exc.value.message)

    async def test_login_nonexistent_user(self, db_session: AsyncSession):
        svc = UserService(db_session)
        with pytest.raises(AuthException) as exc:
            await svc.login(UserLogin(username="nouser", password="test123456"))
        assert "用户名或密码错误" in str(exc.value.message)


class TestProfile:
    async def _register(self, db_session: AsyncSession) -> int:
        svc = UserService(db_session)
        result = await svc.register(UserRegister(username="profileuser", password="test123456"))
        return result.id

    @pytest.mark.smoke
    async def test_profile_success(self, db_session: AsyncSession):
        user_id = await self._register(db_session)
        user = await _get_user(db_session, user_id)
        svc = UserService(db_session)
        result = await svc.profile(user)
        assert result.id == user.id
        assert result.username == "profileuser"


class TestChangePassword:
    async def _register(self, db_session: AsyncSession) -> int:
        svc = UserService(db_session)
        result = await svc.register(UserRegister(username="pwuser", password="old123456"))
        return result.id

    @pytest.mark.smoke
    async def test_change_password_success(self, db_session: AsyncSession):
        user_id = await self._register(db_session)
        user = await _get_user(db_session, user_id)
        svc = UserService(db_session)
        await svc.change_password(
            user, old_password="old123456", new_password="new123456"
        )

        result = await svc.login(UserLogin(username="pwuser", password="new123456"))
        assert result.access_token

    async def test_change_password_wrong_old(self, db_session: AsyncSession):
        user_id = await self._register(db_session)
        user = await _get_user(db_session, user_id)
        svc = UserService(db_session)
        with pytest.raises(AuthException) as exc:
            await svc.change_password(
                user, old_password="wrongold", new_password="new123456"
            )
        assert "原密码错误" in str(exc.value.message)
