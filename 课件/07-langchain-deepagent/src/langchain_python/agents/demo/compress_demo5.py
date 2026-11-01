from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from deepagents.middleware import SummarizationMiddleware
from langchain.chat_models import init_chat_model
from langchain_python.core.config import openai_settings

model = init_chat_model(
    model=openai_settings.default_model,
    model_provider="openai",
    extra_body={
        "enable_thinking": False,
    },
    profile={
        "max_input_tokens": 80_000,
    },
)
backend = FilesystemBackend(
    root_dir="/Users/yuanjin/工作/课/录播课/AI/langchain-python/backup"
)

# 课件最后一个代码块中的默认配置。
summarization_middleware = SummarizationMiddleware(
    model=model,
    backend=backend,
    # 整个对话达到模型上下文窗口的 85% 时触发摘要
    trigger=("fraction", 0.85),
    # 摘要时保留最近4条消息
    keep=("messages", 4),
    trim_tokens_to_summarize=4000,
)

agent = create_deep_agent(
    model=model,
    backend=backend,
    middleware=[summarization_middleware],
)
