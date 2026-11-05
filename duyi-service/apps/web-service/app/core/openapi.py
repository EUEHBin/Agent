from fastapi import FastAPI


def _build_envelope_properties(data_schema: dict) -> dict:
    return {
        "code": {
            "type": "string",
            "description": "状态码，0 表示成功",
            "example": "0",
        },
        "data": data_schema,
        "message": {
            "type": "string",
            "description": "提示信息",
            "example": "success",
        },
    }


def _make_envelope(data_schema: dict) -> dict:
    return {
        "type": "object",
        "properties": _build_envelope_properties(data_schema),
        "required": ["code", "data", "message"],
    }


def _wrap_ref_schema(openapi_schema: dict, schema: dict) -> dict:
    ref_path: str = schema["$ref"]
    ref_name = ref_path.split("/")[-1]

    title = ref_name.replace("_", " ")
    wrapper_name = f"ApiResponse_{ref_name}"

    schemas = openapi_schema.setdefault("components", {}).setdefault("schemas", {})
    if wrapper_name not in schemas:
        schemas[wrapper_name] = {
            "title": f"ApiResponse[{title}]",
            "type": "object",
            "properties": _build_envelope_properties(schema),
            "required": ["code", "data", "message"],
        }

    return {"$ref": f"#/components/schemas/{wrapper_name}"}


def _wrap_array_schema(openapi_schema: dict, schema: dict) -> dict:
    items = schema.get("items")
    if isinstance(items, dict) and "$ref" in items:
        item_name = items["$ref"].split("/")[-1]
        title = f"List[{item_name.replace('_', ' ')}]"
        wrapper_name = f"ApiResponse_List_{item_name}"

        schemas = openapi_schema.setdefault("components", {}).setdefault("schemas", {})
        if wrapper_name not in schemas:
            schemas[wrapper_name] = {
                "title": f"ApiResponse[{title}]",
                "type": "object",
                "properties": _build_envelope_properties(schema),
                "required": ["code", "data", "message"],
            }

        return {"$ref": f"#/components/schemas/{wrapper_name}"}

    return _make_envelope(schema)


def setup_openapi(app: FastAPI) -> None:
    _original = app.openapi

    def _custom():
        if app.openapi_schema:
            return app.openapi_schema

        schema = _original()

        for path, path_item in schema.get("paths", {}).items():
            if not path.startswith("/api/"):
                continue

            for method in ("get", "post", "put", "delete", "patch"):
                operation = path_item.get(method)
                if operation is None:
                    continue

                responses = operation.get("responses", {})
                for status_code_str, response in list(responses.items()):
                    status_code = int(status_code_str)
                    if status_code not in (200, 201):
                        del responses[status_code_str]
                        continue

                    content = response.get("content", {})
                    json_content = content.get("application/json")
                    if json_content is None:
                        continue

                    original_schema = json_content.get("schema")
                    if original_schema is None:
                        continue

                    if "$ref" in original_schema:
                        wrapped = _wrap_ref_schema(schema, original_schema)
                    elif original_schema.get("type") == "array":
                        wrapped = _wrap_array_schema(schema, original_schema)
                    else:
                        wrapped = _make_envelope(original_schema)

                    json_content["schema"] = wrapped

        app.openapi_schema = schema
        return schema

    app.openapi = _custom  # type: ignore[method-assign]
