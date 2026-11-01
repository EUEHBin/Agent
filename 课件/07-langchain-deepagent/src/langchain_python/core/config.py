from pydantic_settings import BaseSettings


class BaseSettingsWithEnv(BaseSettings):
    model_config = {"env_file": ".env", "extra": "ignore"}


class OpenAISettings(BaseSettingsWithEnv):
    api_key: str = ""
    base_url: str = ""
    default_model: str = ""

    model_config = {"env_prefix": "OPENAI_"}


class AnthropicSettings(BaseSettingsWithEnv):
    api_key: str = ""
    base_url: str = ""
    default_model: str = ""

    model_config = {"env_prefix": "ANTHROPIC_"}


class TavilySettings(BaseSettingsWithEnv):
    api_key: str = ""
    model_config = {"env_prefix": "TAVILY_"}


class SandboxSettings(BaseSettingsWithEnv):
    api_key: str = ""
    api_url: str = ""
    domain: str = ""
    role_arn: str = ""
    oss_endpoint: str = ""
    oss_bucket: str = ""
    template: str = ""

    model_config = {"env_prefix": "E2B_"}


openai_settings = OpenAISettings()
anthropic_settings = AnthropicSettings()
tavily_settings = TavilySettings()
sandbox_settings = SandboxSettings()
