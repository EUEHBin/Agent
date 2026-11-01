from deepagents import create_deep_agent
from langchain_python.core.mock_model import mock_model
from deepagents.backends import FilesystemBackend
from deepagents.middleware import SummarizationMiddleware

content = "\n".join([f"第{i}条数据" for i in range(1, 10001)])

model = mock_model(
    {
        "responses": [
            {
                "tool_calls": [
                    {
                        "name": "write_file",
                        "args": {
                            "file_path": "large_result.txt",
                            "content": content,
                        },
                    }
                ]
            }
        ],
        "rules": [
            {
                "when": {"last_message": "tool_result"},
                "max_tool_calls": 20,
                "respond": {
                    "reasoning": "需要再次调用工具获取更多数据。",
                    "tool_calls": [
                        {
                            "name": "write_file",
                            "args": {
                                "file_path": "large_result.txt",
                                "content": content,
                            },
                        }
                    ],
                },
                "final": {"text": "调用工具完成"},
            }
        ],
    }
)

backend = FilesystemBackend(
    root_dir="/Users/yuanjin/工作/课/录播课/AI/langchain-python/backup"
)

summarization_middleware = SummarizationMiddleware(
    model=model,
    backend=backend,
    # 旧工具调用参数卸载配置
    truncate_args_settings={
        # 对话达到 60000 tokens 时，开始检查旧工具调用参数
        "trigger": ("tokens", 60_000),
        # 最近 5 条消息中的工具参数保持完整
        "keep": ("messages", 5),
        # 单个参数字符串超过 2000 个字符才卸载
        "max_length": 2_000,
    },
)

agent = create_deep_agent(
    model=model,
    backend=backend,
    middleware=[summarization_middleware],
)
