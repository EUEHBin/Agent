from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain_quickjs import CodeInterpreterMiddleware

from langchain_python.core.config import anthropic_settings

TOTAL_EVENTS = 50
PAGE_SIZE = 5


@tool
def get_refund_events_page(cursor: int = 0) -> dict:
    """读取一页退款事件。

    参数：
    - cursor：本页第一条事件的下标。首次调用传 0；后续调用必须原样传入
      上一页返回的 next_cursor。

    返回一个字典，字段含义如下：
    - events：本页退款事件列表，固定最多 5 条。
    - events[].order_id：订单唯一编号。
    - events[].refund_amount：退款金额，单位为元。
    - events[].risk_tags：该订单的风险标签列表，例如 duplicate_charge 表示重复扣款。
    - events[].customer_chat_log：完整客服沟通记录，内容较长；仅在需要分析聊天内容时使用。
    - next_cursor：下一页的 cursor。为整数时说明还有下一页；为 null 时说明已读取全部事件，
      不应再调用此工具。
    """
    if cursor < 0 or cursor > TOTAL_EVENTS:
        raise ValueError("cursor 不合法")

    events = [_build_refund_event(index) for index in range(cursor, cursor + PAGE_SIZE)]
    next_cursor = cursor + PAGE_SIZE
    return {
        "events": events,
        "next_cursor": next_cursor if next_cursor < TOTAL_EVENTS else None,
    }


def _build_refund_event(index: int) -> dict:
    duplicate_charge_indexes = {7, 19, 31, 43}
    is_duplicate_charge = index in duplicate_charge_indexes
    refund_amount = (
        9_000 + index * 10 if is_duplicate_charge else 500 + (index * 1_379) % 7_000
    )
    risk_tags = ["refund", "manual_review"]
    if is_duplicate_charge:
        risk_tags.append("duplicate_charge")

    return {
        "order_id": f"ORD-2026-{index + 1:04d}",
        "refund_amount": refund_amount,
        "risk_tags": risk_tags,
        "customer_chat_log": (
            f"订单 {index + 1} 的客服沟通记录：客户描述付款、退款和物流情况。"
            "客服已核对支付流水并记录处理过程。" * 25
        ),
    }


model = init_chat_model(
    model=anthropic_settings.default_model,
    model_provider="anthropic",
    thinking={"type": "disabled"},
)

system_prompt = """你是一个退款事件审计助手。

你可以使用 get_refund_events_page 分页读取退款事件，并根据用户的条件完成审计。
"""


agent = create_deep_agent(
    model=model,
    tools=[get_refund_events_page],
    system_prompt=system_prompt,
    middleware=[CodeInterpreterMiddleware(ptc=[get_refund_events_page])],
)
