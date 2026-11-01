from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from langchain_python.core.config import anthropic_settings
from langchain.tools import tool

model = init_chat_model(
    model=anthropic_settings.default_model,
    model_provider="anthropic",
    thinking={"type": "disabled"},
)


@tool
def send_mail(mail: str, title: str, content: str):
    "发送邮件"
    return "邮件已发送"


@tool
def call(tel: str):
    "拨打电话"
    return "电话已拨打"


def format_description(tool_call, state, runtime):
    """根据本次工具调用动态生成审批说明。"""
    return f"是否允许发送邮件：{tool_call['args']['mail']}"


agent = create_deep_agent(
    model=model,
    system_prompt="这是一个测试的Demo，无论用户发什么样的消息，你要做的事情是同时调用两个工具: send_mail、call，任意填写参数即可。",
    tools=[send_mail, call],
    interrupt_on={
        "send_mail": {
            "allowed_decisions": ["approve", "reject"],
            "description": format_description,
        },
        "call": {
            "allowed_decisions": ["approve", "reject"],
            "description": "是否允许拨打电话",
        },
    },
)
