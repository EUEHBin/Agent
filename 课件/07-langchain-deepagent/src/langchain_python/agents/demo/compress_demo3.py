from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain_python.core.mock_model import mock_model

model = mock_model(
    {
        "responses": [
            {
                "reasoning": "我应该按照模拟的配置返回给用户消息",
                "text": "你好，我是由配置文件驱动的模拟模型。你可以修改 mock_model.config.jsonc 来改变我的行为。",
            }
        ],
        "rules": [],
    }
)


agent = create_deep_agent(
    model=model,
    backend=FilesystemBackend(
        root_dir="/Users/yuanjin/工作/课/录播课/AI/langchain-python/backup"
    ),
)
