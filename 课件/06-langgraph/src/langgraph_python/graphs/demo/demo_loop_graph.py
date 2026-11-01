import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


class DemoLoopGraphState(TypedDict):
    """循环图演示状态"""

    # 追踪信息，使用 operator.add reducer 追加累积，观察每次进入节点的变化
    traces: Annotated[list[str], operator.add]
    # A 节点的执行次数
    a_count: int


def _make_node(name: str):
    """生成一个向 traces 中追加节点名的简单节点"""

    async def node(state: DemoLoopGraphState) -> dict:
        print(f"进入节点：{name}")
        return {"traces": [name]}

    return node


async def node_a(state: DemoLoopGraphState) -> dict:
    """A 节点，每次进入将 a_count 减一"""
    print(f"进入节点：A，剩余次数 {state['a_count']}")
    return {"traces": ["A"], "a_count": state["a_count"] - 1}


def build_graph():
    """生成带循环的图：START -> A -> B -> (a_count>0 回到 A，否则进入 C) -> END"""
    workflow = StateGraph(DemoLoopGraphState)

    workflow.add_node("A", node_a)
    for node_name in ["B", "C"]:
        workflow.add_node(node_name, _make_node(node_name))

    workflow.add_edge(START, "A")
    workflow.add_edge("A", "B")
    # B 根据 a_count 字段决定是回到 A 继续循环，还是进入 C 结束
    workflow.add_conditional_edges(
        "B",
        lambda state: "A" if state["a_count"] > 0 else "C",
        {"A": "A", "C": "C"},
    )
    workflow.add_edge("C", END)

    return workflow
