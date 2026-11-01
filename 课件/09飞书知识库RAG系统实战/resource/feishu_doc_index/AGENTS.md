# 飞书文档索引教学骨架

- 本目录配合 `课件/29. LangGraph实现索引流水线.md` 保存课堂填空骨架；正式运行实现为 `src/deal_pilot/graphs/feishu_doc_index`，服务入口只注册正式实现。
- `state.py` 定义并发 Context、使用 add reducer 的统计状态及字符串失败记录列表；状态类型通过 `deal_pilot.graphs...` 导入时仍来自正式包。
- `graph.py:async factory()` 仅组装 fetch_batch、index_document 及其连边；两个内部节点函数体都是省略号，未创建目录迭代器、未取批、未调用子图，也未导出 factory_with_trace。导入 trace_wrapper 不代表已接通追踪。
- 不将本目录说明成可运行的索引流程，不将正式源码的实现状态或验证结果直接移植到教学骨架。保留教学占位，填充函数或迁移代码须在用户授权的开发范围内进行。
- `document_index/` 保存子图连边、状态和业务节点占位；其导入仍指向正式包，局部边界见下级指令。本目录不是不依赖 src 的独立实现。
- 当前没有本目录专门测试，`tests/units/test_feishu_doc_index.py` 不存在。检查时核对占位、导入和课件路径，不能以构图或源码阅读声称完成真实入库。
