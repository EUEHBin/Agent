from deepagents import create_deep_agent
from langchain_python.core.config import anthropic_settings
from langchain.chat_models import init_chat_model
from langchain.agents.middleware import TodoListMiddleware

model = init_chat_model(
    model=anthropic_settings.default_model,
    model_provider="anthropic",
    thinking={"type": "disabled"},
)

agent = create_deep_agent(model=model, middleware=[TodoListMiddleware()])
