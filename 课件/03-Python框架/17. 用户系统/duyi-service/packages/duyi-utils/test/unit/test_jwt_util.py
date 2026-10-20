from datetime import datetime, timedelta, timezone

import jwt
import pytest

from duyi_utils.auth.jwt_util import create_token, decode_token


SECRET = "a-32-byte-long-secret-key-for-testing-hs256"


class TestCreateToken:
    def test_returns_string(self):
        token = create_token({"sub": "user1"}, SECRET)
        assert isinstance(token, str)

    def test_token_can_be_decoded(self):
        token = create_token({"sub": "user1"}, SECRET)
        decoded = decode_token(token, SECRET)
        assert decoded["sub"] == "user1"

    def test_contains_custom_data(self):
        token = create_token({"sub": "user1", "role": "admin"}, SECRET)
        decoded = decode_token(token, SECRET)
        assert decoded["sub"] == "user1"
        assert decoded["role"] == "admin"

    def test_contains_jti(self):
        token = create_token({"sub": "user1"}, SECRET)
        decoded = decode_token(token, SECRET)
        assert "jti" in decoded
        assert isinstance(decoded["jti"], str)

    def test_contains_iat(self):
        token = create_token({"sub": "user1"}, SECRET)
        decoded = decode_token(token, SECRET)
        assert "iat" in decoded

    def test_contains_exp(self):
        token = create_token({"sub": "user1"}, SECRET)
        decoded = decode_token(token, SECRET)
        assert "exp" in decoded

    def test_default_expires_in_2_hours(self):
        token = create_token({"sub": "user1"}, SECRET)
        decoded = decode_token(token, SECRET)
        iat = decoded["iat"]
        exp = decoded["exp"]
        assert exp - iat == 7200

    def test_custom_expires_delta(self):
        token = create_token({"sub": "user1"}, SECRET, expires_delta=timedelta(minutes=30))
        decoded = decode_token(token, SECRET)
        iat = decoded["iat"]
        exp = decoded["exp"]
        assert exp - iat == 1800

    def test_input_data_is_not_mutated(self):
        data = {"sub": "user1"}
        create_token(data, SECRET)
        assert data == {"sub": "user1"}

    def test_different_tokens_for_same_data(self):
        token1 = create_token({"sub": "user1"}, SECRET)
        token2 = create_token({"sub": "user1"}, SECRET)
        assert token1 != token2


class TestDecodeToken:
    def test_decodes_valid_token(self):
        token = create_token({"sub": "user1"}, SECRET)
        decoded = decode_token(token, SECRET)
        assert decoded["sub"] == "user1"

    def test_wrong_secret_key_raises_error(self):
        token = create_token({"sub": "user1"}, SECRET)
        with pytest.raises(jwt.InvalidSignatureError):
            decode_token(token, "a-wrong-secret-key-that-does-not-match")

    def test_expired_token_raises_error(self):
        token = create_token(
            {"sub": "user1"}, SECRET, expires_delta=timedelta(seconds=-1)
        )
        with pytest.raises(jwt.ExpiredSignatureError):
            decode_token(token, SECRET)
