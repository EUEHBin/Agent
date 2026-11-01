# 认识 Agent

## 创建 Agent

```python
# 创建一个编译好的图
agent = create_agent(
    model="anthropic:qwen3.7-plus", # 必填，Provider:Model Name
)
```

## 选填参数

| 参数名           | 含义                                        | 默认                   |
| ---------------- | ------------------------------------------- | ---------------------- |
| `tools`          | 工具列表                                    | 无工具                 |
| `system_prompt`  | 系统提示词                                  | 无系统提示词           |
| `state_schema`   | 图状态的数据结构                            | 只有一个`messages`字段 |
| `context_schema` | context结构                                 | 无                     |
| `checkpointer`   | 检查点存储方案<br />使用AgentServer无须传递 | 无检查点               |
| `store`          | store存储方案<br />使用AgentServer无须传递  | 无store                |

