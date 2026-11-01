import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph
import asyncio


class DemoComplexGraphState(TypedDict):
    """复杂图演示状态"""

    # 追踪信息，使用 operator.add reducer 追加累积，观察每次进入节点的变化
    traces: Annotated[list[str], operator.add]


def _make_node(name: str, sleep=0):
    """生成一个向 traces 中追加节点名的简单节点"""

    async def node(state: DemoComplexGraphState) -> dict:
        print(f"进入节点：{name}")
        await asyncio.sleep(sleep)
        return {"traces": [name]}

    return node


def build_graph():
    """生成并发图：
    START -> A -> {B1, C1, D1} -> {B2, C2, D2} -> E(结束)
    """
    workflow = StateGraph(DemoComplexGraphState)

    for node_name, sleep in [
        ("A", 0),
        ("B1", 1),
        ("C1", 2),
        ("D1", 3),
        ("B2", 1),
        ("C2", 2),
        ("D2", 3),
        ("E", 0),
    ]:
        workflow.add_node(node_name, _make_node(node_name, sleep))

    workflow.add_edge(START, "A")
    # A 并发进入 B1、C1、D1
    workflow.add_edge("A", "B1")
    workflow.add_edge("A", "C1")
    workflow.add_edge("A", "D1")
    # 链式推进
    workflow.add_edge("B1", "B2")
    workflow.add_edge("C1", "C2")
    workflow.add_edge("D1", "D2")
    # B2、C2、D2 汇合到 E
    workflow.add_edge("B2", "E")
    workflow.add_edge("C2", "E")
    workflow.add_edge("D2", "E")
    workflow.add_edge("E", END)

    return workflow
