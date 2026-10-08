# 多智能体协同调研系统

一个基于异步编程的多智能体协作系统，利用 AI 自动完成调研任务的分解、并行执行、结果汇总和报告生成。

## 模块概览

```
main.py → orchestrator.py → decomposer.py → ai_tools.py → config.py
                         → worker.py     → ai_tools.py
                         → merger.py
                         → summarizer.py → ai_tools.py
                         → reporter.py   → config.py
```

### 各模块说明

#### config.py
配置模块，从 `.env` 文件加载 API 地址、模型名称、API Key 和输出目录等全局配置。

**依赖**: 无内部依赖；外部依赖 `python-dotenv`

#### ai_tools.py
AI API 通信层。封装了与 LLM 模型的流式对话交互，对外暴露两个异步函数：
- `completions()` — 流式返回生成内容
- `get_text()` — 非流式返回完整文本

**依赖**: `config.py`

#### decomposer.py
任务分解器。将用户输入的调研需求，通过 AI 拆分为 3-5 个相互独立的子任务，返回字符串列表。

**依赖**: `ai_tools.py`

#### worker.py
子任务执行器。接收一个子任务描述，调用 AI 进行调研并返回结果文本。

**依赖**: `ai_tools.py`

#### merger.py
结果合并器。纯函数模块，将调研主题、子任务列表和各个结果合并为一个 Markdown 格式的文档。

**依赖**: 无

#### summarizer.py
报告总结器。将合并后的内容通过 AI 整合为一份结构清晰、内容完整的调研报告。

**依赖**: `ai_tools.py`

#### reporter.py
报告保存器。将最终生成的报告异步写入文件系统，文件名包含主题和时间戳。

**依赖**: `config.py`；外部依赖 `aiofiles`

#### orchestrator.py
流程编排器。编排完整的调研流程：任务分解 → 并行执行子任务 → 合并结果 → AI 总结 → 保存报告。使用 `asyncio.gather` 实现子任务的并发执行。

**依赖**: `decomposer.py`, `worker.py`, `merger.py`, `summarizer.py`, `reporter.py`

#### main.py
程序入口。从命令行接收用户输入的调研主题，调用编排器执行完整流程。

**依赖**: `orchestrator.py`

## 依赖关系图

```
config.py
  ├── ai_tools.py
  │     ├── decomposer.py
  │     ├── worker.py
  │     └── summarizer.py
  └── reporter.py

merger.py (纯函数，无依赖)

orchestrator.py
  ├── decomposer.py
  ├── worker.py
  ├── merger.py
  ├── summarizer.py
  └── reporter.py

main.py
  └── orchestrator.py
```

## 建议阅读顺序

按依赖层级从底层向上阅读，能最快理解整个系统：

| 顺序 | 模块 | 理由 |
|------|------|------|
| 1 | `config.py` | 最底层，无内部依赖，了解全局配置 |
| 2 | `ai_tools.py` | 核心通信层，理解如何与 AI API 交互 |
| 3 | `merger.py` | 纯函数，无异步逻辑，最简单的模块 |
| 4 | `reporter.py` | 异步文件操作，理解 `aiofiles` 的用法 |
| 5 | `worker.py` | 单个子任务的执行逻辑 |
| 6 | `decomposer.py` | 理解如何将大任务拆分为子任务 |
| 7 | `summarizer.py` | 理解如何将分散结果整合为报告 |
| 8 | `orchestrator.py` | **核心模块**，理解完整的流程编排和并发控制 |
| 9 | `main.py` | 入口，收尾了解 |

模块本身按**架构分层**从底层到高层组织，先读底层（配置、工具函数）再读高层（编排器、入口），顺序阅读即可。

## 运行方式

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 API_KEY 等信息

# 3. 运行
python -m src.main
```
