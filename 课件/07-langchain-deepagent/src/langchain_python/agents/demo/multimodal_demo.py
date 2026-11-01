from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from langchain_python.core.config import anthropic_settings
from deepagents.backends import FilesystemBackend

model = init_chat_model(
    model="qwen3.7-flash",
    model_provider="anthropic",
    thinking={"type": "disabled"},
    profile={
        # 是否支持对应输入类型
        "image_inputs": True,
        "pdf_inputs": True,
        "audio_inputs": False,
        "video_inputs": False,
        # 是否允许媒体出现在工具结果 ToolMessage 中
        "image_tool_message": True,
        "pdf_tool_message": True,
    },
)

system_prompt = (
    "这是一个测试多模态的Demo。"
    "如果用户给予的是一个路径，"
    "比如，用户输入：test.jpg，你就调用工具 read_file: /test.jpg 文件即可。"
    "如果用户直接给予一个多模态消息，你就读取消息内容即可。"
)


agent = create_deep_agent(
    model=model,
    system_prompt=system_prompt,
    backend=FilesystemBackend(
        root_dir="/Users/yuanjin/工作/课/录播课/AI/langchain-python/backup/files"
    ),
)
