from collections.abc import AsyncGenerator
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.exception.ai import AiException
from app.model.ai_conversation import AiConversation
from app.model.product import Product
from app.model.setting import Setting
from app.service.base import BaseService
from duyi_utils.ai.chat import AIChat, AIChatConfig, AIMessage, MessageRole

MESSAGE_ROLE_SYSTEM = "system"
MESSAGE_ROLE_USER = "user"
MESSAGE_ROLE_ASSISTANT = "assistant"

_template_dir = Path(__file__).parent / "template"
_jinja_env = Environment(loader=FileSystemLoader(str(_template_dir)))


class AiService(BaseService):

    async def _load_product(self, product_id: int) -> Product:
        result = await self.db.execute(
            select(Product)
            .options(selectinload(Product.categories), selectinload(Product.skus))
            .where(Product.id == product_id)
        )
        return result.unique().scalar_one()

    def _render_system_prompt(self, product: Product) -> str:
        template = _jinja_env.get_template("product_intro.j2")
        categories_str = "、".join(c.name for c in product.categories) or None
        skus = [
            {"sku_code": s.sku_code, "price": str(s.price), "stock": s.stock}
            for s in product.skus
        ]
        return template.render(
            product={
                "name": product.name,
                "brand": product.brand,
                "description": product.description,
                "categories": categories_str,
                "skus": skus or None,
            }
        )

    async def _get_required_ai_config(self) -> AIChatConfig:
        keys = ["ai_api_key", "ai_base_url", "ai_model"]
        result = await self.db.execute(select(Setting).where(Setting.key.in_(keys)))
        settings_map = {s.key: s.value for s in result.scalars().all()}

        missing = [k for k in keys if not settings_map.get(k)]
        if missing:
            raise AiException(
                message="AI服务配置不完整，请联系管理员",
                detail=f"缺少以下配置项：{', '.join(missing)}",
            )

        return AIChatConfig(
            api_key=settings_map["ai_api_key"],
            base_url=settings_map["ai_base_url"],
            model=settings_map["ai_model"],
        )

    async def _get_conversation(
        self, user_id: int, product_id: int
    ) -> AiConversation | None:
        result = await self.db.execute(
            select(AiConversation).where(
                AiConversation.user_id == user_id,
                AiConversation.product_id == product_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_history(self, user_id: int, product_id: int) -> list[dict]:
        conv = await self._get_conversation(user_id, product_id)
        if conv is None:
            return []
        return [m for m in conv.messages if m["role"] != MESSAGE_ROLE_SYSTEM]

    async def initialize(
        self, user_id: int, product_id: int
    ) -> AsyncGenerator[str, None]:
        conv = await self._get_conversation(user_id, product_id)

        if conv is not None and len(conv.messages) > 1:
            raise AiException(message="该产品已有对话历史记录，请先清空后再初始化")

        product = await self._load_product(product_id)
        system_prompt = self._render_system_prompt(product)

        config = await self._get_required_ai_config()
        ai_chat = AIChat(config)
        await self.db.commit()
        await self.db.close()  # 回归连接池

        full_response = ""
        async for chunk in ai_chat.chat_stream(
            [AIMessage(role=MessageRole.SYSTEM, content=system_prompt)]
        ):
            full_response += chunk
            yield chunk

        if conv is None:
            conv = AiConversation(
                user_id=user_id,
                product_id=product_id,
                messages=[
                    {"role": MESSAGE_ROLE_SYSTEM, "content": system_prompt},
                    {"role": MESSAGE_ROLE_ASSISTANT, "content": full_response},
                ],
            )
            self.db.add(conv)
        else:
            conv.messages = [
                {"role": MESSAGE_ROLE_SYSTEM, "content": system_prompt},
                {"role": MESSAGE_ROLE_ASSISTANT, "content": full_response},
            ]
            conv = await self.db.merge(conv)

        await self.db.flush()

    async def send_message_stream(
        self, user_id: int, product_id: int, content: str
    ) -> AsyncGenerator[str, None]:
        conv = await self._get_conversation(user_id, product_id)
        if conv is None:
            raise AiException(message="未找到对话记录，请先初始化AI导购")

        ai_messages = [
            AIMessage(role=MessageRole(m["role"]), content=m["content"])
            for m in conv.messages
        ]
        ai_messages.append(AIMessage(role=MessageRole.USER, content=content))

        config = await self._get_required_ai_config()
        ai_chat = AIChat(config)
        await self.db.commit()
        await self.db.close()  # 回归连接池

        full_response = ""
        async for chunk in ai_chat.chat_stream(ai_messages):
            full_response += chunk
            yield chunk

        conv.messages = [
            *conv.messages,
            {"role": MESSAGE_ROLE_USER, "content": content},
            {"role": MESSAGE_ROLE_ASSISTANT, "content": full_response},
        ]
        conv = await self.db.merge(conv)
        await self.db.flush()

    async def delete_conversation(self, user_id: int, product_id: int) -> None:
        conv = await self._get_conversation(user_id, product_id)
        if conv is not None:
            await self.db.delete(conv)
            await self.db.flush()
