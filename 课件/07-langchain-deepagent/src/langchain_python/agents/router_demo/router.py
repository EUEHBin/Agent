from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from .router_node import route_node
from .hr_agent import hr
from .administration_agent import administration
from .it_agent import it
from .unknown import unknown
from langchain.messages import AIMessage, HumanMessage
from .synthesize_node import synthesize_node
from .router_types import RouteState


def after_route(state: RouteState):
    return [Send(route["agent_name"], route) for route in state["routes"]]


agent = (
    StateGraph(RouteState)
    .add_node("route_node", route_node)
    .add_node("it", it)
    .add_node("administration", administration)
    .add_node("hr", hr)
    .add_node("unknown", unknown)
    .add_node("synthesize_node", synthesize_node)
    .add_edge(START, "route_node")
    .add_conditional_edges(
        "route_node", after_route, ["it", "administration", "hr", "unknown"]
    )
    .add_edge("it", "synthesize_node")
    .add_edge("administration", "synthesize_node")
    .add_edge("hr", "synthesize_node")
    .add_edge("unknown", "synthesize_node")
)
