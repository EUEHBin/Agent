from langchain.chat_models import init_chat_model
from ai_eval.config.anthropic_settings import anthropic_settings
from ai_eval.utils.anthropic_compat import patch_nullable_cache_creation_usage


def create_model(**kwargs):
    patch_nullable_cache_creation_usage()
    config = {
        "model": anthropic_settings.default_model,
        "thinking": {"type": "disabled"},
        "model_provider": "anthropic",
    }
    config.update(kwargs)

    model = init_chat_model(**config)
    return model
