from typing import Never

from langgraph_sdk import Auth
from .mock_user import MOCK_USER

auth = Auth()


def _raise_invalid_token() -> Never:
    raise Auth.exceptions.HTTPException(status_code=401, detail="invalid token")


@auth.authenticate
async def authenticate(
    authorization: str | None,
) -> Auth.types.MinimalUserDict:
    """验证 Authorization: Bearer <token> 并返回当前用户。"""
    if not authorization:
        _raise_invalid_token()
    schema, sep, token = authorization.partition(" ")
    if not token:
        _raise_invalid_token()
    # 解析token，通常要访问后端web服务（用户中心）
    if token not in MOCK_USER:
        _raise_invalid_token()

    return MOCK_USER[token]


@auth.on.store
async def on_store(ctx: Auth.types.AuthContext, value: dict):
    permission = f"{ctx.resource}:{ctx.action}"
    if permission not in ctx.permissions:
        return False
    namespace = tuple(value["namespace"]) if value["namespace"] else ()
    if not namespace or namespace[0] != ctx.user.identity:
        return False
    return True


@auth.on.assistants
async def on_assistants(ctx: Auth.types.AuthContext, value: dict):
    permission = f"{ctx.resource}:{ctx.action}"
    if permission not in ctx.permissions:
        return False
    return True


@auth.on
async def authorization(ctx: Auth.types.AuthContext, value: dict):
    permission = f"{ctx.resource}:{ctx.action}"
    if permission not in ctx.permissions:
        return False
    metadata = value.setdefault("metadata", {})
    metadata["owner"] = ctx.user.identity

    return {"owner": ctx.user.identity}
