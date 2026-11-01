from langgraph.graph import END, START, StateGraph
from langgraph_python.nodes.check import check
from langgraph_python.nodes.call_model import call_model
from langgraph_python.nodes.initialize_system_prompt import initialize_system_prompt
from langgraph_python.states.core_agent_state import CoreAgentState, ContextSchema
from langgraph.prebuilt import ToolNode
from langgraph_python.tools import tools
from langgraph.types import RetryPolicy, Send, TimeoutPolicy
from langgraph.errors import NodeError
from langgraph.types import Command
from langchain.messages import AIMessage


def should_continue(state: CoreAgentState) -> str | list[Send]:
    """为每个 tool call 动态创建一个 tools 节点调用。"""
    last_message = state["messages"][-1]
    if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
        return END

    return [Send("tools", [tool_call]) for tool_call in last_message.tool_calls]


def error_handler(state: CoreAgentState, error: NodeError):
    msg = f"{error.node}节点发生了错误：{error.error}"
    return Command(update={"messages": [AIMessage(msg)]}, goto=END)


def build_graph():
    """生成核心 Agent 图（未编译）"""
    workflow = StateGraph(CoreAgentState, context_schema=ContextSchema)

    # 容错机制
    workflow.set_node_defaults(
        # retry_policy=RetryPolicy(max_attempts=3),
        # timeout=TimeoutPolicy(run_timeout=3, idle_timeout=1),
        error_handler=error_handler  # type: ignore
    )

    workflow.add_node("check_user_id", check)
    workflow.add_node("initialize_system_prompt", initialize_system_prompt)
    workflow.add_node("model", call_model)
    workflow.add_node("tools", ToolNode(tools))

    workflow.add_edge(START, "check_user_id")
    workflow.add_edge("check_user_id", "initialize_system_prompt")
    workflow.add_edge("initialize_system_prompt", "model")
    workflow.add_conditional_edges("model", should_continue, ["tools", END])
    workflow.add_edge("tools", "model")
    return workflow
