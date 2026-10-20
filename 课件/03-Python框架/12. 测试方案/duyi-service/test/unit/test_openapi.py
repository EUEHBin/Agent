import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel

from app.core.openapi import (
    _build_envelope_properties,
    _make_envelope,
    _wrap_array_schema,
    _wrap_ref_schema,
    setup_openapi,
)


class TestBuildEnvelopeProperties:
    def test_builds_envelope_with_data_schema(self):
        data_schema = {"type": "string"}
        result = _build_envelope_properties(data_schema)
        assert result["code"] == {
            "type": "string",
            "description": "状态码，0 表示成功",
            "example": "0",
        }
        assert result["data"] is data_schema
        assert result["message"]["type"] == "string"


class TestMakeEnvelope:
    def test_creates_envelope_schema(self):
        data_schema = {"type": "string"}
        result = _make_envelope(data_schema)
        assert result["type"] == "object"
        assert "code" in result["properties"]
        assert "data" in result["properties"]
        assert "message" in result["properties"]
        assert set(result["required"]) == {"code", "data", "message"}


class TestWrapRefSchema:
    def test_wraps_ref_into_api_response(self):
        openapi_schema = {}
        schema = {"$ref": "#/components/schemas/ProductResponse"}
        result = _wrap_ref_schema(openapi_schema, schema)
        assert result == {"$ref": "#/components/schemas/ApiResponse_ProductResponse"}
        assert "ApiResponse_ProductResponse" in openapi_schema["components"]["schemas"]

    def test_reuses_existing_wrapper(self):
        openapi_schema = {
            "components": {
                "schemas": {
                    "ApiResponse_TestModel": {"type": "object"}
                }
            }
        }
        schema = {"$ref": "#/components/schemas/TestModel"}
        result = _wrap_ref_schema(openapi_schema, schema)
        assert result == {"$ref": "#/components/schemas/ApiResponse_TestModel"}


class TestWrapArraySchema:
    def test_wraps_array_with_ref_items(self):
        openapi_schema = {}
        schema = {
            "type": "array",
            "items": {"$ref": "#/components/schemas/ProductResponse"},
        }
        result = _wrap_array_schema(openapi_schema, schema)
        assert result == {"$ref": "#/components/schemas/ApiResponse_List_ProductResponse"}
        assert "ApiResponse_List_ProductResponse" in openapi_schema["components"]["schemas"]

    def test_wraps_array_without_ref_items(self):
        openapi_schema = {}
        schema = {"type": "array", "items": {"type": "string"}}
        result = _wrap_array_schema(openapi_schema, schema)
        assert result["type"] == "object"
        assert "code" in result["properties"]


class TestSetupOpenapi:
    async def test_wraps_api_response_schemas(self):
        class ItemOut(BaseModel):
            id: int
            name: str

            model_config = {"from_attributes": True}

        app = FastAPI()

        @app.get("/api/items/{item_id}", response_model=ItemOut)
        def get_item(item_id: int):
            return {"id": item_id, "name": "test"}

        @app.get("/api/items", response_model=list[ItemOut])
        def list_items():
            return []

        @app.get("/health")
        def health():
            return {"status": "ok"}

        setup_openapi(app)

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/openapi.json")
            assert resp.status_code == 200
            schema = resp.json()

            paths = schema["paths"]
            get_item_resp = paths["/api/items/{item_id}"]["get"]["responses"]["200"]
            item_schema = get_item_resp["content"]["application/json"]["schema"]
            assert "$ref" in item_schema
            assert "ApiResponse" in item_schema["$ref"]

            list_resp = paths["/api/items"]["get"]["responses"]["200"]
            list_schema = list_resp["content"]["application/json"]["schema"]
            assert "$ref" in list_schema
            assert "ApiResponse_List" in list_schema["$ref"]

            health_paths = [p for p in paths.keys() if "health" in p]
            assert len(health_paths) > 0

    async def test_does_not_wrap_non_api_paths(self):
        app = FastAPI()

        @app.get("/other")
        def other():
            return {"ok": True}

        setup_openapi(app)

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/openapi.json")
            assert resp.status_code == 200
            schema = resp.json()
            other_resp = schema["paths"]["/other"]["get"]["responses"]["200"]
            assert other_resp["content"]["application/json"]["schema"] != {
                "$ref": "#/components/schemas/ApiResponse_..."
            }

    async def test_returns_cached_schema(self):
        app = FastAPI()

        @app.get("/api/test")
        def test():
            return {"ok": True}

        setup_openapi(app)

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp1 = await client.get("/openapi.json")
            resp2 = await client.get("/openapi.json")
            assert resp1.content == resp2.content
