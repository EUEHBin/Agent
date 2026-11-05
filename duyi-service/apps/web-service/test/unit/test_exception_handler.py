from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from app.exception.base import BusinessException
from app.exception.database import DatabaseException
from app.exception.handler.errors import ERROR_MAP, PROTOCOL_ERROR_MAP
from app.exception.handler.handlers import (
    _format_validation_error,
    _lookup,
    exception_handler,
)
from app.exception.not_found import NotFoundException


class TestLookup:
    def test_returns_mapped_entry_for_known_exception(self):
        code, http_status, msg = _lookup(NotFoundException("test"))
        assert code == "404001"
        assert http_status == 404
        assert msg == "资源不存在"

    def test_returns_mapped_entry_via_mro(self):
        code, http_status, msg = _lookup(DatabaseException("test"))
        assert code == "422002"
        assert http_status == 422

    def test_falls_back_to_exception_handler(self):
        code, http_status, msg = _lookup(ValueError("unknown"))
        assert code == "500001"
        assert http_status == 500
        assert msg == "服务器内部错误"


class TestFormatValidationError:
    def test_formats_simple_error(self):
        err = {"loc": ["body", "name"], "msg": "field required"}
        result = _format_validation_error(err)
        assert result == "body.name: field required"

    def test_formats_with_multiple_loc_parts(self):
        err = {"loc": ["body", "items", 0, "price"], "msg": "invalid"}
        result = _format_validation_error(err)
        assert result == "body.items.0.price: invalid"


@pytest.fixture
def mock_request():
    req = MagicMock(spec=Request)
    return req


class TestExceptionHandler:
    async def test_handles_http_exception_with_known_status(self, mock_request):
        exc = HTTPException(status_code=404, detail="Not Found")
        response = await exception_handler(mock_request, exc)
        assert response.status_code == 404
        body = response.body  # type: ignore[attr-defined]
        import json
        content = json.loads(body)
        assert content["code"] == "404"
        assert content["message"] == "路径不存在"

    async def test_handles_http_exception_with_unknown_status(self, mock_request):
        exc = HTTPException(status_code=418, detail="I'm a teapot")
        response = await exception_handler(mock_request, exc)
        assert response.status_code == 418
        import json
        content = json.loads(response.body)  # type: ignore[attr-defined]
        assert content["message"] == "I'm a teapot"

    async def test_handles_request_validation_error(self, mock_request):
        from pydantic import ValidationError as PydanticValidationError
        try:
            from pydantic import BaseModel, Field
            class TestModel(BaseModel):
                name: str = Field(min_length=1)
            TestModel(name="")
        except PydanticValidationError as e:
            exc = RequestValidationError(errors=e.errors())
        else:
            pytest.fail("Expected ValidationError")

        response = await exception_handler(mock_request, exc)
        assert response.status_code == 422
        import json
        content = json.loads(response.body)  # type: ignore[attr-defined]
        assert content["code"] == "422001"
        assert "name" in content["message"]

    @pytest.mark.smoke
    async def test_handles_business_exception(self, mock_request):
        exc = NotFoundException(message="资源未找到")
        response = await exception_handler(mock_request, exc)
        assert response.status_code == 404
        import json
        content = json.loads(response.body)  # type: ignore[attr-defined]
        assert content["code"] == "404001"
        assert content["message"] == "资源未找到"

    async def test_handles_generic_exception(self, mock_request):
        exc = RuntimeError("unexpected error")
        response = await exception_handler(mock_request, exc)
        assert response.status_code == 500
        import json
        content = json.loads(response.body)  # type: ignore[attr-defined]
        assert content["code"] == "500001"
        assert content["message"] == "服务器内部错误"
