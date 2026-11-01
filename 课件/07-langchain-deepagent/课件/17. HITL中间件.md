# HITL中间件



## 配置中断时机

```python
from langchain.agents.middleware import HumanInTheLoopMiddleware


def format_description(tool_call, state, runtime):
    """根据本次工具调用动态生成审批说明。"""
    return f"即将写入文件：{tool_call['args']['file_path']}"


def should_interrupt(request):
    """只有写入 /home/user 目录时才中断。"""
    return request.tool_call["args"]["file_path"].startswith("/home/user/")


HumanInTheLoopMiddleware(
    interrupt_on={
        # 调用时始终中断，允许 approve、edit、reject、respond
        "write_file": True,

        # 调用时不中断，直接执行
        "read_file": False,

        # 调用时始终中断，但只允许批准或拒绝
        "delete_file": {
            "allowed_decisions": ["approve", "reject"],
            "description": "删除文件前需要人工确认。",
        },

        # 根据本次工具调用的参数，动态决定是否中断
        "edit_file": {
            "allowed_decisions": ["approve", "edit", "reject"],
            "description": format_description,
            "when": should_interrupt,
        },
    },
    # 没有单独配置 description 时，使用这个前缀生成审批说明
    description_prefix="工具执行前需要人工审批",
)
```

## 中断消息格式

```json
{
  "action_requests": [ 		
    {
      "name": "write_file",
      "args": {
        "file_path": "/home/user/notes.md",
        "content": "文件内容"
      },
      "description": "工具执行前需要人工审批……"
    }
  ],
  "review_configs": [
    {
      "action_name": "write_file",
      "allowed_decisions": ["approve", "edit", "reject", "respond"]
    }
  ]
}

```

## 恢复中断的消息格式

### 批准

使用原工具名和原参数继续执行工具。

```json
{
  "decisions": [
    {
      "type": "approve"
    }
  ]
}
```

### 修改后批准

```json
{
  "decisions": [
    {
      "type": "edit",
      "edited_action": {
        "name": "write_file",
        "args": {
          "file_path": "/home/user/notes.md",
          "content": "修改后的文件内容"
        }
      }
    }
  ]
}
```

### 拒绝

跳过本次工具执行。`message` 是可选的拒绝原因，中间件会将它作为失败的 `ToolMessage` 返回给模型。

```json
{
  "decisions": [
    {
      "type": "reject",
      "message": "不允许覆盖该文件，请改用新文件名。"
    }
  ]
}
```

### 代替工具回答

跳过本次工具执行，将 `message` 作为工具的成功返回值交给模型。这种决定适合由人直接回答的工具。

```json
{
  "decisions": [
    {
      "type": "respond",
      "message": "请将文件保存到 /home/user/drafts/notes.md。"
    }
  ]
}
```

