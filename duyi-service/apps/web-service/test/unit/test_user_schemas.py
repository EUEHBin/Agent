import pytest
from pydantic import ValidationError

from app.schema.user import (
    ChangePassword,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)


class TestUserRegister:
    @pytest.mark.smoke
    def test_valid_register(self):
        u = UserRegister(username="testuser", password="test123456")
        assert u.username == "testuser"
        assert u.password == "test123456"

    def test_username_too_short_fails(self):
        with pytest.raises(ValidationError) as exc:
            UserRegister(username="", password="test123456")
        assert "String should have at least 1 character" in str(exc.value)

    def test_username_too_long_fails(self):
        with pytest.raises(ValidationError) as exc:
            UserRegister(username="x" * 101, password="test123456")
        assert "String should have at most 100 characters" in str(exc.value)

    def test_password_too_short_fails(self):
        with pytest.raises(ValidationError) as exc:
            UserRegister(username="testuser", password="12345")
        assert "String should have at least 6 characters" in str(exc.value)

    def test_password_too_long_fails(self):
        with pytest.raises(ValidationError) as exc:
            UserRegister(username="testuser", password="x" * 101)
        assert "String should have at most 100 characters" in str(exc.value)

    def test_missing_username_fails(self):
        with pytest.raises(ValidationError):
            UserRegister(password="test123456")  # type: ignore

    def test_missing_password_fails(self):
        with pytest.raises(ValidationError):
            UserRegister(username="testuser")  # type: ignore


class TestUserLogin:
    def test_valid_login(self):
        u = UserLogin(username="testuser", password="test123456")
        assert u.username == "testuser"
        assert u.password == "test123456"

    def test_missing_username_fails(self):
        with pytest.raises(ValidationError):
            UserLogin(password="test123456")  # type: ignore

    def test_missing_password_fails(self):
        with pytest.raises(ValidationError):
            UserLogin(username="testuser")  # type: ignore


class TestChangePassword:
    @pytest.mark.smoke
    def test_valid_change(self):
        c = ChangePassword(old_password="old123456", new_password="new123456")
        assert c.old_password == "old123456"
        assert c.new_password == "new123456"

    def test_new_password_too_short_fails(self):
        with pytest.raises(ValidationError) as exc:
            ChangePassword(old_password="old123456", new_password="12345")
        assert "String should have at least 6 characters" in str(exc.value)

    def test_new_password_too_long_fails(self):
        with pytest.raises(ValidationError) as exc:
            ChangePassword(old_password="old123456", new_password="x" * 101)
        assert "String should have at most 100 characters" in str(exc.value)

    def test_missing_old_password_fails(self):
        with pytest.raises(ValidationError):
            ChangePassword(new_password="new123456")  # type: ignore

    def test_missing_new_password_fails(self):
        with pytest.raises(ValidationError):
            ChangePassword(old_password="old123456")  # type: ignore


class TestUserResponse:
    def test_valid_response(self):
        r = UserResponse(id=1, username="testuser")
        assert r.id == 1
        assert r.username == "testuser"

    def test_missing_id_fails(self):
        with pytest.raises(ValidationError):
            UserResponse(username="testuser")  # type: ignore

    def test_missing_username_fails(self):
        with pytest.raises(ValidationError):
            UserResponse(id=1)  # type: ignore


class TestTokenResponse:
    def test_valid_response(self):
        t = TokenResponse(access_token="abc123", token_type="bearer")
        assert t.access_token == "abc123"
        assert t.token_type == "bearer"

    def test_default_token_type(self):
        t = TokenResponse(access_token="abc123")
        assert t.token_type == "bearer"

    def test_missing_access_token_fails(self):
        with pytest.raises(ValidationError):
            TokenResponse()  # type: ignore
