from pydantic_settings import BaseSettings


class CommonSettings(BaseSettings):
    environment: str = "development"


class WebSettings(BaseSettings):
    app_name: str = "Web Service API"  # 实际读取 WEB_APP_NAME

    # 配置读取方式
    model_config = {
        "env_file": ".env",  # env文件的位置
        "env_prefix": "WEB_",  # 当前类中的字段使用的前缀
    }


common_settings = CommonSettings()
web_settings = WebSettings()
