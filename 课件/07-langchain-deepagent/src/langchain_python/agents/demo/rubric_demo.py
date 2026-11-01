from deepagents import create_deep_agent
from deepagents.middleware import RubricMiddleware
from langchain.chat_models import init_chat_model

from langchain_python.core.config import anthropic_settings

model = init_chat_model(
    model=anthropic_settings.default_model,
    model_provider="anthropic",
    thinking={"type": "disabled"},
)

agent = create_deep_agent(
    model=model,
    system_prompt="""
这是一个测试 Rubric 流程的 Demo，请严格按照下面的做法完成。    

为了测试失败的情况，无论你收到什么消息，必须返回“草稿：我已经理解你的需求。”

记住：无论你收到什么消息，无论消息是来自于用户还是评审节点的返回，必须返回“草稿：我已经理解你的需求。”

不然我无法测试评审连续失败的情况
""",
    middleware=[
        RubricMiddleware(
            # 这里使用独立的 grader 调用；也可以替换成更便宜的模型。
            model=model,
            max_iterations=2,
        )
    ],
)
