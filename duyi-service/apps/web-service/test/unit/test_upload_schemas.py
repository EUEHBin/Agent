import pytest
from pydantic import ValidationError

from app.schema.upload import UploadSignRequest, UploadSignResponse


class TestUploadSignRequest:
    @pytest.mark.smoke
    def test_valid_request(self):
        req = UploadSignRequest(filename="photo.png", file_size=1024)
        assert req.filename == "photo.png"
        assert req.file_size == 1024

    def test_empty_filename_fails(self):
        with pytest.raises(ValidationError) as exc:
            UploadSignRequest(filename="", file_size=1024)
        assert "String should have at least 1 character" in str(exc.value)

    def test_missing_filename_fails(self):
        with pytest.raises(ValidationError):
            UploadSignRequest(file_size=1024)  # pyright: ignore[reportCallIssue]

    def test_missing_file_size_fails(self):
        with pytest.raises(ValidationError):
            UploadSignRequest(filename="photo.png")  # pyright: ignore[reportCallIssue]

    def test_zero_file_size_fails(self):
        with pytest.raises(ValidationError) as exc:
            UploadSignRequest(filename="photo.png", file_size=0)
        assert "Input should be greater than 0" in str(exc.value)

    def test_negative_file_size_fails(self):
        with pytest.raises(ValidationError) as exc:
            UploadSignRequest(filename="photo.png", file_size=-1)
        assert "Input should be greater than 0" in str(exc.value)


class TestUploadSignResponse:
    def test_all_fields_present(self):
        resp = UploadSignResponse(
            host="https://bucket.endpoint",
            access_id="test_id",
            policy="test_policy",
            signature="test_signature",
            key="uploads/test.png",
            content_type="image/png",
            bucket_domain="custom.domain.com",
        )
        assert resp.host == "https://bucket.endpoint"
        assert resp.access_id == "test_id"
        assert resp.policy == "test_policy"
        assert resp.signature == "test_signature"
        assert resp.key == "uploads/test.png"
        assert resp.content_type == "image/png"
        assert resp.bucket_domain == "custom.domain.com"

    def test_bucket_domain_empty_string(self):
        resp = UploadSignResponse(
            host="https://bucket.endpoint",
            access_id="test_id",
            policy="test_policy",
            signature="test_signature",
            key="uploads/test.png",
            content_type="image/png",
            bucket_domain="",
        )
        assert resp.bucket_domain == ""

    def test_missing_bucket_domain_fails(self):
        with pytest.raises(ValidationError):
            UploadSignResponse(
                host="https://bucket.endpoint",
                access_id="test_id",
                policy="test_policy",
                signature="test_signature",
                key="uploads/test.png",
                content_type="image/png",
            )  # pyright: ignore[reportCallIssue]
