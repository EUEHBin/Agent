from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langgraph_python.states.core_agent_state import ContextSchema

SUB_AGENTS: dict[str, ContextSchema] = {
    "web_researcher": ContextSchema(
        system_prompt=(
            "你是网络调研专家，擅长通过搜索引擎和网页抓取完成资料调研。\n"
            "工作步骤：\n"
            "1. 先用 web_search 搜索关键词；\n"
            "2. 如有必要，再用 fetch_url 抓取关键页面；\n"
            "3. 综合结果给出有依据的结论，并列出信息来源。\n"
            "始终用中文回答。"
        ),
        tools=["web_search", "fetch_url"],
    ),
    "poet": ContextSchema(
        system_prompt=(
            "你是一个诗人\n" "擅长各种诗词旋律和结构\n" "请根据要求作诗一首"
        ),
        temperature=0.9,
        tools=[""],  # 无工具
    ),
}


@tool
async def call_sub_agent(agent_name: str, task: str) -> str:
    """把任务委托给一个子Agent去完成。子Agent 会独立运行自己的一套工具调用流程，完成后把最终结果返回给你。

    可选子Agent：
    - web_researcher：网络调研专家，适合搜索资料、抓取网页进行调研
    - poet: 专门擅长写诗的诗人，这个子代理无法进行网络搜索

    Args:
        agent_name: 子Agent 名称，从上面的列表中选择
        task: 要委托给子Agent的任务描述
    """
    from langgraph_python.graphs.core_agent_graph import build_graph

    graph = build_graph().compile()
    context = SUB_AGENTS.get(agent_name)
    if context is None:
        return f"error: 未知的子Agent：{agent_name}。可选：{', '.join(SUB_AGENTS)}"

    result = await graph.ainvoke(
        {"messages": [HumanMessage(task)]},
        context=context,
    )
    return result["messages"][-1].content
