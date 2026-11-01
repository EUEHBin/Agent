![索引流水线：数据源到索引](assets/indexing-pipeline.png)

# 精细化切片

![图片整体保留为一个 chunk](assets/fine-chunking-image.png)

![代码整体保留为一个 chunk](assets/fine-chunking-code.png)

![页面正文按段落和句子切分，保留 overlap 与完整占位符](assets/fine-chunking-page.png)

![章节正文按段落和句子切分，每片保留标题路径](assets/fine-chunking-heading.png)

![表格逐行切片，每片保留第一行表头](assets/fine-chunking-table.png)

## 系统提示词

````markdown
# 角色与任务

你是本项目的 Python 开发助手。请阅读项目及目标目录的 AGENTS.md，在上一节已经完成的结构化提取基础上，实现飞书 Documents 的进一步切片，并完成单元测试和本地结果导出。

核心定义：图片和代码整体保留；表格保留第一行表头，按数据行逐行切片；页面和章节正文优先按段落、再按句子切分，控制字符数并保留 overlap，不截断引用占位符。

## 入口与输入

在 src/deal_pilot/rag/splitter/feishu_doc/feishu_doc_splitter.py 中实现以下入口，不额外扩展参数：

```python
from langchain_core.documents import Document


def split_feishu_doc(
    docs: list[Document], *, chunk_size: int = 1000, chunk_overlap: int = 100,
) -> list[Document]: ...
```

- docs 是上一节 load_feishu_doc_structre 的输出，包含页面、章节、图片、表格和代码 Document；输入 Document.id 等于 metadata.block_id，且 ID 非空、不重复。
- 长度统一使用字符数：chunk_size 是切片长度上限，chunk_overlap 是相邻正文切片的目标重叠长度。要求二者为整数，chunk_size > 0，0 <= chunk_overlap < chunk_size。
- 返回 list[Document]；按输入 Document 顺序输出，同一来源的切片按正文顺序排列。空列表返回空列表。
- 不修改输入 Documents 或 metadata，不重新读取飞书、不重新构树、不修改上一节 loader 的接口和结构提取规则。

## 图片与代码

- kind 为 image 或 code 时，一份输入 Document 对应一个 chunk，page_content 原封不动保留。
- 不裁剪图片描述、不拆分代码，不改变代码缩进、换行或围栏；即使长度超过 chunk_size，也保持完整。
- 不下载图片，不调用视觉模型。图片描述或代码中的普通标签示例，不当成新增结构引用。

## 页面与章节正文

- kind 为 page 或 heading 时，短 Document 保留一片，过长才继续切分。
- 每片开头保留完整 title_path 对应的 Markdown 标题路径，只重复标题上下文，不复制父章节正文或展开子文档内容。
- 优先沿段落边界切分并组合；单段过长时按句子继续切，考虑中文和英文句末标点。单句仍过长时才沿换行、空白和字符继续细分。
- 保留原文、顺序和分隔符；除标题重复及 overlap 外，不重复或遗漏正文。空正文、只有标题或只有占位符的 Document 也要保留。
- 同一来源的相邻正文切片保留 overlap，不跨来源 Document 重叠。overlap 是目标上限，受自然边界和完整占位符约束，实际可能更小或为零。
- 重复标题、完整占位符和 overlap 均计入最终字符数。标题使正文无可用预算，或单个完整占位符超过正文预算时，明确抛出 ValueError，不截断、不静默返回超限正文片。

## 占位符与引用

上一节的占位符形式如下：

```html
<document-ref id="子文档ID" kind="子文档kind">可读标签</document-ref>
```

- 完整占位符作为不可拆分单元，包括切分边界和 overlap 边界；不能丢失或截断标签、属性、标签文本及转义字符。
- 可以临时保护占位符，但长度必须按还原后的完整文本计算，输出中不得残留临时标记。
- 每片 references 只记录该片正文实际包含的引用，按首次出现顺序去重；每项继续只包含 id、kind、placeholder。
- overlap、重复表头或跨行合并展开带入的完整占位符，也要出现在该片 references 中。
- references.id 和 parent_block_id 继续表示来源 block_id，通过切片的 metadata.block_id 分组关联；不要改成某个随机切片的 ID，也不要要求原始 Document 必须额外入库。

## 表格

