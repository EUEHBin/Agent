from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schema.ai import AiConversationResponse, AiMessageItem


class TestAiMessageItem:
    @pytest.mark.smoke
    def test_valid_item(self):
        item = AiMessageItem(role="user", content="你好")
        assert item.role == "user"
        assert item.content == "你好"

    def test_empty_role_allowed(self):
        item = AiMessageItem(role="", content="你好")
        assert item.role == ""

    def test_empty_content_allowed(self):
        item = AiMessageItem(role="user", content="")
        assert item.content == ""

    def test_missing_role_fails(self):
        with pytest.raises(ValidationError):
            AiMessageItem(content="你好")  # pyright: ignore[reportCallIssue]

    def test_missing_content_fails(self):
        with pytest.raises(ValidationError):
            AiMessageItem(role="user")  # pyright: ignore[reportCallIssue]


class TestAiConversationResponse:
    def test_from_attributes_config(self):
        assert AiConversationResponse.model_config.get("from_attributes") is True

    def test_full_fields(self):
        now = datetime.now()
        r = AiConversationResponse(
            user_id=1,
            product_id=2,
            messages=[
                AiMessageItem(role="user", content="hello"),
                AiMessageItem(role="assistant", content="hi"),
            ],
            created_at=now,
            updated_at=now,
        )
        assert r.user_id == 1
        assert r.product_id == 2
        assert len(r.messages) == 2
        assert r.messages[0].role == "user"
        assert r.messages[0].content == "hello"
        assert r.messages[1].role == "assistant"
        assert r.messages[1].content == "hi"
        assert r.created_at == now
        assert r.updated_at == now

    def test_default_messages_empty_list(self):
        now = datetime.now()
        r = AiConversationResponse(
            user_id=1,
            product_id=2,
            created_at=now,
            updated_at=now,
        )
        assert r.messages == []

    def test_missing_user_id_fails(self):
        with pytest.raises(ValidationError):
            AiConversationResponse(  # pyright: ignore[reportCallIssue]
                product_id=2,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

    def test_missing_product_id_fails(self):
        with pytest.raises(ValidationError):
            AiConversationResponse(  # pyright: ignore[reportCallIssue]
                user_id=1,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

    def test_missing_created_at_fails(self):
        with pytest.raises(ValidationError):
            AiConversationResponse(  # pyright: ignore[reportCallIssue]
                user_id=1,
                product_id=2,
                updated_at=datetime.now(),
            )

    def test_missing_updated_at_fails(self):
        with pytest.raises(ValidationError):
            AiConversationResponse(  # pyright: ignore[reportCallIssue]
                user_id=1,
                product_id=2,
                created_at=datetime.now(),
            )
