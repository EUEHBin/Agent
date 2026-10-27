from pydantic_settings import BaseSettings
import os

_current_dir = os.path.dirname(os.path.abspath(__file__))
_env_file = os.path.abspath(os.path.join(_current_dir, "../.env"))


class BaseSettingsWithEnv(BaseSettings):
    model_config = {"env_file": _env_file, "extra": "ignore"}


class OpenAISettings(BaseSettingsWithEnv):
    api_key: str = ""
    base_url: str = ""
    model: str = ""

    model_config = {"env_prefix": "OPENAI_"}


class TavilySettings(BaseSettingsWithEnv):
    api_key: str = ""
    model_config = {"env_prefix": "TAVILY_"}


openai_settings = OpenAISettings()
tavily_settings = TavilySettings()
