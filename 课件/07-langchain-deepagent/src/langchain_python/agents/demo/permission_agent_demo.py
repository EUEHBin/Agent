from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from langchain_python.core.config import anthropic_settings
from deepagents.middleware import FilesystemPermission

model = init_chat_model(
    model=anthropic_settings.default_model,
    model_provider="anthropic",
    thinking={"type": "disabled"},
)

system_prompt = (
    "这是一个测试权限的Demo，不管用户发什么样的消息，你都要同时调用以下工具: \n"
    "write_file: 向/home/user/.env写入任意内容\n"
    "read_file: 读取/.env的内容"
)


agent = create_deep_agent(
    model=model,
    system_prompt=system_prompt,
    permissions=[
        FilesystemPermission(
            operations=["read", "write"],
            paths=["/home/user", "/home/user/**", "/home/user/**/.*{,/**}"],
            mode="allow",
        ),
        FilesystemPermission(
            operations=["read", "write"],
            paths=["/**", "/**/.*{,/**}"],
            mode="deny",
        ),
    ],
)
