import asyncio
from mcp import StdioServerParameters, ClientSession
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamable_http_client
from contextlib import asynccontextmanager

mcp = {
    "servers": {
        "time": {"type": "stdio", "command": "uvx", "args": ["mcp-server-time"]},
        "microsoft-learn": {
            "type": "http",
            "url": "https://learn.microsoft.com/api/mcp",
        },
    }
}


@asynccontextmanager
async def connect_mcp(server_config: dict):
    """根据配置连接 MCP 服务器，返回已初始化的 ClientSession"""
    if server_config["type"] == "stdio":
        params = StdioServerParameters(
            command=server_config["command"], args=server_config.get("args", [])
        )
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session
    elif server_config["type"] == "http":
        async with streamable_http_client(server_config["url"]) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session
    else:
        raise ValueError(f"不支持的服务器类型: {server_config['type']}")


import threading


def run_async(coro):
    """在独立线程中运行异步协程，同步等待并返回结果"""
    result = None
    error = None

    def _run():
        nonlocal result, error
        try:
            result = asyncio.run(coro)
        except Exception as e:
            error = e

    t = threading.Thread(target=_run)
    t.start()
    t.join()

    if error:
        raise error
    return result


class MCPClient:
    def __init__(self, config: dict):
        self.servers = config["servers"]

    async def alist_tools(self) -> list:
        """异步：获取所有服务器的工具列表"""
        results = []
        for name, config in self.servers.items():
            async with connect_mcp(config) as session:
                tools = await session.list_tools()
                results.append({"server": name, "tools": tools})
        return results

    async def acall_tool(
        self, server_name: str, tool_name: str, arguments: dict | None = None
    ):
        """异步：调用指定服务器上的工具"""
        config = self.servers[server_name]
        async with connect_mcp(config) as session:
            return await session.call_tool(tool_name, arguments or {})

    def list_tools(self) -> list:
        """同步：获取所有 MCP 服务器的工具列表"""
        return run_async(self.alist_tools())  # type: ignore

    def call_tool(
        self, server_name: str, tool_name: str, arguments: dict | None = None
    ):
        """同步：调用指定服务器上的工具"""
        return run_async(self.acall_tool(server_name, tool_name, arguments))