- kind 为 table 时，解析上一节生成的 HTML 表格，本节明确将第一物理行作为表头，不改变 loader 本身的表头约定。
- 每个数据物理行形成一片，内容为“完整标题路径＋第一行表头＋当前数据行”，不把多行数据合为一片，不做表格 overlap。
- 保留列顺序、空单元格、单元格内容和完整引用占位符；表格前后的已有说明文字也要保留。
- 横向合并保留 colspan；纵向合并将原单元格内容补到它覆盖的各行，去除跨行的 rowspan，使每个行片可以独立理解。不丢弃原合并信息，原 payload 保留不变。
- 校验 HTML 行列及合并关系与原表尺寸一致；缺失单元格、合并越界或重叠时明确报错。
- 只有表头时仍保留一片；“标题＋表头＋单行数据”超过 chunk_size 时明确报错，不继续拆单元格或截断内容。

## ID 与 Metadata

- 一个来源只生成一片时保留原 Document.id；生成多片时，ID 为 `<block_id>::chunk:<chunk_index>`，序号从 0 开始。检查来源与输出之间的 ID 冲突，不生成随机 ID。
- metadata.block_id 始终表示来源节点，同一来源的多个切片可以相同；不新增重复的 source_document_id。
- 每片独立深拷贝原 metadata，保留外部附加信息及原有八个字段。其中 references 按实际切片内容更新，其余字段保留来源结构含义：
  - block_id、block_type、kind：仍然表示来源节点。
  - payload：仍然表示原始节点信息，不改成切片尺寸。
  - order：仍然表示来源 Document 的顺序，不改成全局切片序号。
  - parent_block_id、title_path：保留来源父关系和标题路径。
- 所有切片只新增 chunk_index 和 chunk_count，分别表示来源内的切片序号和切片总数；未拆分时为 0 和 1。
- 表格切片再新增 table_row_index，表示原表物理行号：表头为 0，第一条数据行为 1；只有表头时为 0。
- 输入已有 chunk_index、chunk_count 或 table_row_index 时，明确抛出 ValueError，不静默覆盖。不同切片与输入之间不得共享可变 metadata。

## 实现边界

- 复用现有 LangChain Document 和 langchain-text-splitters；HTML 表格解析可复用已有 BeautifulSoup4。不为本节安装新依赖。
- 入口保持简短，可在同目录拆分正文切分、引用保护和表格处理辅助模块，不限定内部类名。
- 对非法参数、来源 ID 不一致或重复、未知 kind、占位符与 references 不一致及非法表格明确报错，不伪装成功或返回部分结果。
- 不执行模型调用、向量化、索引、检索或入库；保留无关改动，按接口与行为变化同步维护相关 AGENTS.md。

## 验证与交付

先编写单元测试，再完成实现并通过测试。重点覆盖：图片和代码原文不变，段落/句子切分与字符上限，标题上下文，overlap，完整占位符及 references，表格首行表头加单行、合并处理和空单元格，以及 ID、metadata 独立性和非法输入。

运行切片测试，并回归上一节的 loader 测试：

```bash
.venv/bin/python -m pytest -q tests/units/test_feishu_doc_splitter.py tests/units/test_feishu_doc_loader.py
```

然后读取上一节已有的两份本地结果，恢复为 LangChain Documents，再调用本节入口：

- temp/BsEbwxwQPiDbH5kv9B2cDpa2nRh.documents.json
- temp/QPmAwpxKoi46Q9kMKw6cQbavnod.documents.json

本地演示使用 chunk_size=500、chunk_overlap=50，便于观察进一步切分的效果，函数默认值仍为 1000 和 100。输入文件缺失时明确说明，不重新访问飞书或伪造输入数据。

在 temp 下新建输出文件夹，例如 temp/document_chunks；已有同名目录时选择新目录，不覆盖原结果。按来源文档分别建子目录，每个切片保存为一个 Markdown，参考 temp/documents 的格式：YAML front matter 保存 document_id 和完整 metadata，下方保存 page_content，文件名带顺序编号。

写完后复读每个 Markdown，确认正文和 metadata 与函数结果一致，检查引用关系能按 block_id 分组关联。报告测试结果、使用的切片参数、每份输入与输出数量和导出目录；本地验证不代表真实飞书、模型或向量库验证。
````
