from agent.tool.core import tool
from tavily import TavilyClient
from agent.config import tavily_settings
import json


@tool(query="搜索关键字")
def web_search(query: str):
    "根据关键字进行网络搜索，返回结构化的搜索结果"
    client = TavilyClient(api_key=tavily_settings.api_key)
    response = client.search(query=query)
    return json.dumps(response, ensure_ascii=False)


@tool(urls="要抓取的url链接数组")
def fetch_url(urls: list[str]):
    "根据提供的url数组，抓取网页内容，返回结构化的搜索结果"
    client = TavilyClient(api_key=tavily_settings.api_key)
    response = client.extract(urls=urls, include_images=False)

    return json.dumps(response, ensure_ascii=False)
