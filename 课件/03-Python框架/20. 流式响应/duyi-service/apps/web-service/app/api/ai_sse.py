from typing import Annotated
from app.exception.base import BusinessException
from sqlalchemy.ext.asyncio import AsyncSession
from app.model.user import User
from fastapi import APIRouter, Depends, Request
from starlette.responses import StreamingResponse

from app.core.auth import get_current_user, security_scheme
from app.core.database import get_db, get_session_factory
from app.schema.ai import AiSendMessageRequest
from app.service.ai_service import AiService

router = APIRouter(prefix="/api/ai/sse", tags=["AI SSE"])


@router.get("/initialize/{product_id}")
async def initialize_conversation(
    request: Request,
    product_id: int,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    request.state.is_stream = True
    svc = AiService(db)

    async def event_stream():
        try:
            async for chunk in svc.initialize(user.id, product_id):
                yield f"data: {chunk}\n\n"
        except BusinessException as e:
            yield f"event: error\ndata: {e.message}\n\n"
        except Exception as e:
            yield f"event: error\ndata: 未知异常\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/message")
async def send_message(
    request: Request,
    data: AiSendMessageRequest,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    request.state.is_stream = True
    svc = AiService(db)

    async def event_stream():
        try:
            async for chunk in svc.send_message_stream(
                user.id, data.product_id, data.content
            ):
                yield f"data: {chunk}\n\n"
        except BusinessException as e:
            yield f"event: error\ndata: {e.message}\n\n"
        except Exception as e:
            yield f"event: error\ndata: 未知异常\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
