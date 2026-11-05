import json

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.auth import get_user_from_token
from app.core.database import get_session_factory
from app.exception.ai import AiException
from app.exception.auth import AuthException
from app.service.ai_service import AiService

router = APIRouter()


@router.websocket("/{product_id}")
async def ai_websocket(
    websocket: WebSocket,
    product_id: int,
    token: str = Query(...),
):
    await websocket.accept()  # 协议升级
    db = get_session_factory()()
    try:
        user = await get_user_from_token(token, db)
    except AuthException:
        await db.close()
        await websocket.close(code=1008, reason="认证失败")
        return
    await db.close()
    user_id = user.id

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json(
                    {"type": "error", "message": "无效的JSON格式"}
                )
                continue

            action = data.get("action")

            if action == "initialize":
                db = get_session_factory()()
                try:
                    svc = AiService(db)
                    async for chunk in svc.initialize(user_id, product_id):
                        await websocket.send_json({"type": "chunk", "content": chunk})
                    await websocket.send_json({"type": "done"})
                    await db.commit()
                except AiException as e:
                    await websocket.send_json(
                        {"type": "error", "message": e.message, "detail": e.detail}
                    )
                finally:
                    await db.close()

            elif action == "send_message":
                content = data.get("content", "").strip()
                if not content:
                    await websocket.send_json(
                        {"type": "error", "message": "消息内容不能为空"}
                    )
                    continue

                db = get_session_factory()()
                try:
                    svc = AiService(db)
                    async for chunk in svc.send_message_stream(
                        user_id, product_id, content
                    ):
                        await websocket.send_json({"type": "chunk", "content": chunk})
                    await websocket.send_json({"type": "done"})
                    await db.commit()
                except AiException as e:
                    await websocket.send_json(
                        {"type": "error", "message": e.message, "detail": e.detail}
                    )
                finally:
                    await db.close()

            else:
                await websocket.send_json(
                    {"type": "error", "message": f"未知操作: {action}"}
                )

    except WebSocketDisconnect:
        print("断开")
        pass
