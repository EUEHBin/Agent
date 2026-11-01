import operator
from typing import Annotated, Any, TypedDict, cast

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send, interrupt


class State(TypedDict):
    number: int
    result: Annotated[list[str], operator.add]


def fan_out(state: State) -> list[Send]:
    return [Send("worker", f"task_{index}") for index in range(1, state["number"] + 1)]

    # return [Send("worker", "任务1"), Send("worker", "任务2"), Send("worker", "任务3")]


def worker(task: str) -> dict[str, list[str]]:
    return {"result": [f"{task}:result"]}


def build_graph():
    workflow = StateGraph(State)

    workflow.add_node("worker", worker)  # type: ignore

    workflow.add_conditional_edges(START, fan_out, ["worker"])
    workflow.add_edge("worker", END)

    return workflow
