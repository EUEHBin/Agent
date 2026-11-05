from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.model.user import User
from app.schema.ai import AiMessageItem
from app.service.ai_service import AiService

router = APIRouter(prefix="/api/ai", tags=["AI"])


@router.get("/conversation/{product_id}", response_model=list[AiMessageItem])
async def get_conversation_history(
    product_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await AiService(db).get_history(current_user.id, product_id)


@router.delete("/conversation/{product_id}", status_code=204)
async def delete_conversation(
    product_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await AiService(db).delete_conversation(current_user.id, product_id)
