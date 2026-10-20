from duyi_utils.auth.password import hash_password, verify_password


class TestHashPassword:
    def test_returns_string(self):
        result = hash_password("my_password")
        assert isinstance(result, str)

    def test_returns_different_from_input(self):
        result = hash_password("my_password")
        assert result != "my_password"

    def test_different_passwords_produce_different_hashes(self):
        hash1 = hash_password("password_a")
        hash2 = hash_password("password_b")
        assert hash1 != hash2

    def test_same_password_produces_different_hash_each_time(self):
        hash1 = hash_password("same_password")
        hash2 = hash_password("same_password")
        assert hash1 != hash2


class TestVerifyPassword:
    def test_correct_password_returns_true(self):
        plain = "secret123"
        hashed = hash_password(plain)
        assert verify_password(plain, hashed) is True

    def test_wrong_password_returns_false(self):
        hashed = hash_password("secret123")
        assert verify_password("wrong_password", hashed) is False

    def test_empty_password(self):
        hashed = hash_password("")
        assert verify_password("", hashed) is True
        assert verify_password("x", hashed) is False
