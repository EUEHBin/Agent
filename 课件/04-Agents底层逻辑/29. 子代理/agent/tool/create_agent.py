from agent.tool.core import tool
import threading
import json


@tool(
    agent_config="每个子代理的配置。每个子代理要配置名称、用户提示词，子代理会根据提示词启动任务，然后根据提示词的要求返回任务执行结果"
)
def create_agent(agent_config: list[dict[str, str]]) -> str:
    """
    创建并启动多个子代理，每个子代理在独立线程中运行，完成任务后合并返回结果
    参数示例：
    [
        {
            "name": "sub-agent1",
            "query": "初始的用户提示词"
        },
        {
            "name": "sub-agent2",
            "query": "初始的用户提示词"
        }
    ]
    返回结果示例：
    [
        {
            "name": "sub-agent1",
            "result": "子代理1的完成结果"
        },
        {
            "name": "sub-agent2",
            "result": "子代理2的完成结果"
        }
    ]
    """

    from agent.agent import Agent

    results: list[dict[str, str]] = []
    results_lock = threading.Lock()
    threads: list[threading.Thread] = []

    def run_sub_agent(name: str, query: str) -> None:
        agent = Agent()
        responses = agent.invoke(query)
        final_resp = responses[-1]
        content = final_resp.message.get("content", "")
        agent.session.save(f"{name}-")
        with results_lock:
            results.append({"name": name, "result": content})

    for config in agent_config:
        name = config.get("name", "unnamed")
        query = config.get("query", "")
        thread = threading.Thread(target=run_sub_agent, args=(name, query))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return json.dumps(results, indent=2, ensure_ascii=False)
