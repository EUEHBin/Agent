from typing import NotRequired

from langgraph.graph import StateGraph, START
from langchain.agents import AgentState
from .web_agent import agent as web_agent
from .coding_agent import agent as coding_agent


class GraphState(AgentState):
    active_agent: NotRequired[str]


flow = StateGraph(GraphState)

flow.add_node("web_agent", web_agent)
flow.add_node("coding_agent", coding_agent)
flow.add_conditional_edges(
    START,
    lambda state: state.get("acitve_agent", "web_agent"),
    ["web_agent", "coding_agent"],
)

agent = flow.compile()
