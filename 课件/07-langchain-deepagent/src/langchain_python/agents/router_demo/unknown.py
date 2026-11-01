from langchain_python.agents.router_demo.router_types import RouteConfig


def unknown(state: RouteConfig):
    query = state["query"]
    agent_name = state["agent_name"]
    answer = "无法处理的请求"

    return {"answers": [{"query": query, "agent_name": agent_name, "answer": answer}]}
