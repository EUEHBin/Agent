from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from langchain_python.core.config import anthropic_settings
from deepagents.backends import CompositeBackend, StateBackend, FilesystemBackend

model = init_chat_model(
    model=anthropic_settings.default_model,
    model_provider="anthropic",
    thinking={"type": "disabled"},
)

system_prompt = (
    "这是一个测试权限的Demo，不管用户发什么样的消息，你都要同时调用以下工具: \n"
    "read_file: /home/user/1.md\n"
    "read_file: /static/2.md"
)


agent = create_deep_agent(
    model=model,
    system_prompt=system_prompt,
    backend=CompositeBackend(
        default=StateBackend(),
        routes={
            "/static/": FilesystemBackend(
                root_dir="/Users/yuanjin/工作/课/录播课/AI/langchain-python/temp"
            )
        },
    ),
)
