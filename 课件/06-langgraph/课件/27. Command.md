# Command

`Command` 是一种控制图执行的底层原语

```python
# 某个节点
def node(state: State):
    return { "foo": "bar" }
  
# 等效于
def node(state: State):
    return Command(
        update={"foo": "bar"}
    )
```

## 位置

`Command`可以用于三个地方：

- 节点返回
- 工具函数返回
- 图调用

### 节点返回

```python
def node(state: State):
    return Command(...)
```

### 工具函数返回

```python
@tool
def search(
  	query: str, 
  	runtime: ToolRuntime[ContextSchema, StateSchema] # 依赖注入
) -> Command:
    return Command(...)
```

- `runtime.tool_call_id` → 当前这次 tool call 的 id
- `runtime.state` → 当前图状态
- `runtime.context` → 传入的 context

### 图调用

```python
graph.invoke(input=Command(...))
```

> 下节课学习

## 参数

`Command`对象中支持四个参数：

- `update`: 更新图状态的指令
- `goto`：指定下一个节点（动态边）
- `graph`：在子图中使用，跳到父图的某个节点
- `resume`：恢复中断，下节课学习



```python
def node(state:State):
   return Command(
   		update={..}, # 更新的状态
      goto="node_b",
      graph=Command.PARENT
   )
```



## 使用方式

| 参数     | 节点返回/工具返回 | 图调用 |
| -------- | ----------------- | ------ |
| `update` | ✅                 | ❌      |
| `goto`   | ✅                 | ❌      |
| `graph`  | ✅（必须在子图中） | ❌      |
| `resume` | ❌                 | ✅      |

## 注意事项

节点的静态边和动态边都会得到执行。