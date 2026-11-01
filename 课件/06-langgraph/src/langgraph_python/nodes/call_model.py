from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool

from langgraph.runtime import get_runtime
from langgraph_python.core.create_model import create_model
from langgraph_python.core.mock_model import mock_model
from langgraph_python.states.core_agent_state import ContextSchema, CoreAgentState
from langgraph_python.tools import get_tools, tools

# create_model 中声明的可配置模型字段，Context 中的同名字段需要转给模型的调用配置
_MODEL_CONFIG_FIELDS = ("model", "temperature", "top_p", "thinking")


def _get_context() -> ContextSchema:
    return get_runtime(ContextSchema).context


def _get_system_prompts(state: CoreAgentState) -> list[SystemMessage]:
    "根据 Thread 状态获取首次运行时生成的系统提示词快照"
    system_prompt = state.get("system_prompt")
    if not system_prompt:
        return []
    return [SystemMessage(system_prompt)]


def _get_model(context: ContextSchema):
    "根据 Context 获取模型对象"
    if context and context.model == "fake":
        return mock_model()
    return create_model()


def _get_tools(context: ContextSchema) -> list[BaseTool]:
    "根据 Context 获取工具列表，未配置时返回全部工具"
    if context is None or context.tools is None:
        return tools
    return get_tools(context.tools)


def _get_model_config(context: ContextSchema) -> RunnableConfig:
    "模型 invoke 只读 config.configurable，不读 Context，需手动把模型配置转成调用配置"
    if not context:
        return {}
    configurable = {
        name: getattr(context, name)
        for name in _MODEL_CONFIG_FIELDS
        if getattr(context, name) is not None
    }
    return {"configurable": configurable}


async def call_model(state: CoreAgentState) -> dict:
    """调用模型节点"""
    context = _get_context()
    messages = state["messages"]

    # 根据 Context 获取模型对象
    model = _get_model(context)
    # 从 Thread 状态读取已经冻结的系统提示词
    system_prompts = _get_system_prompts(state)
    # 根据 Context 获取工具列表
    active_tools = _get_tools(context)
    model_with_tools = model.bind_tools(active_tools)

    # 调用模型
    response = await model_with_tools.ainvoke(
        [*system_prompts, *messages],
        config=_get_model_config(context),
    )
    return {"messages": [response]}
