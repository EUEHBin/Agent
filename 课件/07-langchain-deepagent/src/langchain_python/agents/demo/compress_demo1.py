from deepagents import create_deep_agent
from langchain_python.core.mock_model import mock_model
from deepagents.backends import FilesystemBackend

model = mock_model(
    {
        "responses": [
            {
                "tool_calls": [
                    {
                        "name": "read_file",
                        "args": {
                            "file_path": "./红楼梦.txt",
                            "offset": 0,
                            "limit": 10000000,
                        },
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


agent = create_deep_agent(
    model=model,
    backend=FilesystemBackend(
        root_dir="/Users/yuanjin/工作/课/录播课/AI/langchain-python/backup"
    ),
)
