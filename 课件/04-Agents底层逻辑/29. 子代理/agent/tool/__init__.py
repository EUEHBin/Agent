from agent.tool.core import Tool
import json
from agent.tool.read_file import read_file
from agent.tool.write_file import write_file
from agent.tool.bash_command import bash_command
from agent.tool.web import web_search, fetch_url
from agent.tool.use_skill import use_skill
from agent.tool.use_mcp import use_mcp
from agent.tool.create_agent import create_agent


class _ToolRegistry:
    _tools: dict[str, Tool] = {}

    def register(self, tool: Tool):
        """注册一个工具"""
        self._tools[tool.name] = tool

    def schemas(self) -> list[dict]:
        """返回所有工具的 Schema 列表，可直接赋值给 session.tools"""
        return [t.schema() for t in self._tools.values()]

    def invoke(self, message: dict) -> list[dict] | None:
        """从模型返回的消息中提取 tool_calls 并逐一执行"""
        tool_calls = message.get("tool_calls", [])
        if not tool_calls:
            return None
        results = []
        for tc in message.get("tool_calls", []):
            id = tc["id"]
            name = tc["function"]["name"]
            args = json.loads(tc["function"]["arguments"])
            tool = self._tools[name]
            result = ""
            if not tool:
                result = "无此工具，请仔细检查你传递的工具名称是否正确"
            else:
                result = tool(**args)
            results.append(
                {
                    "role": "tool",
                    "tool_call_id": id,
                    "name": name,
                    "content": result,
                }
            )
        return results


registry = _ToolRegistry()
registry.register(read_file)
registry.register(write_file)
registry.register(bash_command)
registry.register(web_search)
registry.register(fetch_url)
registry.register(use_skill)
registry.register(use_mcp)
registry.register(create_agent)
