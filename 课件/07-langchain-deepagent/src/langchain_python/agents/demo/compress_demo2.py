from deepagents import create_deep_agent
from langchain_python.core.mock_model import mock_model
from deepagents.backends import FilesystemBackend, CompositeBackend
from langchain.tools import tool

model = mock_model(
    {
        "responses": [
            {
                "tool_calls": [
                    {
                        "name": "large_result",
                        "args": {},
                    }
                ]
            }
        ],
        "rules": [
            {
                "when": {"last_message": "tool_result"},
                "respond": {"reasoning": "", "text": "工具调用完成"},
            }
        ],
    }
)


@tool
def large_result():
    "工具会返回超大的结果"
    return ",".join([str(i) for i in range(100000)])


agent = create_deep_agent(
    model=model,
    backend=CompositeBackend(
        default=FilesystemBackend(
            root_dir="/Users/yuanjin/工作/课/录播课/AI/langchain-python/backup"
        ),
        routes={},
        artifacts_root="/.deepagents",
    ),
    tools=[large_result],
)
