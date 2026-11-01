import operator
from typing import Annotated, Any, TypedDict
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt


class State(TypedDict):
    # 追踪信息，使用 operator.add reducer 追加累积，观察每次进入节点的变化
    traces: Annotated[list[str], operator.add]


async def A(state: State) -> dict:
    print("进入节点A")
    answer = interrupt("请问你要继续执行节点A吗？")
    print(f"answer A:{answer}")
    return {"traces": ["A"]}


async def B(state: State) -> dict:
    print("进入节点B")
    answer = interrupt("请问你要继续执行节点B吗？")
    print(f"answer B:{answer}")
    return {"traces": ["B"]}


def build_graph():
    workflow = StateGraph(State)

    workflow.add_node(A)
    workflow.add_node(B)

    workflow.add_edge(START, "A")
    workflow.add_edge("A", "B")
    workflow.add_edge("B", END)

    return workflow
