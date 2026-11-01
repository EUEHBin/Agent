> 🟢 完全讲完　
> 🔴 未讲解　
> 🟠 讲了一半（接口已能调用，但部分语义依赖后续概念，如中断/人在回路）

| 接口 | 含义 | 是否讲解 |
| --- | --- | --- |
| POST /assistants | 创建助手 | 🟢 |
| POST /assistants/search | 搜索助手 | 🟢 |
| POST /assistants/count | 统计助手数量 | 🟢 |
| GET /assistants/{assistant_id} | 获取助手 | 🟢 |
| DELETE /assistants/{assistant_id} | 删除助手 | 🟢 |
| PATCH /assistants/{assistant_id} | 更新助手 | 🟢 |
| GET /assistants/{assistant_id}/graph | 获取助手图 | 🟢 |
| GET /assistants/{assistant_id}/subgraphs | 获取子图 | 🟢 |
| GET /assistants/{assistant_id}/subgraphs/{namespace} | 按命名空间获取子图 | 🟢 |
| GET /assistants/{assistant_id}/schemas | 获取助手Schema | 🟢 |
| POST /assistants/{assistant_id}/versions | 获取助手版本 | 🟢 |
| POST /assistants/{assistant_id}/latest | 设置最新版本 | 🟢 |
| POST /threads | 创建线程 | 🟢 |
| POST /threads/search | 搜索线程 | 🟢 |
| POST /threads/count | 统计线程数量 | 🟢 |
| POST /threads/prune | 清理线程 | 🟢 |
| GET /threads/{thread_id}/state | 获取线程状态 | 🟢 |
| POST /threads/{thread_id}/state | 更新线程状态 | 🟢 |
| GET /threads/{thread_id}/state/{checkpoint_id} | 获取指定检查点状态 | 🟢 |
| POST /threads/{thread_id}/state/checkpoint | 获取指定检查点状态 | 🟢 |
| GET /threads/{thread_id}/history | 获取线程历史 | 🟢 |
| POST /threads/{thread_id}/history | 获取线程历史 | 🟢 |
| POST /threads/{thread_id}/copy | 复制线程 | 🟢 |
| GET /threads/{thread_id} | 获取线程 | 🟢 |
| DELETE /threads/{thread_id} | 删除线程 | 🟢 |
| PATCH /threads/{thread_id} | 更新线程 | 🟢 |
| GET /threads/{thread_id}/runs | 列出运行 | 🟢 |
| POST /threads/{thread_id}/runs | 创建后台运行 | 🟢 |
| POST /threads/{thread_id}/runs/crons | 创建线程定时任务 | 🟢 |
| POST /threads/{thread_id}/runs/stream | 创建运行并流式输出 | 🟢 |
| POST /threads/{thread_id}/runs/wait | 创建运行并等待输出 | 🟢 |
| GET /threads/{thread_id}/runs/{run_id} | 获取运行 | 🟢 |
| DELETE /threads/{thread_id}/runs/{run_id} | 删除运行 | 🟢 |
| GET /threads/{thread_id}/runs/{run_id}/join | 等待运行完成 | 🟢 |
| GET /threads/{thread_id}/runs/{run_id}/stream | 加入运行流 | 🟢 |
| POST /threads/{thread_id}/runs/{run_id}/cancel | 取消运行 | 🟢 |
| POST /runs/crons | 创建定时任务 | 🟢 |
| POST /runs/crons/search | 搜索定时任务 | 🟢 |
| POST /runs/crons/count | 统计定时任务 | 🟢 |
| GET /runs/crons/{cron_id} | 获取定时任务 | 🟢 |
| PATCH /runs/crons/{cron_id} | 更新定时任务 | 🟢 |
| DELETE /runs/crons/{cron_id} | 删除定时任务 | 🟢 |
| POST /runs/stream | 创建运行并流式输出 | 🟢 |
| POST /runs/wait | 创建运行并等待输出 | 🟢 |
| POST /runs | 创建后台运行 | 🟢 |
| POST /runs/batch | 批量创建运行 | 🟢 |
| POST /runs/cancel | 取消运行 | 🟢 |
| PUT /store/items | 存储或更新条目 | 🟢 |
| DELETE /store/items | 删除条目 | 🟢 |
| GET /store/items | 获取条目 | 🟢 |
| POST /store/items/search | 搜索或列出条目 | 🟢 |
| POST /store/namespaces | 列出命名空间 | 🟢 |
| POST /a2a/{assistant_id} | A2A协议通信 | 🔴 |
| POST /mcp/ | MCP协议请求 | 🟢 |
| GET /mcp/ | MCP协议流式 | 🟢 |
| DELETE /mcp/ | 终止会话 | 🟢 |
| GET /info | 服务器信息 | 🟢 |
| GET /metrics | 系统指标 | 🟢 |
| GET /docs | API文档 | 🟢 |
| GET /ok | 健康检查 | 🟢 |

