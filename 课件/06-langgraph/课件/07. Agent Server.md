# Agent Server

Agent Server 可以帮你搞定 API 接口和数据持久化

## 安装 LangGraph CLI

```bash
uv add "langgraph-cli[inmem]==0.4.31"
```

验证是否安装成功：

```bash
langgraph --version
```

## 配置文件

见 `langgraph.json`

## 启动服务

在工程根目录执行：

```bash
langgraph dev
```

启动后，可以通过以下地址访问：http://127.0.0.1:2024/docs

## 使用 Studio

https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024

浏览器打开上面的 Studio 地址，即可在可视化界面中与 Agent 对话、查看图结构和运行轨迹。

## 使用 Agent Chat

打开 <https://agentchat.vercel.app/>，填入本地服务地址 `http://127.0.0.1:2024` 和图 ID（本工程的图 ID 为 `agent`），即可在网页上直接与 Agent 聊天。
