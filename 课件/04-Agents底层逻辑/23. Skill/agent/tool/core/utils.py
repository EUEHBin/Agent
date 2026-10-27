# 实现 create_params_model 函数
import inspect
from typing import Any
from pydantic import Field, create_model


def create_params_model(func, param_descriptions={}):
    model_name = f"{func.__name__}_params"
    args = {}
    sig = inspect.signature(func)
    for pname, param in sig.parameters.items():
        py_type = param.annotation if param.annotation is not param.empty else Any
        desc = param_descriptions.get(pname, "")

        if param.default is param.empty:
            # 必填参数：不设默认值
            args[pname] = (py_type, Field(description=desc))
        else:
            # 可选参数：设置默认值
            args[pname] = (
                py_type,
                Field(default=param.default, description=desc),
            )

    return create_model(model_name, **args)
