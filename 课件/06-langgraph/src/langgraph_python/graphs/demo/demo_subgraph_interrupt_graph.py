import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt


class State(TypedDict):
    # 追踪信息，使用 operator.add reducer 追加累积，观察每次进入节点的变化
    traces: Annotated[list[str], operator.add]


# ============ 子图 ============


async def sub_a(state: State) -> dict:
    print("进入子图节点 a")
    answer = interrupt("子图节点 a 的中断：请问你要继续吗？")
    print(f"子图 answer a:{answer}")
    return {"traces": ["子图a"]}


async def sub_b(state: State) -> dict:
    print("进入子图节点 b")
    return {"traces": ["子图b"]}


def build_subgraph():
    workflow = StateGraph(State)

    workflow.add_node("a", sub_a)
    workflow.add_node("b", sub_b)

    workflow.add_edge(START, "a")
    workflow.add_edge("a", "b")
    workflow.add_edge("b", END)

    # 子图 checkpoint 模式设置为 None（per-invocation：每次调用全新开始，
    # 但在单次调用内继承父图 checkpointer，从而支持 interrupt 中断/恢复）
    return workflow.compile(checkpointer=None)


subgraph = build_subgraph()


# ============ 父图 ============


async def A(state: State) -> dict:
    print("进入节点 A")
    # 在节点内部调用子图，checkpointer 会自动继承父图
    result = await subgraph.ainvoke({"traces": []})
    print(f"子图返回:{result}")
    return {"traces": ["A"] + result["traces"]}


async def B(state: State) -> dict:
    print("进入节点 B")
    return {"traces": ["B"]}


def build_graph():
    workflow = StateGraph(State)

    workflow.add_node("A", A)
    workflow.add_node("B", B)

    workflow.add_edge(START, "A")
    workflow.add_edge("A", "B")
    workflow.add_edge("B", END)

    return workflow
