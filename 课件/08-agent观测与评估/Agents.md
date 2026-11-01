## 沟通规范

**非常重要：**

1. 当用户提问时，不能修改任何东西，不能新增任何东西，不能删除任何东西，仅回答用户问题即可
2. 回答问题要言简意赅，不要长篇大论，用户有不明白的地方会自行追问

## 课件规范

- 某些课件以 **Jupyter Notebook** 格式编写
- 使用 VS Code 的 Jupyter 插件运行
- Jupyter 的 Python 解释器必须使用**当前工程的虚拟环境**中的解释器，切勿使用其他环境

## 工程管理

- 使用 **UV** 进行工程管理
- 安装依赖时，统一使用 UV 格式：`uv add <package>`
- **绝对不允许擅自进行 git 操作，除非用户特别要求**
- 当用户要求你在某一个分支上工作时，你首先应该检查该分支是否有对应的工作树；如果有，就应该在工作树上进行工作。

## 工程说明

当前工程使用`langgraph + langchain + deepagent`搭建，通过`agent server`作为运行时

- `Agent Server`的基地址是：`http://localhost/`

  如果访问不了，说明没有启动，你可以自行启动。

- 通过`langgraph dev`启动`Agent Server`
- `Agent Server`的配置在`langgraph.json`中
- 通过`langsmith studio`调试应用
- 该工程使用Langfuse作为观测和评估的平台。

  `langfuse`的基地址是：`http://localhost:3000/`
  - API接口文档：`工程根目录/temp/langfuse-api.yaml`

  需要的时候，你可以访问相应的API接口获取你需要的信息或完成用户要求的功能

如果用户没有特别说明，默认就表示使用`langgraph dev`启动的应用，在`langsmith studio`中进行的调试，跟踪数据在`langfuse上`

**非常重要：**

需要调试的时候，优先通过API接口去获取需要的信息，而不是去调试浏览器。
