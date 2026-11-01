import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt
import asyncio


class State(TypedDict):
    # 追踪信息，使用 operator.add reducer 追加累积，观察每次进入节点的变化
    traces: Annotated[list[str], operator.add]


async def A(state: State) -> dict:
    print("进入节点A")
    answer1 = interrupt("A 的第一个中断：请问你要继续吗？")
    print(f"answer A1:{answer1}")
    answer2 = interrupt("A 的第二个中断：请问你要继续吗？")
    print(f"answer A2:{answer2}")
    return {"traces": ["A"]}


async def B(state: State) -> dict:
    print("进入节点B")
    answer1 = interrupt("B 的第一个中断：请问你要继续吗？")
    print(f"answer B1:{answer1}")
    answer2 = interrupt("B 的第二个中断：请问你要继续吗？")
    print(f"answer B2:{answer2}")
    answer3 = interrupt("B 的第三个中断：请问你要继续吗？")
    print(f"answer B3:{answer3}")
    return {"traces": ["B"]}


def build_graph():
    workflow = StateGraph(State)

    workflow.add_node(A)
    workflow.add_node(B)

    # START 并发进入 A、B
    workflow.add_edge(START, "A")
    workflow.add_edge(START, "B")

    # A、B 各自连到结束
    workflow.add_edge("A", END)
    workflow.add_edge("B", END)

    return workflow
