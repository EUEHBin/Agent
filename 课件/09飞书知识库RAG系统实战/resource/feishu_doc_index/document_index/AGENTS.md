# 单文档索引教学骨架

- 本目录保存单文档子图的课堂填空材料；正式实现位于 `src/deal_pilot/graphs/feishu_doc_index/document_index`，不要将两者的完成状态混用。
- `state.py` 定义包含来源节点、版本比较、中间数据、写入数与 success/skipped 状态的 DocumentIndexState；root 使用正式包的 BlockNodeDict，省略循环引用。
- 本地 `nodes.py` 中所有业务函数和版本路由均抛出 NotImplementedError，尚未实现版本读取、比较、metadata、正文读取、结构化、Loader、Splitter、写入、删除及收尾。
- `graph.py` 展示完整的节点顺序和条件边，但节点函数及状态均从 `deal_pilot.graphs.feishu_doc_index.document_index...` 导入，使用的是正式包，不是本地占位节点。不能通过该图调用结果证明本目录函数已实现。
- 教学目标流程为版本读取 → 比较 → 跳过或解析、切片、写入、旧版本清理 → 收尾；这是骨架的目标，实际运行契约以正式模块指令和源码为准。按课堂要求保留占位，不自动复制正式实现。
- 当前没有对应的专门自动化测试，不能引用不存在的 `tests/units/test_feishu_doc_index.py` 或宣称已有结构化到 Loader 的 Mock / 检查点覆盖。
