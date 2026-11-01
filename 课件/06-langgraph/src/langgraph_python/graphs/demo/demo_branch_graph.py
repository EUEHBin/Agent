import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


class DemoBranchGraphState(TypedDict):
    """分支图演示状态"""

    # 追踪信息，使用 operator.add reducer 追加累积，观察每次进入节点的变化
    traces: Annotated[list[str], operator.add]
    # 分支选择信息
    branch: str


def _make_node(name: str):
    """生成一个向 traces 中追加节点名的简单节点"""

    async def node(state: DemoBranchGraphState) -> dict:
        print(f"进入节点：{name}")
        return {"traces": [name]}

    return node


def build_graph():
    """生成带分支的图"""
    workflow = StateGraph(DemoBranchGraphState)

    for node_name in ["A", "B", "C"]:
        workflow.add_node(node_name, _make_node(node_name))

    workflow.add_edge(START, "A")
    # A 之后根据 branch 字段条件路由到 B 分支或 C 分支
    workflow.add_conditional_edges(
        "A",
        lambda state: "小白兔" if state["branch"] == "B" else "大灰狼",
        {"小白兔": "B", "大灰狼": "C"},
    )
    workflow.add_edge("B", END)
    workflow.add_edge("C", END)

    return workflow
