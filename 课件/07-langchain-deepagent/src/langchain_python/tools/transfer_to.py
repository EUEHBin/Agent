from langchain.tools import tool, ToolException, ToolRuntime
from langgraph.types import Command
from langchain.messages import ToolMessage


def make_transfer_to(current_agent_name: str):

    @tool
    def transfer_to(agent_name: str, runtime: ToolRuntime):
        """
        通过此工具，可以将当前Agent无法完成的任务交给其他Agent去处理。
        目前有以下Agent是可用的。
        - web_agent:
        负责网络搜索、抓取网页正文、核实公开信息并总结分析。
        适合需要查询最新资料、查找官方文档或新闻、提炼指定 URL 内容、
        比较多个公开来源，或需要附带可追溯来源链接的任务。

        - coding_agent:
        负责代码编写、文件处理、前端工程构建与静态网站部署。
        适合需要创建或修改代码、生成可交付静态网页或应用、打包文件，
        以及需要在沙箱中验证构建结果的任务。
        不能交付依赖服务器 API、数据库、后端认证、定时任务或持续运行服务的后端应用。
        """
        if agent_name not in ["web_agent", "coding_agent"]:
            raise ToolException(f"无效的名称：{agent_name}")
        if agent_name == current_agent_name:
            raise ToolException(f"当前的Agent已经是：{agent_name}")

        # 消息补全
        # 这里的课程代码有bug，课堂上相当于只保留了当前agent的最后一条ai消息，实际上是要保留当前agent运行的全部消息的
        # ai_message = runtime.state.get("messages", [])[-1]
        # 下面是正确的做法
        all_messages = runtime.state.get("messages", [])
        tool_messsage = ToolMessage(
            content=f"控制权已移交给{agent_name}", tool_call_id=runtime.tool_call_id
        )

        return Command(
            graph=Command.PARENT,
            goto=agent_name,
            update={
                "active_agent": agent_name,
                "messages": [*all_messages, tool_messsage],
            },
        )

    transfer_to.handle_tool_error = True

    return transfer_to
