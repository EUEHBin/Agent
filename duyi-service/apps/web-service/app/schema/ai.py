from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AiMessageItem(BaseModel):
    role: str
    content: str


class AiSendMessageRequest(BaseModel):
    product_id: int = Field(description="产品ID")
    content: str = Field(description="用户发送的消息内容")


class AiConversationResponse(BaseModel):
    user_id: int
    product_id: int
    messages: list[AiMessageItem] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
