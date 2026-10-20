from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AiMessageItem(BaseModel):
    role: str
    content: str


class AiConversationResponse(BaseModel):
    user_id: int
    product_id: int
    messages: list[AiMessageItem] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
