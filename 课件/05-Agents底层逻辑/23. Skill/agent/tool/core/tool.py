# 创建 Tool 类
import inspect
import traceback
from typing import Any, Callable
from agent.tool.core.utils import create_params_model


class Tool:

    def __init__(
        self,
        func: Callable,
        param_descriptions: dict = {},
    ):
        self.func = func
        self.name = func.__name__
        self.description = inspect.getdoc(func) or ""
        self.param_descriptions = param_descriptions or {}
        self.param_model = create_params_model(func, param_descriptions)

    def schema(self) -> dict:
        param_schema = self.param_model.model_json_schema()
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        name: {
                            "type": prop.get("type", "string"),
                            "description": prop.get("description", ""),
                        }
                        for name, prop in param_schema.get("properties", {}).items()
                    },
                    "required": param_schema.get("required", []),
                },
            },
        }

    def __call__(self, **kwargs) -> Any:
        result = ""
        try:
            # 验证参数
            validated = self.param_model(**kwargs)
            result = str(self.func(**validated.model_dump()))  # 将结果转换为字符串
        except Exception as e:
            # 完整堆栈字符串
            result = "".join(traceback.format_exception(type(e), e, e.__traceback__))

        return result


def tool(**args):
    """装饰器：将普通函数包装为 Tool 对象"""

    def decorator(func):
        return Tool(func, param_descriptions=args)

    return decorator
